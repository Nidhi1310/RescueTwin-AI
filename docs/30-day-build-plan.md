# RescueTwin AI: 21-Day Build Plan

This is a complete implementation guide for building **RescueTwin AI: Autonomous Flood Response Command Center**, an AI/ML-first flagship project for a fictional district. The project is a decision-support digital twin, not a real emergency platform. It should be built incrementally, with a runnable application at the end of every day, using Git-friendly commits and no placeholder-only work.

## 1. Project Overview

RescueTwin AI is an interactive flood-response command center that lets a user simulate flood conditions across a fictional district, inspect damage and route impacts, and receive explainable recommendations for rescue operations.

The finished MVP must support this end-to-end loop:

1. Open the dashboard.
2. Select a rainfall scenario.
3. Update the district map and flood layers.
4. Inspect flooded zones and blocked roads.
5. Select an incident.
6. Receive route, hospital, shelter, and rescue-team recommendations.
7. Review the reasoning behind each recommendation.
8. Generate an incident report.

The project is intentionally scoped to one fictional district and one disaster type: flooding. That keeps the build realistic in about three weeks while still demonstrating system design, AI integration, geospatial reasoning, and enough full-stack execution to present the work well.

### Core Capabilities

- Interactive digital twin map
- Deterministic flood simulation
- Flood severity prediction using XGBoost
- Damage assessment using a pretrained model or deterministic fallback
- Safe route optimization with NetworkX
- Hospital recommendation
- Shelter recommendation
- Rescue team allocation
- Explainable recommendations
- AI-generated incident report
- Compact analytics dashboard

### Explicit Exclusions

- Authentication
- Microservices
- Kubernetes
- Redis
- RabbitMQ
- Reinforcement learning
- Real IoT
- Weather APIs
- Satellite APIs
- Drone APIs
- Multiple disaster types
- Cloud infrastructure

## 2. Target Architecture

The architecture should stay simple, modular, and easy to demo.

### Logical Layers

```text
frontend/         React + TypeScript + Vite + Tailwind + Leaflet + Recharts
backend/          FastAPI application and API routes
simulation/       Deterministic flood simulation engine
routing/          NetworkX-based route optimizer
ai/               Prediction, damage scoring, and decision services
reports/          Incident report generation
data/             Fictional district data, sample images, synthetic datasets
tests/            Automated tests
docs/             Documentation and implementation guide
```

### Runtime Flow

```text
UI scenario selection
    -> backend /simulate
        -> simulation engine
        -> prediction service
        -> routing service
        -> allocation engine
        -> report generator
    -> UI updates map, dashboard, and incident panel
```

### Backend Responsibilities

- Serve district metadata
- Run flood simulation
- Predict flood severity
- Compute damaged and blocked areas
- Recommend safe routes
- Recommend hospitals and shelters
- Assign rescue teams
- Produce explainable incident summaries
- Return a single decision payload for the dashboard

### Frontend Responsibilities

- Render district map and incident overlays
- Show scenario controls
- Display key metrics and analytics
- Surface recommendations and explanations
- Show generated incident reports
- Keep the experience visually polished and interview-ready

## 3. Engineering Principles

These principles should govern every daily change.

1. Build the smallest complete version of each capability before moving on.
2. Prefer deterministic logic when it improves reliability and demo stability.
3. Avoid hidden dependencies between modules.
4. Keep domain logic in backend services, not inside UI components.
5. Separate pure functions from IO-heavy code.
6. Make every API response explicit and typed.
7. Use real sample data instead of placeholder stubs.
8. Let the UI consume stable backend contracts.
9. Add tests as soon as a module has meaningful behavior.
10. Every day ends with a runnable application.

## 4. Development Workflow

### Daily Workflow

1. Review the prior day’s deliverable.
2. Implement only the day’s scope.
3. Verify behavior locally.
4. Run the relevant tests.
5. Commit the work as a single coherent increment.
6. Update docs if the behavior or API changed.

### Implementation Rules

- Do not start the next feature until the current one runs.
- Do not build speculative abstractions.
- Do not add unrelated polish before the core flow works.
- Do not introduce a dependency unless it directly supports a scoped requirement.
- If a module can be deterministic, make it deterministic.
- If a library can solve the problem reliably, use it instead of custom complexity.

### Git Strategy

- Commit once per day or once per coherent feature slice.
- Use descriptive commit messages:
  - `day-01: backend skeleton and district data`
  - `day-07: route optimizer and safety rules`
  - `day-24: dashboard polish and analytics`
- Keep branches and commits small enough to review quickly.

