"""Typed response models for image-based damage assessment."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class DamageLevel(str, Enum):
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class DamageAssessmentResponse(BaseModel):
    """An *indicative* colour-based estimate of floodwater coverage in an image.

    This is a prototype heuristic, not a trained model and not a structural
    assessment, so no statistical confidence is reported.
    """

    filename: str
    damage_level: DamageLevel
    confidence: float | None = Field(default=None, ge=0, le=100)
    rationale: str
    method: str = "heuristic_water_color_coverage"
    water_coverage_pct: float = Field(default=0.0, ge=0, le=100)
    disclaimer: str = "Indicative colour heuristic only. Not a structural or safety assessment; verify on site."
