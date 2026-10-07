# RescueTwin AI

> **Autonomous Disaster Response Digital Twin** — an explainable flood-response decision-support platform combining deterministic flood simulation, machine-learning prediction, safe-route planning, resource recommendation, damage assessment, and incident reporting in one operational command center.

RescueTwin AI is a **fictional, reproducible disaster-response prototype** built around a simulated district called **Sundarpur, Bihar, India**. A selected rainfall scenario changes the simulated flood state; the system identifies affected zones and blocked roads, predicts severity, calculates safer routes, recommends response resources, and generates an incident report from the same decision state.

> **Important:** This is a demonstration/decision-support prototype, not a live emergency-management system. Its simulated outputs must not be used for real-world emergency decisions.

---

## Table of Contents

- [Overview](#overview)
- [Key Capabilities](#key-capabilities)
- [End-to-End Workflow](#end-to-end-workflow)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Core Modules](#core-modules)
- [API Reference](#api-reference)
- [Frontend Command Center](#frontend-command-center)
- [Local Development](#local-development)
- [Model Training](#model-training)
- [Testing](#testing)
- [Docker](#docker)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Design Principles](#design-principles)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Project Status](#project-status)

---

## Overview

Flood response requires several decisions to be made together: understanding the affected area, estimating severity, avoiding blocked roads, allocating rescue resources, identifying suitable facilities, and documenting the incident.

RescueTwin AI demonstrates how these tasks can be connected through a single backend-authoritative workflow:

**one incident state → one decision workflow → one operational view.**

The project combines:

- a deterministic fictional district model,
- scenario-based flood simulation,
- an XGBoost flood-severity baseline,
- graph-based safe routing,
- explainable resource recommendations,
- optional image-based damage assessment,
- a unified decision engine,
- incident-report generation,
- and a React operational dashboard.

---

## Key Capabilities

| Capability | Implementation |
|---|---|
| 🌧️ Flood simulation | Deterministic Moderate, Severe, and Extreme rainfall scenarios |
| 🤖 Flood prediction | Persisted XGBoost baseline using environmental inputs |
| 🗺️ Tactical map | Zones, flood impact, facilities, rescue teams, blocked roads, and routes |
| 🚧 Blocked roads | Scenario simulation produces routing constraints |
| 🧭 Safe routing | Weighted graph + Dijkstra shortest-path search |
| 🚑 Rescue-team allocation | Hard specialty constraint, committed-team reservations, severity-weighted scoring, boat/air fallback |
| 🏥 Hospital recommendation | Ranks operationally suitable hospitals using route/capacity context |
| 🛟 Shelter recommendation | Identifies suitable evacuation shelter options |
| 📷 Image assessment | Validated upload + indicative floodwater-colour heuristic (not a trained model) |
| 🧠 Decision engine | Combines simulation, prediction, assessment, routing, and recommendations |
| 📄 Incident reporting | Converts the decision bundle into a readable report |
| 📊 Analytics | Dashboard view of incident and scenario information |
| 🧪 Testing | Unit, API, regression, and integration coverage |
| 🐳 Deployment | Docker/Compose and Render configuration |

---

## End-to-End Workflow

```text
                 User selects scenario
                         │
                         ▼
                ┌─────────────────┐
                │ Flood Simulation│
                └────────┬────────┘
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
        Affected      Blocked     Scenario
          zones        roads       state
             │           │           │
             └───────────┼───────────┘
                         ▼
                  Select incident
                         │
                         ▼
                ┌─────────────────┐
                │ Decision Engine │
                └────────┬────────┘
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
  ML prediction    Damage assessment   Resource decisions
   (XGBoost)          (optional)       ├─ Rescue team
                                       ├─ Hospital
                                       ├─ Shelter
                                       └─ Safe routes
                         │
                         ▼
                 Unified decision bundle
                    │             │
                    ▼             ▼
             Command Center   Incident Report
```

The **backend is authoritative**: the frontend visualizes backend results and handles user interaction rather than independently recreating operational decisions.

---

## Architecture

```text
┌───────────────────────────────────────────────────────────┐
│                  React Command Center                     │
│  Scenario │ Tactical Map │ Decision Engine │ Analytics   │
│  Facilities │ Rescue Teams │ Routes │ Incident Controls  │
└──────────────────────────┬────────────────────────────────┘
                           │ HTTP / JSON / multipart
                           ▼
┌───────────────────────────────────────────────────────────┐
│                    FastAPI Backend                        │
│                       /api/v1                             │
├───────────────────────────────────────────────────────────┤
│ District │ Simulation │ Prediction │ Routing             │
│ Team Allocation │ Hospital/Shelter │ Decision Engine     │
│ Damage Assessment │ Incident Reporting                  │
└──────────────┬──────────────┬──────────────┬─────────────┘
               │              │              │
               ▼              ▼              ▼
        District Model   XGBoost Model   Routing Graph
        + Synthetic     + JSON model    + Dijkstra
          Dataset
```

### Architectural decisions

- **Backend authoritative:** operational decisions originate in backend services.
- **Deterministic simulation:** the fictional environment is reproducible.
- **Typed contracts:** Pydantic models define API/domain contracts.
- **Modular services:** major capabilities are separated into focused services.
- **Explainable decisions:** recommendation responses expose supporting factors.
- **Frontend/backend separation:** the UI consumes APIs instead of owning domain logic.
- **Consistent incident state:** simulation, routing, recommendations, dashboard, and reporting use the selected scenario/incident.

---

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Leaflet
- React Leaflet
- Recharts

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- python-multipart

### Machine Learning

- XGBoost
- scikit-learn
- NumPy
- Pillow (image validation)

### Algorithms

- Deterministic flood simulation
- Weighted graph modeling
- Dijkstra shortest-path algorithm
- Rule-based rescue-team scoring
- Operational recommendation scoring

### Engineering

- pytest
- HTTPX / FastAPI TestClient
- Docker
- Docker Compose
- Render

---

## Repository Structure

```text
RescueTwin-AI/
│
├── .github/workflows/           # CI/deployment workflows
├── ai/
│   └── train_flood_model.py     # XGBoost training entry point
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py        # FastAPI routes
│   │   ├── models/              # Pydantic/domain models
│   │   ├── security.py          # API key, rate limit, upload cap, audit log
│   │   └── services/
│   │       ├── damage_assessment.py
│   │       ├── decision_engine.py
│   │       ├── dispatch_ledger.py   # committed-team reservations
│   │       ├── district_service.py
│   │       ├── flood_prediction.py
│   │       ├── flood_simulation.py
│   │       ├── hospital_recommendation.py
│   │       ├── report_generation.py
│   │       ├── report_integrity.py  # HMAC signing of decision bundles
│   │       ├── routing_service.py
│   │       ├── synthetic_data.py
│   │       └── team_allocation.py
│   ├── artifacts/               # XGBoost-native JSON model + metadata (checksummed)
│   ├── Dockerfile
│   ├── requirements.txt         # pinned runtime deps
│   └── requirements-dev.txt
│
├── data/
│   └── generate_flood_dataset.py
├── docs/                        # Documentation/release material
├── frontend/
│   ├── src/
│   │   ├── components/          # Dashboard components
│   │   ├── api.ts               # API client
│   │   └── types.ts             # TypeScript contracts
│   └── package.json
├── tests/                       # Automated tests
├── docker-compose.yml
├── render.yaml
└── README.md
```

---

## Core Modules

### 1. District and simulation

The district service provides the fictional operational environment: flood zones, facilities, rescue teams, coordinates, capacities, and other domain data.

The flood simulation supports:

- **Moderate**
- **Severe**
- **Extreme**

Simulation is deterministic, making demonstrations and regression tests reproducible.

### 2. Flood prediction

The prediction service uses a persisted XGBoost baseline.

Primary environmental inputs include:

- rainfall (mm),
- elevation (m),
- drainage score,
- previous water level (m).

The model is trained on synthetic data and should be understood as a **baseline demonstration model**, not a production flood-forecasting system.

### 3. Routing

The routing service represents the operational network as a weighted graph.

When a scenario produces blocked roads:

1. blocked road IDs are collected,
2. those edges are excluded from routing,
3. Dijkstra searches the remaining graph,
4. the API returns route status, distance, and path coordinates.

### 4. Rescue-team allocation

The allocation engine ranks candidates using operational factors such as:

- availability,
- incident distance,
- specialty,
- personnel,
- flood severity.

The result contains the selected team and allocation information.

### 5. Hospital and shelter recommendation

Facility recommendations consider operational context including:

- route availability,
- capacity,
- current occupancy,
- incident/safety context.

This demonstrates decision-support ranking rather than simply selecting the nearest facility.

### 6. Decision engine

The decision engine is the central orchestration layer.

It receives the selected incident and environmental inputs and combines:

- flood prediction,
- scenario simulation,
- optional damage assessment,
- rescue-team allocation,
- facility recommendations,
- safe-route calculations.

The result is a unified decision bundle consumed by the dashboard and report generator.

### 7. Damage assessment

The backend accepts an optional incident image through multipart upload and returns a structured damage-assessment result.

### 8. Incident reporting

The report service converts the decision-engine response into a readable incident report, keeping reporting consistent with the operational decision state.

---

## API Reference

All operational endpoints are under `/api/v1`. When `RESCUETWIN_API_KEY` is set, every endpoint except `/health` requires an `X-API-Key` header.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check (always public) |
| GET | `/district` | Fictional district metadata |
| GET | `/scenarios` | Preset inputs used when only a scenario is selected |
| GET | `/simulate` | Run a rainfall scenario |
| GET | `/route` | Calculate a scenario-aware route |
| GET | `/recommendations/hospital` | Recommend a hospital (`required_service` is a hard filter) |
| GET | `/recommendations/team` | Recommend a rescue team (`required_specialty` is a hard filter) |
| POST | `/predict` | Predict flood severity (with input-support-aware confidence) |
| POST | `/assess-damage` | Validate and assess an uploaded image (max 8 MB) |
| POST | `/decision-engine` | Full decision bundle. `commit=true` reserves the team |
| POST | `/generate-report` | Report from a **server-signed** decision bundle only |
| GET | `/dispatch` | Teams currently committed to incidents |
| DELETE | `/dispatch/{zone_id}` | Release the teams committed to an incident |

### Decision-engine input rules

The server is authoritative:

- `elevation_m` / `drainage_score` come from district data. You may echo them; contradicting the zone returns `422`.
- Send a `scenario` and/or `rainfall_mm`. A scenario alone uses that scenario's preset rainfall and water level (flagged in `warnings` as *not live sensor data*). A rainfall value and scenario in different bands return `422`.
- `required_specialty` / `required_service` must match known values (`422` lists the valid options).
- By default the call is a **what-if preview**; it reserves nothing. `commit=true` atomically reserves the selected team until `DELETE /dispatch/{zone_id}`.

### What the bundle adds beyond recommendations

`priority` (from the ML severity), `incident_isolated`, per-resource `fallback` options (boat/air, informational straight-line only) when no road-accessible resource exists, `warnings` (rejected image, prediction/simulation disagreement, out-of-range model inputs, shelter capacity gap), and a `signature`.

FastAPI interactive docs: `http://127.0.0.1:8000/docs`.

---

## Frontend Command Center

The frontend presents RescueTwin as a tactical flood-response command center.

### Main UI

- RescueTwin system header
- District overview
- Flood-zone KPI
- Resident KPI
- Care-facility KPI
- Rescue-team KPI
- Rainfall scenario selector
- Interactive operational map
- Decision Engine
- Facilities panel
- Rescue Teams panel
- Incident analytics
- Operational map legend and controls

### Tactical map

The map displays:

- operational zones,
- flood-affected zones,
- hospitals,
- shelters,
- rescue teams,
- blocked roads,
- safe routes,
- selected incidents,
- zoom/layer/location controls.

The current map uses **keyless OpenStreetMap tiles**, so the frontend does not require a CARTO API key.

---

## Windows setup (first time only)

1. Install **Python 3.12** from python.org and tick **"Add python.exe to PATH"** on the first screen.
   If you see *"Python was not found; run without arguments to install from the Microsoft Store"*, open **Settings → Apps → Advanced app settings → App execution aliases** and turn off the two `python.exe` / `python3.exe` entries, then reopen PowerShell.
2. Install **Node.js 22 LTS** from nodejs.org (needs 20.19+ or 22+).
3. Close and reopen PowerShell, then check `python --version` and `node --version`.
4. Run `start.bat`. The model is trained automatically on first run if the artifact is missing.

## Local Development

**Quick start:** run `start.bat` (Windows) or `./start.sh` (Linux/macOS). It stops any stale servers, installs dependencies, starts both services, and opens the app.


### Prerequisites

- Python 3.11+
- Node.js and npm
- Git
- Docker Desktop (optional)

### 1. Clone

```powershell
git clone https://github.com/Nidhi1310/RescueTwin-AI.git
cd RescueTwin-AI
```

### 2. Backend

```powershell
cd backend
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Health:

```text
http://127.0.0.1:8000/api/v1/health
```

Docs:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend

Open another terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend:

```text
http://127.0.0.1:5173
```

Build for production:

```powershell
npm.cmd run build
```

If PowerShell blocks `npm.ps1`, use `npm.cmd`.

---

## Model Training

The model is stored as **XGBoost-native JSON** plus a metadata file with a SHA-256 checksum (no pickle). The service refuses to load an artifact whose checksum does not match.

```powershell
# from the repository root
python data/generate_flood_dataset.py --samples 1200
python ai/train_flood_model.py
```

Paths default to the repository layout and can be overridden with `RESCUETWIN_DATASET_PATH` and `RESCUETWIN_ARTIFACT_PATH` (the Docker image uses these).

Outputs: `backend/artifacts/flood_severity_xgb.json` and `flood_severity_xgb.meta.json`.

> **Read the metrics honestly.** The training label is a hand-written formula of the four inputs, so the near-perfect R² only shows the model can reproduce that formula. It says nothing about real-world forecasting skill. The API therefore reports `expected_error_points`, downgrades `confidence` when inputs fall outside (or near the edge of) the training range, and labels the output `synthetic_training_data`.

---

## Testing

```powershell
python -m pip install -r backend/requirements-dev.txt
$env:PYTHONPATH = "backend"
python -m pytest tests -q
```

`tests/test_review_fixes.py` pins every fix from the project review (routing thread-safety, fallbacks, hard constraints, reservations, report forgery, input consistency, auth, rate limiting, artifact integrity). The frontend is type-checked by `npm run build`.

---

## Docker

```powershell
docker compose up --build
```

```text
Backend   → http://127.0.0.1:8000   (loopback only)
Frontend  → http://127.0.0.1:5173
```

Both images run as non-root users, the backend has a health check, and the frontend waits for it. Optional env vars: `RESCUETWIN_API_KEY`, `RESCUETWIN_SIGNING_KEY`.

---

## Production Deployment

The repository includes `render.yaml` defining a two-service Render deployment.

### Backend

```text
Service: rescuetwin-api
Runtime: Docker
Health check: /api/v1/health
```

Set these on the backend (see Configuration): `RESCUETWIN_CORS_ORIGINS` (your frontend URL, **never `*`**), `RESCUETWIN_SIGNING_KEY` (generated by the blueprint), and optionally `RESCUETWIN_API_KEY`.

> The Render free plan spins the API down when idle, so the first request can take 30–60 s. Use a paid plan or an uptime pinger for anything beyond a demo.

### Frontend

```text
Service: rescuetwin-frontend
Runtime: Static
Build: npm ci && npm run build
Publish directory: dist
```

The frontend receives the deployed backend URL through:

```text
VITE_API_BASE_URL
```

### Deployment architecture

```text
                 GitHub main
                     │
                     ▼
               Render Blueprint
                 │          │
                 ▼          ▼
          FastAPI API    React/Vite UI
             Docker        Static
                 │          │
                 └──── API ──┘
```

For production, keep the deployment branch and environment variables aligned with the current Render configuration.

---

## Configuration

| Variable | Where | Purpose |
|---|---|---|
| `RESCUETWIN_CORS_ORIGINS` | backend | Comma-separated allowed origins (default: local Vite). A warning is logged if `*` is used |
| `RESCUETWIN_API_KEY` | backend | If set, requires `X-API-Key` on all endpoints except `/health` |
| `RESCUETWIN_SIGNING_KEY` | backend | HMAC key for decision bundles. If unset, a random per-process key is used (bundles stop verifying after a restart) |
| `RESCUETWIN_RATE_LIMIT_PER_MIN` | backend | Per-client limit (default 300; `0` disables) |
| `RESCUETWIN_TRUST_PROXY` | backend | Set to `1` only behind a trusted proxy that sets `X-Forwarded-For` |
| `RESCUETWIN_DATASET_PATH` / `RESCUETWIN_ARTIFACT_PATH` | backend/training | Override data and model locations |
| `VITE_API_BASE_URL` | frontend build | Backend URL (empty = same-origin `/api`) |
| `VITE_API_KEY` | frontend build | Optional. A static SPA cannot keep a secret, so this only deters casual use; use a real authenticating gateway for non-demo deployments |

---

## Troubleshooting

### PowerShell blocks npm

Use:

```powershell
npm.cmd install
npm.cmd run dev
npm.cmd run build
```

### pytest cannot import `app`

From the repository root:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest tests -q
```

### Missing prediction artifact

```powershell
python ai/train_flood_model.py   # run from the repository root
```

If loading fails with an *integrity* error, the artifact and its `.meta.json` are out of sync; retrain.

### Frontend loads but API calls fail

Check:

1. FastAPI is running on port 8000.
2. The frontend is using the expected Vite configuration.
3. `VITE_API_BASE_URL` is correct in production.
4. Backend CORS permits the frontend origin.

### Map does not load

The current map uses OpenStreetMap tiles and does not require a CARTO API key. Rebuild the frontend and check browser network errors if tiles are unavailable.

---

## Design Principles

### Deterministic

Fictional district data and simulation behavior are reproducible.

### Backend authoritative

Operational decisions are generated by backend services.

### Explainable

Recommendations expose relevant factors rather than presenting unexplained outputs.

### Modular

Simulation, prediction, routing, recommendations, assessment, and reporting have separate service responsibilities.

### Consistent

The same incident/scenario state flows from simulation through decision-making and reporting.

### Engineering-focused

The project demonstrates practical patterns including REST APIs, typed contracts, ML inference, graph algorithms, geospatial visualization, automated testing, containerization, and cloud deployment.

---

## Limitations

RescueTwin AI intentionally operates in a controlled demonstration environment.

- The district is fictional.
- Flood simulation is deterministic rather than a real hydrological model.
- The XGBoost model is trained on synthetic data whose label is a formula of its own inputs; its metrics are not evidence of forecasting skill.
- Rainfall and water level are scenario presets unless supplied by the caller; there is no live data feed.
- Image assessment is a colour heuristic (water-coloured pixel share), not a trained classifier or structural assessment.
- Fallback (boat/air) options use straight-line distance and are informational, not routed.
- Team reservations are in-memory and per-process (single worker); hospital/shelter occupancy is static.
- Capacity is surfaced as a warning, not modelled as demand.
- Geographic and operational assets are simulated.
- Recommendations are prototypes, not certified emergency procedures.
- The map is visualization, not authoritative emergency geography.
- Damage assessment is a prototype and not a certified structural assessment.

These limitations are intentional: the project focuses on demonstrating the **complete software and decision-support architecture** without presenting simulated intelligence as real emergency information.

---

## Future Enhancements

Potential extensions include:

- real-time weather/rainfall feeds,
- satellite and drone imagery,
- richer flood-depth and terrain modeling,
- live traffic and road-closure data,
- rescue-team telemetry,
- probabilistic uncertainty estimates,
- historical incident analytics,
- role-based access control,
- decision audit logs,
- model monitoring and retraining,
- stronger geospatial routing,
- multi-district digital-twin support.

---

## Project Status

**Functional prototype / portfolio-ready demonstration**

### Implemented

- ✅ Deterministic flood simulation
- ✅ Moderate / Severe / Extreme scenarios
- ✅ XGBoost flood-severity prediction
- ✅ Interactive tactical flood map
- ✅ Keyless OpenStreetMap map tiles
- ✅ Flood-affected zone visualization
- ✅ Blocked-road detection
- ✅ Dijkstra-based safe routing
- ✅ Hospital recommendation
- ✅ Shelter recommendation
- ✅ Rescue-team allocation
- ✅ Validated image upload with indicative heuristic assessment
- ✅ Unified decision engine
- ✅ Incident report generation
- ✅ Incident analytics
- ✅ Automated testing
- ✅ Docker support
- ✅ Render deployment configuration
- ✅ Production-oriented command-center UI

---

## Project Objective

RescueTwin AI demonstrates how **digital-twin concepts, machine learning, graph algorithms, explainable decision logic, geospatial visualization, and modern web engineering** can be combined into one coherent disaster-response workflow.

The goal is not to claim perfect prediction. The goal is to demonstrate a complete engineering pipeline:

```text
Model the environment
        ↓
Simulate the incident
        ↓
Predict severity
        ↓
Understand operational impact
        ↓
Calculate feasible routes
        ↓
Allocate response resources
        ↓
Recommend facilities
        ↓
Explain the decision
        ↓
Generate the incident report
```

This end-to-end workflow is the core of **RescueTwin AI**.

---

## Author

**Nidhi Kumari**  
B.Tech — Electronics and Communication Engineering

RescueTwin AI demonstrates applied AI/ML, backend engineering, frontend engineering, algorithms, geospatial visualization, testing, and deployment in a single portfolio project.