## 5. Recommended Tools

### Development

- VS Code or similar editor
- Git
- Python 3.11+
- Node.js 20+
- pnpm or npm

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Leaflet
- OpenStreetMap tiles
- Recharts

### Backend

- FastAPI
- Uvicorn
- Pydantic
- SQLite
- Pandas
- NumPy
- scikit-learn
- XGBoost
- NetworkX

### Testing and Quality

- Pytest
- Vitest or React Testing Library
- ESLint
- TypeScript compiler

### Final Week Delivery

- Docker

## 6. Standard Implementation Prompts

Use these prompt templates when starting a day in Codex.

### Build Prompt Template

```text
You are continuing the RescueTwin AI project.

Implement only the current day’s scope.
Use the existing codebase as the source of truth.
Keep the application runnable at the end of the task.
Prefer production-quality code over shortcuts.
Add tests for meaningful logic.
Do not introduce features outside the current day’s scope.

Before coding, summarize what will be built today, why it matters, and which files will likely change.
Then implement the work incrementally and verify it locally.
At the end, explain exactly how to run and test the result.
```

### Review Prompt Template

```text
Review the current RescueTwin AI implementation for correctness, edge cases, maintainability, and scope drift.
Focus on bugs, missing tests, weak abstractions, and integration risks.
Return findings first, ordered by severity.
Then give a concise summary of any broader risks that remain.
```

### Testing Prompt Template

```text
Run the relevant tests for the current RescueTwin AI module.
If anything fails, diagnose the failure, fix the code, and re-run the tests.
Confirm the application still runs after the fix.
Only report success when the module is verified end-to-end.
```

## 7. Review Prompts

Use these prompts for targeted quality checks during the month.

### API Review

```text
Review the FastAPI contract for RescueTwin AI.
Check that request and response shapes are typed, stable, and consistent with the frontend.
Look for missing validation, ambiguous fields, and error-handling gaps.
```

### Data Model Review

```text
Review the fictional district data and domain models.
Check whether the data is sufficient for simulation, routing, recommendation, and reporting.
Flag any missing relationships or unrealistic assumptions.
```

### Frontend Review

```text
Review the React dashboard for usability, state flow, map interaction quality, and visual hierarchy.
Check that the UI clearly explains flood status, blocked roads, and recommendations.
```

### AI Logic Review

```text
Review the flood prediction, routing, allocation, and reporting logic.
Check that each recommendation is explainable, stable, and justified by explicit inputs.
```

## 8. Testing Prompts

### Backend Tests

```text
Run the backend tests for simulation, prediction, routing, allocation, and API endpoints.
Verify deterministic outputs, edge cases, and failed-input behavior.
```

### Frontend Tests

```text
Run the frontend tests for dashboard state, scenario switching, recommendation rendering, and report generation flow.
Verify that the UI still renders and the main interaction loop works.
```

### Integration Tests

```text
Run the end-to-end checks that confirm the frontend can call the backend and render the full decision payload.
Verify scenario selection, map updates, and incident reports.
```

## 9. Daily Implementation Schedule

The schedule below is organized as a 21-day core build. If you have extra time, use the later days in this guide as polish and stabilization instead of expanding scope.

---

## Day 1

**Goal**

Establish the repository structure, backend entrypoint, shared domain model, and fictional district dataset.

**Tasks**

- Create the backend FastAPI app shell.
- Define core domain entities for zones, roads, facilities, and rescue teams.
- Create the fictional district with 10 zones, roads, hospitals, shelters, and rescue teams.
- Add basic health and district endpoints.
- Ensure the backend starts cleanly.

**Codex Implementation Prompt**

```text
Build the initial RescueTwin AI backend foundation.

Create the project skeleton with backend/app, backend/app/models, backend/app/services, backend/app/api, simulation, routing, ai, reports, tests, and docs.
Define the domain models for zones, roads, facilities, rescue teams, and district metadata.
Create a realistic fictional district dataset with exactly 10 flood zones, 25-40 roads, 2 hospitals, 3 shelters, and 5 rescue teams.
Add a FastAPI health endpoint and a district metadata endpoint.
Keep the code typed, modular, and easy to extend.
Do not add simulation or AI logic yet.
At the end, show exactly how to run the backend and confirm it starts successfully.
```

**Acceptance Checks**

- Backend starts without errors.
- Health endpoint returns `ok`.
- District endpoint returns the fictional district payload.
- All core domain objects are defined and imported correctly.

**End-of-Day Deliverable**

- Runnable backend skeleton with concrete district data.

