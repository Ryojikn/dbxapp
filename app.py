import os
import json as _json
import time as _time

from dotenv import load_dotenv
load_dotenv()  # loads .env file for local dev; no-op in Databricks Apps

from flask import request, Response, stream_with_context

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from theme import THEME
import tabs.home         as home_tab
import tabs.architecture as arch_tab
import tabs.dashboard    as dash_tab
import callbacks.navigation   as nav_cb
import callbacks.architecture as arch_cb
import callbacks.chat         as chat_cb
import callbacks.theme        as theme_cb
import callbacks.dashboard    as dash_anim_cb

app = dash.Dash(
    __name__,
    external_stylesheets=[THEME],
    suppress_callback_exceptions=True,
    title="Databricks Platform Demo",
)

server = app.server


# ── SSE streaming endpoint ───────────────────────────────────────────────────

@server.route('/api/chat-stream', methods=['POST'])
def _chat_stream():
    """Server-Sent Events: streams LLM tokens (live) or fixture words (demo) to the browser."""
    payload  = request.get_json(silent=True) or {}
    question = (payload.get('question') or '').strip()
    history  = payload.get('history') or []

    demo_mode = os.environ.get('DEMO_MODE', 'fixture')
    endpoint  = os.environ.get('DATABRICKS_SERVING_ENDPOINT', '')

    def generate():
        if demo_mode != 'live' or not endpoint:
            # Fixture mode: stream canned response word-by-word so the typewriter effect is visible
            from data.fixtures import KPI_SUMMARY, CHAT_QA
            from data.chat import match_rule, render_response, get_chat_rules
            rules  = get_chat_rules()
            rule   = match_rule(question, rules)
            answer = render_response(rule, KPI_SUMMARY, CHAT_QA)
            words  = answer.split(' ')
            for i, word in enumerate(words):
                token = ('' if i == 0 else ' ') + word
                yield f"data: {_json.dumps({'token': token})}\n\n"
                _time.sleep(0.025)
            yield 'data: [DONE]\n\n'
            return

        # Live mode: stream from Databricks Model Serving
        # chat_cb._SYSTEM_PROMPT is built at import time from KPI_SUMMARY
        messages = [{'role': 'system', 'content': chat_cb._SYSTEM_PROMPT}]
        for turn in history[-6:]:
            messages.append({'role': turn['role'], 'content': turn['content']})
        messages.append({'role': 'user', 'content': question})

        try:
            import requests as _requests
            from databricks.sdk import WorkspaceClient
            w    = WorkspaceClient()
            host = w.config.host.rstrip('/')
            auth = w.config.authenticate()
            print(f"[chat-stream] host={host!r} endpoint={endpoint!r} auth_keys={list(auth.keys())}", flush=True)

            with _requests.post(
                f"{host}/serving-endpoints/{endpoint}/invocations",
                headers={**auth, 'Content-Type': 'application/json'},
                json={'messages': messages, 'max_tokens': 300, 'temperature': 0.1, 'stream': True},
                stream=True,
                timeout=30,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    line = line.decode('utf-8') if isinstance(line, bytes) else line
                    if not line.startswith('data: '):
                        continue
                    data_str = line[6:].strip()
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = _json.loads(data_str)
                        token = chunk['choices'][0]['delta'].get('content', '')
                        if token:
                            yield f"data: {_json.dumps({'token': token})}\n\n"
                    except Exception:
                        pass

        except Exception as exc:
            import traceback
            traceback.print_exc()
            yield f"data: {_json.dumps({'error': str(exc)})}\n\n"

        yield 'data: [DONE]\n\n'

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control':     'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection':        'keep-alive',
        },
    )


# ── Layout ──────────────────────────────────────────────────────────────────

_HEADER = dbc.Navbar(
    dbc.Container([
        html.A(
            html.Span([
                html.Span(className="brand-mark"),
                "Databricks Platform Demo",
            ], className="navbar-brand"),
            href="#",
            style={"textDecoration": "none"},
        ),
        html.Span(
            "Medallion Architecture · Unity Catalog · AI/BI",
            className="navbar-subtitle d-none d-md-inline",
        ),
        html.Div(
            dbc.Button(
                html.Span(id="theme-toggle-label", children="Light"),
                id="theme-toggle",
                n_clicks=0,
                className="theme-toggle-btn",
            ),
            className="ms-auto",
        ),
    ], fluid=True),
    color="dark",
    dark=True,
    className="mb-0 py-2",
)

app.layout = html.Div([
    _HEADER,
    dcc.Store(id="tab-state-store", storage_type="memory"),
    dcc.Store(id="theme-store",     storage_type="local", data="dark"),
    dbc.Container(
        dcc.Tabs(
            id="app-tabs",
            value="tab-home",
            className="mt-0",
            children=[
                dcc.Tab(
                    label="Home",
                    value="tab-home",
                    children=home_tab.layout(),
                    className="app-tab",
                    selected_className="app-tab app-tab--active",
                ),
                dcc.Tab(
                    label="Architecture",
                    value="tab-architecture",
                    children=arch_tab.layout(),
                    className="app-tab",
                    selected_className="app-tab app-tab--active",
                ),
                dcc.Tab(
                    label="Dashboard",
                    value="tab-dashboard",
                    children=dash_tab.layout(),
                    className="app-tab",
                    selected_className="app-tab app-tab--active",
                ),
            ],
        ),
        fluid=True,
    ),
], style={"minHeight": "100vh"})

# ── Register callbacks ──────────────────────────────────────────────────────
nav_cb.register(app)
arch_cb.register(app)
chat_cb.register(app)
theme_cb.register(app)
dash_anim_cb.register(app)

# ── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
