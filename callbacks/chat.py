"""
Chat callback for the Dashboard tab.
Registers a single callback that handles both keyboard-submit and button-click.
Supports DEMO_MODE=fixture (default) and DEMO_MODE=live (Databricks Model Serving).
"""

from __future__ import annotations

import json
import logging
import os

import dash
from dash import Input, Output, State, html
import dash_bootstrap_components as dbc

from data.fixtures import KPI_SUMMARY, CHAT_QA
from data.chat import get_chat_rules, match_rule, render_response

logger = logging.getLogger(__name__)

_DEMO_MODE        = os.environ.get("DEMO_MODE", "fixture")
_DATABRICKS_HOST  = os.environ.get("DATABRICKS_HOST", "")
_SERVING_ENDPOINT = os.environ.get("DATABRICKS_SERVING_ENDPOINT", "")
_TOKEN            = os.environ.get("DATABRICKS_TOKEN", "")

_RULES = get_chat_rules()

_SYSTEM_PROMPT = (
    "You are a data analytics assistant for a retail e-commerce platform. "
    f"Current March 2025 metrics: "
    f"Total MTD Revenue: ${KPI_SUMMARY['total_revenue_mtd']:,.0f} "
    f"(+{KPI_SUMMARY['revenue_mom_pct']:.0f}% MoM). "
    f"Total Orders: {KPI_SUMMARY['total_orders_mtd']:,}. "
    f"Avg Order Value: ${KPI_SUMMARY['avg_order_value_mtd']:,.2f}. "
    f"Top category: {KPI_SUMMARY['top_category']} "
    f"(${KPI_SUMMARY['top_category_revenue']:,.0f}). "
    f"Fastest growing: {KPI_SUMMARY['fastest_growing_category']} "
    f"(+{KPI_SUMMARY['fastest_growing_qoq_pct']:.0f}% QoQ). "
    f"Active anomalies: {KPI_SUMMARY['active_anomaly_count']} — "
    "Electronics COGS spike on March 18 (margin 23%→6%, order ORD-48821). "
    "Answer concisely and reference these numbers."
)


def _bubble(role: str, text: str) -> html.Div:
    is_user = role == "user"
    return html.Div(
        text,
        style={
            "alignSelf":      "flex-end"   if is_user else "flex-start",
            "background":     "#E04B2A"    if is_user else "#F1F3F4",
            "color":          "white"      if is_user else "#212529",
            "borderRadius":   "12px 12px 2px 12px" if is_user else "12px 12px 12px 2px",
            "padding":        "8px 12px",
            "maxWidth":       "90%",
            "fontSize":       "12px",
            "lineHeight":     "1.5",
            "wordBreak":      "break-word",
        },
    )


def _call_model_serving(question: str, history: list[dict]) -> str | None:
    if not _DATABRICKS_HOST or not _SERVING_ENDPOINT or not _TOKEN:
        return None
    try:
        import requests as _requests  # local import to keep startup fast in fixture mode
        messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
        for turn in history[-6:]:  # last 6 turns for context
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": question})
        resp = _requests.post(
            f"{_DATABRICKS_HOST}/serving-endpoints/{_SERVING_ENDPOINT}/invocations",
            headers={
                "Authorization": f"Bearer {_TOKEN}",
                "Content-Type":  "application/json",
            },
            json={"messages": messages, "max_tokens": 300, "temperature": 0.1},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        logger.warning("Model Serving call failed: %s", exc)
        return None


def register(app: dash.Dash) -> None:

    @app.callback(
        Output("dash-chat-messages", "children"),
        Output("dash-chat-store",    "data"),
        Output("dash-chat-input",    "value"),
        Input("dash-chat-send",  "n_clicks"),
        Input("dash-chat-input", "n_submit"),
        State("dash-chat-input", "value"),
        State("dash-chat-store", "data"),
        prevent_initial_call=True,
    )
    def handle_chat(n_clicks, n_submit, question, history):
        if not question or not question.strip():
            return dash.no_update, dash.no_update, dash.no_update

        question = question.strip()
        history  = history or []

        # ---- determine response ------------------------------------------
        rule = match_rule(question, _RULES)

        if rule["is_anomaly_rule"]:
            # Anomaly always uses fixture response regardless of DEMO_MODE
            answer = render_response(rule, KPI_SUMMARY, CHAT_QA)
        elif _DEMO_MODE == "live":
            answer = _call_model_serving(question, history) or render_response(rule, KPI_SUMMARY, CHAT_QA)
        else:
            answer = render_response(rule, KPI_SUMMARY, CHAT_QA)

        # ---- update history (keep last 20 turns) -------------------------
        history = (history + [
            {"role": "user",      "content": question},
            {"role": "assistant", "content": answer},
        ])[-20:]

        # ---- render bubbles -----------------------------------------------
        bubbles = []
        for turn in history:
            bubbles.append(_bubble(turn["role"], turn["content"]))

        return bubbles, history, ""
