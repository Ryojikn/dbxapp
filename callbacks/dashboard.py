"""Dashboard animation callback: triggers chart animation when dashboard tab is selected."""

import dash
from dash import Input, Output


def register(app: dash.Dash) -> None:

    app.clientside_callback(
        """
        function(tab_value) {
            if (tab_value !== 'tab-dashboard') { return ''; }

            /* Debounce: don't re-fire within 2 s of last animation */
            var now = Date.now();
            if (window._dashLastAnim && (now - window._dashLastAnim) < 2000) { return ''; }
            window._dashLastAnim = now;

            /* Give Plotly a tick to finish rendering after tab reveal */
            setTimeout(function () {
                if (window.dashboardAnimate) { window.dashboardAnimate(); }
            }, 140);

            return '';
        }
        """,
        Output("dash-anim-sink", "data"),
        Input("app-tabs", "value"),
        prevent_initial_call=False,
    )
