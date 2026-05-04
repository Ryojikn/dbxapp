# Feature Specification: Databricks Platform Demo App

**Feature Branch**: `001-databricks-demo-app`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "Build an interactive demo application that showcases an end-to-end Databricks data platform reference architecture, deployable as a Databricks App."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Audience Orientation via Home Tab (Priority: P1)

A technical stakeholder (data engineer, architect, or data leader) opens the app for the first time and immediately understands the purpose of the demo, the business problem being solved, and what they are about to see — without any verbal explanation from the presenter.

**Why this priority**: If a viewer cannot orient themselves in the first 60 seconds, the rest of the demo loses its narrative thread. The Home tab is the foundation everything else builds on.

**Independent Test**: A user can open the app, read the Home tab alone, and correctly describe the demo's purpose, audience, and structure to someone who has not seen it — without clicking any other tab.

**Acceptance Scenarios**:

1. **Given** the app is open on the Home tab, **When** a first-time viewer reads the page for 90 seconds, **Then** they can name the project, the business problem it solves, and the three tabs available.
2. **Given** the Home tab is visible, **When** the presenter clicks a preview card, **Then** the app navigates to the corresponding tab without a full page reload and without losing scroll position in the Home tab if the user returns.
3. **Given** the Home tab is visible, **When** the viewer examines the metadata section, **Then** they can identify the intended audience, the data domain, and find links to the underlying repo and reference documentation.

---

### User Story 2 — Architecture Diagram Walkthrough (Priority: P2)

A presenter navigates to the Architecture tab and walks the audience through the end-to-end data flow, from source systems through the medallion layers to downstream consumers and the AI anomaly agent, using the visual diagram as the primary narrative device.

**Why this priority**: The architecture diagram is the core intellectual artifact of the demo. It must convey the platform story without supplemental slides or verbal scaffolding.

**Independent Test**: A viewer can read the Architecture tab diagram without any narration and correctly trace the path data takes from a source system to a gold-layer consumer, including naming the three medallion stages and identifying the AI agent's position in the flow.

**Acceptance Scenarios**:

1. **Given** the Architecture tab is open, **When** the viewer reads the diagram without narration, **Then** they can identify all six component categories: sources, ingestion pipelines, Unity Catalog, bronze/silver/gold medallion layers, downstream consumers (ML pipeline + BI dashboard), and the anomaly AI agent.
2. **Given** the diagram is rendered, **When** the viewer hovers over or clicks any node, **Then** a tooltip or detail panel appears with a plain-language paragraph describing that component's role.
3. **Given** the Architecture tab is visible on a 1920×1080 screen, **When** a screenshot is taken, **Then** all node labels, arrows, and captions are legible and unclipped — the image is ready to paste into a slide deck without cropping or relabeling.
4. **Given** the presenter has opened the Architecture tab and then switches to Dashboard, **When** they switch back to Architecture, **Then** the diagram is in the same scroll/zoom state as when they left.

---

### User Story 3 — Interactive Dashboard with Embedded Chat (Priority: P3)

An audience member or presenter interacts with the Dashboard tab, reads the KPI tiles and charts driven by gold-layer fixture data, and uses the embedded "Ask the data" chat panel to ask natural-language questions — including a pre-rehearsed anomaly question that triggers a specific investigative response.

**Why this priority**: The dashboard makes the gold layer tangible and shows the AI-assisted analytics experience. It is the most engaging part of the demo but depends on the narrative context established by tabs 1 and 2.

**Independent Test**: A user can open only the Dashboard tab, read the KPIs and charts, ask three pre-rehearsed questions in the chat panel, receive on-topic answers that reference the visible metrics, and witness at least one anomaly callout with a proposed next step.

**Acceptance Scenarios**:

1. **Given** the Dashboard tab is open, **When** the viewer reads the KPI tiles, **Then** they can identify at least three business metrics (e.g., total revenue, order count, anomaly count) with current values.
2. **Given** the Dashboard tab is open, **When** the viewer reads the charts, **Then** they can see a time-series trend, a categorical breakdown, and an anomaly/status table — all driven by internally consistent fixture data.
3. **Given** the chat panel is visible, **When** the presenter types a pre-rehearsed question about a visible metric (e.g., "What drove the revenue spike last week?"), **Then** the chat returns an answer that references the specific metric value shown in the chart.
4. **Given** the chat panel is visible, **When** the presenter asks an anomaly question (e.g., "Are there any unusual patterns I should investigate?"), **Then** the chat names at least one specific anomaly visible in the status table and proposes an investigative or remedial next step.
5. **Given** the presenter is on Dashboard and switches to Architecture, **When** they return to Dashboard, **Then** chart state and chat history are preserved without re-fetching or re-rendering.

---

### Edge Cases

