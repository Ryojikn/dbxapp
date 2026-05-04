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

def _sse_response(gen_fn):
    return Response(
        stream_with_context(gen_fn()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no', 'Connection': 'keep-alive'},
    )


def _stream_text(text: str):
    """Yield SSE token events for *text* word-by-word, then DONE."""
    words = text.split(' ')
    for i, word in enumerate(words):
        token = ('' if i == 0 else ' ') + word
        yield f"data: {_json.dumps({'token': token})}\n\n"
        _time.sleep(0.022)
    yield 'data: [DONE]\n\n'


@server.route('/api/chat-stream', methods=['POST'])
def _chat_stream():
    """SSE: routes to Genie API, Model Serving, or fixture mode."""
    payload       = request.get_json(silent=True) or {}
    question      = (payload.get('question') or '').strip()
    history       = payload.get('history') or []
    genie_conv_id = payload.get('genie_conv_id') or None

    genie_space_id = os.environ.get('GENIE_SPACE_ID', '')
    demo_mode      = os.environ.get('DEMO_MODE', 'fixture')
    endpoint       = os.environ.get('DATABRICKS_SERVING_ENDPOINT', '')

    # ── Mode 1: Genie Conversation API ──────────────────────────────────────
    if genie_space_id:
        def _genie_gen():
            try:
                from databricks.sdk import WorkspaceClient
                w = WorkspaceClient()

                if genie_conv_id:
                    msg = w.genie.create_message(
                        space_id=genie_space_id,
                        conversation_id=genie_conv_id,
                        content=question,
                    )
                    conv_id = genie_conv_id
                else:
                    conv = w.genie.start_conversation(
                        space_id=genie_space_id,
                        content=question,
                    )
                    msg     = conv
                    conv_id = conv.conversation_id

                # Poll until the message is complete (max 120 s)
                message_id = msg.message_id
                import time as _t
                deadline = _t.time() + 120
                while _t.time() < deadline:
                    current = w.genie.get_message(
                        space_id=genie_space_id,
                        conversation_id=conv_id,
                        message_id=message_id,
                    )
                    state = str(current.status).upper()
                    if 'COMPLETED' in state or 'FAILED' in state or 'CANCELLED' in state:
                        break
                    _t.sleep(1.5)

                # Extract text answer from attachments
                text = None
                if current.attachments:
                    for att in current.attachments:
                        if hasattr(att, 'text') and att.text and att.text.content:
                            text = att.text.content
                            break
                if not text:
                    text = "Genie returned a result but no text summary was included."

                # Emit the conversation_id so the JS can send it on the next turn
                yield f"data: {_json.dumps({'meta': {'genie_conv_id': conv_id}})}\n\n"
                yield from _stream_text(text)

            except Exception as exc:
                import traceback; traceback.print_exc()
                yield f"data: {_json.dumps({'error': str(exc)})}\n\n"
                yield 'data: [DONE]\n\n'

        return _sse_response(_genie_gen)

    # ── Mode 2: Fixture / keyword-matched demo ───────────────────────────────
    if demo_mode != 'live' or not endpoint:
        def _fixture_gen():
            from data.live import ALLBANK_DATA
            from data.chat import match_rule, render_response, get_chat_rules
            rules  = get_chat_rules()
            rule   = match_rule(question, rules)
            answer = render_response(rule, ALLBANK_DATA['kpi'], ALLBANK_DATA.get('chat_qa', {}))
            yield from _stream_text(answer)

        return _sse_response(_fixture_gen)

    # ── Mode 3: Databricks Model Serving (LLM) ───────────────────────────────
    def _llm_gen():
        messages = [{'role': 'system', 'content': chat_cb._SYSTEM_PROMPT}]
        for turn in history[-6:]:
            if turn.get('role') in ('user', 'assistant'):
                messages.append({'role': turn['role'], 'content': turn['content']})
        messages.append({'role': 'user', 'content': question})

        try:
            import requests as _requests
            from databricks.sdk import WorkspaceClient
            w    = WorkspaceClient()
            host = w.config.host.rstrip('/')
            auth = w.config.authenticate()

            with _requests.post(
                f"{host}/serving-endpoints/{endpoint}/invocations",
                headers={**auth, 'Content-Type': 'application/json'},
                json={'messages': messages, 'max_tokens': 300, 'temperature': 0.1, 'stream': True},
                stream=True, timeout=30,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    line = line.decode('utf-8') if isinstance(line, bytes) else line
                    if not line.startswith('data: '):
                        continue
                    ds = line[6:].strip()
                    if ds == '[DONE]':
                        break
                    try:
                        token = _json.loads(ds)['choices'][0]['delta'].get('content', '')
                        if token:
                            yield f"data: {_json.dumps({'token': token})}\n\n"
                    except Exception:
                        pass

        except Exception as exc:
            import traceback; traceback.print_exc()
            yield f"data: {_json.dumps({'error': str(exc)})}\n\n"

        yield 'data: [DONE]\n\n'

    return _sse_response(_llm_gen)


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
            "AllBank · Lakeflow Pipelines · Unity Catalog · AI/BI Genie",
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
