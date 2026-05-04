"""Tab 2 — Architecture diagram with zone bands and interactive detail panel."""

import dash_cytoscape as cyto
from dash import html

from data.architecture import get_elements, CYTOSCAPE_STYLESHEET

cyto.load_extra_layouts()

_NARRATIVE = (
    "A retail transaction travels from operational source systems through Databricks "
    "ingestion pipelines, across three Medallion refinement layers governed by Unity "
    "Catalog, and out to downstream consumers: an ML model pipeline, an analytics "
    "dashboard, and an AI anomaly agent. Select any node to explore that layer."
)


def layout() -> html.Div:
    return html.Div([
        html.Div("Data Platform Architecture", className="section-label mt-3"),
        html.P(_NARRATIVE, style={
            "fontSize": "var(--text-sm)",
            "color": "var(--color-text-muted)",
            "lineHeight": "1.65",
            "maxWidth": "80ch",
            "marginBottom": "var(--sp-5)",
        }),

        html.Div(
            cyto.Cytoscape(
                id="arch-diagram",
                elements=get_elements(),
                stylesheet=CYTOSCAPE_STYLESHEET,
                layout={"name": "preset"},
                style={"width": "100%", "height": "560px"},
                responsive=True,
                userZoomingEnabled=False,
                userPanningEnabled=False,
                autoungrabify=True,
            ),
            className="arch-diagram-card",
            style={"marginBottom": "var(--sp-5)"},
        ),

        html.Div(
            id="arch-node-detail",
            children=html.P(
                "Select a node to explore the platform layer.",
                className="arch-detail-hint",
            ),
            className="arch-detail-panel",
        ),

    ], style={"padding": "0 var(--sp-4) var(--sp-8)"})
