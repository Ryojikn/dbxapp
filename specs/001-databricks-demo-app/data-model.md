# Data Model: Databricks Platform Demo App

**Branch**: `001-databricks-demo-app` | **Date**: 2026-05-03

All data is in-memory Python objects. No database, no file I/O. Defined in `data/fixtures.py` and `data/chat.py`.

---

## Entity 1: SalesRecord

Represents one row of the fixture dataset — daily sales for one product category.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `date` | `datetime.date` | Non-null; range Jan 1 – Mar 31 2025 | Index dimension for time-series chart |
| `category` | `str` | One of: `Electronics`, `Apparel`, `Home & Garden`, `Sports` | Partition dimension for category chart |
| `revenue` | `float` | > 0 | Daily gross revenue in USD |
| `order_count` | `int` | > 0 | Number of orders placed |
| `avg_order_value` | `float` | `revenue / order_count` | Derived; stored for convenience |
| `cogs` | `float` | > 0; normally 65-80% of revenue | Cost of goods sold |
| `gross_margin_pct` | `float` | `(revenue - cogs) / revenue * 100` | Normally 20-35% |
| `is_anomaly` | `bool` | Default `False` | `True` for exactly one record in the fixture |
| `anomaly_reason` | `str \| None` | Non-null when `is_anomaly=True` | Human-readable cause description |
| `anomaly_order_ref` | `str \| None` | Non-null when `is_anomaly=True` | Order ID implicated in the anomaly |

**Fixture specification**:
- 360 records total (90 days × 4 categories)
- Revenue follows a smooth upward trend with ±15% daily noise
- Seasonal uplift: Sports +20% in Jan-Feb, Electronics +10% in Mar
- Exactly one anomaly: `date=2025-03-18`, `category=Electronics`, `cogs` inflated 5.8× normal → `gross_margin_pct` ≈ 6 (normally 23), `anomaly_reason="COGS spike: bulk order ORD-48821 priced below cost"`, `anomaly_order_ref="ORD-48821"`

---

## Entity 2: KPISummary

Derived aggregate computed from `SalesRecord` filtered to current calendar month (March 2025 in the fixture). Computed once at app startup in `data/fixtures.py`.

| Field | Type | Fixture Value | Notes |
|-------|------|---------------|-------|
| `total_revenue_mtd` | `float` | 2,847,392.00 | Sum of `revenue` for March 2025 |
| `total_orders_mtd` | `int` | 18,429 | Sum of `order_count` for March 2025 |
| `avg_order_value_mtd` | `float` | 154.52 | `total_revenue_mtd / total_orders_mtd` |
| `revenue_mom_pct` | `float` | 12.0 | vs February 2025 total |
| `active_anomaly_count` | `int` | 1 | Count of `SalesRecord` where `is_anomaly=True` |
| `top_category` | `str` | `Electronics` | Category with highest March revenue |
| `top_category_revenue` | `float` | 891,034.00 | March revenue for top category |
| `fastest_growing_category` | `str` | `Sports` | Highest QoQ growth rate |
| `fastest_growing_qoq_pct` | `float` | 28.0 | Q1 2025 vs Q4 2024 (implied) |

---

## Entity 3: ArchitectureNode

One component in the Tab 2 architecture diagram. Defined in `data/architecture.py`.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | `str` | Unique; kebab-case | Used as Cytoscape node `id` |
| `label` | `str` | ≤ 25 chars | Displayed inside the node box |
| `category` | `str` | One of: `source`, `ingestion`, `catalog`, `bronze`, `silver`, `gold`, `consumer`, `agent` | Controls node color and icon class |
| `description` | `str` | 1-2 sentences | Shown in detail panel on hover/click |
| `position_hint` | `str` | One of: `left`, `center-left`, `center`, `center-right`, `right` | Guides dagre layout column grouping |

**Fixture nodes** (13 total):

