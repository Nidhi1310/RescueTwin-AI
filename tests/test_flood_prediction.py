"""Tests for XGBoost baseline training, artifact loading, and predictions."""

from app.models.prediction import FloodPredictionRequest
from app.services.flood_prediction import (
    DEFAULT_DATASET_PATH,
    DEFAULT_ARTIFACT_PATH,
    FloodPredictionService,
    bootstrap_model,
    check_model_readiness,
    train_baseline_model,
)
from app.services.synthetic_data import generate_training_records, write_training_dataset


def test_training_writes_a_loadable_model_artifact(tmp_path) -> None:
    dataset_path = tmp_path / "training.csv"
    artifact_path = tmp_path / "flood_model.json"
    write_training_dataset(dataset_path, generate_training_records(sample_count=400))

    result = train_baseline_model(dataset_path, artifact_path)

    assert artifact_path.exists()
    assert result.training_rows == 320
    assert result.test_rows == 80
    assert result.metrics.r2_score > 0.9


def test_loaded_model_returns_deterministic_prediction_shape(tmp_path) -> None:
    dataset_path = tmp_path / "training.csv"
    artifact_path = tmp_path / "flood_model.json"
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


def test_default_paths_are_portable_repository_paths() -> None:
    assert DEFAULT_DATASET_PATH.name == "flood_training.csv"
    assert DEFAULT_DATASET_PATH.parent.name == "data"
    assert DEFAULT_ARTIFACT_PATH.name == "flood_severity_xgb.json"
    assert DEFAULT_ARTIFACT_PATH.parent.name == "artifacts"


def test_bootstrap_generates_dataset_and_artifact_when_missing(tmp_path) -> None:
    dataset_path = tmp_path / "generated" / "flood_training.csv"
    artifact_path = tmp_path / "generated" / "model.json"

    result = bootstrap_model(dataset_path, artifact_path)

    assert dataset_path.exists()
    assert artifact_path.exists()
    assert result.training_rows > 0
    assert FloodPredictionService(artifact_path).predict(
        FloodPredictionRequest(
            rainfall_mm=100.0,
            elevation_m=80.0,
            drainage_score=3,
            previous_water_level_m=1.5,
        )
    ).predicted_flood_severity >= 0


def test_readiness_reports_missing_artifact(tmp_path) -> None:
    ready, message = check_model_readiness(tmp_path / "missing.json")

    assert not ready
    assert "Run 'python ai/train_flood_model.py'" in message
