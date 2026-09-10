"""Environment-aware application configuration for RescueTwin AI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _path_from_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    path = Path(value).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


@dataclass(frozen=True)
class Settings:
    """Runtime paths and report settings with stable local-development defaults."""

    dataset_path: Path
    model_artifact_path: Path
    report_title: str
    api_prefix: str


def get_settings() -> Settings:
    """Build settings from environment variables without requiring a .env file."""

    return Settings(
        dataset_path=_path_from_env("RESCUETWIN_DATASET_PATH", PROJECT_ROOT / "data" / "flood_training.csv"),
        model_artifact_path=_path_from_env("RESCUETWIN_MODEL_ARTIFACT_PATH", PROJECT_ROOT / "backend" / "artifacts" / "flood_severity_xgb.joblib"),
        report_title=os.getenv("RESCUETWIN_REPORT_TITLE", "RescueTwin AI Incident Report"),
        api_prefix=os.getenv("RESCUETWIN_API_PREFIX", "/api/v1"),
    )


settings = get_settings()