| id | label | category |
|----|-------|----------|
| `postgres-db` | PostgreSQL DB | source |
| `salesforce-crm` | Salesforce CRM | source |
| `s3-files` | S3 / File Drops | source |
| `kafka-stream` | Kafka Stream | source |
| `autoloader` | Auto Loader (DLT) | ingestion |
| `dlt-pipeline` | Lakeflow Pipelines | ingestion |
| `unity-catalog` | Unity Catalog | catalog |
| `bronze-layer` | Bronze — Raw | bronze |
| `silver-layer` | Silver — Curated | silver |
| `gold-layer` | Gold — Enriched | gold |
| `ml-pipeline` | ML Model Pipeline | consumer |
| `bi-dashboard` | BI / Analytics | consumer |
| `ai-agent` | Anomaly AI Agent | agent |

---

## Entity 4: ArchitectureEdge

Directed connection between two `ArchitectureNode` instances.

| Field | Type | Notes |
|-------|------|-------|
| `source` | `str` | `ArchitectureNode.id` of originating node |
| `target` | `str` | `ArchitectureNode.id` of destination node |
| `label` | `str \| None` | Optional short edge label (e.g., "ingests", "registers") |

**Fixture edges** (12 total):

```
postgres-db    → autoloader
salesforce-crm → autoloader
s3-files       → autoloader
kafka-stream   → dlt-pipeline
autoloader     → bronze-layer
dlt-pipeline   → bronze-layer
bronze-layer   → unity-catalog
bronze-layer   → silver-layer
silver-layer   → unity-catalog
silver-layer   → gold-layer
gold-layer     → unity-catalog
gold-layer     → ml-pipeline
gold-layer     → bi-dashboard
gold-layer     → ai-agent
```

---

## Entity 5: ChatRule

Pre-baked input→output mapping for the Tab 3 chat panel. Defined in `data/chat.py`.

| Field | Type | Notes |
|-------|------|-------|
| `id` | `str` | Unique identifier |
| `trigger_keywords` | `list[str]` | Any word from this list in the lowercased question triggers this rule |
| `response_template` | `str` | Answer text; `{metric_name}` placeholders resolved against current `KPISummary` |
| `is_anomaly_rule` | `bool` | If `True`, response always includes anomaly details + remediation step |
| `priority` | `int` | Lower = checked first; anomaly rule has priority 0 |

**Fixture rules** (5 total):

| id | trigger_keywords | is_anomaly_rule |
|----|-----------------|-----------------|
| `revenue-query` | `["revenue", "sales", "total", "how much", "month"]` | False |
| `category-query` | `["category", "categories", "product", "segment", "best", "top", "growing", "fastest"]` | False |
| `anomaly-query` | `["anomaly", "anomalies", "unusual", "investigate", "alert", "problem", "issue", "flag", "warning"]` | **True** |
| `orders-query` | `["orders", "transactions", "order count", "volume"]` | False |
| `fallback` | `[]` (empty — matched last) | False |

**Matching logic**: Iterate rules in `priority` order. First rule where any `trigger_keyword` appears in `question.lower()` wins. If no keyword matches, fallback rule fires. Anomaly rule always returns the full COGS spike narrative + ORD-48821 remediation regardless of LLM mode.

---

## State Transitions

```
App startup
    → load_fixtures()                → SalesRecord[] (360 rows), KPISummary
    → build_architecture_graph()     → ArchitectureNode[], ArchitectureEdge[]
    → build_chat_rules()             → ChatRule[]

Tab switch (Dash callback)
    → No data reload; DOM state preserved via dcc.Store
    → Architecture tab: selected node ID in dcc.Store → detail panel content
    → Dashboard tab: active filters in dcc.Store → chart traces

Chat question submitted
    → match_chat_rule(question, rules) → ChatRule
    → if ChatRule.is_anomaly_rule OR env vars absent → render template response
    → else → call Databricks Model Serving with seeded system prompt
    → append (question, response) to chat history in dcc.Store
```
