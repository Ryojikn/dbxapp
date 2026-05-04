# Tasks: Databricks Platform Demo App

**Input**: Design documents from `specs/001-databricks-demo-app/`  
**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · data-model.md ✅ · contracts/ ✅  
**Branch**: `001-databricks-demo-app`  
**Stack**: Dash 2.17 · Plotly 5.22 · Dash Bootstrap Components 1.6 · dash_cytoscape 1.0.2 · Pandas 2.2 · Python 3.11+

**User Stories (from spec.md)**:
- **US1 (P1)**: Audience orientation via Home Tab
- **US2 (P2)**: Architecture diagram walkthrough
- **US3 (P3)**: Interactive Dashboard with embedded chat

**Sequential build order (highest risk first)**: US3 Dashboard → US2 Architecture → US1 Home  
**All three can run in parallel after Phase 0 completes.**

---

## Format: `[ID] [P?] [Story?] Description — file path(s)`

- **[P]**: Parallelizable (different files, no incomplete-task dependencies)
- **[Story]**: Maps task to a user story (US1, US2, US3)
- **[BLOCKING]**: Must complete before downstream phases can start
- **[SMOKE]**: Spot-check that the unit of work renders / runs without errors
- **[POLISH]**: Optional; execute only if time budget allows

---

## Phase 0: Scaffolding (Critical Path — sequential, ~6 min)

**Purpose**: Shared infrastructure every tab module imports. Nothing else can start until T006 is done.

**⚠️ CRITICAL**: No tab work can begin until all Phase 0 tasks are complete.

- [x] T001 [BLOCKING] Create `requirements.txt` with pinned versions (`dash==2.17.0`, `plotly==5.22.0`, `dash-bootstrap-components==1.6.0`, `dash-cytoscape==1.0.2`, `pandas==2.2.2`, `requests==2.31.0`, `gunicorn==21.2.0`) and `.gitignore` (Python standard + `.env`) — `requirements.txt`, `.gitignore`
- [x] T002 [BLOCKING] Decide diagram approach: use `dash-cytoscape` (interactive hover; `dash-cytoscape==1.0.2` already in requirements.txt from T001). Add one-line comment `# Architecture diagram: dash_cytoscape with dagre layout (interactive hover)` to `app.py` — `app.py`
- [x] T003 [BLOCKING] Scaffold `app.py`: `dash.Dash` with `dbc.themes.BOOTSTRAP`, top-level layout with a branded header `dbc.Navbar`, `dcc.Tabs(id="app-tabs", value="tab-home")` containing three empty `dcc.Tab` children (value `tab-home` / `tab-architecture` / `tab-dashboard`), one `dcc.Store(id="tab-state-store", storage_type="memory")` for cross-tab state, and `server = app.server` exposed — `app.py`, `assets/styles.css`
- [x] T004 [BLOCKING] Write `app.yaml` declaring the Python runtime command `["gunicorn", "app:server", "--bind", "0.0.0.0:${PORT:-8050}", "--workers", "1"]` — `app.yaml`
- [x] T005 [BLOCKING] Write `theme.py`: Databricks brand color palette (deep red `#E04B2A`, dark `#1B1F23`, surface white `#FFFFFF`, text-muted `#6C757D`), spacing constants (`PAD_SM=8`, `PAD_MD=16`, `PAD_LG=24`), and Plotly base `layout_template` dict (background, font, gridlines) — `theme.py`
- [x] T006 [BLOCKING] Write `data/fixtures.py`: build 360-row Pandas DataFrame (`date`, `category`, `revenue`, `order_count`, `avg_order_value`, `cogs`, `gross_margin_pct`, `is_anomaly`, `anomaly_reason`, `anomaly_order_ref`); compute `KPI_SUMMARY` dict; export `CHAT_QA` dict with three pre-baked Q&A pairs (revenue, category growth, anomaly); all per `specs/001-databricks-demo-app/contracts/fixture-data.md` — `data/__init__.py`, `data/fixtures.py`

