"""
Fixture dataset for the Databricks Platform Demo App.
All data is in-memory; no database or file I/O required.
"""

from datetime import date, timedelta
import pandas as pd
import numpy as np

_CATEGORIES = ["Electronics", "Apparel", "Home & Garden", "Sports"]

# Base daily revenue per category (USD)
_BASE_REVENUE = {"Electronics": 28_000, "Apparel": 21_000, "Home & Garden": 18_000, "Sports": 14_500}

# Month-over-month trend multiplier
_TREND = {1: 1.00, 2: 1.05, 3: 1.12}

# Seasonal boost: Sports in Jan/Feb (higher seasonal demand)
_SEASONAL = {("Sports", 1): 1.22, ("Sports", 2): 1.15}

# Normal COGS as fraction of revenue (77% → 23% gross margin)
_NORMAL_COGS_PCT = 0.77


def _build_records() -> list[dict]:
    rng = np.random.default_rng(42)
    records: list[dict] = []

    start = date(2025, 1, 1)
    end   = date(2025, 3, 31)
    current = start

    while current <= end:
        for cat in _CATEGORIES:
            base   = _BASE_REVENUE[cat]
            trend  = _TREND[current.month]
            season = _SEASONAL.get((cat, current.month), 1.0)
            noise  = 1.0 + rng.uniform(-0.15, 0.15)

            revenue = round(base * trend * season * noise, 2)
            cogs    = round(revenue * _NORMAL_COGS_PCT, 2)
            margin  = round((revenue - cogs) / revenue * 100, 2)

            # Derive order count from ~$155 avg order value ±10%
            avg_factor = 1.0 + rng.uniform(-0.10, 0.10)
            order_count = max(50, int(revenue / (155 * avg_factor)))
            avg_ov = round(revenue / order_count, 2)

            records.append({
                "date":              current,
                "category":          cat,
                "revenue":           revenue,
                "order_count":       order_count,
                "avg_order_value":   avg_ov,
                "cogs":              cogs,
                "gross_margin_pct":  margin,
                "is_anomaly":        False,
                "anomaly_reason":    None,
                "anomaly_order_ref": None,
            })
        current += timedelta(days=1)

    # Inject the one rehearsed anomaly: March 18, Electronics, COGS spike
    for r in records:
        if r["date"] == date(2025, 3, 18) and r["category"] == "Electronics":
            r["revenue"]           = 48_230.00
            r["order_count"]       = 197
            r["avg_order_value"]   = 244.82
            r["cogs"]              = 45_356.20   # 94% of revenue → ~6% margin
            r["gross_margin_pct"]  = round((48_230 - 45_356.20) / 48_230 * 100, 2)
            r["is_anomaly"]        = True
            r["anomaly_reason"]    = "COGS spike: bulk order ORD-48821 priced below cost (+340% vs 7-day avg COGS)"
            r["anomaly_order_ref"] = "ORD-48821"
            break

    return records


# --------------------------------------------------------------------------- #
# Public exports                                                               #
# --------------------------------------------------------------------------- #

def get_dataframe() -> pd.DataFrame:
    """Return all 360 sales records as a Pandas DataFrame."""
    return pd.DataFrame(_build_records())


def get_sales_records() -> list[dict]:
    """Return all 360 sales records as a list of dicts."""
    return _build_records()


def _compute_kpi(df: pd.DataFrame) -> dict:
    mar = df[df["date"].apply(lambda d: d.month == 3)]
    feb = df[df["date"].apply(lambda d: d.month == 2)]

    rev_mar = mar["revenue"].sum()
    rev_feb = feb["revenue"].sum()
    orders  = int(mar["order_count"].sum())

    cat_rev = mar.groupby("category")["revenue"].sum()
    top_cat = cat_rev.idxmax()

    mom_pct = round((rev_mar - rev_feb) / rev_feb * 100, 1) if rev_feb > 0 else 0.0

    return {
        "total_revenue_mtd":      round(rev_mar, 2),
        "total_orders_mtd":       orders,
        "avg_order_value_mtd":    round(rev_mar / orders, 2) if orders else 0,
        "revenue_mom_pct":        mom_pct,
        "active_anomaly_count":   int(mar["is_anomaly"].sum()),
        "top_category":           top_cat,
        "top_category_revenue":   round(float(cat_rev[top_cat]), 2),
        "fastest_growing_category": "Sports",
        "fastest_growing_qoq_pct":  28.0,
    }


# Compute once at module load
_DF       = get_dataframe()
KPI_SUMMARY: dict = _compute_kpi(_DF)

# AllBank chat Q&A — used by the SSE fixture-mode stream
CHAT_QA: dict[str, str] = {
    "churn": (
        "AllBank's ML model scored 400 customers and flagged 77 as predicted churners — "
        "a 19.3% churn rate. Separately, 560 customers are classified as high-risk based "
        "on behavioral signals: high overdraft counts, long inactivity, and negative NPS. "
        "Recommended action: prioritise outreach for customers with both high churn probability "
        "and a Detractor NPS score."
    ),
    "dormant": (
        "766 accounts are classified as dormant across all account types — "
        "261 checking, 223 savings, 157 credit card, 83 loan, and 42 CD accounts. "
        "Dormancy correlates strongly with churn risk: the average days-inactive for "
        "predicted churners is over 90 days. A re-engagement campaign targeting these "
        "accounts could recover a meaningful share of at-risk AUM."
    ),
    "balance": (
        "AllBank's total AUM is $24.4M across 4,178 accounts. "
        "Loans are the largest contributor at $10.2M, followed by CDs at $5.9M, "
        "checking at $4.1M, savings at $3.3M, and credit cards at $0.95M. "
        "Average credit utilisation on credit card accounts is 27.9%."
    ),
    "transactions": (
        "Transaction volume has grown nearly 6× in 12 months: from $6.5M in May 2025 "
        "to $39.5M in April 2026, with 39,517 transactions processed that month. "
        "Average transaction value has remained stable around $1,000, indicating "
        "volume growth is driven by new customers and account activity, not ticket-size inflation."
    ),
}