---

## Day 2

**Goal**

Implement deterministic flood simulation inputs and outputs for rainfall scenarios.

**Tasks**

- Define rainfall scenarios: moderate, severe, extreme.
- Implement deterministic flood simulation using zone elevation, drainage, and scenario intensity.
- Return flood severity, affected zones, and blocked roads.
- Add simulation tests.

**Codex Implementation Prompt**

```text
Add the deterministic flood simulation engine for RescueTwin AI.

Use the fictional district model created earlier.
Implement rainfall scenarios with configurable intensity and generate flood severity per zone based on elevation, drainage score, and scenario weight.
Return a structured result containing scenario name, severity score, affected zones, blocked roads, and short explanation text.
Keep the simulator deterministic so the same inputs always produce the same result.
Add tests covering all three rainfall scenarios and edge cases for low- and high-elevation zones.
Expose the simulation through a backend endpoint without changing unrelated modules.
At the end, confirm the backend still runs and the new endpoint returns valid JSON.
```

**Acceptance Checks**

- All three scenarios produce stable results.
- Flood severity is explainable and reproducible.
- Blocked road logic is visible in the output.
- Tests pass.

**End-of-Day Deliverable**

- Working flood simulator API.

---

## Day 3

**Goal**

Create the synthetic data pipeline for flood prediction.

**Tasks**

- Define synthetic training data structure.
- Generate training data from rainfall, elevation, drainage score, and previous water level.
- Build a reusable dataset writer under `data/`.
- Add lightweight validation for the generated data.

**Codex Implementation Prompt**

```text
Build the synthetic data pipeline for the flood prediction model.

Generate a realistic tabular dataset for RescueTwin AI using rainfall, elevation, drainage score, previous water level, and target flood severity.
Write the dataset generation code so it can be reused later for training and testing.
Ensure the synthetic data is stable, shaped correctly, and large enough for a simple XGBoost baseline.
Add validation checks for missing values, expected ranges, and label distribution.
Do not train the model yet.
Confirm the backend and data scripts remain runnable.
```

**Acceptance Checks**

- Synthetic data can be generated on demand.
- Feature ranges are sensible.
- Dataset structure matches later training needs.

**End-of-Day Deliverable**

- Reusable synthetic training-data generator.

---

## Day 4

**Goal**

Train the flood prediction model with XGBoost and expose prediction endpoints.

**Tasks**

- Train an XGBoost model on synthetic data.
- Add a scikit-learn preprocessing and evaluation flow.
- Save model artifacts locally.
- Add a prediction endpoint that accepts district inputs.

**Codex Implementation Prompt**

```text
Implement the flood prediction service for RescueTwin AI using XGBoost.

Train a baseline model on the synthetic data generated previously.
Use scikit-learn utilities for train/test split and evaluation.
Save the trained model artifact locally so the backend can load it at runtime.
Expose a backend endpoint that accepts rainfall, elevation, drainage score, and previous water level and returns predicted flood severity plus a simple confidence indicator.
Add tests for training output, model loading, and prediction shape.
Do not build the UI yet.
At the end, confirm predictions are deterministic for the same inputs and the backend still runs.
```

**Acceptance Checks**

- Model trains successfully.
- Prediction endpoint returns severity and confidence.
- Saved artifact loads correctly.
- Tests pass.

**End-of-Day Deliverable**

- Operational flood prediction service.

---

## Day 5

**Goal**

Add static district map data and first-pass frontend shell.

**Tasks**

- Initialize the Vite React TypeScript app.
- Add Tailwind and base layout styles.
- Render the district outline and key markers.
- Connect the frontend to the district metadata endpoint.

**Codex Implementation Prompt**

```text
Start the RescueTwin AI frontend.

Create a Vite React TypeScript app with Tailwind styling and a clean layout for the command center.
Render the district overview using the backend district metadata endpoint.
Show a minimal map shell with zones, hospitals, shelters, and rescue team markers.
Keep the UI polished but simple.
Do not add scenario controls or recommendation logic yet.
Make sure the frontend runs locally and can call the backend successfully.
```

**Acceptance Checks**

- Frontend builds and runs.
- District data renders on the page.
- Styling is clean and readable.

**End-of-Day Deliverable**

- Running frontend shell connected to district data.

---

## Day 6

**Goal**

Implement the interactive Leaflet map and flood overlay rendering.

**Tasks**

- Integrate Leaflet and OpenStreetMap tiles.
- Render zones, roads, hospitals, shelters, and rescue teams on the map.
- Highlight flooded zones and blocked roads.
- Add scenario-driven visual updates.

