"""
Chat response logic for the AllBank demo dashboard.
Keyword-matched fixture responses; live passthrough uses the LLM-backed SSE stream.
"""

from __future__ import annotations

_RULES: list[dict] = [
    {
        "id":               "churn-query",
        "trigger_keywords": [
            "churn", "at-risk", "at risk", "risk", "lose", "losing",
            "retention", "predict", "leaving",
        ],
        "response_key":     "churn",
        "priority":         0,
    },
    {
        "id":               "dormant-query",
        "trigger_keywords": ["dormant", "inactive", "sleeping", "idle", "not active"],
        "response_key":     "dormant",
        "priority":         1,
    },
    {
        "id":               "balance-query",
        "trigger_keywords": ["balance", "aum", "asset", "deposit", "money", "total"],
        "response_key":     "balance",
        "priority":         2,
    },
    {
        "id":               "transaction-query",
        "trigger_keywords": ["transaction", "volume", "txn", "payment", "trend", "grow"],
        "response_key":     "transactions",
        "priority":         3,
    },
    {
        "id":               "customer-query",
        "trigger_keywords": ["customer", "client", "account", "how many", "count"],
        "response_key":     "customers",
        "priority":         4,
    },
    {
        "id":               "fallback",
        "trigger_keywords": [],
        "response_key":     "fallback",
        "priority":         99,
    },
]


def get_chat_rules() -> list[dict]:
    return sorted(_RULES, key=lambda r: r["priority"])


def match_rule(question: str, rules: list[dict] | None = None) -> dict:
    if rules is None:
        rules = get_chat_rules()
    q = question.lower()
    for rule in sorted(rules, key=lambda r: r["priority"]):
        if not rule["trigger_keywords"]:
            continue
        if any(kw in q for kw in rule["trigger_keywords"]):
            return rule
    return next(r for r in rules if r["id"] == "fallback")


def render_response(rule: dict, kpi: dict, chat_qa: dict) -> str:
    key = rule["response_key"]
    if key in chat_qa:
        return chat_qa[key]

    # Dynamic fallbacks using live KPI values
    if key == "customers":
        return (
            f"AllBank has {int(kpi.get('total_customers', 2000)):,} total customers. "
            f"Of those, {int(kpi.get('churned_customers', 385)):,} have already churned "
            f"and {int(kpi.get('high_risk_churn', 560)):,} are in the high-risk churn segment."
        )

    return (
        "I can help you explore AllBank's data. Try asking about churn risk, "
        "dormant accounts, total AUM, or transaction volume trends."
    )
