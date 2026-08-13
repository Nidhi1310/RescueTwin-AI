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
    """Response containing the deterministic classification of an incident image."""

    filename: str
    damage_level: DamageLevel
    confidence: float = Field(ge=0, le=100)
    rationale: str
