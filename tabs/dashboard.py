"""Tab 3 — AllBank dashboard: KPI tiles, transaction trend, account mix, churn risk table, Genie panel."""

import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import pandas as pd

from data.live import ALLBANK_DATA
from theme import PLOTLY_LAYOUT, CHART_COLORS

_TABLE_HEADER_STYLE = {
    "backgroundColor": "#1A1815",
    "color":           "#D6D4D0",
    "fontWeight":      "600",
    "fontSize":        "11px",
    "letterSpacing":   "0.05em",
    "textTransform":   "uppercase",
    "padding":         "10px 14px",
    "borderBottom":    "1px solid #38352F",
}
_TABLE_DATA_STYLE = {
    "backgroundColor": "#1F1D1A",
    "color":           "#C8C4C0",
    "fontSize":        "12px",
}
_TABLE_CELL_STYLE = {
    "textAlign":  "left",
    "padding":    "9px 14px",
    "fontFamily": "Inter, 'Segoe UI', system-ui, sans-serif",
    "border":     "1px solid #2E2C2A",
}
_TABLE_WRAP_STYLE = {
    "overflowX":    "auto",
    "borderRadius": "6px",
    "overflow":     "hidden",
}


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


def _build_trend_figure(trend_df: pd.DataFrame):
    fig = px.bar(
        trend_df,
        x="date",
        y="total_volume",
        title="Monthly Transaction Volume — May 2025 – Apr 2026",
        color_discrete_sequence=[CHART_COLORS[0]],
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        yaxis_title="Transaction Volume (USD)",
        xaxis_title=None,
        xaxis_tickformat="%b %Y",
    )
    fig.update_traces(marker_color=CHART_COLORS[0])

    # Annotate the Apr 2026 spike
    last = trend_df.iloc[-1]
    fig.add_annotation(
        x=last["date"],
        y=last["total_volume"],
        text=f"<b>Apr 2026</b><br>${last['total_volume'] / 1e6:.1f}M<br>{int(last['txn_count']):,} txns",
        showarrow=True,
        arrowhead=2,
        arrowsize=0.85,
        arrowwidth=1.5,
        arrowcolor="#E04B2A",
        ax=-80,
        ay=-50,
        font={"size": 10, "color": "#F0A090",
              "family": "Inter, 'Segoe UI', system-ui, sans-serif"},
        bgcolor="rgba(18, 11, 9, 0.93)",
        bordercolor="rgba(224, 75, 42, 0.52)",
        borderwidth=1,
        borderpad=6,
        align="left",
    )
    return fig


def _build_mix_figure(mix_df: pd.DataFrame):
    labels = {
        "loan": "Loan", "cd": "CD", "savings": "Savings",
        "checking": "Checking", "credit_card": "Credit Card",
    }
    mix_df = mix_df.copy()
    mix_df["label"] = mix_df["account_type"].map(lambda t: labels.get(t, t.title()))
    mix_df["balance_fmt"] = mix_df["total_balance"].apply(lambda v: f"${v / 1e6:.2f}M")

    fig = px.bar(
        mix_df,
        x="label",
        y="total_balance",
        color="label",
        title="Total Balance by Account Type",
        text="balance_fmt",
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, yaxis_title="Balance (USD)", xaxis_title=None)
    fig.update_traces(textposition="outside")
    return fig


def _build_churn_table(churn_df: pd.DataFrame):
    display = churn_df.copy()
    display["Churn Risk"] = display["churn_prob_pct"].apply(lambda v: f"{v:.1f}%")
    display["Credit Score"] = display["credit_score"].astype(int)
    display["Balance"] = display["total_balance"].apply(lambda v: f"${v:,.0f}")
    display["Accounts"] = display["num_accounts"].astype(int)
    display["Overdrafts"] = display["total_overdrafts"].astype(int)
    display["Days Inactive"] = display["avg_days_inactive"].apply(lambda v: f"{int(v)}d")
    display["NPS"] = display["nps_score"].map({1: "Promoter", 0: "Neutral", -1: "Detractor"}).fillna("—")
    display["Customer ID"] = display["customer_id"].astype(int)

    cols = ["Customer ID", "Churn Risk", "Credit Score", "Balance",
            "Accounts", "Overdrafts", "Days Inactive", "NPS"]

    return dash_table.DataTable(
        id="dash-churn-table",
        columns=[{"name": c, "id": c} for c in cols],
        data=display[cols].to_dict("records"),
        style_header=_TABLE_HEADER_STYLE,
        style_data=_TABLE_DATA_STYLE,
        style_cell=_TABLE_CELL_STYLE,
        style_table=_TABLE_WRAP_STYLE,
        style_data_conditional=[
            {
                "if": {"filter_query": '{Churn Risk} > "90"'},
                "backgroundColor": "rgba(224, 75, 42, 0.09)",
                "color": "#F0A090",
            },
            {
                "if": {"filter_query": '{NPS} = "Detractor"'},
                "color": "#E08080",
            },
        ],
    )