**Checkpoint**: `python -c "from data.fixtures import KPI_SUMMARY, CHAT_QA; print(KPI_SUMMARY)"` prints the KPI dict without error.

---

## Phase 1: Foundational Data and Chat Logic

**Purpose**: Data-layer modules consumed by US3 and US2. No Dash imports; independently unit-testable.

**Depends on**: Phase 0 complete

- [x] T007 [P] Write `data/architecture.py`: 13 `ArchitectureNode` dicts + 14 `ArchitectureEdge` dicts; `get_elements()` returning the merged Cytoscape-format list; `get_node_description(node_id: str) -> str`; per `specs/001-databricks-demo-app/contracts/fixture-data.md` — `data/architecture.py`
- [x] T008 [P] Write `data/chat.py`: 5 `ChatRule` dicts with `trigger_keywords`, `response_template`, `is_anomaly_rule`, `priority`; `match_rule(question, rules) -> dict`; `render_response(rule, kpi) -> str`; per `specs/001-databricks-demo-app/contracts/fixture-data.md` — `data/chat.py`

**Checkpoint**: `python -c "from data.architecture import get_elements; print(len(get_elements()))"` prints `27` (13 nodes + 14 edges). `python -c "from data.chat import match_rule, render_response, get_chat_rules; r=match_rule('anomaly', get_chat_rules()); print(r['is_anomaly_rule'])"` prints `True`.

---

## Phase 2: User Story 3 — Dashboard + Chat Tab (Priority: P3) ⚠️ Build First (Highest Risk)

**Goal**: An interactive analytics tab with 4 KPI tiles, trend chart, category chart, anomaly table, and a chat panel that answers three pre-rehearsed questions from fixture data (and optionally proxies to Databricks Model Serving).

**Independent Test**: Open only the Dashboard tab in a browser. Read KPIs. Type "total revenue" → response cites $2,847,392. Type "fastest growing" → response cites Sports +28%. Type "any anomalies" → response names March 18 COGS spike, ORD-48821, and a remediation step.

**Depends on**: Phase 0, Phase 1

### Implementation for US3

- [x] T101 [P] [US3] KPI tile row: four `dbc.Card` components in a `dbc.Row` reading `KPI_SUMMARY` from `data/fixtures.py`; display revenue (formatted `$2,847,392`), order count (`18,429`), avg order value (`$154.52`), and anomaly count (`1`, styled with `danger` color variant) — `tabs/dashboard.py`
- [x] T102 [P] [US3] Revenue trend chart: `px.line(df, x="date", y="revenue", color="category", template=LAYOUT_TEMPLATE)` from `data/fixtures.py`; wrapped in `dcc.Graph(id="trend-chart", figure=fig)`; title "Daily Revenue by Category — Jan–Mar 2025" — `tabs/dashboard.py`
- [x] T103 [P] [US3] Category breakdown chart: `px.bar(df.groupby("category")["revenue"].sum().reset_index(), x="category", y="revenue", color="category", template=LAYOUT_TEMPLATE)`; wrapped in `dcc.Graph(id="category-chart")`; title "Total Revenue by Category, Q1 2025" — `tabs/dashboard.py`
- [x] T104 [P] [US3] Anomaly status table: `dash_table.DataTable` showing date, category, gross_margin_pct, anomaly_reason for rows where `is_anomaly=True`; style anomaly rows with `backgroundColor="#FFF3CD"` (amber highlight) — `tabs/dashboard.py`
- [x] T105 [US3] Chat panel UI (layout only): right-side `dbc.Col(width=4)` containing `html.Div(id="chat-messages", style={"height":"360px","overflowY":"auto"})`, `dcc.Store(id="chat-history-store", storage_type="memory", data=[])`, `dcc.Input(id="chat-input", type="text", placeholder="Ask the data...")`, and a `dbc.Button("Send", id="chat-send-btn")` — `tabs/dashboard.py`
- [x] T106 [US3] Chat fixture callback in `callbacks/chat.py`: `@app.callback` on `chat-send-btn.n_clicks` + `chat-input.n_submit`; reads `chat-input.value` + `chat-history-store.data`; calls `match_rule` + `render_response` from `data/chat.py`; appends Q+A to history; returns updated `chat-history-store.data`, rendered `html.Div` bubbles in `chat-messages.children`, and `""` to clear `chat-input.value` — `callbacks/__init__.py`, `callbacks/chat.py`
- [x] T107 [US3] Live Model Serving wiring in `callbacks/chat.py`: read `os.environ.get("DEMO_MODE", "fixture")`; when `DEMO_MODE=live`, call `POST {DATABRICKS_HOST}/serving-endpoints/{DATABRICKS_SERVING_ENDPOINT}/invocations` with Bearer token and a system prompt seeded from `KPI_SUMMARY` values; 10-second timeout; fall back silently to fixture responder on any error; anomaly rule always uses fixture response regardless of mode — `callbacks/chat.py`, `.env.example`
- [x] T108 [SMOKE] [US3] Start app, navigate to Dashboard tab, verify no `dash.exceptions.DuplicateCallbackOutput` or layout errors in console; ask "total revenue", "fastest growing", "any anomalies" in chat; confirm all three return on-topic answers — _(manual smoke test)_

