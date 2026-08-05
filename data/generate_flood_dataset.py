"""CLI for generating RescueTwin's deterministic synthetic flood dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.synthetic_data import DEFAULT_SAMPLE_COUNT, DEFAULT_SEED, create_training_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a deterministic RescueTwin training CSV.")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "flood_training.csv")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLE_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    arguments = parser.parse_args()

    output_path = arguments.output if arguments.output.is_absolute() else PROJECT_ROOT / arguments.output
    validation = create_training_dataset(output_path, sample_count=arguments.samples, seed=arguments.seed)
    print(f"Wrote {validation.row_count} rows to {output_path}")
    print(f"Label distribution: {validation.label_distribution}")


if __name__ == "__main__":
    main()
