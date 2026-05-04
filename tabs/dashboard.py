"""Tab 3 — Dashboard with KPI tiles, charts, anomaly table, and chat panel."""

import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import pandas as pd

from data.fixtures import get_dataframe, KPI_SUMMARY
from theme import PLOTLY_LAYOUT, CHART_COLORS, COLOR_DARK, COLOR_SURFACE, COLOR_BG, COLOR_BORDER


def _kpi_card(title: str, value: str, subtitle: str = "", alert: bool = False) -> dbc.Card:
    card_class = "kpi-card kpi-card--alert" if alert else "kpi-card"
    return dbc.Card(
        dbc.CardBody([
            html.P(title, className="kpi-label"),
            html.Div(value, className="kpi-value"),
            html.Div(subtitle, className="kpi-subtitle") if subtitle else None,
        ]),
        className=card_class,
    )


_ANOMALY_DATE    = "2025-03-18"
_ANOMALY_REVENUE = 48_230.0


def _build_trend_figure(df: pd.DataFrame):
    fig = px.line(
        df,
        x="date",
        y="revenue",
        color="category",
        title="Daily Revenue by Category — Jan–Mar 2025",
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_traces(line={"width": 2})

    # Vertical reference line at the anomaly date
    fig.add_vline(
        x=_ANOMALY_DATE,
        line_width=1,
        line_dash="dot",
        line_color="rgba(224, 75, 42, 0.38)",
    )

    # Callout annotation pointing at the Electronics COGS spike
    fig.add_annotation(
        x=_ANOMALY_DATE,
        y=_ANOMALY_REVENUE,
        text="<b>Mar 18 · Electronics</b><br>COGS +340% · Margin 6%<br>Order ORD-48821",
        showarrow=True,
        arrowhead=2,
        arrowsize=0.85,
        arrowwidth=1.5,
        arrowcolor="#E04B2A",
        ax=72,
        ay=-58,
        font={"size": 10, "color": "#F0A090",
              "family": "Inter, 'Segoe UI', system-ui, sans-serif"},
        bgcolor="rgba(18, 11, 9, 0.93)",
        bordercolor="rgba(224, 75, 42, 0.52)",
        borderwidth=1,
        borderpad=6,
        align="left",
        xanchor="left",
    )

    return fig


def _build_category_figure(df: pd.DataFrame):
    mar = df[df["date"].apply(lambda d: d.month == 3)]
    agg = mar.groupby("category", as_index=False)["revenue"].sum()
    agg["revenue_fmt"] = agg["revenue"].apply(lambda v: f"${v:,.0f}")
    fig = px.bar(
        agg,
        x="category",
        y="revenue",
        color="category",
        title="Total Revenue by Category — March 2025",
        text="revenue_fmt",
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
    fig.update_traces(textposition="outside")
    return fig


def _build_anomaly_table(df: pd.DataFrame):
    anomalies = df[df["is_anomaly"]].copy()
    anomalies["date"] = anomalies["date"].astype(str)
    anomalies["revenue_fmt"] = anomalies["revenue"].apply(lambda v: f"${v:,.2f}")
    anomalies["margin_fmt"] = anomalies["gross_margin_pct"].apply(lambda v: f"{v:.1f}%")
    display = anomalies[["date", "category", "revenue_fmt", "margin_fmt", "anomaly_reason", "anomaly_order_ref"]].copy()
    display.columns = ["Date", "Category", "Revenue", "Margin", "Anomaly Reason", "Order Ref"]

    return dash_table.DataTable(
        id="dash-anomaly-table",
        columns=[{"name": c, "id": c} for c in display.columns],
        data=display.to_dict("records"),
        style_header={
            "backgroundColor": "#1A1815",
            "color":           "#D6D4D0",
            "fontWeight":      "600",
            "fontSize":        "11px",
            "letterSpacing":   "0.05em",
            "textTransform":   "uppercase",
            "padding":         "10px 14px",
            "borderBottom":    "1px solid #38352F",
        },
        style_data={
            "backgroundColor": "#1F1D1A",
            "color":           "#C8C4C0",
            "fontSize":        "12px",
        },
        style_cell={
            "textAlign":   "left",
            "padding":     "9px 14px",
            "fontFamily":  "Inter, 'Segoe UI', system-ui, sans-serif",
            "border":      "1px solid #2E2C2A",
        },
        style_table={
            "overflowX":    "auto",
            "borderRadius": "6px",
            "overflow":     "hidden",
        },
        style_data_conditional=[
            {
                "if": {"filter_query": '{Anomaly Reason} contains "COGS"'},
                "backgroundColor": "rgba(224, 75, 42, 0.07)",
                "color":           "#F0A090",
            },
        ],
    )


def layout() -> html.Div:
    df = get_dataframe()
    kpi = KPI_SUMMARY

    trend_fig    = _build_trend_figure(df)
    category_fig = _build_category_figure(df)

    return html.Div([
        # Section header — generous breathing room before the data story
        html.Div("Gold Layer Analytics — Q1 2025", className="section-label",
                 style={"marginTop": "var(--sp-8)"}),

        # KPI row — 4-2-2-4 rhythm: primary / supporting / supporting / alert
        dbc.Row([
            dbc.Col(_kpi_card("Total Revenue (MTD)", f"${kpi['total_revenue_mtd']:,.0f}",
                              f"+{kpi['revenue_mom_pct']:.0f}% MoM"), md=4),
            dbc.Col(_kpi_card("Total Orders (MTD)", f"{kpi['total_orders_mtd']:,}",
                              "March 2025"), md=2),
            dbc.Col(_kpi_card("Avg Order Value", f"${kpi['avg_order_value_mtd']:,.2f}",
                              "March 2025"), md=2),
            dbc.Col(_kpi_card("Active Anomalies", str(kpi["active_anomaly_count"]),
                              "Requires investigation", alert=True), md=4),
        ], className="g-3", style={"marginBottom": "var(--sp-8)"}),

        # Charts + Chat
        dbc.Row([
            # Left: trend chart (hero), bar chart (supporting), anomaly section
            dbc.Col([
                # Trend chart — the primary data story, taller
                html.Div(
                    dcc.Graph(id="dash-trend-chart", figure=trend_fig,
                              config={"displayModeBar": False},
                              style={"height": "360px"}),
                    className="chart-wrap",
                    style={"marginBottom": "var(--sp-5)"},
                ),
                # Bar chart — supporting breakdown, shorter
                html.Div(
                    dcc.Graph(id="dash-category-chart", figure=category_fig,
                              config={"displayModeBar": False},
                              style={"height": "260px"}),
                    className="chart-wrap",
                ),
                # Anomaly section — visually separated alert zone
                html.Div([
                    html.Div("Anomaly Status", className="section-label--alert"),
                    _build_anomaly_table(df),
                ], className="anomaly-section"),
            ], md=8),

            # Right: chat panel
            dbc.Col([
                html.Div([
                    html.Div([
                        "Ask the Data",
                        html.Span("AI", className="chat-panel-badge"),
                    ], className="chat-panel-header"),
                    html.Div(
                        id="dash-chat-messages",
                        className="chat-messages",
                        children=[
                            html.Div(
                                "Ask about revenue, category trends, or anomalies.",
                                className="chat-intro",
                            ),
                        ],
                    ),
                    html.Div([
                        dbc.InputGroup([
                            dbc.Input(
                                id="dash-chat-input",
                                type="text",
                                placeholder="Ask the data...",
                                n_submit=0,
                                debounce=False,
                                style={"fontSize": "var(--text-sm)"},
                            ),
                            dbc.Button(
                                "Send",
                                id="dash-chat-send",
                                color="primary",
                                n_clicks=0,
                                size="sm",
                            ),
                        ]),
                        html.Div(
                            "Try: 'total revenue', 'fastest growing category', 'any anomalies'",
                            style={
                                "fontSize":   "var(--text-2xs)",
                                "color":      "var(--color-text-subtle)",
                                "marginTop":  "var(--sp-2)",
                                "lineHeight": "1.4",
                            },
                        ),
                    ], className="chat-input-area"),
                ], className="chat-panel"),
                dcc.Store(id="dash-chat-store", storage_type="memory", data=[]),
            ], md=4),
        ], className="g-4"),

        # Animation infrastructure — not rendered
        dcc.Store(id="dash-anim-sink", data=""),

    ], style={"padding": "0 var(--sp-4) var(--sp-10)"})
