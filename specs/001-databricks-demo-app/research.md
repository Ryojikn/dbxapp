# Research: Databricks Platform Demo App

**Branch**: `001-databricks-demo-app` | **Date**: 2026-05-03  
**Resolved by**: `/speckit-plan` Phase 0

---

## Decision 1: Application Framework

**Decision**: **Dash 2.x with Dash Bootstrap Components (DBC)**

**Rationale**:

| Dimension | Gradio | Streamlit | **Dash** | Next.js |
|-----------|--------|-----------|----------|---------|
| Time to first render (writing code) | 10 min | 15 min | **18-22 min** | 30-40 min |
| Tab state preservation | Partial / buggy | Re-renders whole script; scroll position lost | **`dcc.Store` preserves chart + chat state** | Excellent (React) |
| Architecture diagram quality | SVG-only, no tooltips | Text-only tooltips (streamlit-agraph) | **Rich HTML tooltips via dash_cytoscape** | Excellent (react-flow) |
| Chat wiring to Model Serving | Simple (requests) | Simple (requests + `st.session_state`) | **Callback + requests** | API route + fetch |
| Databricks App template | Minimal | ✅ Official | ✅ Official | Manual app.yaml |
| Screenshot-ready diagram | ❌ | ⚠️ adequate | ✅ | ✅ |
| 30-min build risk | Low | Low | **Medium (manageable)** | High |

**Why not Streamlit**: Streamlit's tab implementation re-renders all components on every interaction. While `st.session_state` preserves values, the actual chart DOM state (zoom level, pan position) is lost on every tab switch — violating SC-006. More critically, `streamlit-agraph` node tooltips are plain-text-only: this fails SC-003 (screenshot-ready architecture diagram). The architecture diagram is the highest-visibility artifact of the demo and must meet the "drop into slide deck" bar.

**Why not Gradio**: Known tab-switching bugs with state. Suited for single-function ML model demos, not a multi-section narrative presentation. Architecture diagram customization is severely limited.

**Why not Next.js**: The 30-minute budget covers clone-to-running-Databricks-App. A Next.js project (create-next-app + npm install + next build + app.yaml configuration) consumes that window before a single line of feature code is written. Viable for a 2-day sprint; not for a 30-minute timebox.

**Dash trade-off accepted**: ~3-5 minutes slower than Streamlit on initial code-write. Offset by template scaffolding and the diagram quality payoff.

**Alternatives considered**:
- Streamlit: rejected (diagram quality, chart state loss)
- Gradio: rejected (tab state bugs, layout limitations)
- Next.js: rejected (30-min constraint)

---

## Decision 2: Architecture Diagram Library

**Decision**: **dash_cytoscape 1.x**

**Rationale**: The spec requires nodes with hover-revealed description paragraphs and the diagram must be screenshot-ready at 1920×1080 for slide decks. dash_cytoscape provides:
- Cytoscape.js layout engine (dagre layout for clean directed graphs)
- `mouseoverNodeData` event → Dash callback → detail panel update (one-paragraph description)
- Arrow markers on edges via stylesheet `target-arrow-shape: triangle`
- Full CSS-level control over node size, color, font, and spacing
- Renders entirely as an HTML canvas — no SVG serialization, no CDN dependency

**Alternatives considered**:
- Inline SVG with hover handlers: hand-crafted positioning is fragile at different viewport sizes; "screenshot-ready" bar is hard to guarantee
- streamlit-agraph: text-only tooltips; not on the Dash stack
- react-flow: not on the Dash stack

---

## Decision 3: Chart Library

**Decision**: **Plotly Express (bundled with Dash)**

**Rationale**: No additional install required. `dcc.Graph` wraps Plotly figures natively. Plotly charts:
- Are interactive out of the box (zoom, pan, hover) with no extra code
- Export cleanly via the "camera" icon in the chart toolbar
- Support all required chart types: time-series line (`px.line`), categorical bar (`px.bar`), and a styled table for the anomaly status panel (`dash_table.DataTable`)
- Render without any CDN dependency (all JS bundled by Dash)

---

