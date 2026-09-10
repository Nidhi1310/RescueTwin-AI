"""Typed response models for hospital suitability recommendations."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.models.reasoning import ReasoningFactor


class HospitalCandidate(BaseModel):
    """A hospital that is reachable and suitable for the active scenario."""

    hospital_id: str
    hospital_name: str
    zone_id: str
    route_distance_km: float = Field(ge=0)
    estimated_travel_time_minutes: float = Field(ge=0)
    available_capacity: int = Field(ge=0)
    flood_risk_score: float = Field(ge=0, le=100)
    suitability_score: float = Field(ge=0, le=100)
    rationale: str = Field(min_length=1)
    reasoning_factors: list[ReasoningFactor] = Field(min_length=1)


class HospitalExclusion(BaseModel):
    """A hospital excluded before final suitability ranking."""

    hospital_id: str
    hospital_name: str
    reason: str


class HospitalRecommendationResponse(BaseModel):
    """Frontend-ready selection, ranking, and exclusions for one incident origin."""

    status: Literal["success", "no_suitable_hospital"]
    start_id: str
    scenario: str
    selected_hospital: HospitalCandidate | None
    ranked_hospitals: list[HospitalCandidate]
    excluded_hospitals: list[HospitalExclusion]
    explanation: str = Field(min_length=1)
