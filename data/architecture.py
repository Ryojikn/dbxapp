"""
Architecture diagram data for the Databricks Platform Demo App.
Provides Cytoscape elements (nodes + edges) for the Tab 2 diagram.
"""

from theme import CATEGORY_COLORS

# Node descriptions shown in the detail panel on hover/click
_NODE_DESCRIPTIONS = {
    "postgres-db": (
        "PostgreSQL is the primary operational database storing transactional "
        "records — orders, customers, and product inventory. It feeds the data "
        "platform via Change Data Capture (CDC), ensuring every committed row "
        "is captured and ingested in near-real time."
    ),
    "salesforce-crm": (
        "Salesforce CRM holds customer relationship and sales pipeline data. "
        "A scheduled export or REST API pull lands opportunity, account, and "
        "contact records into the platform for enrichment alongside transactional data."
    ),
    "s3-files": (
        "S3 (and compatible object stores) receive batch file drops — supplier "
        "cost sheets, marketing attribution exports, and third-party data feeds. "
        "Auto Loader monitors these prefixes and ingests new files as they arrive."
    ),
    "kafka-stream": (
        "Kafka delivers clickstream events and IoT sensor readings in real time. "
        "A Lakeflow Declarative Pipeline (DLT) source reads from the Kafka topic "
        "and lands events into the Bronze layer within seconds of production."
    ),
    "autoloader": (
        "Auto Loader (cloudFiles) is Databricks' incremental file ingestion engine. "
        "It detects new files in cloud storage using directory listing or event "
        "notifications, checkpoints progress, and writes raw records into Bronze "
        "Delta tables with exactly-once semantics."
    ),
    "dlt-pipeline": (
        "Lakeflow Declarative Pipelines (formerly Delta Live Tables) define "
        "Bronze-to-Silver-to-Gold transformations as SQL or Python declarations. "
        "The pipeline engine handles dependency ordering, error recovery, and "
        "data quality enforcement via expectations."
    ),
    "unity-catalog": (
        "Unity Catalog is the unified governance layer for all data assets. It "
        "provides a three-level namespace (catalog.schema.table), column-level "
        "lineage, fine-grained access control, and a searchable metadata registry "
        "spanning every Bronze, Silver, and Gold table in the platform."
    ),
    "bronze-layer": (
        "Bronze is the raw ingestion layer — data lands here exactly as it arrived "
        "from the source, with an appended ingestion timestamp and source identifier. "
        "No business logic is applied; Bronze is the immutable audit trail. "
        "Schema-on-read and schema evolution are handled here."
    ),
    "silver-layer": (
        "Silver is the curated, validated layer. Records are deduplicated, "
        "null-checked, typed correctly, and joined across sources. Silver tables "
        "are conformed to a canonical domain model and registered in Unity Catalog "
        "with column descriptions and data quality SLAs."
    ),
    "gold-layer": (
        "Gold holds business-ready, aggregated datasets optimised for specific "
        "analytical use cases. Denormalised for query performance, these tables "
        "are the single source of truth for dashboards, ML feature stores, and "
        "the AI agent monitoring layer. Liquid Clustering keeps them fast as data grows."
    ),
    "ml-pipeline": (
        "The ML Model Pipeline reads feature tables from the Gold layer via the "
        "Feature Engineering in Unity Catalog store, trains demand-forecast and "
        "anomaly-detection models with MLflow tracking, and registers champions "
        "to the UC Model Registry for scheduled batch scoring."
    ),
    "bi-dashboard": (
        "The BI / Analytics Dashboard queries Gold Delta tables through a SQL "
        "Warehouse. KPI tiles, trend charts, and anomaly tables refresh on a "
        "schedule or on user demand, giving business stakeholders a governed, "
        "low-latency view of operational performance."
    ),
    "ai-agent": (
        "The Anomaly-Aware AI Agent monitors Gold-layer signals and dashboard "
        "metrics using the Mosaic AI Agent Framework. When it detects a statistical "
        "deviation — like a COGS spike or a margin collapse — it fires a natural-"
        "language alert with a proposed remediation step, routed to the on-call team."
    ),
}

