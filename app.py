# Architecture diagram: dash_cytoscape with preset layout and interactive node detail panel.
import os

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

app = dash.Dash(
    __name__,
    external_stylesheets=[THEME],
    suppress_callback_exceptions=True,
    title="Databricks Platform Demo",
)

# Expose Flask server for gunicorn: `gunicorn app:server`
server = app.server

# ── Layout ──────────────────────────────────────────────────────────────────

_HEADER = dbc.Navbar(
    dbc.Container([
        html.Span("⬡ Databricks Platform Demo", className="navbar-brand fw-bold fs-5"),
        html.Span("Medallion Architecture · Unity Catalog · AI/BI", className="text-white-50 small d-none d-md-inline"),
    ], fluid=True),
    color="dark",
    dark=True,
    className="mb-0 py-2",
)

app.layout = html.Div([
    _HEADER,
    dcc.Store(id="tab-state-store", storage_type="memory"),
    dbc.Container(
        dcc.Tabs(
            id="app-tabs",
            value="tab-home",
            className="mt-2",
            children=[
                dcc.Tab(
                    label="🏠 Home",
                    value="tab-home",
                    children=home_tab.layout(),
                    className="px-2",
                    selected_className="fw-bold border-bottom border-2 border-primary",
                ),
                dcc.Tab(
                    label="🗺 Architecture",
                    value="tab-architecture",
                    children=arch_tab.layout(),
                    className="px-2",
                    selected_className="fw-bold border-bottom border-2 border-primary",
                ),
                dcc.Tab(
                    label="📊 Dashboard",
                    value="tab-dashboard",
                    children=dash_tab.layout(),
                    className="px-2",
                    selected_className="fw-bold border-bottom border-2 border-primary",
                ),
            ],
        ),
        fluid=True,
    ),
], style={"minHeight": "100vh", "backgroundColor": "#F8F9FA"})

# ── Register all callbacks ───────────────────────────────────────────────────
nav_cb.register(app)
arch_cb.register(app)
chat_cb.register(app)

# ── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
