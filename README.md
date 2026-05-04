# Databricks Platform Demo App

An interactive, three-tab demo showcasing an end-to-end Databricks data platform reference architecture. Built with Dash (Plotly), deployable as a Databricks App.

## 30-Minute Clone-to-Deploy Runbook

### Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.10+ | `python --version` |
| pip | 23+ | `pip --version` |
| Databricks CLI | 0.200+ | `databricks --version` |
| Databricks workspace | — | `databricks auth status` |

### Step 1 — Clone and install (~3 min)

```bash
git clone <repo-url> databricks-demo-app
cd databricks-demo-app
pip install -r requirements.txt
```

### Step 2 — Run locally (~2 min)

```bash
python app.py
```

Open `http://localhost:8050`. You should see three tabs: Home, Architecture, Dashboard.

### Step 3 — (Optional) Enable live LLM chat

```bash
export DEMO_MODE=live
export DATABRICKS_HOST="https://<workspace-host>"
export DATABRICKS_TOKEN="<token>"
export DATABRICKS_SERVING_ENDPOINT="<endpoint-name>"
python app.py
```

When `DEMO_MODE=fixture` (default), the chat panel uses pre-baked keyword responses — **no external calls, zero dependencies on the rehearsed path.**

### Step 4 — Deploy to Databricks Apps (~5 min)

```bash
databricks apps create databricks-demo-app
databricks apps deploy databricks-demo-app --source-code-path .
```

Or via the Workspace UI: **Compute → Apps → Create App → Custom → set command `python app.py`**.

## DEMO_MODE values

| Value | Behaviour |
|-------|-----------|
| `fixture` (default) | All chat responses use pre-baked keyword matching. No network calls. Safe for live demo. |
| `live` | Chat proxies to Databricks Model Serving endpoint. Falls back to fixture on timeout/error. |

## Three Pre-Rehearsed Chat Questions

Ask these in the Dashboard tab chat panel:

1. **"What is our total revenue this month?"**
   → Cites MTD revenue, MoM growth, and the top category with its revenue share.

2. **"Which category is growing the fastest?"**
   → Names Sports (+28% QoQ seasonal) and compares absolute contribution vs growth rate.

3. **"Are there any anomalies I should investigate?"**
   → Names March 18 COGS spike, margin collapse from 23% to ~6%, order ORD-48821, and recommends procurement team review.

## Rehearsed Demo Path (< 5 minutes)

1. **Home tab** — Read the value proposition and narrative. Click "Open Dashboard →".
2. **Architecture tab** — Point out the Bronze/Silver/Gold medallion row and the Unity Catalog governance layer below it. Click on the "Gold — Enriched" node to show its description. Mention the Anomaly AI Agent on the right.
3. **Dashboard tab** — Read the four KPI tiles aloud. Ask the three chat questions in order, ending with the anomaly question.

## Rollback

If a post-demo polish task breaks the build:

```bash
git checkout demo-stable-v1
```

## Project Structure

```
app.py                  Entry point; Dash layout + callback registration + server
app.yaml                Databricks Apps deployment config (gunicorn)
requirements.txt        Pinned Python dependencies
theme.py                Design tokens, colour palette, Plotly layout template
data/
  fixtures.py           360-row retail fixture dataset + KPI_SUMMARY + CHAT_QA
  architecture.py       Architecture diagram nodes, edges, Cytoscape stylesheet
  chat.py               Chat rules, keyword matching, response rendering
tabs/
  home.py               Tab 1 layout
  architecture.py       Tab 2 layout (dash_cytoscape diagram)
  dashboard.py          Tab 3 layout (KPIs, charts, anomaly table, chat panel)
callbacks/
  navigation.py         Home → tab navigation
  architecture.py       Node tap → detail panel
  chat.py               Chat submit → fixture/LLM response
assets/
  styles.css            Global CSS overrides
  architecture_export.svg  Static SVG export of the architecture diagram
```
