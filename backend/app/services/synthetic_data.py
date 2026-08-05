"""Deterministic synthetic training-data generation for future flood prediction."""

from __future__ import annotations

import csv
import random
from collections import Counter
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path
from typing import Iterable

from app.models.district import DistrictProfile
from app.services.district_service import get_district

FEATURE_COLUMNS = ("rainfall_mm", "elevation_m", "drainage_score", "previous_water_level_m")
TARGET_COLUMN = "flood_severity"
CSV_COLUMNS = (*FEATURE_COLUMNS, TARGET_COLUMN)
DEFAULT_SAMPLE_COUNT = 1_200
DEFAULT_SEED = 20260805


@dataclass(frozen=True)
class FloodTrainingRecord:
    """One tabular observation for the future flood-severity model."""

    rainfall_mm: float
    elevation_m: float
    drainage_score: int
    previous_water_level_m: float
    flood_severity: float


@dataclass(frozen=True)
class DatasetValidationResult:
    """Outcome of structural, range, and label-distribution validation."""

    row_count: int
    label_distribution: dict[str, float]
    errors: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _calculate_target_severity(
    rainfall_mm: float,
    elevation_m: float,
    drainage_score: int,
    previous_water_level_m: float,
) -> float:
    """Create a deterministic synthetic label with plausible causal influence."""

    rainfall_component = (rainfall_mm / 320.0) * 42.0
    elevation_component = _clamp((105.0 - elevation_m) / 50.0, 0.0, 1.0) * 18.0
    drainage_component = ((10 - drainage_score) / 9.0) * 15.0
    water_level_component = (previous_water_level_m / 4.0) * 25.0
    return round(_clamp(rainfall_component + elevation_component + drainage_component + water_level_component, 0.0, 100.0), 2)


def generate_training_records(
    district: DistrictProfile | None = None,
    *,
    sample_count: int = DEFAULT_SAMPLE_COUNT,
    seed: int = DEFAULT_SEED,
) -> tuple[FloodTrainingRecord, ...]:
    """Generate a reproducible dataset using the district's zone characteristics."""

    if sample_count <= 0:
        raise ValueError("sample_count must be greater than zero")

    source_district = district or get_district()
    generator = random.Random(seed)
    records: list[FloodTrainingRecord] = []
    for index in range(sample_count):
        zone = source_district.zones[index % len(source_district.zones)]
        rainfall_mm = round(generator.uniform(15.0, 320.0), 2)
        elevation_m = round(_clamp(zone.elevation_m + generator.uniform(-10.0, 10.0), 55.0, 110.0), 2)
        drainage_score = int(_clamp(zone.drainage_score + generator.choice((-1, 0, 0, 0, 1)), 1, 10))
        previous_water_level_m = round(
            _clamp((rainfall_mm / 160.0) + generator.uniform(-0.65, 0.65), 0.0, 4.0), 2
        )
        records.append(
            FloodTrainingRecord(
                rainfall_mm=rainfall_mm,
                elevation_m=elevation_m,
                drainage_score=drainage_score,
                previous_water_level_m=previous_water_level_m,
                flood_severity=_calculate_target_severity(
                    rainfall_mm, elevation_m, drainage_score, previous_water_level_m
                ),
            )
        )
    return tuple(records)


def validate_training_records(records: Iterable[FloodTrainingRecord]) -> DatasetValidationResult:
    """Validate schema values and ensure low, medium, and high labels are represented."""

    materialized_records = tuple(records)
    errors: list[str] = []
    expected_fields = tuple(field.name for field in fields(FloodTrainingRecord))
    if expected_fields != CSV_COLUMNS:
        errors.append("Training record schema does not match the expected feature columns.")
    if not materialized_records:
        errors.append("Dataset must contain at least one row.")

    label_bands: Counter[str] = Counter()
    for row_number, record in enumerate(materialized_records, start=1):
        values = asdict(record)
        if any(value is None for value in values.values()):
            errors.append(f"Row {row_number} contains a missing value.")
            continue
        if not 0.0 <= record.rainfall_mm <= 320.0:
            errors.append(f"Row {row_number} rainfall_mm is outside 0-320.")
        if not 55.0 <= record.elevation_m <= 110.0:
            errors.append(f"Row {row_number} elevation_m is outside 55-110.")
        if not 1 <= record.drainage_score <= 10:
            errors.append(f"Row {row_number} drainage_score is outside 1-10.")
        if not 0.0 <= record.previous_water_level_m <= 4.0:
            errors.append(f"Row {row_number} previous_water_level_m is outside 0-4.")
        if not 0.0 <= record.flood_severity <= 100.0:
            errors.append(f"Row {row_number} flood_severity is outside 0-100.")
        label_bands["low" if record.flood_severity < 35 else "medium" if record.flood_severity < 65 else "high"] += 1

    row_count = len(materialized_records)
    distribution = {band: round(label_bands[band] / row_count, 4) if row_count else 0.0 for band in ("low", "medium", "high")}
    if row_count >= 100 and any(distribution[band] < 0.05 for band in distribution):
        errors.append("Dataset label distribution requires at least 5% of rows in each severity band.")
    return DatasetValidationResult(row_count=row_count, label_distribution=distribution, errors=tuple(errors))


def write_training_dataset(path: Path, records: Iterable[FloodTrainingRecord]) -> DatasetValidationResult:
    """Validate and write records as a headered CSV ready for future training."""

    materialized_records = tuple(records)
    validation = validate_training_records(materialized_records)
    if not validation.is_valid:
        raise ValueError("Cannot write invalid training dataset: " + "; ".join(validation.errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(asdict(record) for record in materialized_records)
    return validation


def create_training_dataset(output_path: Path, *, sample_count: int = DEFAULT_SAMPLE_COUNT, seed: int = DEFAULT_SEED) -> DatasetValidationResult:
    """Generate, validate, and persist a reproducible training dataset."""

    return write_training_dataset(output_path, generate_training_records(sample_count=sample_count, seed=seed))
