"""Tab 3 — Dashboard with KPI tiles, charts, anomaly table, and chat panel."""

import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import pandas as pd

from data.fixtures import get_dataframe, KPI_SUMMARY
from theme import PLOTLY_LAYOUT, CHART_COLORS, COLOR_DANGER, COLOR_WARNING


def _kpi_card(title: str, value: str, subtitle: str = "", color: str = "primary") -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.P(title, className="text-muted small mb-1"),
            html.H4(value, className=f"text-{color} mb-0 fw-bold"),
            html.Small(subtitle, className="text-muted"),
        ]),
        className="shadow-sm h-100",
        style={"borderLeft": f"4px solid var(--bs-{color})"},
    )


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
            "backgroundColor": "#343A40",
            "color":           "white",
            "fontWeight":      "bold",
            "fontSize":        "12px",
        },
        style_data={
            "backgroundColor": "#FFF3CD",
            "color":           "#212529",
            "fontSize":        "12px",
        },
        style_cell={"textAlign": "left", "padding": "8px"},
        style_table={"overflowX": "auto"},
    )


def layout() -> html.Div:
    df = get_dataframe()
    kpi = KPI_SUMMARY

    trend_fig    = _build_trend_figure(df)
    category_fig = _build_category_figure(df)

    return html.Div([
        html.H4("Gold Layer Analytics — Q1 2025", className="mb-3 mt-2"),

        # KPI row
        dbc.Row([
            dbc.Col(_kpi_card("Total Revenue (MTD)", f"${kpi['total_revenue_mtd']:,.0f}",
                              f"+{kpi['revenue_mom_pct']:.0f}% MoM"), md=3),
            dbc.Col(_kpi_card("Total Orders (MTD)", f"{kpi['total_orders_mtd']:,}",
                              "March 2025"), md=3),
            dbc.Col(_kpi_card("Avg Order Value", f"${kpi['avg_order_value_mtd']:,.2f}",
                              "March 2025"), md=3),
            dbc.Col(_kpi_card("Active Anomalies", str(kpi["active_anomaly_count"]),
                              "Requires investigation", color="danger"), md=3),
        ], className="mb-3 g-3"),

        # Charts + Chat — 8 + 4 column split
        dbc.Row([
            # Left: charts and anomaly table
            dbc.Col([
                dbc.Row([
                    dbc.Col(dcc.Graph(id="dash-trend-chart",    figure=trend_fig,    config={"displayModeBar": False}), md=12),
                ], className="mb-2"),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="dash-category-chart", figure=category_fig, config={"displayModeBar": False}), md=12),
                ], className="mb-2"),
                dbc.Row([
                    dbc.Col([
                        html.H6("⚠ Anomaly Status Table", className="text-danger mb-1"),
                        _build_anomaly_table(df),
                    ], md=12),
                ]),
            ], md=8),

            # Right: chat panel
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H6("Ask the Data", className="mb-0")),
                    dbc.CardBody([
                        html.Div(
                            id="dash-chat-messages",
                            style={
                                "height":     "380px",
                                "overflowY":  "auto",
                                "display":    "flex",
                                "flexDirection": "column",
                                "gap":        "8px",
                                "padding":    "4px",
                            },
                            children=[
                                html.Div(
                                    "👋 Ask me about revenue, category trends, or anomalies.",
                                    className="text-muted small",
                                ),
                            ],
                        ),
                    ]),
                    dbc.CardFooter([
                        dbc.InputGroup([
                            dbc.Input(
                                id="dash-chat-input",
                                type="text",
                                placeholder="Ask the data…",
                                n_submit=0,
                                debounce=False,
                                style={"fontSize": "13px"},
                            ),
                            dbc.Button("Send", id="dash-chat-send", color="primary", n_clicks=0),
                        ]),
                        html.Small(
                            "Try: 'total revenue', 'fastest growing category', 'any anomalies'",
                            className="text-muted mt-1 d-block",
                            style={"fontSize": "11px"},
                        ),
                    ]),
                ], className="shadow-sm h-100"),
                # Store for chat history
                dcc.Store(id="dash-chat-store", storage_type="memory", data=[]),
            ], md=4),
        ], className="g-3"),
    ], style={"padding": "0 16px 24px"})
