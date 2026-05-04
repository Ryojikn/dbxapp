"""
Chat response logic for the Databricks Platform Demo App.
Uses keyword matching over pre-baked responses.
Optional passthrough to Databricks Model Serving when DEMO_MODE=live.
"""

from __future__ import annotations

_RULES: list[dict] = [
    {
        "id":               "anomaly-query",
        "trigger_keywords": [
            "anomal", "unusual", "investigat", "alert", "problem",
            "issue", "flag", "warning", "spike", "wrong", "weird",
        ],
        "response_key":     "anomaly",
        "is_anomaly_rule":  True,
        "priority":         0,
    },
    {
        "id":               "revenue-query",
        "trigger_keywords": ["revenue", "sales", "total", "how much", "money", "earn"],
        "response_key":     "revenue",
        "is_anomaly_rule":  False,
        "priority":         1,
    },
    {
        "id":               "category-query",
        "trigger_keywords": [
            "categor", "product", "segment", "best", "top",
            "grow", "fastest", "perform", "sport", "electron", "apparel",
        ],
        "response_key":     "category",
        "is_anomaly_rule":  False,
        "priority":         2,
    },
    {
        "id":               "orders-query",
        "trigger_keywords": ["order", "transaction", "volume", "count", "customer"],
        "response_key":     "orders",
        "is_anomaly_rule":  False,
        "priority":         3,
    },
    {
        "id":               "fallback",
        "trigger_keywords": [],   # always matches last
        "response_key":     "fallback",
        "is_anomaly_rule":  False,
        "priority":         99,
    },
]


def get_chat_rules() -> list[dict]:
    return sorted(_RULES, key=lambda r: r["priority"])


def match_rule(question: str, rules: list[dict] | None = None) -> dict:
    """Return the first matching rule for *question* (case-insensitive)."""
    if rules is None:
        rules = get_chat_rules()
    q = question.lower()
    for rule in sorted(rules, key=lambda r: r["priority"]):
        if not rule["trigger_keywords"]:  # fallback
            continue
        if any(kw in q for kw in rule["trigger_keywords"]):
            return rule
    # Fallback
    return next(r for r in rules if r["id"] == "fallback")


def render_response(rule: dict, kpi: dict, chat_qa: dict) -> str:
    """Return the pre-baked response string for *rule*, referencing *kpi* values."""
    key = rule["response_key"]

    if key in chat_qa:
        return chat_qa[key]

    if key == "orders":
        return (
            f"In March we processed {kpi['total_orders_mtd']:,} orders, "
            f"with an average order value of ${kpi['avg_order_value_mtd']:,.2f}. "
            f"Order volume is tracking {kpi['revenue_mom_pct']:.0f}% ahead of February."
        )

    # fallback
    return (
        "I can help you explore this data. Try asking about total revenue, "
        "category performance, or whether there are any anomalies to investigate."
    )
