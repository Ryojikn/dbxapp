"""
Chat callback for the Dashboard tab.
Streaming via /api/chat-stream (SSE). The clientside callback handles
the full send/stream/render cycle so the UI updates as tokens arrive.
"""

from __future__ import annotations

import os

import dash
from dash import Input, Output, State

from data.fixtures import KPI_SUMMARY

_SERVING_ENDPOINT = os.environ.get("DATABRICKS_SERVING_ENDPOINT", "")

_SYSTEM_PROMPT = (
    "You are a data analytics assistant embedded in a retail e-commerce dashboard. "
    "Respond only to questions about the data below. "
    "If greeted or asked something unrelated to the data, reply with one short sentence "
    "inviting the user to ask about revenue, categories, orders, or anomalies — nothing else. "
    "When answering data questions, be direct and concise: 2-3 sentences maximum. "
    "Cite specific numbers from the dataset. Do not repeat every metric in every answer. "
    "Do not use markdown headers or bullet lists unless the question explicitly asks for a breakdown.\n\n"
    "Dataset — March 2025 (MTD):\n"
    f"- Total Revenue: ${KPI_SUMMARY['total_revenue_mtd']:,.0f} "
    f"(+{KPI_SUMMARY['revenue_mom_pct']:.0f}% vs February)\n"
    f"- Total Orders: {KPI_SUMMARY['total_orders_mtd']:,} | "
    f"Avg Order Value: ${KPI_SUMMARY['avg_order_value_mtd']:,.2f}\n"
    f"- Top Category: {KPI_SUMMARY['top_category']} "
    f"(${KPI_SUMMARY['top_category_revenue']:,.0f} revenue)\n"
    f"- Fastest Growing: {KPI_SUMMARY['fastest_growing_category']} "
    f"(+{KPI_SUMMARY['fastest_growing_qoq_pct']:.0f}% QoQ)\n"
    f"- Active Anomalies: {KPI_SUMMARY['active_anomaly_count']} — "
    "Electronics COGS spike on March 18: margin dropped from 23% to 6%, "
    "linked to bulk order ORD-48821 (COGS +340% vs 7-day avg). "
    "Recommended action: audit ORD-48821 and review Electronics cost records for March 16-20."
)

# ── Clientside callback — async Promise, handles streaming entirely in JS ───

_STREAM_FN = """
async function(nClicks, nSubmit, question, history) {
    var dc = window.dash_clientside;

    if (!question || !question.trim()) {
        return [dc.no_update, dc.no_update, dc.no_update];
    }

    question = question.trim();
    history  = history || [];

    var el = document.getElementById('dash-chat-messages');
    if (!el) return [dc.no_update, dc.no_update, dc.no_update];

    /* Clear input immediately */
    var inputEl = document.getElementById('dash-chat-input');
    if (inputEl) inputEl.value = '';

    /* Remove intro placeholder on first send */
    var intro = el.querySelector('.chat-intro');
    if (intro) intro.remove();

    /* User bubble — appears immediately */
    var userEl = document.createElement('div');
    userEl.className = 'chat-bubble chat-bubble--user';
    userEl.textContent = question;
    el.appendChild(userEl);

    /* Typing indicator — three bouncing dots */
    var assistantEl = document.createElement('div');
    assistantEl.className = 'chat-bubble chat-bubble--assistant chat-typing';
    assistantEl.innerHTML = '<span></span><span></span><span></span>';
    el.appendChild(assistantEl);
    el.scrollTop = el.scrollHeight;

    var fullText = '';
    var streaming = false;

    try {
        var resp = await fetch('/api/chat-stream', {
            method:  'POST',
            headers: {'Content-Type': 'application/json'},
            body:    JSON.stringify({question: question, history: history}),
        });

        if (!resp.ok) throw new Error('HTTP ' + resp.status);

        var reader  = resp.body.getReader();
        var decoder = new TextDecoder();
        var buf     = '';
        var done    = false;

        while (!done) {
            var chunk = await reader.read();
            if (chunk.done) break;

            buf += decoder.decode(chunk.value, {stream: true});
            var lines = buf.split('\\n');
            buf = lines.pop();

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                if (!line.startsWith('data: ')) continue;

                var payload = line.slice(6).trim();
                if (payload === '[DONE]') { done = true; break; }

                var parsed;
                try { parsed = JSON.parse(payload); } catch (e) { continue; }

                if (parsed.error) {
                    assistantEl.classList.remove('chat-typing', 'chat-streaming');
                    assistantEl.textContent = 'Could not reach the model — try again.';
                    fullText = assistantEl.textContent;
                    done = true;
                    break;
                }

                if (parsed.token) {
                    if (!streaming) {
                        assistantEl.classList.remove('chat-typing');
                        assistantEl.classList.add('chat-streaming');
                        assistantEl.textContent = '';
                        streaming = true;
                    }
                    fullText += parsed.token;
                    assistantEl.textContent = fullText;
                    el.scrollTop = el.scrollHeight;
                }
            }
        }

    } catch (err) {
        assistantEl.classList.remove('chat-typing', 'chat-streaming');
        assistantEl.textContent = 'Connection error — check your configuration.';
        fullText = assistantEl.textContent;
    }

    assistantEl.classList.remove('chat-streaming');

    var newHistory = history.concat([
        {role: 'user',      content: question},
        {role: 'assistant', content: fullText || '(no response)'},
    ]).slice(-20);

    /* Leave the DOM as-is (imperative bubbles own the display).
       Only update the store and clear the input — returning children
       here would cause React to double-render the bubbles. */
    return [dc.no_update, newHistory, ''];
}
"""


def register(app: dash.Dash) -> None:
    app.clientside_callback(
        _STREAM_FN,
        Output("dash-chat-messages", "children"),
        Output("dash-chat-store",    "data"),
        Output("dash-chat-input",    "value"),
        Input("dash-chat-send",  "n_clicks"),
        Input("dash-chat-input", "n_submit"),
        State("dash-chat-input", "value"),
        State("dash-chat-store", "data"),
        prevent_initial_call=True,
    )