**Checkpoint**: Dashboard tab is fully functional and independently demonstrable.

---

## Phase 3: User Story 2 — Architecture Tab (Priority: P2)

**Goal**: A presentation-grade interactive diagram with 13 nodes, directional arrows, and a hover-triggered description panel. Screenshot-ready at 1920×1080.

**Independent Test**: Open only the Architecture tab. Count that all six component categories are visible (source, ingestion, catalog, bronze/silver/gold, consumer, agent). Hover over "Gold — Enriched" → description paragraph appears. Screenshot at 1920×1080 → all labels and arrows visible without clipping.

**Depends on**: Phase 0, Phase 1 (T007)

### Implementation for US2

- [x] T201 [P] [US2] Cytoscape stylesheet in `data/architecture.py`: define `CYTOSCAPE_STYLESHEET` list — one style rule per `category` value setting `background-color`, `shape` (`rectangle` for all), `width`, `height`, `font-size: 11px`, `text-wrap: wrap`, `text-max-width: 80px`; arrow edges styled with `target-arrow-shape: triangle`, `curve-style: bezier`, `line-color: #6C757D` — `data/architecture.py`
- [x] T202 [P] [US2] Architecture tab layout (`tabs/architecture.py`): `html.H4("End-to-End Data Platform Architecture")`, one-paragraph narrative, `cyto.Cytoscape(id="arch-diagram", elements=get_elements(), stylesheet=CYTOSCAPE_STYLESHEET, layout={"name":"dagre","rankDir":"LR","nodeSep":30,"rankSep":80}, style={"width":"100%","height":"520px"})`, color-coded legend row (`dbc.Badge` per category), and a `dbc.Card(id="node-detail-panel")` below the diagram for descriptions — `tabs/architecture.py`
- [x] T203 [US2] Node hover callback in `callbacks/architecture.py`: `@app.callback(Output("node-detail-panel","children"), Input("arch-diagram","tapNodeData"))`; on tap, calls `get_node_description(node_id)` and returns a `dbc.CardBody([html.H6(label), html.P(description)])` — `callbacks/architecture.py`
- [x] T204 [US2] Export affordance: `dbc.Button("⬇ Download Diagram", id="export-btn", size="sm", outline=True)` + `dcc.Download(id="diagram-download")` callback that serves `assets/architecture_export.svg` (a static SVG fallback generated once from the cytoscape render); alternatively, if export library unavailable, link `html.A("Download SVG", href="/assets/architecture_export.svg", target="_blank")` — `tabs/architecture.py`, `assets/architecture_export.svg`
- [x] T205 [SMOKE] [US2] Open Architecture tab; confirm diagram renders with visible nodes and arrows; hover one node; confirm description panel updates; check no callback errors — _(manual smoke test)_