**Codex Implementation Prompt**

```text
Implement the RescueTwin AI interactive map with Leaflet.

Render the fictional district on top of OpenStreetMap tiles.
Show zones, roads, hospitals, shelters, and rescue teams.
Use the flood simulation output to highlight affected zones and blocked roads.
Keep the map responsive and readable on standard desktop widths.
Do not add decision logic yet.
At the end, the user should be able to select a rainfall scenario and see the map update visually.
```

**Acceptance Checks**

- Map loads with tiles and overlays.
- Flooded zones and blocked roads are visually distinct.
- Scenario selection updates the map.

**End-of-Day Deliverable**

- Interactive map with flood overlays.

---

## Day 7

**Goal**

Implement safe route optimization using NetworkX.

**Tasks**

- Build the district graph from road segments.
- Remove flooded or blocked roads from path search.
- Calculate shortest safe route between an incident and candidate destinations.
- Return distance, estimated travel time, and explanation.

**Codex Implementation Prompt**

```text
Add the route optimization service to RescueTwin AI using NetworkX.

Build a graph from the fictional district road network.
Implement shortest-path logic that avoids flooded and blocked roads.
Return route distance, travel time, excluded roads, and a plain-language explanation of why the route is safe.
Add tests for normal routes, blocked roads, and no-route-available cases.
Expose the routing logic through a backend endpoint so the frontend can query it later.
```

**Acceptance Checks**

- Routes avoid blocked roads.
- Route output includes distance and time.
- No-route cases are handled gracefully.
- Tests pass.

**End-of-Day Deliverable**

- Working safe route optimizer API.

---

## Day 8

**Goal**

Implement hospital recommendation logic.

**Tasks**

- Score hospitals by distance, flood risk, and capacity.
- Select the nearest suitable hospital.
- Return a reasoned recommendation.

**Codex Implementation Prompt**

```text
Build hospital recommendation for RescueTwin AI.

Use the district graph and facility metadata to rank hospitals by suitability.
Consider route safety, travel distance, flood impact, and hospital capacity.
Return the selected hospital, ranking rationale, and any hospitals excluded due to flood risk or capacity constraints.
Add tests that verify the selection logic under normal and degraded conditions.
Keep the output structured and easy for the frontend to consume.
```

**Acceptance Checks**

- Hospital selection is explainable.
- Risk and capacity influence the ranking.
- Endpoint response is structured.

**End-of-Day Deliverable**

- Hospital recommendation service.

---

## Day 9

**Goal**

Implement shelter recommendation logic.

**Tasks**

- Score shelters by distance, safety, and capacity.
- Filter shelters that are too risky or too far.
- Return ranked options and rationale.

**Codex Implementation Prompt**

```text
Add shelter recommendation to RescueTwin AI.

Rank shelters using distance from the incident, flood safety, and remaining capacity.
Return the top shelter recommendation plus alternative options, with clear reasoning for the ranking.
Add tests for safe shelter choice, unsafe shelter exclusion, and capacity exhaustion.
Make sure the API shape stays consistent with the hospital recommendation pattern.
```

**Acceptance Checks**

- Shelter recommendations are stable and explainable.
- Unsafe shelters are filtered correctly.
- Alternatives are returned when available.

**End-of-Day Deliverable**

- Shelter recommendation service.

---

## Day 10

**Goal**

Implement rescue team allocation.

**Tasks**

- Score rescue teams by distance, availability, specialization, and flood severity.
- Pick the best team for each incident.
- Return the reasoning and score breakdown.

**Codex Implementation Prompt**

```text
Implement the rescue team allocation engine for RescueTwin AI.

Use rule-based scoring to choose the best available rescue team for the incident.
Consider distance, team availability, specialization, and flood severity.
Return the winning team, score breakdown, and a short explanation of why the team was chosen.
Add tests covering available teams, unavailable teams, and specialization preference.
```

**Acceptance Checks**

- Allocation is deterministic and explainable.
- Unavailable teams are not selected.
- Specialization affects the result.

**End-of-Day Deliverable**

- Rescue team allocation service.

---

## Day 11

**Goal**

Implement damage assessment using a pretrained model or deterministic fallback.

**Tasks**

- Add sample damage images to the repository.
- Implement image selection and upload handling.
- Use a pretrained classifier if available, otherwise use a deterministic classifier with clear labels.
- Return damage level and confidence.

**Codex Implementation Prompt**