# Preset x/y positions for a clean left-to-right data-flow layout
_POSITIONS = {
    # Sources — column 1
    "postgres-db":    {"x": 80,   "y": 80},
    "salesforce-crm": {"x": 80,   "y": 200},
    "s3-files":       {"x": 80,   "y": 320},
    "kafka-stream":   {"x": 80,   "y": 440},
    # Ingestion — column 2
    "autoloader":     {"x": 280,  "y": 160},
    "dlt-pipeline":   {"x": 280,  "y": 360},
    # Unity Catalog — below medallion row (governance layer)
    "unity-catalog":  {"x": 620,  "y": 420},
    # Medallion — columns 3-5
    "bronze-layer":   {"x": 480,  "y": 240},
    "silver-layer":   {"x": 640,  "y": 240},
    "gold-layer":     {"x": 800,  "y": 240},
    # Consumers — column 6
    "ml-pipeline":    {"x": 1000, "y": 160},
    "bi-dashboard":   {"x": 1000, "y": 320},
    # AI Agent — column 7
    "ai-agent":       {"x": 1170, "y": 240},
}

_NODES_META = [
    ("postgres-db",    "PostgreSQL DB",      "source"),
    ("salesforce-crm", "Salesforce CRM",     "source"),
    ("s3-files",       "S3 / File Drops",    "source"),
    ("kafka-stream",   "Kafka Stream",       "source"),
    ("autoloader",     "Auto Loader (DLT)",  "ingestion"),
    ("dlt-pipeline",   "Lakeflow Pipelines", "ingestion"),
    ("unity-catalog",  "Unity Catalog",      "catalog"),
    ("bronze-layer",   "Bronze — Raw",       "bronze"),
    ("silver-layer",   "Silver — Curated",   "silver"),
    ("gold-layer",     "Gold — Enriched",    "gold"),
    ("ml-pipeline",    "ML Model Pipeline",  "consumer"),
    ("bi-dashboard",   "BI / Analytics",     "consumer"),
    ("ai-agent",       "Anomaly AI Agent",   "agent"),
]

_EDGES_META = [
    ("postgres-db",    "autoloader",     None),
    ("salesforce-crm", "autoloader",     None),
    ("s3-files",       "autoloader",     None),
    ("kafka-stream",   "dlt-pipeline",   None),
    ("autoloader",     "bronze-layer",   "ingest"),
    ("dlt-pipeline",   "bronze-layer",   "ingest"),
    ("bronze-layer",   "silver-layer",   "refine"),
    ("silver-layer",   "gold-layer",     "enrich"),
    ("bronze-layer",   "unity-catalog",  "register"),
    ("silver-layer",   "unity-catalog",  "register"),
    ("gold-layer",     "unity-catalog",  "register"),
    ("gold-layer",     "ml-pipeline",    "features"),
    ("gold-layer",     "bi-dashboard",   "query"),
    ("gold-layer",     "ai-agent",       "monitor"),
]


def get_nodes() -> list[dict]:
    nodes = []
    for node_id, label, category in _NODES_META:
        nodes.append({
            "data": {
                "id":          node_id,
                "label":       label,
                "category":    category,
                "description": _NODE_DESCRIPTIONS.get(node_id, ""),
            },
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


CYTOSCAPE_STYLESHEET = [
    # Default node style
    {
        "selector": "node",
        "style": {
            "label":          "data(label)",
            "shape":          "roundrectangle",
            "width":          "130px",
            "height":         "50px",
            "text-valign":    "center",
            "text-halign":    "center",
            "text-wrap":      "wrap",
            "text-max-width": "120px",
            "font-size":      "10px",
            "font-family":    "Inter, sans-serif",
            "color":          "#FFFFFF",
            "font-weight":    "600",
            "border-width":   "2px",
            "border-color":   "rgba(255,255,255,0.3)",
        },
    },
    # Default edge style
    {
        "selector": "edge",
        "style": {
            "curve-style":         "bezier",
            "target-arrow-shape":  "triangle",
            "target-arrow-color":  "#9E9E9E",
            "line-color":          "#9E9E9E",
            "width":               "2px",
            "font-size":           "9px",
            "color":               "#555",
            "label":               "data(label)",
            "text-rotation":       "autorotate",
        },
    },
    # Registration edges (UC) — dashed
    {
        "selector": ".registration-edge",
        "style": {
            "line-style":         "dashed",
            "line-color":         CATEGORY_COLORS["catalog"],
            "target-arrow-color": CATEGORY_COLORS["catalog"],
            "width":              "1.5px",
        },
    },
    # Highlighted node on tap
    {
        "selector": "node:selected",
        "style": {"border-width": "3px", "border-color": "#FFFFFF", "opacity": "1"},
    },
]

# Per-category background colors
for _cat, _color in CATEGORY_COLORS.items():
    CYTOSCAPE_STYLESHEET.append({
        "selector": f".{_cat}",
        "style": {"background-color": _color},
    })
