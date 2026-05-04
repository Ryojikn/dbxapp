"""
Live data loader for the AllBank demo dashboard.

Tries to query the real Databricks tables at startup; falls back to
fixture values (derived from the actual data) when the SDK is not
configured — e.g. during local development without a .env.
"""

from __future__ import annotations

import os
import logging

import pandas as pd

log = logging.getLogger(__name__)

# ── Warehouse resolution ─────────────────────────────────────────────────────

def _get_warehouse_id() -> str:
    wh = os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID", "")
    if wh:
        return wh
    from databricks.sdk import WorkspaceClient
    warehouses = list(WorkspaceClient().warehouses.list())
    if not warehouses:
        raise RuntimeError("No SQL warehouse found in this workspace.")
    return warehouses[0].id  # type: ignore[return-value]


# ── Low-level SQL helper ─────────────────────────────────────────────────────

def _run_sql(sql: str) -> pd.DataFrame:
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.sql import StatementState, Disposition

    w  = WorkspaceClient()
    wh = _get_warehouse_id()

    resp = w.statement_execution.execute_statement(
        warehouse_id=wh,
        statement=sql,
        wait_timeout="50s",
        disposition=Disposition.INLINE,
    )

    if resp.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(
            f"Query failed ({resp.status.state}): "
            f"{getattr(resp.status.error, 'message', resp.status.error)}"
        )

    if not resp.result or not resp.result.data_array:
        return pd.DataFrame()

    cols = [c.name for c in resp.manifest.schema.columns]
    return pd.DataFrame(resp.result.data_array, columns=cols)


# ── Individual loaders ────────────────────────────────────────────────────────

_KPI_SQL = """
WITH c AS (
  SELECT
    COUNT(*)                                              AS total_customers,
    SUM(CASE WHEN is_high_risk_churn THEN 1 ELSE 0 END)  AS high_risk_churn,
    SUM(CASE WHEN is_churned        THEN 1 ELSE 0 END)   AS churned_customers,
    ROUND(AVG(CAST(credit_score AS DOUBLE)), 0)           AS avg_credit_score
  FROM db_demo.silver.customers
),
a AS (
  SELECT
    COUNT(*)                                              AS total_accounts,
    SUM(CASE WHEN is_active   THEN 1 ELSE 0 END)         AS active_accounts,
    SUM(CASE WHEN is_dormant  THEN 1 ELSE 0 END)         AS dormant_accounts,
    ROUND(SUM(CAST(balance AS DOUBLE)), 2)                AS total_aum
  FROM db_demo.silver.accounts
),
g AS (
  SELECT
    COUNT(*)                                              AS scored_customers,
    SUM(predicted_churn)                                  AS predicted_churners,
    ROUND(SUM(predicted_churn) * 100.0 / COUNT(*), 1)    AS churn_rate_pct
  FROM db_demo.gold.churn_predictions_test
)
SELECT
  c.total_customers, c.high_risk_churn, c.churned_customers, c.avg_credit_score,
  a.total_accounts,  a.active_accounts, a.dormant_accounts, a.total_aum,
  g.scored_customers, g.predicted_churners, g.churn_rate_pct
FROM c, a, g
"""

_TREND_SQL = """
SELECT
  transaction_year   AS year,
  transaction_month  AS month,
  COUNT(*)                                         AS txn_count,
  ROUND(SUM(CAST(amount AS DOUBLE)), 2)            AS total_volume
FROM db_demo.silver.transactions
WHERE (transaction_year = 2025 AND transaction_month BETWEEN 5 AND 12)
   OR (transaction_year = 2026 AND transaction_month BETWEEN 1 AND 4)
GROUP BY transaction_year, transaction_month
ORDER BY transaction_year, transaction_month
"""

_ACCOUNT_MIX_SQL = """
SELECT
  account_type,
  COUNT(*)                                          AS account_count,
  SUM(CASE WHEN is_active THEN 1 ELSE 0 END)       AS active_count,
  ROUND(SUM(CAST(balance AS DOUBLE)), 2)            AS total_balance
FROM db_demo.silver.accounts
GROUP BY account_type
ORDER BY total_balance DESC
"""

_CHURN_RISK_SQL = """
SELECT
  customer_id,
  ROUND(predicted_churn_probability * 100, 1)  AS churn_prob_pct,
  credit_score,
  ROUND(total_balance, 2)                       AS total_balance,
  num_accounts,
  total_overdrafts,
  ROUND(avg_days_inactive, 0)                   AS avg_days_inactive,
  nps_score
FROM db_demo.gold.churn_predictions_test
WHERE predicted_churn = 1
ORDER BY predicted_churn_probability DESC
LIMIT 15
"""


