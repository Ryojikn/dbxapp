"""
Architecture diagram data for the Databricks Platform Demo App.
Provides Cytoscape elements (nodes + edges) for the Tab 2 diagram.
"""

_NODE_DESCRIPTIONS = {
    "postgres-db": (
        "AllBank's core banking system runs on PostgreSQL, storing transactional "
        "records — accounts, transactions, and customer profiles. Change Data Capture "
        "(CDC) feeds every committed row into the Lakehouse in near-real time, "
        "replacing fragile nightly ETL jobs that left management flying blind."
    ),
    "salesforce-crm": (
        "Salesforce CRM holds customer relationship data — churn risk scores, "
        "product holdings, and NPS history. A scheduled export lands opportunity "
        "and contact records into the platform for enrichment alongside transactional "
        "data, enabling the 360° customer view that previously required weeks of work."
    ),
    "s3-files": (
        "S3 (and compatible object stores) receive batch file drops — regulatory "
        "reporting exports, third-party risk feeds, and partner data exchanges. "
        "Auto Loader monitors these prefixes with event-notification triggers and "
        "ingests new files incrementally with exactly-once semantics via checkpointing."
    ),
    "databricks-jobs": (
        "Databricks Jobs orchestrates the end-to-end pipeline schedule — triggering "
        "Lakeflow Pipeline runs, coordinating file-arrival dependencies, and chaining "
        "downstream ML scoring and report refresh tasks. Retry logic, alerting, and "
        "audit history are all managed centrally, replacing the fragmented scheduler "
        "landscape that previously caused AllBank's data reliability issues."
    ),
    "dlt-pipeline": (
        "Lakeflow Declarative Pipelines (formerly Delta Live Tables) are the core "
        "of AllBank's ingestion and transformation layer. Auto Loader (cloudFiles) "
        "is used inside the pipeline to ingest files from S3 and CDC feeds from "
        "operational systems. The pipeline engine then applies declarative "
        "Bronze-to-Silver-to-Gold transformations — deduplication, type enforcement, "
        "and business-rule enrichment — with built-in data quality expectations that "
        "replace the silent data failures that eroded business leader trust."
    ),
    "unity-catalog": (
        "Unity Catalog is the unified governance layer that solves AllBank's siloed "
        "data and trust problems. A three-level namespace (catalog.schema.table) "
        "provides a single, auditable registry across every Bronze, Silver, and Gold "
        "table. Column-level lineage, row/column masks, and attribute-based access "
        "control ensure each business unit sees exactly what they're permitted to see — "
        "eliminating the 'which number is right?' debates between teams."
    ),
    "bronze-layer": (
        "Bronze is the raw ingestion layer — data lands here exactly as it arrived "
        "from the source, with an appended ingestion timestamp and source identifier. "
        "No business logic is applied; Bronze is the immutable audit trail. "
        "Schema evolution is handled automatically via Lakeflow Pipelines, "
        "so source schema changes no longer break downstream consumers."
    ),
    "silver-layer": (
        "Silver is the curated, validated layer. Lakeflow Pipelines deduplicate "
        "records, enforce types, null-check critical fields, and join across sources "
        "into a canonical domain model. Data quality expectations gate every row — "
        "failures are quarantined rather than silently corrupting Gold, which was the "
        "root cause of AllBank's analyst throughput and trust issues."
    ),
    "gold-layer": (
        "Gold holds business-ready, aggregated datasets optimised for specific "
        "analytical use cases. Denormalised for query performance via Liquid Clustering, "
        "these tables are the single source of truth for dashboards, ML feature stores, "
        "and the AI/BI Genie layer. Because every Gold table is lineage-tracked in "
        "Unity Catalog, business leaders can trace any KPI back to its source row."
    ),
    "ml-pipeline": (
        "The ML Model Pipeline reads feature tables from the Gold layer via the "
        "Feature Engineering in Unity Catalog store, trains churn-prediction and "
        "anomaly-detection models with MLflow tracking, and registers champions "
        "to the UC Model Registry. Scheduled batch scoring runs via Databricks Jobs, "
        "surfacing at-risk customers before they churn — AllBank's primary revenue concern."
    ),
    "bi-dashboard": (
        "AI/BI Genie and Databricks Apps give AllBank's business leaders a natural-"
        "language interface over Gold Delta tables, served through a SQL Warehouse. "
        "Executives ask questions in plain English and get governed, auditable answers — "
        "no analyst intermediary required. This directly addresses the management "
        "insight lag and the growing analyst headcount pressure."
    ),
    "ai-agent": (
        "The Anomaly-Aware AI Agent monitors Gold-layer signals using the Mosaic AI "
        "Agent Framework. When it detects a statistical deviation — a churn rate spike, "
        "a margin collapse, or an unusual transaction cluster — it fires a natural-"
        "language alert with a proposed remediation step, routed to the on-call team. "
        "Central observability, previously absent at AllBank, is now automated."
    ),
}

