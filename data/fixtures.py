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

# Three pre-rehearsed chat Q&A pairs — values templated from KPI_SUMMARY so
# they are always consistent with what the charts display.
def _build_chat_qa(kpi: dict) -> dict[str, str]:
    top_pct = round(kpi["top_category_revenue"] / kpi["total_revenue_mtd"] * 100)
    return {
        "revenue": (
            f"As of March 31, total month-to-date revenue is "
            f"${kpi['total_revenue_mtd']:,.0f} — up {kpi['revenue_mom_pct']:.0f}% "
            f"month-over-month. {kpi['top_category']} leads with "
            f"${kpi['top_category_revenue']:,.0f} ({top_pct}% of total revenue), "
            f"followed by the other categories."
        ),
        "category": (
            f"{kpi['fastest_growing_category']} is the fastest-growing category this quarter "
            f"at +{kpi['fastest_growing_qoq_pct']:.0f}% QoQ, driven by seasonal demand in Q1. "
            f"{kpi['top_category']} remains the highest absolute revenue contributor "
            f"at ${kpi['top_category_revenue']:,.0f} for March."
        ),
        "anomaly": (
            "Yes — one active anomaly is flagged in the Gold layer: on March 18, the "
            "Electronics category saw a COGS spike of +340% vs the 7-day rolling average. "
            "Revenue held at $48,230 but gross margin collapsed from 23% to 5.96%. "
            "The likely cause is bulk order ORD-48821, which appears to have been priced "
            "below cost. Recommended action: review cost-basis records for Electronics "
            "orders from March 16–20 and escalate ORD-48821 to the procurement team "
            "for correction."
        ),
    }


CHAT_QA: dict[str, str] = _build_chat_qa(KPI_SUMMARY)
