"""Tab 2 — Architecture diagram with interactive node detail panel."""

import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import html

from data.architecture import get_elements, CYTOSCAPE_STYLESHEET
from theme import CATEGORY_COLORS

cyto.load_extra_layouts()   # enables 'dagre' layout

_NARRATIVE = (
    "This diagram traces the journey of a retail transaction from its origin "
    "in operational source systems, through Databricks ingestion pipelines, "
    "across the three Medallion refinement layers (Bronze → Silver → Gold) "
    "governed by Unity Catalog, and out to downstream consumers — a machine-"
    "learning model pipeline, an analytics dashboard, and an anomaly-aware "
    "AI agent that monitors the Gold layer for data quality signals."
)

_LEGEND_ITEMS = [
    ("source",    "Source Systems"),
    ("ingestion", "Ingestion Pipelines"),
    ("catalog",   "Unity Catalog"),
    ("bronze",    "Bronze (Raw)"),
    ("silver",    "Silver (Curated)"),
    ("gold",      "Gold (Enriched)"),
    ("consumer",  "Consumers"),
    ("agent",     "AI Agent"),
]


def layout() -> html.Div:
    return html.Div([
        html.H4("End-to-End Data Platform Architecture", className="mb-1 mt-2"),
        html.P(_NARRATIVE, className="text-muted small mb-2"),

        # Diagram
        dbc.Card(
            cyto.Cytoscape(
                id="arch-diagram",
                elements=get_elements(),
                stylesheet=CYTOSCAPE_STYLESHEET,
                layout={"name": "preset"},
                style={"width": "100%", "height": "520px"},
                responsive=True,
                userZoomingEnabled=True,
                userPanningEnabled=True,
            ),
            className="mb-2 shadow-sm",
        ),

        # Legend
        dbc.Row(
            [
                dbc.Col(
                    dbc.Badge(
                        label,
                        style={"backgroundColor": CATEGORY_COLORS[cat], "fontSize": "11px"},
                        className="me-1",
                    ),
                    width="auto",
                )
                for cat, label in _LEGEND_ITEMS
            ],
            className="mb-3 gx-1",
        ),

        # Node detail panel
        html.Div(
            id="arch-node-detail",
            children=html.P(
                "Hover over a node to see its description.",
                className="text-muted fst-italic small",
            ),
            style={"minHeight": "60px"},
        ),

        # Export hint
        html.Div([
            html.Small(
                "📸 To save the diagram: right-click the diagram area → Save image as…  "
                "or use the download button below.",
                className="text-muted",
            ),
            html.Br(),
            html.A(
                dbc.Button("⬇ Download Diagram SVG", size="sm", outline=True, color="secondary", className="mt-1"),
                id="arch-export-link",
                href="/assets/architecture_export.svg",
                target="_blank",
                download="databricks-architecture.svg",
            ),
        ], className="mt-1"),
    ], style={"padding": "0 16px 24px"})