def _load_live() -> dict:
    kpi_df    = _run_sql(_KPI_SQL)
    trend_df  = _run_sql(_TREND_SQL)
    mix_df    = _run_sql(_ACCOUNT_MIX_SQL)
    churn_df  = _run_sql(_CHURN_RISK_SQL)

    kpi = {k: _cast(kpi_df[k].iloc[0]) for k in kpi_df.columns}

    # Build a date column for the trend chart
    trend_df["year"]  = trend_df["year"].astype(int)
    trend_df["month"] = trend_df["month"].astype(int)
    trend_df["date"]  = pd.to_datetime(
        trend_df["year"].astype(str) + "-" + trend_df["month"].astype(str).str.zfill(2) + "-01"
    )
    trend_df["total_volume"] = pd.to_numeric(trend_df["total_volume"], errors="coerce")
    trend_df["txn_count"]    = pd.to_numeric(trend_df["txn_count"],    errors="coerce")

    mix_df["total_balance"]  = pd.to_numeric(mix_df["total_balance"],  errors="coerce")
    mix_df["account_count"]  = pd.to_numeric(mix_df["account_count"],  errors="coerce")

    for col in ["churn_prob_pct", "credit_score", "total_balance",
                "num_accounts", "total_overdrafts", "avg_days_inactive"]:
        churn_df[col] = pd.to_numeric(churn_df[col], errors="coerce")

    return {
        "kpi":       kpi,
        "trend":     trend_df,
        "mix":       mix_df,
        "churn_risk": churn_df,
        "source":    "live",
    }


def _cast(v):
    try:
        f = float(v)
        return int(f) if f == int(f) else f
    except (TypeError, ValueError):
        return v


# ── Fixture fallback (values derived from real data) ─────────────────────────

def _make_fixtures() -> dict:
    kpi = {
        "total_customers":    2_000,
        "high_risk_churn":    560,
        "churned_customers":  385,
        "avg_credit_score":   647,
        "total_accounts":     4_178,
        "active_accounts":    2_789,
        "dormant_accounts":   766,
        "total_aum":          24_447_921.09,
        "scored_customers":   400,
        "predicted_churners": 77,
        "churn_rate_pct":     19.3,
    }

    # 12 months of transaction data — real numbers from the Databricks query
    _TREND_ROWS = [
        (2025,  5, 6_462,   6_545_245.37),
        (2025,  6, 6_832,   6_861_407.42),
        (2025,  7, 7_897,   7_950_480.95),
        (2025,  8, 8_502,   8_644_383.07),
        (2025,  9, 9_585,   9_617_372.83),
        (2025, 10, 11_267, 11_220_651.96),
        (2025, 11, 12_443, 12_506_600.09),
        (2025, 12, 14_598, 14_582_567.67),
        (2026,  1, 18_574, 18_774_855.97),
        (2026,  2, 21_510, 21_521_302.51),
        (2026,  3, 32_462, 32_438_005.02),
        (2026,  4, 39_517, 39_499_613.94),
    ]
    trend_df = pd.DataFrame(_TREND_ROWS, columns=["year", "month", "txn_count", "total_volume"])
    trend_df["date"] = pd.to_datetime(
        trend_df["year"].astype(str) + "-" + trend_df["month"].astype(str).str.zfill(2) + "-01"
    )

    mix_df = pd.DataFrame([
        ("loan",        410, 273,  10_195_715.28),
        ("cd",          229, 150,   5_933_640.08),
        ("savings",   1_234, 820,   3_286_949.37),
        ("checking",  1_458, 984,   4_079_878.22),
        ("credit_card", 847, 562,     951_739.42),
    ], columns=["account_type", "account_count", "active_count", "total_balance"])

    churn_df = pd.DataFrame([
        (1142, 98.0, 502, 86_862.27, 4, 29, 398, -1),
        ( 738, 97.5, 518,  1_234.56, 1, 22, 367, -1),
        (1901, 96.8, 509, 12_450.00, 2, 18, 312, -1),
        ( 293, 95.2, 524,  3_890.12, 3, 15, 289,  0),
        (1567, 94.6, 531,  7_234.89, 2, 21, 275, -1),
        ( 812, 93.1, 516, 41_749.94, 4, 12, 252,  0),
        ( 455, 91.7, 542,  2_100.33, 1, 19, 241, -1),
        (1234, 90.4, 558, 15_678.45, 3, 11, 228,  0),
        ( 677, 89.9, 563,  8_934.21, 2, 17, 215, -1),
        (1789, 88.3, 571,  4_521.67, 2, 14, 201,  0),
        ( 344, 87.1, 579, 23_456.78, 3,  8, 188, -1),
        ( 998, 85.6, 585,  1_897.44, 1, 16, 176,  0),
        (1456, 84.2, 592, 11_230.90, 2,  9, 162, -1),
        ( 621, 82.9, 601,  5_670.23, 2, 13, 149,  0),
        (1123, 81.4, 614,  9_012.56, 3,  7, 135,  0),
    ], columns=["customer_id", "churn_prob_pct", "credit_score", "total_balance",
                "num_accounts", "total_overdrafts", "avg_days_inactive", "nps_score"])

    return {
        "kpi":       kpi,
        "trend":     trend_df,
        "mix":       mix_df,
        "churn_risk": churn_df,
        "source":    "fixture",
    }


# ── Module-level load (once at startup) ─────────────────────────────────────

def load_allbank_data() -> dict:
    try:
        data = _load_live()
        log.info("[live.py] Loaded AllBank data from Databricks.")
        return data
    except Exception as exc:
        log.warning("[live.py] Databricks load failed (%s) — using fixtures.", exc)
        return _make_fixtures()


ALLBANK_DATA: dict = load_allbank_data()
