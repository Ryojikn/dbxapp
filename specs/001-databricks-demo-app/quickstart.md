# Quickstart: Databricks Platform Demo App

**Target**: Clone → running Databricks App in under 30 minutes  
**Stack**: Dash 2.x · Dash Bootstrap Components · Plotly Express · dash_cytoscape

---

## Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| Python | 3.10+ | `python --version` |
| pip | 23+ | `pip --version` |
| Databricks CLI | 0.200+ | `databricks --version` |
| Databricks workspace access | — | `databricks auth status` |
| (Optional) Model Serving endpoint | — | Serving → Endpoints in workspace UI |

---

## Step 1: Clone and Install (~3 min)

```bash
git clone <repo-url> databricks-demo-app
cd databricks-demo-app
pip install -r requirements.txt
```

**`requirements.txt`**:
```
dash==2.17.0
dash-bootstrap-components==1.6.0
dash-cytoscape==1.0.2
plotly==5.22.0
pandas==2.2.2
requests==2.31.0
```

---

## Step 2: Verify Locally (~2 min)

```bash
python app.py
```

Open `http://localhost:8050` in a browser. You should see:
- Three tabs: Home, Architecture, Dashboard
- Architecture diagram with 13 nodes and directional arrows
- Dashboard with 4 KPI tiles, 2 charts, anomaly table, and chat panel
- Chat responds to: "total revenue", "which category", "any anomalies"

---

## Step 3: (Optional) Wire Live Chat to Model Serving

Skip this step if you want the pre-baked chat mode only.

Set these environment variables before running or before Databricks App deploy:

```bash
export DATABRICKS_HOST="https://<workspace-host>"
export DATABRICKS_TOKEN="<personal-access-token-or-SP-token>"
export DATABRICKS_SERVING_ENDPOINT="<endpoint-name>"   # e.g., databricks-meta-llama-3-1-70b-instruct
```

When these are set, questions that do not match a keyword rule are forwarded to the Model Serving endpoint with a system prompt seeded with the current KPI values.

---

## Step 4: Deploy to Databricks Apps (~5 min)

```bash
databricks apps create databricks-demo-app
databricks apps deploy databricks-demo-app --source-code-path .
```

Or via the Databricks workspace UI:
1. Go to **Compute → Apps → Create App**
2. Select **Custom** → upload this folder or link the repo
3. Set the command to `python app.py`
4. (Optional) Set `DATABRICKS_SERVING_ENDPOINT` in the app environment config
5. Click **Deploy**

The app URL appears in the Apps panel. Share it with the audience before the demo.

---

## Step 5: Rehearse the Demo Path (~10 min)

Walk through this path before the live session:

| Step | Action | Expected outcome |
|------|--------|-----------------|
| 1 | Open app → Home tab | Title, value prop, 3 preview cards, metadata links visible |
| 2 | Click "Architecture" preview card | Architecture tab opens; 13-node diagram rendered |
| 3 | Hover over "Gold — Enriched" node | Description panel shows gold layer explanation |
| 4 | Hover over "Anomaly AI Agent" node | Description panel shows AI agent explanation |
| 5 | Click "Dashboard" in nav | Dashboard tab opens; 4 KPI tiles visible |
| 6 | Read KPI tiles | Revenue $2.85M, Orders 18,429, Avg $154.52, Anomalies 1 |
| 7 | Type in chat: "What is our total revenue?" | Response references $2,847,392 and +12% MoM |
| 8 | Type in chat: "Which category is growing fastest?" | Response names Sports +28% QoQ |
| 9 | Type in chat: "Are there any anomalies I should investigate?" | Response names March 18, margin 23%→6%, order ORD-48821, recommends procurement review |
| 10 | Switch back to Architecture tab | Diagram scroll state preserved; no reload |

---

## Total Time Budget

| Task | Time |
|------|------|
| Clone + pip install | 3 min |
| Local smoke test | 2 min |
| Databricks App deploy | 5 min |
| Rehearsal run | 10 min |
| **Total** | **20 min** |

Buffer: 10 minutes for troubleshooting or configuration.

---

## Troubleshooting

**App shows blank page after deploy**: Check that `app.py` reads `PORT = int(os.environ.get("PORT", 8050))` and passes it to `app.run(port=PORT, host="0.0.0.0")`.

**Architecture diagram not rendering**: Ensure `dash-cytoscape==1.0.2` is in requirements.txt. The dagre layout script is bundled by dash_cytoscape — no CDN needed.

**Chat returns "I could not reach the model"**: The LLM proxy timed out or env vars are missing. The keyword-matched fallback takes over automatically. Pre-rehearsed questions still work.

**Tab switch loses chart state**: Confirm `dcc.Store(id="dashboard-filter-store", storage_type="memory")` is in the app layout, and that the chart callbacks read from the store rather than from a standalone dropdown.
