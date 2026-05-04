"""Tab 1 — Home landing page."""

import dash_bootstrap_components as dbc
from dash import html


_NARRATIVE_P1 = (
    "AllBank is a mid-size financial institution facing a converging set of pressures: "
    "churn risk is rising, management waits days for basic business insights, analysts "
    "are overwhelmed with ad-hoc requests, and business leaders openly distrust each "
    "other's numbers. The root cause is technical — siloed data, no central governance, "
    "fragile pipelines, and no observability."
)

_NARRATIVE_P2 = (
    "This demo shows how the Databricks Lakehouse resolves each of those concerns. "
    "Lakeflow Declarative Pipelines ingest from operational systems using Auto Loader "
    "and orchestrated by Databricks Jobs, transforming raw records through Bronze, "
    "Silver, and Gold layers governed by Unity Catalog. Business leaders query Gold "
    "tables directly via AI/BI Genie — in plain English, with full lineage — "
    "eliminating the analyst bottleneck and rebuilding data trust."
)

_DEMO_CARDS = [
    {
        "index":    "01",
        "title":    "Architecture",
        "description": (
            "Trace an AllBank transaction through operational source systems, "
            "Lakeflow Pipelines orchestrated by Databricks Jobs, three Medallion "
            "layers governed by Unity Catalog, and out to AI/BI Genie, ML, and "
            "anomaly-detection consumers. Every node is interactive."
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
            "Gold layer in action: KPI tiles, trend charts, anomaly table, and "
            "an embedded AI/BI Genie space — ask questions in plain English and "
            "get governed, lineage-tracked answers without analyst intermediaries."
        ),
        "tab":      "tab-dashboard",
        "btn_id":   "home-nav-to-dash",
        "btn_text": "Open dashboard",
        "featured": False,
    },
]

_METADATA = {
    "Customer scenario": "AllBank — Financial Services (fictional)",
    "Intended audience": "Data Engineers, Solutions Architects, Business Leaders",
    "Platform":          "Databricks Lakehouse — Databricks Apps",
    "Key capabilities":  "Lakeflow Pipelines · Unity Catalog · AI/BI Genie · Mosaic AI",
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
                html.Div("AllBank · Financial Services", className="home-hero-label"),
                html.H1("End-to-End Lakehouse", className="home-title"),
                html.P(
                    "From siloed, untrusted data to AI-powered insights — "
                    "how Databricks solves AllBank's data, governance, and AI challenges.",
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