**Checkpoint**: Architecture tab is fully functional and independently demonstrable.

---

## Phase 4: User Story 1 — Home Tab (Priority: P1)

**Goal**: A landing page that orients first-time viewers in under 90 seconds — project name, value proposition, narrative, three nav cards, and metadata.

**Independent Test**: Open only the Home tab. Read for 90 seconds. Verbalize: project name, the business problem, and where to find Architecture and Dashboard. Click each nav card → correct tab opens.

**Depends on**: Phase 0 (T003 — tab state store must exist for navigation callbacks)

### Implementation for US1

- [x] T301 [P] [US1] Hero section (`tabs/home.py`): `html.H1("Databricks Platform Demo")`, `html.H5("From raw data to AI-powered insights — a live end-to-end reference architecture")`, a `dbc.Card` with the narrative paragraph explaining the retail analytics problem and Medallion architecture approach — `tabs/home.py`
- [x] T302 [P] [US1] Three navigation preview cards (`tabs/home.py`, `callbacks/navigation.py`): `dbc.Row` of three `dbc.Card` components — "Home" (active, no link), "Architecture" (description + `dbc.Button("Explore →", id="nav-to-arch")`), "Dashboard" (description + `dbc.Button("Explore →", id="nav-to-dash")`); callback in `callbacks/navigation.py` on each button click updates `app-tabs.value` to `"tab-architecture"` or `"tab-dashboard"` — `tabs/home.py`, `callbacks/navigation.py`
- [x] T303 [P] [US1] Metadata footer (`tabs/home.py`): `dbc.Row` with three `html.Small` cells — Audience: "Data Engineers, Architects, Data Leaders", Domain: "Retail / E-Commerce Analytics (fixture data)", Links: `html.A("GitHub Repo", href="#")` + `html.A("Databricks Docs", href="#")`; placeholder `href="#"` accepted in initial build — `tabs/home.py`
- [x] T304 [SMOKE] [US1] Open Home tab; confirm hero text visible; click "Architecture →" card button → app switches to Architecture tab; click browser back or "Home" tab → Home scroll position intact — _(manual smoke test)_

**Checkpoint**: Home tab is fully functional and independently demonstrable.

---

## Phase 5: Integration and Demo Path Validation

**Purpose**: Wire all three tabs into `app.py`, confirm no regressions, walk the full rehearsed path.

**Depends on**: Phases 2, 3, 4 complete

- [x] T401 [BLOCKING] Wire all tab modules into `app.py`: import `tabs/home.py`, `tabs/architecture.py`, `tabs/dashboard.py`; import `callbacks/chat.py`, `callbacks/architecture.py`, `callbacks/navigation.py`; assign each `dcc.Tab.children` to the corresponding layout function return value; confirm `app.layout` serializes without `DuplicateCallbackOutput` — `app.py`
- [x] T402 [BLOCKING] Full rehearsed path walk: Home → read hero → click "Architecture →" → hover "Gold — Enriched" node → verify description → click "Dashboard" tab → read 4 KPI tiles → type "total revenue" → verify response → type "which category is growing fastest" → verify response → type "are there any anomalies" → verify anomaly name + ORD-48821 + remediation step appear — _(manual validation)_
- [x] T403 [BLOCKING] Success-criteria mapping: for each SC in `specs/001-databricks-demo-app/spec.md` (SC-001 through SC-006), document "Met / Partially Met / Not Met" with one-line evidence in a comment block at the top of `app.py` — `app.py`
- [x] T404 [BLOCKING] Tag the last green commit: `git tag demo-stable-v1` so the demo can revert in under 30 seconds if Polish tasks destabilize the build — _(git command)_

**Checkpoint**: Full demo path walks cleanly. All six success criteria mapped. Green tag exists.

---

## Phase 6: Polish (Optional — execute only if time remains, ~2 min budget)

**Purpose**: Audience-visible refinements. Every task is demoteable with no functional loss.