```text
Add the damage assessment module for RescueTwin AI.

Support selecting or uploading one of several sample incident images.
Use a pretrained image classifier if a reliable local option is available; otherwise implement a deterministic fallback classifier that still produces realistic labels and confidence values.
Do not train a custom computer vision model.
Add clear API responses for damage level, confidence, and rationale.
Include tests for sample images and unsupported input handling.
```

**Acceptance Checks**

- Sample images can be assessed.
- Confidence and label are returned.
- Fallback mode works without external APIs.

**End-of-Day Deliverable**

- Functional damage assessment module.

---

## Day 12

**Goal**

Create the decision engine that combines all recommendations.

**Tasks**

- Build a single backend endpoint for full incident decisioning.
- Combine flood prediction, routing, hospital, shelter, allocation, and damage outputs.
- Return a unified response payload.

**Codex Implementation Prompt**

```text
Implement the RescueTwin AI decision engine.

Create one backend endpoint that accepts an incident context and returns the full recommendation bundle:
flood severity prediction, affected zones, blocked roads, safe route, hospital recommendation, shelter recommendation, rescue team assignment, and damage assessment.
Make the endpoint the single source of truth for the frontend workflow.
Ensure the response is typed, explainable, and stable.
Add tests that confirm the full payload is internally consistent.
```

**Acceptance Checks**

- One endpoint returns all recommendations.
- The payload is internally consistent.
- Each recommendation references the same incident context.

**End-of-Day Deliverable**

- Full decision engine API.

---

## Day 13

**Goal**

Implement AI incident report generation.

**Tasks**

- Create a deterministic report template system.
- Use an LLM API only if available locally, otherwise fall back to templates.
- Include summary, affected zones, route, hospital, shelter, team, reasoning, and confidence.

**Codex Implementation Prompt**

```text
Add incident report generation to RescueTwin AI.

Generate a readable incident report from the decision engine output.
If a local LLM API is available, use it as an optional enhancement; otherwise create a deterministic report from templates so the application works without external AI services.
Include the situation summary, affected zones, selected rescue team, recommended hospital, recommended shelter, route summary, reasoning, and confidence level.
Add tests that verify a valid report is always produced.
```

**Acceptance Checks**

- Report generation always succeeds.
- The report includes all required sections.
- The fallback path works without external APIs.

**End-of-Day Deliverable**

- Incident report generator.

---

## Day 14

**Goal**

Connect the frontend scenario flow to the backend decision engine.

**Tasks**

- Add scenario controls.
- Add incident selection.
- Display the unified recommendation bundle.
- Show explanations and report output.

**Codex Implementation Prompt**

```text
Connect the RescueTwin AI frontend to the decision engine.

Build the full user flow:
scenario selection -> map update -> incident selection -> recommendation panel -> incident report.
Render flood prediction, route, hospital, shelter, team allocation, explanations, and report text in a clean dashboard layout.
Keep the application responsive and understandable.
Do not add analytics charts yet.
At the end, the user must be able to complete the main workflow end-to-end.
```

**Acceptance Checks**

- The full core flow works.
- The dashboard shows the unified recommendation output.
- Reports render correctly.

**End-of-Day Deliverable**

- End-to-end workflow through the UI.

---

## Day 15

**Goal**

Add analytics basics for flood severity and response quality.

**Tasks**

- Add Recharts visualizations.
- Show flood severity by zone.
- Show road impact and recommendation summaries.
- Add key metrics cards.

**Codex Implementation Prompt**

```text
Add analytics views to RescueTwin AI.

Use Recharts to display flood severity distribution, affected zone counts, blocked road counts, and recommendation summaries.
Add a dashboard section that helps a user understand the incident at a glance.
Keep the charts readable and visually restrained.
Do not introduce new backend behavior.
Make sure the dashboard still works end-to-end after the UI update.
```

**Acceptance Checks**

- Charts render correctly.
- Analytics reflect the active scenario.
- UI remains stable.

**End-of-Day Deliverable**

- Command center analytics dashboard.

---

## Day 16

**Goal**

Strengthen explainability across all modules.

**Tasks**

- Add score breakdowns.
- Add human-readable rationale for route, hospital, shelter, and team choices.
- Improve endpoint metadata.

**Codex Implementation Prompt**

```text
Improve explainability in RescueTwin AI.

Every recommendation should explain the main factors behind its score.
Add structured reasoning fields and concise human-readable summaries to the decision payload.
Ensure the frontend can display those reasons clearly.
Add tests that verify explanations are non-empty and aligned with the chosen outputs.
```

**Acceptance Checks**

