"""
Architecture diagram data for the Databricks Platform Demo App.
Provides Cytoscape elements (nodes + edges) for the Tab 2 diagram.
"""

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

# Preset positions for all leaf nodes
_POSITIONS = {
    "postgres-db":    {"x": 80,   "y": 90},
    "salesforce-crm": {"x": 80,   "y": 210},
    "s3-files":       {"x": 80,   "y": 330},
    "kafka-stream":   {"x": 80,   "y": 450},
    "autoloader":     {"x": 295,  "y": 170},
    "dlt-pipeline":   {"x": 295,  "y": 375},
    "unity-catalog":  {"x": 645,  "y": 440},
    "bronze-layer":   {"x": 490,  "y": 255},
    "silver-layer":   {"x": 645,  "y": 255},
    "gold-layer":     {"x": 800,  "y": 255},
    "ml-pipeline":    {"x": 1010, "y": 170},
    "bi-dashboard":   {"x": 1010, "y": 330},
    "ai-agent":       {"x": 1010, "y": 450},
}

# Leaf node metadata: (id, label, category)
_NODES_META = [
    ("postgres-db",    "PostgreSQL DB",      "source"),
    ("salesforce-crm", "Salesforce CRM",     "source"),
    ("s3-files",       "S3 / File Drops",    "source"),
    ("kafka-stream",   "Kafka Stream",       "source"),
    ("autoloader",     "Auto Loader",        "ingestion"),
    ("dlt-pipeline",   "Lakeflow Pipelines", "ingestion"),
    ("unity-catalog",  "Unity Catalog",      "catalog"),
    ("bronze-layer",   "Bronze",             "bronze"),
    ("silver-layer",   "Silver",             "silver"),
    ("gold-layer",     "Gold",               "gold"),
    ("ml-pipeline",    "ML Pipeline",        "consumer"),
    ("bi-dashboard",   "BI Dashboard",       "consumer"),
    ("ai-agent",       "AI Agent",           "agent"),
]

# Parent zone assignment for each leaf node
_NODE_PARENTS = {
    "postgres-db":    "zone-sources",
    "salesforce-crm": "zone-sources",
    "s3-files":       "zone-sources",
    "kafka-stream":   "zone-sources",
    "autoloader":     "zone-ingestion",
    "dlt-pipeline":   "zone-ingestion",
    "bronze-layer":   "zone-medallion",
    "silver-layer":   "zone-medallion",
    "gold-layer":     "zone-medallion",
    "unity-catalog":  "zone-medallion",
    "ml-pipeline":    "zone-insights",
    "bi-dashboard":   "zone-insights",
    "ai-agent":       "zone-insights",
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
