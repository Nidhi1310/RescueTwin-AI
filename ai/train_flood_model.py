"""CLI for training RescueTwin's persisted XGBoost flood-severity baseline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.flood_prediction import DEFAULT_ARTIFACT_PATH, DEFAULT_DATASET_PATH, train_baseline_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the RescueTwin XGBoost flood baseline.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT_PATH)
    arguments = parser.parse_args()
    dataset_path = arguments.dataset if arguments.dataset.is_absolute() else PROJECT_ROOT / arguments.dataset
    artifact_path = arguments.artifact if arguments.artifact.is_absolute() else PROJECT_ROOT / arguments.artifact

    result = train_baseline_model(dataset_path, artifact_path)
    print(f"Saved model to {result.artifact_path}")
    print(f"Training rows: {result.training_rows}; test rows: {result.test_rows}")
    print(f"MAE: {result.metrics.mean_absolute_error}; R2: {result.metrics.r2_score}")


if __name__ == "__main__":
    main()
