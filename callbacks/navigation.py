"""Navigation callbacks: Home preview card buttons → tab switch."""

import dash
from dash import Input, Output


def register(app: dash.Dash) -> None:

    @app.callback(
        Output("app-tabs", "value"),
        Input("home-nav-to-arch", "n_clicks"),
        Input("home-nav-to-dash", "n_clicks"),
        prevent_initial_call=True,
    )
    def navigate(n_arch: int, n_dash: int) -> str:
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        return "tab-architecture" if trigger_id == "home-nav-to-arch" else "tab-dashboard"