- What happens when the presenter clicks a tab during a chart animation? State is preserved; the animation may reset when the tab is revisited but no data is lost.
- How does the chat panel handle a question with no keyword match? It returns a graceful fallback response directing the user to rephrase, rather than an error or empty reply.
- What if the browser window is resized mid-demo? The layout remains usable at common laptop resolutions (1280×800 minimum); mobile breakpoints are not required and not guaranteed.
- What if a node tooltip is partially off-screen at the diagram edge? The tooltip repositions to stay within the viewport.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST present a three-tab navigation interface labeled "Home," "Architecture," and "Dashboard" that preserves scroll position and in-tab state when the user switches between tabs.
- **FR-002**: The Home tab MUST display: a project name, a one-line value proposition, a narrative paragraph describing the business problem and approach, three preview cards linking to Architecture and Dashboard tabs, and a metadata section with intended audience, data domain, and links to the repo and reference docs.
- **FR-003**: The Architecture tab MUST render a visual diagram containing labeled nodes for all six component categories: source systems, ingestion/transformation pipelines, Unity Catalog governed storage, three medallion layers (bronze, silver, gold) with directional refinement arrows and per-stage captions, at least two downstream consumers branching from gold (an ML pipeline and a BI dashboard), and an anomaly-aware AI agent attached to the consumption layer.
- **FR-004**: Each node in the Architecture diagram MUST reveal a plain-language descriptive paragraph on hover or click, without navigating away from the tab.
- **FR-005**: The Architecture diagram MUST be legible at projector distance (clear labels, no overlapping arrows, consistent iconography per component category) and render fully within a standard 1920×1080 viewport without scrolling, so a screenshot requires no post-processing to use in a slide deck.
- **FR-006**: The Dashboard tab MUST display at minimum: three KPI tiles with current metric values, a time-series trend chart, a categorical breakdown chart, and a status/anomaly table — all driven by internally consistent fixture data.
- **FR-007**: The Dashboard tab MUST include an embedded chat panel (side or bottom position, visually subordinate to the charts) that accepts free-text natural-language questions and returns answers referencing visible metric values from the fixture dataset.
- **FR-008**: The chat panel MUST be pre-configured to handle at least three rehearsed question patterns, including one that names a specific anomaly visible in the status table and proposes an investigative or remedial next step.
- **FR-009**: The entire demo path (all three tabs, all chart renders, all chat responses) MUST function with no live external service calls — fixture data and pre-baked response logic are the only required data sources.
- **FR-010**: The application MUST be deployable as a Databricks App and launchable from within a Databricks workspace without additional infrastructure provisioning.
- **FR-011**: A developer following the project README MUST be able to go from a clean repository clone to a running, presentable Databricks App in under 30 minutes.

### Key Entities

- **Demo Dataset**: Internally consistent tabular fixture data representing a plausible business domain (e.g., retail orders or IoT sensor readings). Contains at minimum: a time dimension for trend charting, a categorical dimension for breakdown charting, numeric KPI fields, and one or more anomaly-flagged records for the status table.
- **Architecture Node**: A labeled diagram element representing one platform component. Carries: a unique identifier, a display name, a component category (source / ingestion / storage / medallion / consumer / agent), a short label, and a descriptive paragraph for the hover/click detail panel.
- **Chat Response Rule**: A pre-baked input→output mapping keyed on question keywords or intent patterns. Each rule references specific fixture KPI values so answers remain consistent with the visible dashboard state. At least one rule is designated as the "anomaly" rule and triggers a named anomaly callout with a next-step recommendation.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A presenter can navigate Home → Architecture → Dashboard and complete a coherent verbal walkthrough in under 5 minutes from the moment the first tab renders.
- **SC-002**: After the Architecture tab walkthrough, a first-time audience member (with no prior briefing) can verbalize the data flow — naming sources, ingestion, the three medallion stages, and at least one gold-layer consumer — without prompting.
- **SC-003**: A screenshot of the Architecture diagram taken at 1920×1080 can be pasted directly into a slide deck without cropping, resizing, relabeling, or touching up any element.
- **SC-004**: The chat panel returns a relevant, metric-referencing answer to at least three pre-rehearsed questions, including one that names a specific anomaly and proposes a concrete next step.
- **SC-005**: A developer can clone the repository and reach a running, fully presentable app on Databricks Apps in under 30 minutes following only the instructions in the project README.
- **SC-006**: Switching between any two tabs and back preserves the originating tab's scroll position and in-tab state (chart state, chat history) with no visible flash or reload artifact.

---

## Assumptions

- The presenter laptop runs a modern Chromium-based or Firefox browser at 1920×1080 or similar widescreen resolution; mobile-first responsive design is out of scope.
- The exact business domain for the fixture dataset (retail, IoT, finance, etc.) is chosen by the implementer; the spec does not mandate a domain, only that the data is internally consistent and tells a believable story.
- The chat panel uses keyword/intent matching over fixture data rather than a live LLM call, ensuring zero runtime external dependencies on the rehearsed demo path.
- The application framework is Python-based (the standard for Databricks Apps); specific framework choice (Dash, Streamlit, Flask + React, etc.) is left to the implementer.
- All diagram assets (icons, SVG shapes, fonts) are either inlined or bundled with the app — no CDN dependency is assumed available in the demo environment.
- Authentication, authorization, per-user session persistence, and audit logging are explicitly out of scope for this iteration.
- The app does not need to handle concurrent users beyond a single active presenter session; no load-testing targets are required.
- Links to "repo" and "reference documentation" on the Home tab may point to placeholder URLs in the initial build and be updated before the live demo.