- Every recommendation includes reasoning.
- Explanations match the selected output.
- Tests pass.

**End-of-Day Deliverable**

- Explainable decision output across the stack.

---

## Day 17

**Goal**

Add configuration and environment handling.

**Tasks**

- Introduce environment-based settings.
- Configure backend paths and model artifact locations.
- Centralize constants and shared config.

**Codex Implementation Prompt**

```text
Refactor RescueTwin AI configuration into explicit environment-based settings.

Add clean config handling for backend paths, dataset locations, model artifact paths, and optional report settings.
Keep defaults sensible for local development.
Avoid overengineering; this should support the current app, not a future platform.
Add tests for default config behavior.
```

**Acceptance Checks**

- Configuration is centralized.
- Defaults work locally.
- No feature behavior regresses.

**End-of-Day Deliverable**

- Clean local configuration system.

---

## Day 18

**Goal**

Add backend validation and error handling.

**Tasks**

- Validate request bodies.
- Return useful 4xx responses for bad inputs.
- Normalize API errors.

**Codex Implementation Prompt**

```text
Harden the RescueTwin AI backend API.

Add request validation and consistent error handling for invalid scenarios, missing incident data, invalid image inputs, and route failures.
Return clean, typed error payloads that the frontend can present gracefully.
Add tests for expected failure modes.
Do not change successful behavior.
```

**Acceptance Checks**

- Invalid input produces useful errors.
- API responses are consistent.
- Tests cover failure modes.

**End-of-Day Deliverable**

- Hardened backend API.

---

## Day 19

**Goal**

Improve frontend interaction quality and state management.

**Tasks**

- Tighten component boundaries.
- Improve loading and empty states.
- Keep scenario state and incident state synchronized.

**Codex Implementation Prompt**

```text
Refine the RescueTwin AI frontend interaction model.

Improve state management around scenario selection, incident selection, loading states, and recommendation rendering.
Add helpful empty states and transition states so the UI feels intentional rather than abrupt.
Keep the app simple and maintainable.
Do not add unrelated features.
```

**Acceptance Checks**

- State transitions are smooth.
- Empty/loading states are clear.
- No regressions in the main flow.

**End-of-Day Deliverable**

- More polished dashboard interaction model.

---

## Day 20

**Goal**

Add downloadable or copyable incident report output.

**Tasks**

- Add a report export action.
- Support copy-to-clipboard or file download.
- Keep the report format readable and consistent.

**Codex Implementation Prompt**

```text
Add report export capability to RescueTwin AI.

Allow the generated incident report to be copied or downloaded in a clean text-based format.
Make sure the export matches the current decision payload and report content.
Do not introduce PDF generation unless it can be done cleanly without adding unnecessary complexity.
Add tests or lightweight validation for the export formatting.
```

**Acceptance Checks**

- Report export works.
- Export matches on-screen content.
- UX remains simple.

**End-of-Day Deliverable**

- Exportable incident report.

---

## Day 21

**Goal**

Create a dedicated testing pass for backend services.

**Tasks**

- Expand simulation tests.
- Expand prediction tests.
- Expand routing and allocation tests.
- Confirm decision engine consistency.

**Codex Implementation Prompt**

```text
Run a focused backend hardening pass for RescueTwin AI.

Expand unit and integration coverage for simulation, prediction, routing, allocation, and decision engine behavior.
Pay special attention to deterministic outputs, explanation fields, and edge cases.
If any tests fail, fix the implementation rather than weakening the tests.
Keep the API behavior unchanged unless a clear bug is found.
```

**Acceptance Checks**

- Test coverage is broader and meaningful.
- No behavioral drift.
- Backend still runs.

**End-of-Day Deliverable**

- Hardened backend test suite.

---

## Day 22

**Stretch Day**

**Goal**

Refine the map and visual language.

**Tasks**

- Improve colors, labels, and layer styling.
- Make flooded zones and blocked roads easier to read.
- Tune the layout for interview demo quality.

**Codex Implementation Prompt**

```text
Polish the RescueTwin AI map and visual design.

Improve the district styling, overlay colors, labels, and legend so flooded zones, blocked roads, hospitals, shelters, and rescue teams are easy to understand at a glance.
Keep the visual language professional, restrained, and suitable for a technical portfolio.
Do not change the underlying logic.
Confirm the map still updates correctly with scenario changes.
```

**Acceptance Checks**

- Map readability improves materially.
- Visual distinctions are clear.
- Functional behavior is unchanged.

**End-of-Day Deliverable**

- Polished interactive map.

---

## Day 23

**Stretch Day**