def _build_genie_panel() -> html.Div:
    """Chat panel backed by the Genie Conversation API (or fixture/LLM fallback)."""
    import os
    using_genie = bool(os.environ.get("GENIE_SPACE_ID", ""))
    badge_text  = "Genie" if using_genie else "AI"

    return html.Div([
        html.Div([
            html.Div([
                "Ask the Data",
                html.Span(badge_text, className="chat-panel-badge"),
            ], className="chat-panel-header"),
            html.Div(
                id="dash-chat-messages",
                className="chat-messages",
                children=[
                    html.Div(
                        "Ask about churn risk, account balances, transaction trends, or customer health.",
                        className="chat-intro",
                    ),
                ],
            ),
            html.Div([
                dbc.InputGroup([
                    dbc.Input(
                        id="dash-chat-input",
                        type="text",
                        placeholder="Ask about AllBank data...",
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
                    "Try: 'churn risk', 'dormant accounts', 'transaction volume', 'total balance'",
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
    ])


def layout() -> html.Div:
    data = ALLBANK_DATA
    kpi  = data["kpi"]
    src  = data.get("source", "fixture")

    trend_fig = _build_trend_figure(data["trend"])
    mix_fig   = _build_mix_figure(data["mix"])

    churn_rate = float(kpi.get("churn_rate_pct", 19.3))
    aum        = float(kpi.get("total_aum", 24_447_921))
    dormant    = int(kpi.get("dormant_accounts", 766))
    total_cust = int(kpi.get("total_customers", 2_000))
    high_risk  = int(kpi.get("high_risk_churn", 560))
    predicted  = int(kpi.get("predicted_churners", 77))

    source_badge = html.Span(
        f"● {'Live — Databricks' if src == 'live' else 'Fixture data'}",
        style={
            "fontSize": "var(--text-xs)",
            "color": "#4A9A6A" if src == "live" else "#9A7A4A",
            "marginLeft": "var(--sp-3)",
            "fontWeight": "500",
        },
    )

    return html.Div([
        # Header
        html.Div(
            ["AllBank · Gold Layer Analytics — Q1 2026", source_badge],
            className="section-label",
            style={"marginTop": "var(--sp-8)", "display": "flex", "alignItems": "center"},
        ),

        # KPI row
        dbc.Row([
            dbc.Col(_kpi_card(
                "Total Customers",
                f"{total_cust:,}",
                f"{int(kpi.get('churned_customers', 385)):,} churned to date",
            ), md=3),
            dbc.Col(_kpi_card(
                "Total AUM",
                f"${aum / 1e6:.1f}M",
                "Across all account types",
            ), md=3),
            dbc.Col(_kpi_card(
                "Dormant Accounts",
                f"{dormant:,}",
                "Inactive — requires outreach",
                alert=True,
            ), md=3),
            dbc.Col(_kpi_card(
                "Predicted Churners",
                f"{predicted}",
                f"{churn_rate:.1f}% of scored · {high_risk:,} high-risk",
                alert=True,
            ), md=3),
        ], className="g-3", style={"marginBottom": "var(--sp-8)"}),

        # Charts + Genie/Chat
        dbc.Row([
            dbc.Col([
                html.Div(
                    dcc.Graph(id="dash-trend-chart", figure=trend_fig,
                              config={"displayModeBar": False},
                              style={"height": "360px"}),
                    className="chart-wrap",
                    style={"marginBottom": "var(--sp-5)"},
                ),
                html.Div(
                    dcc.Graph(id="dash-category-chart", figure=mix_fig,
                              config={"displayModeBar": False},
                              style={"height": "260px"}),
                    className="chart-wrap",
                ),
                html.Div([
                    html.Div("Churn Risk — Top At-Risk Customers", className="section-label--alert"),
                    _build_churn_table(data["churn_risk"]),
                ], className="anomaly-section"),
            ], md=8),

            dbc.Col(_build_genie_panel(), md=4),
        ], className="g-4"),

        dcc.Store(id="dash-anim-sink", data=""),

    ], style={"padding": "0 var(--sp-4) var(--sp-10)"})
