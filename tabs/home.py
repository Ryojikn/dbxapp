"""Tab 1 — Home landing page."""

import dash_bootstrap_components as dbc
from dash import html


_NARRATIVE = """
Today's data teams face a common challenge: raw operational data arrives from dozens of
sources — databases, SaaS platforms, event streams, and file drops — but turning it into
trusted, queryable analytics assets takes weeks of fragile pipelines, duplicated governance
work, and hard-to-debug transformations.

This demo shows a reference architecture that solves that challenge on the Databricks
Lakehouse Platform. Data lands in a raw Bronze layer via Auto Loader and Lakeflow
Declarative Pipelines, is curated and validated in a Silver layer, then enriched into
business-ready Gold tables — all registered in Unity Catalog for unified governance, lineage,
and access control. Downstream, a machine-learning pipeline and a BI dashboard consume the
same Gold assets, and an AI anomaly agent watches for data quality signals in real time.
The entire stack is deployable as a Databricks App, keeping the demo inside one platform.
"""

_DEMO_CARDS = [
    {
        "title":       "Architecture",
        "icon":        "🗺",
        "description": (
            "Explore the end-to-end data flow: source systems → ingestion pipelines → "
            "Unity Catalog–governed Medallion layers → ML models, BI dashboard, and "
            "anomaly AI agent. Every node is clickable for a plain-language explanation."
        ),
        "tab":  "tab-architecture",
        "btn_id": "home-nav-to-arch",
        "color": "primary",
    },
    {
        "title":       "Dashboard",
        "icon":        "📊",
        "description": (
            "See the Gold layer in action: live KPI tiles, a time-series revenue trend, "
            "a category breakdown, and an anomaly status table — all driven by a "
            "self-contained fixture dataset. Chat with the data using the Ask panel."
        ),
        "tab":  "tab-dashboard",
        "btn_id": "home-nav-to-dash",
        "color": "success",
    },
]

_METADATA = {
    "Intended audience": "Data Engineers, Solutions Architects, Data Leaders",
    "Data domain":       "Retail / E-Commerce Analytics (fixture dataset)",
    "Platform":          "Databricks Lakehouse — Databricks Apps",
    "Repo":              ("#", "GitHub Repository"),
    "Docs":              ("https://docs.databricks.com", "Databricks Documentation"),
}


def layout() -> html.Div:
    return html.Div([
        # Hero section
        dbc.Row([
            dbc.Col([
                html.H2("Databricks Platform Demo", className="fw-bold mb-1"),
                html.H5(
                    "From raw data to AI-powered insights — a live end-to-end reference architecture.",
                    className="text-muted mb-3",
                ),
                html.P(_NARRATIVE.strip(), className="lead", style={"maxWidth": "820px", "lineHeight": "1.7"}),
            ])
        ], className="mb-4 mt-3"),

        # "What you'll see" section
        html.H5("What you'll see in this demo", className="mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(card["icon"], style={"fontSize": "2rem", "lineHeight": "1"}),
                            html.H5(card["title"], className="mt-2 mb-1 fw-bold"),
                            html.P(card["description"], className="text-muted small mb-3"),
                            dbc.Button(
                                f"Open {card['title']} →",
                                id=card["btn_id"],
                                color=card["color"],
                                size="sm",
                                n_clicks=0,
                            ),
                        ]),
                    ], className="h-100 shadow-sm"),
                    md=6,
                )
                for card in _DEMO_CARDS
            ],
            className="mb-4 g-3",
        ),

        html.Hr(),

        # Metadata footer
        dbc.Row([
            dbc.Col([
                html.H6("About this demo", className="text-muted text-uppercase small mb-2"),
                html.Dl([
                    item
                    for key, val in _METADATA.items()
                    for item in [
                        html.Dt(key, className="col-sm-3 small text-muted"),
                        html.Dd(
                            html.A(val[1], href=val[0], target="_blank")
                            if isinstance(val, tuple)
                            else val,
                            className="col-sm-9 small",
                        ),
                    ]
                ], className="row"),
            ], md=8),
        ]),
    ], style={"padding": "0 16px 32px"})