# Preset positions for all leaf nodes
_POSITIONS = {
    "postgres-db":      {"x": 80,   "y": 120},
    "salesforce-crm":   {"x": 80,   "y": 255},
    "s3-files":         {"x": 80,   "y": 390},
    "databricks-jobs":  {"x": 295,  "y": 170},
    "dlt-pipeline":     {"x": 295,  "y": 340},
    "unity-catalog":    {"x": 645,  "y": 440},
    "bronze-layer":     {"x": 490,  "y": 255},
    "silver-layer":     {"x": 645,  "y": 255},
    "gold-layer":       {"x": 800,  "y": 255},
    "ml-pipeline":      {"x": 1010, "y": 170},
    "bi-dashboard":     {"x": 1010, "y": 330},
    "ai-agent":         {"x": 1010, "y": 450},
}

# Leaf node metadata: (id, label, category)
_NODES_META = [
    ("postgres-db",     "PostgreSQL DB",       "source"),
    ("salesforce-crm",  "Salesforce CRM",      "source"),
    ("s3-files",        "S3 / File Drops",     "source"),
    ("databricks-jobs", "Databricks Jobs",     "ingestion"),
    ("dlt-pipeline",    "Lakeflow Pipelines",  "ingestion"),
    ("unity-catalog",   "Unity Catalog",       "catalog"),
    ("bronze-layer",    "Bronze",              "bronze"),
    ("silver-layer",    "Silver",              "silver"),
    ("gold-layer",      "Gold",                "gold"),
    ("ml-pipeline",     "ML Pipeline",         "consumer"),
    ("bi-dashboard",    "AI/BI + Genie",       "consumer"),
    ("ai-agent",        "AI Agent",            "agent"),
]

# Parent zone assignment for each leaf node
_NODE_PARENTS = {
    "postgres-db":     "zone-sources",
    "salesforce-crm":  "zone-sources",
    "s3-files":        "zone-sources",
    "databricks-jobs": "zone-ingestion",
    "dlt-pipeline":    "zone-ingestion",
    "bronze-layer":    "zone-medallion",
    "silver-layer":    "zone-medallion",
    "gold-layer":      "zone-medallion",
    "unity-catalog":   "zone-medallion",
    "ml-pipeline":     "zone-insights",
    "bi-dashboard":    "zone-insights",
    "ai-agent":        "zone-insights",
}

# Zone compound nodes (rendered as background regions)
_ZONE_NODES = [
    {
        "data": {"id": "zone-sources",   "label": "DATA SOURCES"},
        "classes": "zone-top zone-sources",
    },
    {
        "data": {"id": "zone-lakehouse", "label": "DATABRICKS LAKEHOUSE"},
        "classes": "zone-top zone-lakehouse",
    },
    {
        "data": {"id": "zone-ingestion", "label": "INGESTION",
                 "parent": "zone-lakehouse"},
        "classes": "zone-sub",
    },
    {
        "data": {"id": "zone-medallion", "label": "MEDALLION",
                 "parent": "zone-lakehouse"},
        "classes": "zone-sub",
    },
    {
        "data": {"id": "zone-insights",  "label": "INSIGHT EXTRACTION"},
        "classes": "zone-top zone-insights",
    },
]

_EDGES_META = [
    ("postgres-db",     "dlt-pipeline",    None),
    ("salesforce-crm",  "dlt-pipeline",    None),
    ("s3-files",        "dlt-pipeline",    None),
    ("databricks-jobs", "dlt-pipeline",    "orchestrate"),
    ("dlt-pipeline",    "bronze-layer",    "ingest"),
    ("bronze-layer",    "silver-layer",    "refine"),
    ("silver-layer",    "gold-layer",      "enrich"),
    ("bronze-layer",    "unity-catalog",   "register"),
    ("silver-layer",    "unity-catalog",   "register"),
    ("gold-layer",      "unity-catalog",   "register"),
    ("gold-layer",      "ml-pipeline",     "features"),
    ("gold-layer",      "bi-dashboard",    "query")
]

# Category colors used in the stylesheet
_CAT_COLORS = {
    "source":    {"bg": "#243552", "border": "#3A4E6A"},
    "ingestion": {"bg": "#1E3A3A", "border": "#2E5252"},
    "bronze":    {"bg": "#3C2A18", "border": "#5A4028"},
    "silver":    {"bg": "#28343E", "border": "#3A4A58"},
    "gold":      {"bg": "#3A3210", "border": "#5A4E20"},
    "catalog":   {"bg": "#183A2C", "border": "#285A48"},
    "consumer":  {"bg": "#1A3A24", "border": "#2A5A38"},
    "agent":     {"bg": "#301838", "border": "#4A2858"},
}


