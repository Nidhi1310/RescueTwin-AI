# RescueTwin AI — Demo Guide

## Before the demo

1. Confirm Python dependencies are installed.
2. Ensure the model artifact exists, or train it with `python ai/train_flood_model.py`.
3. Start the backend:
   ```powershell
   cd backend
   python -m uvicorn app.main:app --reload
   ```
4. In a second terminal start the frontend:
   ```powershell
   cd frontend
   npm.cmd install
   npm.cmd run dev
   ```
5. Open `http://127.0.0.1:5173`.

## Recommended demo sequence

### 1. Select a scenario

Choose **Moderate**, **Severe**, or **Extreme**. The dashboard requests the corresponding deterministic simulation.

### 2. Inspect the map

Show affected flood zones and blocked roads. Explain that road closures are derived from the selected scenario.

### 3. Select an incident

Click a flood zone to make it the incident location. The incident zone ID becomes the shared operational reference.

### 4. Run decision analysis

The decision engine evaluates the incident using the selected scenario and environmental inputs.

Highlight:

- predicted flood severity;
- confidence and explanation;
- affected zones and blocked roads;
- safe-route results;
- rescue-team allocation;
- hospital recommendation;
- shelter recommendation.

### 5. Explain recommendations

Each recommendation is based on explicit factors such as safe-route distance, flood safety, available capacity, specialty match, and personnel availability. The system returns ranked candidates and reasoning where supported.

### 6. Optional damage assessment

Upload an incident image when the interface provides the damage-assessment control. The result is attached to the decision bundle and can be represented in the report.

### 7. Generate the report

Select **Generate Incident Report**. The report is generated from the current decision bundle, preserving the selected incident and operational results.

Use **Copy** or **Download** when available.

## What to demonstrate technically

The strongest engineering points to mention are:

- backend-authoritative operational state;
- deterministic fictional district data;
- explicit scenario propagation through the decision engine;
- Dijkstra routing with blocked-road constraints;
- explainable recommendation scoring;
- typed FastAPI/Pydantic contracts;
- persisted XGBoost baseline;
- regression and integration tests;
- Dockerized backend/frontend option.

## Quick API smoke test

With the backend running:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/health"
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/district"
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/simulate?scenario=severe"
```

For the complete decision/report path, use the dashboard or the interactive API documentation at `http://127.0.0.1:8000/docs`.

## Verification

Run from the repository root:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest tests -q

cd frontend
npm.cmd run build
```

A release candidate should have a green test suite and a successful frontend production build.