- [ ] T501 [POLISH] Diagram visual refinement: audit Cytoscape stylesheet for icon/color consistency across all 8 category values; adjust `rankSep` / `nodeSep` if any node labels overlap at 1920×1080 — `data/architecture.py`
- [ ] T502 [POLISH] Plotly chart polish: apply `theme.COLORS` list to both charts so category colors match the diagram legend; add `hovertemplate` with revenue formatted as `$%{y:,.0f}` — `tabs/dashboard.py`, `theme.py`
- [ ] T503 [POLISH] Loading spinners: wrap `dcc.Graph(id="trend-chart")` and `dcc.Graph(id="category-chart")` and `#chat-messages` in `dcc.Loading(type="circle")` — `tabs/dashboard.py`
- [x] T504 [POLISH] README: write `README.md` with the 30-minute clone-to-deploy runbook (mirrors `specs/001-databricks-demo-app/quickstart.md`), `DEMO_MODE` toggle instructions, and the three pre-rehearsed chat questions — `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Scaffolding)**: No dependencies — start immediately. All 6 tasks sequential.
- **Phase 1 (Foundational)**: Depends on Phase 0 complete. T007 and T008 run in parallel.
- **Phases 2 / 3 / 4 (User Stories)**: All depend on Phase 0 + Phase 1 complete. Run in parallel or sequential (see Parallelization Map below).
- **Phase 5 (Integration)**: Depends on Phases 2, 3, and 4 all complete.
- **Phase 6 (Polish)**: Depends on Phase 5 complete.

### Within Each User Story

- Phase 2 (US3): T101–T104 are parallel (different components within `tabs/dashboard.py`). T105 depends on T101–T104 layout decisions. T106 depends on T105 and Phase 1. T107 depends on T106. T108 depends on T105–T107.
- Phase 3 (US2): T201–T202 are parallel. T203 depends on T201+T202. T204 depends on T202. T205 depends on T201–T204.
- Phase 4 (US1): T301–T303 are parallel. T302 depends on T003 (app-tabs store). T304 depends on T301–T303.

---

## Critical-Path Summary

| Order | Task | Cumulative Time |
|-------|------|----------------|
| 1 | T001 — requirements.txt + .gitignore | 1 min |
| 2 | T002 — diagram approach decision | 1 min |
| 3 | T003 — Dash scaffold + dcc.Tabs shell | 2 min |
| 4 | T004 — app.yaml | 1 min |
| 5 | T005 — theme.py tokens | 1 min |
| 6 | T006 — data/fixtures.py (360 rows + KPI + CHAT_QA) | 3 min |
| 7 | T101–T104 — KPI tiles + 2 charts + anomaly table (parallel) | 4 min |
| 8 | T105 — chat panel UI | 1 min |
| 9 | T106 — chat fixture callback | 2 min |
| 10 | T108 — Dashboard smoke test | 1 min |
| 11 | T007+T201+T202 — arch data + cytoscape layout (parallel) | 2 min |
| 12 | T203 — node hover callback | 1 min |
| 13 | T205 — Architecture smoke test | 1 min |
| 14 | T301–T303 — Home hero + cards + footer (parallel) | 2 min |
| 15 | T304 — Home smoke test | 1 min |
| 16 | T401 — wire all tabs into app.py | 1 min |
| 17 | T402 — full rehearsed path walk | 1 min |
| 18 | T403 — SC mapping + T404 git tag | 1 min |
| **Total** | | **≤ 27 min** |

> Critical path assumes sequential execution of highest-risk tasks (US3 first). With parallel agents on D/A/H, total drops to ~17 minutes.

---

## Parallelization Map

Once Phase 0 + Phase 1 are complete, the three sub-groups are fully independent:

```
Phase 0 (T001→T002→T003→T004→T005→T006) [sequential]
Phase 1 (T007 ‖ T008)                   [parallel]
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
[Agent D]   [Agent A]   [Agent H]
US3 tabs    US2 tabs    US1 tabs
T101-T108   T201-T205   T301-T304
                │
     └──────────┼──────────┘
                ▼
          Phase 5 Integration
          T401→T402→T403→T404
