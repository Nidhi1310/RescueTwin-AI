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
| 🚑 Rescue-team allocation | Scores availability, distance, specialty, personnel, and severity |
| 🏥 Hospital recommendation | Ranks operationally suitable hospitals using route/capacity context |
| 🛟 Shelter recommendation | Identifies suitable evacuation shelter options |
| 📷 Damage assessment | Optional incident-image assessment |
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
        + Synthetic     + joblib        + Dijkstra
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
- joblib

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
│   │   └── services/
│   │       ├── damage_assessment.py
│   │       ├── decision_engine.py
│   │       ├── district_service.py
│   │       ├── flood_prediction.py
│   │       ├── flood_simulation.py
│   │       ├── hospital_recommendation.py
│   │       ├── report_generation.py
│   │       ├── routing_service.py
│   │       ├── synthetic_data.py
│   │       └── team_allocation.py
│   ├── artifacts/               # Persisted ML artifacts
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   └── generate_flood_dataset.py
├── docs/                        # Documentation/release material
├── frontend/
│   ├── src/
│   │   ├── components/          # Dashboard components
│   │   ├── services/            # API integration
│   │   └── types/               # TypeScript contracts
│   └── package.json
├── reports/                     # Report assets
├── routing/                     # Routing assets
├── simulation/                  # Simulation assets
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

All operational endpoints are under:

```text
/api/v1
```

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/district` | Fictional district metadata |
| GET | `/simulate` | Run a rainfall scenario |
| GET | `/route` | Calculate a scenario-aware route |
| GET | `/recommendations/hospital` | Recommend a hospital |
| GET | `/recommendations/team` | Recommend a rescue team |
| POST | `/predict` | Predict flood severity |
| POST | `/assess-damage` | Assess uploaded incident image |
| POST | `/decision-engine` | Generate the complete decision bundle |
| POST | `/generate-report` | Generate an incident report |

FastAPI provides interactive documentation at:

```text
http://127.0.0.1:8000/docs
```

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

## Local Development

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
python -m pip install -r requirements.txt
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

### Generate synthetic training data

From the repository root:

```powershell
python data/generate_flood_dataset.py --samples 1200
```

### Train the XGBoost baseline

```powershell
python ai/train_flood_model.py
```

The training command reports:

- artifact path,
- training/test row counts,
- MAE,
- R² score.

Expected artifact:

```text
backend/artifacts/flood_severity_xgb.joblib
```

---

## Testing

Run the test suite from the repository root:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest tests -q
```

The suite covers service behavior, API contracts, simulation, routing, recommendations, team allocation, prediction, damage assessment, reporting, decision-engine integration, and regression behavior.

---

## Docker

Start the complete local stack:

```powershell
docker compose up --build
```

Services:

```text
Backend   → http://127.0.0.1:8000
Frontend  → http://127.0.0.1:5173
```

Stop:

```powershell
docker compose down
```

---

## Production Deployment

The repository includes `render.yaml` defining a two-service Render deployment.

### Backend

```text
Service: rescuetwin-api
Runtime: Docker
Health check: /api/v1/health
```

The backend reads:

```text
RESCUETWIN_CORS_ORIGINS
```

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

### Backend CORS

Local defaults:

```text
http://127.0.0.1:5173,http://localhost:5173
```

Production variable:

```text
RESCUETWIN_CORS_ORIGINS
```

### Frontend API URL

```text
VITE_API_BASE_URL
```

Render can populate this from the deployed backend service.

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
python ai/train_flood_model.py
```

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
- The XGBoost model is trained on synthetic data.
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
- ✅ Optional image damage assessment
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
