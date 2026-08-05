"""Tests for the reusable synthetic flood-training dataset pipeline."""

from dataclasses import replace

from app.services.synthetic_data import (
    CSV_COLUMNS,
    generate_training_records,
    validate_training_records,
    write_training_dataset,
)


def test_generator_is_stable_and_large_enough_for_a_baseline() -> None:
    records = generate_training_records(sample_count=1_200, seed=123)

    assert records == generate_training_records(sample_count=1_200, seed=123)
    assert len(records) == 1_200
    assert tuple(records[0].__dataclass_fields__) == CSV_COLUMNS


def test_generated_records_pass_range_and_distribution_validation() -> None:
    validation = validate_training_records(generate_training_records(sample_count=1_200))

    assert validation.is_valid
    assert validation.row_count == 1_200
    assert all(fraction >= 0.05 for fraction in validation.label_distribution.values())


def test_validation_rejects_out_of_range_feature_values() -> None:
    records = generate_training_records(sample_count=10)
    invalid_records = (replace(records[0], rainfall_mm=-1.0), *records[1:])

    validation = validate_training_records(invalid_records)

    assert not validation.is_valid
    assert any("rainfall_mm" in error for error in validation.errors)


def test_writer_creates_headered_csv(tmp_path) -> None:
    output_path = tmp_path / "flood_training.csv"
    validation = write_training_dataset(output_path, generate_training_records(sample_count=200))

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert validation.is_valid
    assert lines[0].split(",") == list(CSV_COLUMNS)
    assert len(lines) == 201
