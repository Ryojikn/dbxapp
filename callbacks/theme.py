"""Theme toggle callbacks — clientside attribute sync and Plotly chart re-theme."""

from dash import Input, Output, State, Patch

from theme import CHART_DARK, CHART_LIGHT


def register(app) -> None:
    # Sync data-theme attribute on <html> and update toggle button label.
    # Fires on page load (when theme-store initialises from localStorage or default).
    app.clientside_callback(
        """
        function(stored) {
            var t = stored || 'dark';
            document.documentElement.setAttribute('data-theme', t);
            return t === 'dark' ? 'Light' : 'Dark';
        }
        """,
        Output("theme-toggle-label", "children"),
        Input("theme-store", "data"),
    )

    # Flip stored theme on button click.
    app.clientside_callback(
        """
        function(n, stored) {
            return (stored === 'dark') ? 'light' : 'dark';
        }
        """,
        Output("theme-store", "data"),
        Input("theme-toggle", "n_clicks"),
        State("theme-store", "data"),
        prevent_initial_call=True,
    )

    # Update Plotly chart colours when theme changes.
    # Uses Patch so only layout styling properties are sent — data and traces unchanged.
    @app.callback(
        Output("dash-trend-chart",    "figure"),
        Output("dash-category-chart", "figure"),
        Input("theme-store", "data"),
    )
    def sync_chart_theme(theme: str):
        c = CHART_DARK if theme != "light" else CHART_LIGHT

        patch = Patch()
        patch["layout"]["font"]["color"]             = c["font_color"]
        patch["layout"]["xaxis"]["gridcolor"]        = c["grid_color"]
        patch["layout"]["xaxis"]["linecolor"]        = c["grid_color"]
        patch["layout"]["xaxis"]["tickfont"]         = {"color": c["tick_color"], "size": 11}
        patch["layout"]["yaxis"]["gridcolor"]        = c["grid_color"]
        patch["layout"]["yaxis"]["tickfont"]         = {"color": c["tick_color"], "size": 11}
        patch["layout"]["hoverlabel"]["bgcolor"]     = c["hover_bg"]
        patch["layout"]["hoverlabel"]["bordercolor"] = c["hover_bd"]
        patch["layout"]["hoverlabel"]["font"]        = {"color": c["font_color"], "size": 12}
        return patch, patch
