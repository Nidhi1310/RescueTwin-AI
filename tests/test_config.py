from pathlib import Path

from app.config import PROJECT_ROOT, get_settings


def test_default_settings_are_stable(monkeypatch) -> None:
    for name in (
        "RESCUETWIN_DATASET_PATH",
        "RESCUETWIN_MODEL_ARTIFACT_PATH",
        "RESCUETWIN_REPORT_TITLE",
        "RESCUETWIN_API_PREFIX",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = get_settings()
    assert settings.dataset_path == PROJECT_ROOT / "data" / "flood_training.csv"
    assert settings.model_artifact_path == PROJECT_ROOT / "backend" / "artifacts" / "flood_severity_xgb.joblib"
    assert settings.report_title == "RescueTwin AI Incident Report"
    assert settings.api_prefix == "/api/v1"


def test_relative_path_override_is_resolved_from_project_root(monkeypatch) -> None:
    monkeypatch.setenv("RESCUETWIN_DATASET_PATH", "custom/data.csv")
    monkeypatch.setenv("RESCUETWIN_API_PREFIX", "/api/test")
    settings = get_settings()
    assert settings.dataset_path == Path(PROJECT_ROOT / "custom/data.csv")
    assert settings.api_prefix == "/api/test"