**Goal**

Add a lightweight operations summary panel.

**Tasks**

- Surface the most important incident fields.
- Show status cards for flood severity, affected zones, blocked roads, and team assignment.
- Keep the panel compact and useful.

**Codex Implementation Prompt**

```text
Add a compact operations summary panel to RescueTwin AI.

Show the key incident indicators in a form that is fast to scan during a demo:
severity, affected zone count, blocked road count, selected hospital, selected shelter, and rescue team.
Keep the component reusable and backed by the existing decision payload.
Do not duplicate logic that already exists in the backend.
```

**Acceptance Checks**

- Summary cards are accurate and concise.
- Data stays in sync with the active incident.
- Layout remains balanced.

**End-of-Day Deliverable**

- Compact command summary panel.

---

## Day 24

**Stretch Day**

**Goal**

Add Dockerization for local reproducibility.

**Tasks**

- Write backend and frontend Dockerfiles.
- Add a minimal compose setup if helpful.
- Ensure local dev remains the primary path.

**Codex Implementation Prompt**

```text
Dockerize RescueTwin AI for final-week reproducibility.

Create Dockerfiles for the backend and frontend and keep them simple enough for local use.
If a compose file helps, include one, but do not turn the project into an infrastructure exercise.
The main goal is to make the application easy to run consistently for demos and handoff.
Verify the containerized path works without breaking the non-container local workflow.
```

**Acceptance Checks**

- Docker build succeeds.
- App runs in containers.
- Local non-Docker workflow still works.

**End-of-Day Deliverable**

- Containerized development option.

---

## Day 25

**Stretch Day**

**Goal**

Improve performance and code cleanliness.

**Tasks**

- Remove duplicated logic.
- Simplify expensive render paths.
- Tighten backend service boundaries.

**Codex Implementation Prompt**

```text
Refactor RescueTwin AI for clarity and performance.

Remove duplicated logic in the frontend and backend.
Simplify any expensive or noisy render paths.
Keep the architecture clean and explicit.
Do not change product behavior unless needed to fix a bug.
Record any refactor impact with tests.
```

**Acceptance Checks**

- Code is cleaner without losing behavior.
- No regressions.
- Tests still pass.

**End-of-Day Deliverable**

- Cleaner and more maintainable codebase.

---

## Day 26

**Stretch Day**

**Goal**

Add final data polish and sample asset quality improvements.

**Tasks**

- Review sample incident images.
- Check labels, names, and district metadata.
- Make sure the fictional district feels coherent.

**Codex Implementation Prompt**

```text
Polish the dataset and sample assets for RescueTwin AI.

Review the fictional district names, facility names, road labels, and sample incident images for coherence and realism.
Make the dataset feel intentional and consistent across the map, the dashboard, and the report output.
Do not widen the project scope.
Keep the application runnable and deterministic.
```

**Acceptance Checks**

- District assets feel coherent.
- Labels are consistent across surfaces.
- No broken references remain.

**End-of-Day Deliverable**

- Polished fictional district dataset.

---

## Day 27

**Stretch Day**

**Goal**

Add a final integration test pass for the user flow.

**Tasks**

- Verify the scenario selection to report generation path.
- Ensure map, recommendation panel, and report remain synchronized.
- Fix integration regressions.

**Codex Implementation Prompt**

```text
Run an end-to-end integration pass on RescueTwin AI.

Verify that the full workflow works cleanly from scenario selection to final incident report generation.
Check that the map, recommendation panel, analytics, and report output all stay synchronized on the same incident state.
Fix any integration regressions before moving on.
```

**Acceptance Checks**

- Full workflow succeeds end-to-end.
- State remains synchronized.
- Integration regressions are fixed.

**End-of-Day Deliverable**

- Verified end-to-end application flow.

---

## Day 28

**Stretch Day**

**Goal**

Prepare the release documentation.

**Tasks**

- Write setup instructions.
- Document architecture and module responsibilities.
- Explain how to run tests and demos.

**Codex Implementation Prompt**

```text
Write the implementation documentation for RescueTwin AI.

Document the architecture, major modules, local setup instructions, testing commands, and demo flow.
Make the docs precise enough that a new engineer can run the project and understand the system quickly.
Keep the tone practical and professional.
```

**Acceptance Checks**

- Setup is documented.
- Architecture is documented.
- Testing and demo steps are documented.

**End-of-Day Deliverable**

- Release-ready documentation draft.

---

## Day 29

**Stretch Day**

**Goal**

Perform release hardening and bug fixing.

**Tasks**

