# Flood prediction service

The baseline model is an XGBoost regressor trained on the synthetic flood dataset. Training uses a deterministic 80/20 scikit-learn train/test split with `random_state=42`, and writes the model plus its evaluation metrics to `backend/artifacts/flood_severity_xgb.joblib`.

Train or refresh the artifact:

```powershell
python ai/train_flood_model.py
```

Call the API after starting the backend:

```text
POST /api/v1/predict
```

```json
{
  "rainfall_mm": 180,
  "elevation_m": 72,
  "drainage_score": 3,
  "previous_water_level_m": 1.5
}
```

The response includes the 0–100 predicted severity and a heuristic confidence category based on the persisted model's held-out R² score. This is not a calibrated confidence or prediction interval. The demo baseline is trained solely on fictional synthetic data, and its random holdout metrics are not leakage-resistant or real-world validation.

Use `GET /api/v1/ready` to check whether the artifact is present and loadable. If it is missing, run `python ai/train_flood_model.py`; prediction and decision-engine requests return HTTP 503 with a remediation message until the artifact is available.
