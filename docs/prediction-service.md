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

The response includes the 0–100 predicted severity and a confidence band based on the persisted model's held-out R² score. This is a demo baseline trained solely on fictional synthetic data.
