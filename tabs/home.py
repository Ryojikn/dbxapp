"""Tab 1 — Home landing page."""

import dash_bootstrap_components as dbc
from dash import html


_NARRATIVE_P1 = (
    "Raw operational data arrives from dozens of sources — databases, SaaS platforms, "
    "event streams, and file drops — but turning it into trusted, queryable analytics "
    "assets takes weeks of fragile pipelines, duplicated governance work, and "
    "hard-to-debug transformations."
)

_NARRATIVE_P2 = (
    "This demo shows how the Databricks Lakehouse solves that: Auto Loader ingests raw "
    "events into a Bronze layer, Lakeflow Declarative Pipelines curate them into Silver, "
    "and enriched Gold tables are registered in Unity Catalog for unified governance, "
    "lineage, and access control. The code on the right is the real pipeline."
)

_DEMO_CARDS = [
    {
        "index":    "01",
        "title":    "Architecture",
        "description": (
            "Trace a retail transaction through source systems, Auto Loader ingestion, "
            "three Medallion layers governed by Unity Catalog, and out to ML and BI "
            "consumers. Every node is interactive."
        ),
        "tab":      "tab-architecture",
        "btn_id":   "home-nav-to-arch",
        "btn_text": "Explore architecture",
        "featured": True,
    },
    {
        "index":    "02",
        "title":    "Dashboard",
        "description": (
            "Gold layer in action: revenue KPIs, time-series trend, category breakdown, "
            "and anomaly status table — all driven by a self-contained fixture dataset. "
            "Ask questions using the chat panel."
        ),
        "tab":      "tab-dashboard",
        "btn_id":   "home-nav-to-dash",
        "btn_text": "Open dashboard",
        "featured": False,
    },
]

_METADATA = {
    "Intended audience": "Data Engineers, Solutions Architects, Data Leaders",
    "Data domain":       "Retail / E-Commerce Analytics (fixture dataset)",
    "Platform":          "Databricks Lakehouse — Databricks Apps",
    "Repository":        ("#", "GitHub Repository"),
    "Documentation":     ("https://docs.databricks.com", "Databricks Documentation"),
}

# ── Terminal panel ───────────────────────────────────────────────────────────
# The JS in assets/terminal.js types the code into #terminal-code at runtime.

_TERMINAL = html.Div([
    html.Div([
        html.Span(className="term-dot term-dot--close"),
        html.Span(className="term-dot term-dot--min"),
        html.Span(className="term-dot term-dot--max"),
        html.Span("pipeline.py", className="term-filename"),
    ], className="term-header"),
    html.Pre(
        html.Code(id="terminal-code", className="term-code"),
        className="term-body",
    ),
], className="term-panel", id="terminal-panel")


def layout() -> html.Div:
    return html.Div([

        # ── Hero: text + terminal side-by-side ───────────────────────────
        dbc.Row([
            # Left: copy — vertically centred against the terminal height
            dbc.Col([
                html.Div("Reference architecture", className="home-hero-label"),
                html.H1("End-to-End Lakehouse", className="home-title"),
                html.P(
                    "From raw data to AI-powered insights — a live, interactive "
                    "reference architecture on the Databricks Lakehouse Platform.",
                    className="home-subtitle",
                ),
                html.P(_NARRATIVE_P1, className="home-narrative"),
                html.P(_NARRATIVE_P2, className="home-narrative",
                       style={"marginBottom": 0}),
            ], md=5,
               className="d-flex flex-column justify-content-center",
               style={"paddingRight": "var(--sp-4)"}),

            # Right: live-typing terminal
            dbc.Col(
                _TERMINAL,
                md=7,
            ),
        ], className="align-items-center",
           style={"marginTop": "var(--sp-10)", "marginBottom": "var(--sp-12)",
                  "--bs-gutter-x": "var(--sp-6)"}),

        # ── Demo cards ───────────────────────────────────────────────────
        html.Div("Explore the demo", className="demo-section-label"),
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        html.Div(card["index"], className="demo-card-index"),
                        html.Div(card["title"], className="demo-card-title"),
                        html.P(card["description"], className="demo-card-desc"),
                        dbc.Button(
                            card["btn_text"],
                            id=card["btn_id"],
                            color="primary" if card["featured"] else "outline-secondary",
                            size="sm",
                            n_clicks=0,
                        ),
                    ], className=(
                        "demo-card  demo-card--featured"
                        if card["featured"] else "demo-card"
                    )),
                    md=6,
                )
                for card in _DEMO_CARDS
            ],
            className="g-4",
            style={"marginBottom": "var(--sp-12)"},
        ),

        html.Hr(className="home-divider"),

        # ── Metadata ─────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Div("About this demo", className="metadata-section-label"),
                html.Div([
                    html.Div([
                        html.Span(key, className="metadata-key"),
                        html.Span(
                            html.A(val[1], href=val[0], target="_blank")
                            if isinstance(val, tuple)
                            else val,
                            className="metadata-val",
                        ),
                    ], className="metadata-row")
                    for key, val in _METADATA.items()
                ]),
            ], md=8),
        ], style={"paddingBottom": "var(--sp-10)"}),

    ], style={"padding": "0 var(--sp-4)"})