## Decision 4: Chat Panel Implementation

**Decision**: **Keyword-matching engine with optional Databricks Model Serving passthrough**

**Rationale**: FR-009 requires zero external-service calls on the rehearsed demo path. The chat panel uses a deterministic keyword-matching engine keyed on fixture metric values for the three pre-rehearsed questions. When `DATABRICKS_HOST` and `DATABRICKS_SERVING_ENDPOINT` environment variables are present (i.e., deployed inside a Databricks workspace), the app additionally offers a live LLM path. The keyword matcher always wins for the three scripted questions regardless of mode, ensuring the rehearsed demo never fails.

**Model Serving call format** (when live):
```
POST https://{DATABRICKS_HOST}/serving-endpoints/{DATABRICKS_SERVING_ENDPOINT}/invocations
Authorization: Bearer {DATABRICKS_TOKEN}
Content-Type: application/json

{"messages": [{"role": "system", "content": "<seeded-metrics-prompt>"}, {"role": "user", "content": "<user-question>"}]}
```

The system prompt is assembled at runtime from the current KPI fixture values, so the LLM response references the numbers visible on screen.

**Alternatives considered**:
- Live-only LLM: violates FR-009 (demo breaks if no network / endpoint not deployed)
- Pre-baked static responses only: works but misses the "showcasing Databricks AI" narrative

---

## Decision 5: Fixture Data Domain

**Decision**: **Retail / E-commerce** — daily sales by product category

**Rationale**: Universally understood by any technical audience; avoids domain-specific jargon that could distract from the platform story. Data shape is simple: a date dimension, a category dimension, and numeric metrics (revenue, order count, COGS, margin). The anomaly story is immediately believable.

**Fixture dataset summary**:
- 90 days of daily sales: January 2025 through March 2025
- 4 product categories: Electronics, Apparel, Home & Garden, Sports
- One anomaly record: March 18, 2025 — Electronics COGS spike (+340% vs 7-day rolling average), margin collapsed from 23% to 6%, root cause: bulk order ORD-48821 priced below cost
- MTD KPIs (March 2025): Total Revenue $2,847,392 | Total Orders 18,429 | Avg Order Value $154.52 | Active Anomalies 1

**Three pre-rehearsed chat Q&A pairs**:

| # | Question pattern | Scripted response summary |
|---|------------------|--------------------------|
| 1 | "total revenue / how much revenue / revenue this month" | References $2.85M MTD, Electronics leading at $891K (31%), +12% MoM |
| 2 | "fastest growing / best performing category / which category" | Sports +28% QoQ (seasonal); Electronics highest absolute but +9% growth |
| 3 | "anomaly / unusual / investigate / alert / problem" | Names COGS spike on March 18, Electronics, margin 23%→6%, order ORD-48821; recommends procurement review |

---

## Decision 6: Deployment Mechanism

**Decision**: **Databricks Apps with `app.yaml` + Python runtime**

**app.yaml**:
```yaml
command: ["python", "app.py"]
```

Dash listens on `0.0.0.0:PORT` where `PORT` is injected by the Databricks Apps runtime. No Docker, no build step, no additional infrastructure. The official Dash template from `databricks/app-templates` provides the scaffolding.

**Environment variables used**:
- `PORT`: injected by Databricks Apps runtime (required)
- `DATABRICKS_HOST`: injected by runtime (optional — enables live LLM chat)
- `DATABRICKS_TOKEN`: injected or from Databricks secret scope (optional)
- `DATABRICKS_SERVING_ENDPOINT`: set by developer in app config (optional)

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Framework choice | Dash with DBC |
| Architecture diagram | dash_cytoscape (dagre layout) |
| Chart library | Plotly Express (Dash-native) |
| Chat: live vs pre-baked | Keyword-match primary; LLM passthrough when env vars present |
| Business domain | Retail/e-commerce |
| Node.js support on Databricks Apps | Confirmed supported; not needed for Dash/Python stack |
| Tab state | `dcc.Store(storage_type='memory')` per tab for chart filter state; chat history in server-side session via `dcc.Store` in layout |