- Fix last-mile bugs.
- Ensure each module still runs independently.
- Resolve any UI polish issues.

**Codex Implementation Prompt**

```text
Run a release hardening pass on RescueTwin AI.

Fix bugs, awkward UI states, error-path issues, and any remaining inconsistencies in the backend or frontend.
Verify the main workflow remains stable and that every module still runs cleanly.
Do not add new functionality.
This is a stabilization day only.
```

**Acceptance Checks**

- Outstanding bugs are fixed.
- No new behavior is introduced.
- The app remains stable.

**End-of-Day Deliverable**

- Release-stabilized application.

---

## Day 30

**Stretch Day**

**Goal**

Finalize the project and create the shipping checklist.

**Tasks**

- Run the final test sweep.
- Verify the final UX flow.
- Create the final release checklist.
- Prepare the project for portfolio use.

**Codex Implementation Prompt**

```text
Finalize RescueTwin AI for release.

Run the last full verification pass on the application, including backend tests, frontend checks, and the main user workflow.
Make any final small fixes needed for reliability or clarity.
Produce the final release checklist and confirm the project is ready for demo and portfolio use.
Do not add new scope.
```

**Acceptance Checks**

- Full workflow passes.
- Final tests pass.
- Documentation is complete enough for handoff.

**End-of-Day Deliverable**

- Release-ready RescueTwin AI MVP.

## 10. Weekly Milestones

### Week 1

- Backend skeleton is in place.
- Fictional district data exists.
- Flood simulation works.
- Prediction dataset generation is ready.

### Week 2

- XGBoost prediction is live.
- Frontend map shell exists.
- Leaflet map renders district layers.
- Route optimization works.
- Hospital, shelter, and team recommendation services exist.

### Week 3

- Damage assessment works.
- Decision engine returns one full payload.
- Report generation works.
- Frontend is wired to the complete workflow.
- Explainability is visible across the product.

### Week 4

- Analytics and UX polish are complete.
- Docker is available.
- Tests and docs are complete.
- Final release hardening is done.

## 11. Acceptance Criteria

The project is complete when all of the following are true:

- The user can open the dashboard and see the fictional district.
- The user can select a rainfall scenario.
- Flood simulation updates zones and roads.
- The user can inspect blocked roads and affected areas.
- The user can select an incident.
- The system recommends a safe route, hospital, shelter, and rescue team.
- Each recommendation is explainable.
- The report generator produces a usable incident report.
- The backend and frontend both run locally.
- The codebase is modular and maintainable.
- The application is good enough to discuss in an interview as a real engineering project.

## 12. End-of-Day Deliverables

At the end of every day, the following must be true:

- The application still runs.
- The new feature is visible or callable.
- The relevant tests pass.
- No unrelated work is partially broken.
- The day’s change can be committed independently.

## 13. Final Release Checklist

- Backend runs locally.
- Frontend runs locally.
- Scenario selection works.
- Flood map updates correctly.
- Route optimization avoids blocked roads.
- Hospital recommendation is explainable.
- Shelter recommendation is explainable.
- Rescue team allocation is explainable.
- Damage assessment works with sample images.
- Decision engine returns one complete payload.
- Incident report generation works without external APIs.
- Analytics dashboard renders correctly.
- Tests pass.
- Docker build works.
- Documentation is accurate.
- README points to the right startup steps.

## 14. Post-Launch Backlog

These items are intentionally out of scope for the 30-day build, but they are sensible future extensions:

- Multi-district support
- Historical incident timeline storage
- Better map drawing tools
- More advanced image models
- Real-time weather integration
- PDF report export
- Multi-user collaboration
- Scenario replay mode
- Accessibility polish pass
- Broader test coverage and CI automation

## 15. Definition of Done

RescueTwin AI is done when it behaves like a polished decision-support system rather than a demo stub.

That means:

- The system has a clear fictional district and a coherent flood-response workflow.
- The backend produces deterministic, explainable recommendations.
- The frontend presents the workflow in a clean, usable dashboard.
- Every major feature is implemented with real code and real data structures.
- The app is stable enough to show repeatedly in interviews.
- The project can be continued by another Codex session without losing context.

## 16. Recommended Daily Usage Pattern

For the best results, use this document one day at a time.

1. Open the current day section.
2. Paste the Codex implementation prompt into a fresh Codex session.
3. Let Codex implement only that day’s scope.
4. Run the acceptance checks.
5. Commit the result.
6. Move to the next day only after the current day is runnable.

This keeps the project focused, reviewable, and genuinely finishable in 30 days.
