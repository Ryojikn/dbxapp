# Contract: Fixture Data Module

**Type**: Python module interface  
**Defined in**: `data/fixtures.py`, `data/architecture.py`, `data/chat.py`

---

## `data/fixtures.py`

### `get_sales_records() -> list[dict]`

Returns all 360 daily sales records as a list of dicts (Pandas-friendly).

```python
[
  {
    "date": datetime.date(2025, 1, 1),
    "category": "Electronics",
    "revenue": 28430.50,
    "order_count": 184,
    "avg_order_value": 154.51,
    "cogs": 21890.50,
    "gross_margin_pct": 23.0,
    "is_anomaly": False,
    "anomaly_reason": None,
    "anomaly_order_ref": None
  },
  ...
  {
    "date": datetime.date(2025, 3, 18),
    "category": "Electronics",
    "revenue": 48230.00,
    "order_count": 197,
    "avg_order_value": 244.82,
    "cogs": 45356.20,
    "gross_margin_pct": 5.96,
    "is_anomaly": True,
    "anomaly_reason": "COGS spike: bulk order ORD-48821 priced below cost (+340% vs 7-day avg COGS)",
    "anomaly_order_ref": "ORD-48821"
  },
  ...
]
```

**Guarantee**: Exactly one record has `is_anomaly=True`. All other records have `is_anomaly=False` and `anomaly_reason=None`.

### `get_kpi_summary() -> dict`

Returns the `KPISummary` object as a dict. Computed once from `get_sales_records()` at module load.

```python
{
  "total_revenue_mtd": 2847392.00,
  "total_orders_mtd": 18429,
  "avg_order_value_mtd": 154.52,
  "revenue_mom_pct": 12.0,
  "active_anomaly_count": 1,
  "top_category": "Electronics",
  "top_category_revenue": 891034.00,
  "fastest_growing_category": "Sports",
  "fastest_growing_qoq_pct": 28.0
}
```

### `get_dataframe() -> pandas.DataFrame`

Returns `get_sales_records()` as a Pandas DataFrame. Column names match the dict keys above. Used directly by Plotly Express chart functions.

---

## `data/architecture.py`

### `get_nodes() -> list[dict]`

Returns 13 architecture nodes in Cytoscape element format.

```python
[
  {
    "data": {
      "id": "gold-layer",
      "label": "Gold — Enriched",
      "category": "gold",
      "description": "The Gold layer holds business-ready, fully validated datasets aligned to specific analytical use cases. These tables are optimized for query performance and serve as the single source of truth for dashboards, ML models, and AI agents."
    }
  },
  ...
]
```

### `get_edges() -> list[dict]`

Returns 14 directed edges in Cytoscape element format.

```python
[
  {"data": {"source": "gold-layer", "target": "ml-pipeline", "label": "features"}},
  ...
]
```

### `get_elements() -> list[dict]`

Convenience: `get_nodes() + get_edges()`. Pass directly to `cyto.Cytoscape(elements=...)`.

### `get_node_description(node_id: str) -> str`

Returns the description paragraph for a given node ID. Returns `""` for unknown IDs.

---

## `data/chat.py`

### `get_chat_rules() -> list[dict]`

Returns the 5 pre-baked chat rules ordered by priority ascending.

```python
[
  {
    "id": "anomaly-query",
    "trigger_keywords": ["anomaly", "anomalies", "unusual", "investigate", "alert", "problem", "issue", "flag", "warning"],
    "response_template": "Yes — one active anomaly is flagged in the gold layer: on March 18, the Electronics category saw a COGS spike of +340% vs the 7-day rolling average. Revenue held at $48,230 but gross margin collapsed from 23% to 6%. The likely cause is bulk order ORD-48821, which appears to have been priced below cost. Recommended action: review the cost-basis records for Electronics orders from March 16–20 and escalate ORD-48821 to the procurement team for correction.",
    "is_anomaly_rule": True,
    "priority": 0
  },
  ...
]
```

### `match_rule(question: str, rules: list[dict]) -> dict`

Returns the first matching rule (lowest priority number) where any `trigger_keyword` appears in `question.lower()`. Returns the fallback rule if no keywords match.

### `render_response(rule: dict, kpi: dict) -> str`

Substitutes `{metric_name}` placeholders in `rule["response_template"]` with values from `kpi`. Returns the rendered response string.