def get_nodes() -> list[dict]:
    nodes = list(_ZONE_NODES)
    for node_id, label, category in _NODES_META:
        parent = _NODE_PARENTS.get(node_id)
        data = {
            "id":          node_id,
            "label":       label,
            "category":    category,
            "description": _NODE_DESCRIPTIONS.get(node_id, ""),
        }
        if parent:
            data["parent"] = parent
        nodes.append({
            "data":     data,
            "position": _POSITIONS[node_id],
            "classes":  category,
        })
    return nodes


def get_edges() -> list[dict]:
    edges = []
    for source, target, label in _EDGES_META:
        edge: dict = {"data": {"source": source, "target": target}}
        if label:
            edge["data"]["label"] = label
        if label == "register":
            edge["classes"] = "registration-edge"
        edges.append(edge)
    return edges


def get_elements() -> list[dict]:
    return get_nodes() + get_edges()


def get_node_description(node_id: str) -> str:
    return _NODE_DESCRIPTIONS.get(node_id, "")


def _make_stylesheet() -> list[dict]:
    styles = [
        # Default leaf node
        {
            "selector": "node",
            "style": {
                "label":           "data(label)",
                "shape":           "roundrectangle",
                "width":           "130px",
                "height":          "40px",
                "text-valign":     "center",
                "text-halign":     "center",
                "text-wrap":       "wrap",
                "text-max-width":  "120px",
                "font-size":       "11px",
                "font-family":     "Inter, 'Segoe UI', system-ui, sans-serif",
                "color":           "#E8E4E0",
                "font-weight":     "600",
                "border-width":    "1px",
                "border-color":    "rgba(255,255,255,0.15)",
                "background-color":"#2A2624",
                "cursor":          "pointer",
            },
        },
        # Selected state — brand orange glow
        {
            "selector": "node:selected",
            "style": {
                "overlay-color":   "#E04B2A",
                "overlay-opacity": 0.14,
                "border-color":    "#E04B2A",
                "border-width":    "2.5px",
                "z-index":         10,
            },
        },
        # Click feedback
        {
            "selector": "node:active",
            "style": {
                "overlay-opacity": 0.08,
                "overlay-color":   "#FFFFFF",
            },
        },
        # Default edge
        {
            "selector": "edge",
            "style": {
                "curve-style":        "bezier",
                "target-arrow-shape": "triangle",
                "target-arrow-color": "#3A3835",
                "line-color":         "#3A3835",
                "width":              "1.5px",
                "opacity":            0.75,
                "arrow-scale":        0.85,
            },
        },
        # UC registration edges — dashed
        {
            "selector": ".registration-edge",
            "style": {
                "line-style":         "dashed",
                "line-color":         "#285A48",
                "target-arrow-color": "#285A48",
                "width":              "1.2px",
                "line-dash-pattern":  [4, 7],
                "opacity":            0.55,
            },
        },
        # Zone top-level compound nodes
        {
            "selector": ".zone-top",
            "style": {
                "shape":             "roundrectangle",
                "background-opacity": 0.28,
                "border-width":      "1px",
                "border-opacity":    0.35,
                "font-size":         "9px",
                "font-weight":       "bold",
                "text-valign":       "top",
                "text-halign":       "center",
                "text-margin-y":     13,
                "padding":           "24px",
                "events":            "no",
                "cursor":            "default",
            },
        },
        {"selector": ".zone-sources",
         "style": {"background-color": "#1C2A3E", "border-color": "#2A3A52", "color": "#4A6080"}},
        {"selector": ".zone-lakehouse",
         "style": {"background-color": "#1A1714", "border-color": "#2A2520", "color": "#5A5040"}},
        {"selector": ".zone-insights",
         "style": {"background-color": "#182622", "border-color": "#28352E", "color": "#406040"}},
        # Sub-zone compound nodes within lakehouse
        {
            "selector": ".zone-sub",
            "style": {
                "shape":             "roundrectangle",
                "background-color":  "#1A1714",
                "background-opacity": 0.12,
                "border-width":      "0.5px",
                "border-color":      "rgba(255,255,255,0.10)",
                "font-size":         "8px",
                "font-weight":       "bold",
                "text-valign":       "top",
                "text-halign":       "center",
                "text-margin-y":     8,
                "color":             "#484844",
                "padding":           "18px",
                "events":            "no",
                "cursor":            "default",
            },
        },
    ]

    # Per-category fills
    for cat, c in _CAT_COLORS.items():
        styles.append({
            "selector": f".{cat}",
            "style": {"background-color": c["bg"], "border-color": c["border"]},
        })

    return styles


CYTOSCAPE_STYLESHEET = _make_stylesheet()
