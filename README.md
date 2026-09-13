# RescueTwin AI

RescueTwin AI is a deterministic, fictional flood-response decision-support system. It combines flood simulation, baseline ML prediction, safe-route calculation, explainable operational recommendations, damage assessment, and incident-report generation in one workflow.

## What it does

- Models a fictional district and its operational assets.
- Simulates **moderate**, **severe**, and **extreme** rainfall scenarios deterministically.
- Predicts flood severity from rainfall, elevation, drainage, and previous water level using a persisted XGBoost baseline.
- Finds safe routes while excluding roads blocked by the selected flood scenario.
- Recommends a suitable hospital and evacuation shelter using safety, capacity, and route factors.
- Ranks an available rescue team using distance, specialty, and personnel availability.
- Optionally assesses an uploaded incident image.
- Generates a readable incident report from the same decision bundle.
- Provides a React/Vite operational dashboard backed by FastAPI.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Leaflet, Recharts |
| Backend | Python, FastAPI, Pydantic |
| ML | XGBoost, scikit-learn, NumPy, joblib |
| Routing | Deterministic weighted graph + Dijkstra shortest path |
| Testing | pytest + FastAPI TestClient |
| Deployment | Docker + Docker Compose |

## Repository structure

```text
.
├── ai/                 # model-training entry points
├── backend/
│   ├── app/
│   │   ├── api/       # HTTP routes
│   │   ├── models/    # typed API/domain contracts
│   │   └── services/  # simulation, prediction and decision logic
│   └── artifacts/     # persisted model artifact
├── data/               # deterministic synthetic training dataset generator/data
├── docs/               # architecture and demo documentation
├── frontend/
│   └── src/            # React dashboard
├── reports/            # generated/report-related project assets
├── routing/             # routing-related project assets
├── simulation/          # simulation-related project assets
└── tests/               # backend and integration regression tests
```

## Prerequisites

- Python 3.11+ recommended.
- Node.js and npm.
- Git.
- Docker Desktop is optional for the containerized demo.

Create/use a Python virtual environment if desired:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Local backend setup

From the repository root:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The API is then available at:

- `http://127.0.0.1:8000/docs` — interactive OpenAPI documentation
- `http://127.0.0.1:8000/api/v1/health` — health check
- `http://127.0.0.1:8000/api/v1/district` — fictional district metadata

## Model artifact

The prediction service expects the persisted XGBoost artifact at `backend/artifacts/flood_severity_xgb.joblib`.

If it needs to be regenerated, from the repository root run:

```powershell
python ai/train_flood_model.py
```

The training pipeline uses a seeded split and model configuration so the baseline remains reproducible.

To regenerate the deterministic synthetic dataset:

```powershell
python data/generate_flood_dataset.py --samples 1200
```

## Local frontend setup

Keep the backend running in one terminal. In another:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://127.0.0.1:5173`. The Vite development configuration proxies `/api` requests to the local FastAPI service.

For a production build:

```powershell
npm.cmd run build
```

If PowerShell blocks `npm.ps1`, use `npm.cmd` as shown above.

## API surface

The current backend exposes these operational paths under `/api/v1`:

- `GET /health`
- `GET /district`
- `GET /simulate`
- `GET /route`
- `GET /recommendations/hospital`
- `GET /recommendations/team`
- `POST /predict`
- `POST /assess-damage`
- `POST /decision-engine`
- `POST /generate-report`

The decision-engine endpoint accepts the selected incident zone, scenario and environmental inputs, then returns one bundle containing prediction, simulation, damage assessment when supplied, recommendations, and safe routes.

## Testing

From the repository root:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest tests -q
```

The suite covers unit behavior, API contracts, regression behavior, recommendation/routing logic, report generation, and the Day 27 scenario-to-report integration flow.

A successful run should report all tests passing. Warnings from third-party dependencies do not represent test failures; investigate them separately if they become errors.

## End-to-end demo flow

1. Start the FastAPI backend.
2. Start the Vite frontend.
3. Open the dashboard.
4. Select a rainfall scenario: **Moderate**, **Severe**, or **Extreme**.
5. Inspect the resulting flood impacts and blocked roads on the map.
6. Select a flood zone as the incident.
7. Run the decision analysis.
8. Review predicted severity and explanation.
9. Review the dispatched rescue team.
10. Review the recommended hospital and shelter and their route/capacity information.
11. Optionally upload an incident image for damage assessment.
12. Generate the incident report.
13. Copy or download the report when those controls are available.

The selected scenario is carried through the decision-engine workflow so simulation, recommendations, routing constraints, dashboard state, and generated report describe the same incident state.

## Docker demo

The repository includes Docker Compose configuration for the backend and frontend:

```powershell
docker compose up --build
```

Then use the published local ports:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

Stop the stack with:

```powershell
docker compose down
```

## Troubleshooting

### PowerShell says npm scripts are disabled

Use:

```powershell
npm.cmd install
npm.cmd run dev
npm.cmd run build
```

### pytest cannot import `app`

From the repository root set:

```powershell
$env:PYTHONPATH = "backend"
```

Then rerun pytest.

### Prediction artifact is missing

Run:

```powershell
python ai/train_flood_model.py
```

### Frontend starts but API requests fail

Confirm the backend is running on port 8000 and that the frontend is being served through Vite with the expected `/api` proxy.

## Project principles

- **Deterministic:** fictional district data and simulation logic are reproducible.
- **Backend authoritative:** operational decisions originate from the backend decision engine.
- **Explainable:** recommendation responses expose rationale and contributing factors.
- **Narrow scope:** the project is a decision-support prototype, not a live emergency-management system.
