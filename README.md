# RescueTwin AI

RescueTwin AI is an interactive flood-response command center for a fictional district. It combines deterministic flood simulation, an XGBoost severity predictor, safe-route optimization, facility recommendation, rescue-team allocation, damage assessment, incident reporting, analytics, and transparent recommendation reasoning.

> **Scope:** this is a portfolio/demo decision-support system for one fictional district and flooding. It is not a real emergency-response platform.

## Product flow

`Rainfall scenario → flood simulation → incident selection → safe routes → hospital + shelter + rescue team → reasoning → incident report → analytics`

## Architecture

```text
React + TypeScript + Vite + Tailwind + Leaflet + Recharts
                         │
                         ▼
                    FastAPI API
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Simulation       Prediction      Decision
          │              │           orchestration
          ▼              ▼              │
       Routing     XGBoost model       ├─ Hospital
                                      ├─ Shelter
                                      ├─ Rescue team
                                      ├─ Damage assessment
                                      └─ Incident report
```

The backend is the source of truth for decision logic; the frontend renders the returned typed payload.

## Local setup

### Backend

```powershell
cd backend
python -m pip install -r requirements.txt
$env:PYTHONPATH = "."
python -m uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/docs`.

### Frontend

In a second terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the Vite URL shown in the terminal (the checked-in configuration uses port 5173).

## Tests

From the repository root:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest tests -v
```

The suite covers simulation, prediction, routing, hospital/shelter/team recommendations, decision orchestration, reporting, explainability, API validation, and full-flow consistency.

## Training the model

If the persisted artifact needs to be regenerated:

```powershell
python data/generate_flood_dataset.py --samples 1200
python ai/train_flood_model.py
```

The model artifact is stored under `backend/artifacts/`.

## Configuration

Optional environment variables:

- `RESCUETWIN_DATASET_PATH`
- `RESCUETWIN_MODEL_ARTIFACT_PATH`
- `RESCUETWIN_REPORT_TITLE`
- `RESCUETWIN_API_PREFIX`

See `backend/.env.example` for defaults.

## Docker

From the repository root:

```powershell
docker compose up --build
```

The frontend is exposed on port `5175` and proxies `/api` to the backend service on port `8000`.

## Explainability

Hospital, shelter, and rescue-team candidates expose structured `reasoning_factors`. Each factor contains:

- a factor name;
- the observed value;
- its normalized weight;
- its numeric score contribution.

The contributions sum to the candidate suitability score, and the UI presents a concise **Why this was selected** explanation.

## Project structure

```text
backend/     FastAPI API, models, services, configuration
frontend/    React dashboard and operational map
ai/          XGBoost training entrypoint
data/        deterministic fictional training data
tests/       backend unit and integration tests
docs/        data and implementation documentation
```

## Demo checklist

1. Start backend and frontend.
2. Choose Moderate, Severe, or Extreme rainfall.
3. Click a zone to select an incident.
4. Inspect affected zones and blocked roads.
5. Review safe route, hospital, shelter, and rescue-team decisions.
6. Expand the reasoning shown under each recommendation.
7. Generate the incident report and copy/download it.
8. Review analytics and the operations summary.
