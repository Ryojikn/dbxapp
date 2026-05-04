"""Architecture diagram callbacks: node tap -> detail panel."""

from collections import defaultdict

import dash
from dash import Input, Output, html

from data.architecture import _NODES_META, _EDGES_META, get_node_description


# Lookup maps built at import time
_LABEL_MAP    = {nid: label for nid, label, _   in _NODES_META}
_CAT_MAP      = {nid: cat   for nid, _,     cat in _NODES_META}
_UPSTREAM:   dict[str, list[str]] = defaultdict(list)
_DOWNSTREAM: dict[str, list[str]] = defaultdict(list)

for _src, _tgt, _ in _EDGES_META:
    _DOWNSTREAM[_src].append(_LABEL_MAP.get(_tgt, _tgt))
    _UPSTREAM[_tgt].append(_LABEL_MAP.get(_src, _src))

_CAT_DISPLAY = {
    "source":    "Data Source",
    "ingestion": "Ingestion",
    "bronze":    "Bronze Layer",
    "silver":    "Silver Layer",
    "gold":      "Gold Layer",
    "catalog":   "Unity Catalog",
    "consumer":  "Insight Consumer",
    "agent":     "AI Agent",
}

_HINT = html.P(
    "Select a node to explore the platform layer.",
    className="arch-detail-hint",
)


def register(app: dash.Dash) -> None:

    @app.callback(
        Output("arch-node-detail", "children"),
        Input("arch-diagram", "tapNodeData"),
        prevent_initial_call=True,
    )
    def show_node_detail(node_data: dict | None):
        if not node_data:
            return _HINT

        node_id  = node_data.get("id", "")
        # Zone compound nodes carry no description — pass through
        if node_id.startswith("zone-") or node_id not in _LABEL_MAP:
            return _HINT

        label       = _LABEL_MAP[node_id]
        category    = _CAT_MAP[node_id]
        description = get_node_description(node_id)
        upstream    = _UPSTREAM.get(node_id, [])
        downstream  = _DOWNSTREAM.get(node_id, [])
        cat_label   = _CAT_DISPLAY.get(category, category.title())

        conn_items = []
        if upstream:
            conn_items.append(html.Div([
                html.Span("Receives from: ", className="arch-detail-conn-label"),
                html.Span(", ".join(upstream), className="arch-detail-conn-nodes"),
            ], className="arch-detail-conn"))
        if downstream:
            conn_items.append(html.Div([
                html.Span("Sends to: ", className="arch-detail-conn-label"),
                html.Span(", ".join(downstream), className="arch-detail-conn-nodes"),
            ], className="arch-detail-conn"))

        return html.Div([
            html.Div([
                html.Span(cat_label,
                          className=f"arch-detail-badge arch-detail-badge--{category}"),
                html.Span(label, className="arch-detail-title"),
            ], className="arch-detail-header"),
            html.P(description, className="arch-detail-desc") if description else None,
            html.Div(conn_items, className="arch-detail-connections") if conn_items else None,
        ], className="arch-detail-content")
