"""
Chat callback for the Dashboard tab.
Streaming via /api/chat-stream (SSE). The clientside callback handles
the full send/stream/render cycle so the UI updates as tokens arrive.
"""

from __future__ import annotations

import os

import dash
from dash import Input, Output, State

from data.live import ALLBANK_DATA as _D

_SERVING_ENDPOINT = os.environ.get("DATABRICKS_SERVING_ENDPOINT", "")

_kpi = _D["kpi"]
_SYSTEM_PROMPT = (
    "You are a data analytics assistant embedded in the AllBank executive dashboard. "
    "AllBank is a fictional financial institution. "
    "Respond only to questions about the AllBank data below. "
    "If greeted or asked something unrelated to the data, reply with one short sentence "
    "inviting the user to ask about churn risk, account balances, transactions, or dormant accounts. "
    "When answering data questions, be direct and concise: 2-3 sentences maximum. "
    "Cite specific numbers. Do not use markdown headers or bullet lists unless the user asks.\n\n"
    "AllBank Dataset — Q1 2026 snapshot:\n"
    f"- Total Customers: {int(_kpi.get('total_customers', 2000)):,} "
    f"({int(_kpi.get('churned_customers', 385)):,} churned to date)\n"
    f"- High-Risk Churn Segment: {int(_kpi.get('high_risk_churn', 560)):,} customers\n"
    f"- ML Model Predicted Churners: {int(_kpi.get('predicted_churners', 77))} "
    f"({float(_kpi.get('churn_rate_pct', 19.3)):.1f}% of scored customers)\n"
    f"- Avg Credit Score: {int(_kpi.get('avg_credit_score', 647))}\n"
    f"- Total AUM: ${float(_kpi.get('total_aum', 24_447_921)) / 1e6:.1f}M across all account types\n"
    f"- Total Accounts: {int(_kpi.get('total_accounts', 4178)):,} "
    f"({int(_kpi.get('active_accounts', 2789)):,} active, "
    f"{int(_kpi.get('dormant_accounts', 766)):,} dormant)\n"
    "- Transaction Volume (Apr 2026): $39.5M across 39,517 transactions — "
    "up from $6.5M in May 2025, showing strong growth.\n"
    "- Account mix: Loan ($10.2M), CD ($5.9M), Checking ($4.1M), Savings ($3.3M), Credit Card ($0.95M)\n"
    "- Top churn risk factors: high overdraft count, long inactivity, negative NPS score, low credit score."
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
    genie_url = os.environ.get("GENIE_SPACE_URL", "")
    if genie_url:
        # Genie iframe is rendered instead of the chat panel; no callbacks needed.
        return

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
