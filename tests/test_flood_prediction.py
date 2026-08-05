"""Tests for XGBoost baseline training, artifact loading, and predictions."""

from app.models.prediction import FloodPredictionRequest
from app.services.flood_prediction import FloodPredictionService, train_baseline_model
from app.services.synthetic_data import generate_training_records, write_training_dataset


def test_training_writes_a_loadable_model_artifact(tmp_path) -> None:
    dataset_path = tmp_path / "training.csv"
    artifact_path = tmp_path / "flood_model.joblib"
    write_training_dataset(dataset_path, generate_training_records(sample_count=400))

    result = train_baseline_model(dataset_path, artifact_path)

    assert artifact_path.exists()
    assert result.training_rows == 320
    assert result.test_rows == 80
    assert result.metrics.r2_score > 0.9


def test_loaded_model_returns_deterministic_prediction_shape(tmp_path) -> None:
    dataset_path = tmp_path / "training.csv"
    artifact_path = tmp_path / "flood_model.joblib"
    write_training_dataset(dataset_path, generate_training_records(sample_count=400))
    train_baseline_model(dataset_path, artifact_path)
    service = FloodPredictionService(artifact_path)
    request = FloodPredictionRequest(
        rainfall_mm=180.0,
        elevation_m=72.0,
        drainage_score=3,
        previous_water_level_m=1.5,
    )

    first_prediction = service.predict(request)
    second_prediction = service.predict(request)

    assert first_prediction == second_prediction
    assert 0 <= first_prediction.predicted_flood_severity <= 100
    assert first_prediction.confidence in {"low", "medium", "high"}
