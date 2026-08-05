# RescueTwin AI

RescueTwin AI is a fictional flood-response decision-support project. This first increment provides a typed FastAPI backend and a realistic static dataset for Sundarpur District.

## Run the backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/api/v1/health`
- `http://127.0.0.1:8000/api/v1/district`

## Run tests

```powershell
$env:PYTHONPATH = "backend"
python -m pytest tests -q
```

The dataset is deliberately static. Simulation, route optimization, and AI behavior will be added in later increments.

## Generate synthetic training data

```powershell
python data/generate_flood_dataset.py --samples 1200
```

This writes a deterministic CSV to `data/flood_training.csv`. It contains rainfall, elevation, drainage score, previous water level, and a synthetic flood-severity target. It does not train a model.
