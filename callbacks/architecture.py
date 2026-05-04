"""Architecture diagram callbacks: node tap → detail panel."""

import dash
from dash import Input, Output, html
import dash_bootstrap_components as dbc

from data.architecture import get_node_description


def register(app: dash.Dash) -> None:

    @app.callback(
        Output("arch-node-detail", "children"),
        Input("arch-diagram", "tapNodeData"),
        prevent_initial_call=True,
    )
    def show_node_detail(node_data: dict | None):
        if not node_data:
            return dash.no_update

        label       = node_data.get("label", "Node")
        description = get_node_description(node_data.get("id", ""))
        category    = node_data.get("category", "")

        if not description:
            return dash.no_update

        return dbc.Card(
            dbc.CardBody([
                html.H6(label, className="mb-1 fw-bold"),
                html.Small(category.title(), className="text-muted text-uppercase mb-2 d-block"),
                html.P(description, className="mb-0 small"),
            ]),
            className="shadow-sm border-start border-3 border-primary",
        )