```

**Agent assignment**:
- **Agent D** (US3 Dashboard): `tabs/dashboard.py`, `callbacks/chat.py`, `.env.example` — needs `data/fixtures.py`, `data/chat.py`
- **Agent A** (US2 Architecture): `tabs/architecture.py`, `callbacks/architecture.py` — needs `data/architecture.py` (T007)
- **Agent H** (US1 Home): `tabs/home.py`, `callbacks/navigation.py` — needs only `app.py` for tab ID values

No shared file writes between agents. `callbacks/__init__.py` and `app.py` are written only in Phase 0 and Phase 5.

---

## Demoteable Tasks (cut in this order if budget tightens)

| Priority to Cut | Task | What is Lost |
|----------------|------|--------------|
| 1st | T204 — Export button | Diagram not downloadable; presenter uses screenshot instead. SC-003 still met via screenshot. |
| 2nd | T107 — Live Model Serving wiring | Chat stays in fixture mode only. Demo path unaffected (DEMO_MODE defaults to fixture). |
| 3rd | T203 — Node hover descriptions | Hover panel removed; descriptions shown as static legend text below diagram. SC still partially met. |
| 4th | T503 — Loading spinners | No visual feedback on chat/chart load. Not visible at demo speed. |
| 5th | T403 — SC mapping comment | Internal validation skipped; does not affect presenter experience. |
| 6th | T501 — Diagram polish | Minor visual imperfection in node layout; functionally unaffected. |
| 7th | T502 — Chart color polish | Charts use Plotly defaults instead of theme colors. Functionally identical. |
| 8th | T504 — README | Quickstart.md in specs/ serves as substitute. |

---

## Parallel Example: US3 Dashboard (Agent D)

```bash
# After Phase 0 + Phase 1 complete, launch these in parallel:
Task: "T101 — KPI tile row in tabs/dashboard.py"
Task: "T102 — Trend chart in tabs/dashboard.py"
Task: "T103 — Category bar chart in tabs/dashboard.py"
Task: "T104 — Anomaly DataTable in tabs/dashboard.py"
# Then sequentially:
Task: "T105 — Chat panel UI (depends on T101-T104 layout)"
Task: "T106 — Chat fixture callback (depends on T105)"
Task: "T107 — Live Model Serving wiring (depends on T106)"
Task: "T108 — Smoke test"
```

---

## Implementation Strategy

### MVP First (US3 Dashboard Only)

1. Phase 0: Scaffolding (T001–T006)
2. Phase 1: T007 + T008
3. Phase 2: T101–T108 (Dashboard)
4. **STOP and VALIDATE**: Dashboard demonstrates gold-layer analytics story
5. Sufficient to show the dashboard portion of the demo

### Full Demo Path (All Three Tabs)

1. Phase 0 → Phase 1 → Phase 2 (US3) → Phase 3 (US2) → Phase 4 (US1) → Phase 5
2. Each phase adds an independently testable tab
3. Phase 5 integration takes < 2 minutes since all modules are already tested

### Parallel Team Strategy (Three Agents)

1. One developer/agent completes Phase 0 + Phase 1 (sequential, ~9 min)
2. Three agents in parallel: Agent D (US3) ‖ Agent A (US2) ‖ Agent H (US1) (~7 min)
3. All agents finish → Phase 5 integration (~3 min)
4. Total wall time: ~19 minutes + 5-minute rehearsal = **24 minutes**

---

## Notes

- `[P]` tasks touch different files or are pure read-only — no write conflicts
- `[Story]` label maps every task to a specific user story for traceability and independent delivery
- T107 (live LLM) is fully behind `DEMO_MODE=live`; it is never exercised on the rehearsed path
- T105 (chat UI) is downstream of T101–T104 but does not block them — Dashboard is demonstrable with charts alone if T105–T107 are not yet done
- Tag `demo-stable-v1` (T404) before executing any Phase 6 Polish tasks
