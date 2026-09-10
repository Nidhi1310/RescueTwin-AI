"""Typed response models for shelter suitability recommendations."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.models.reasoning import ReasoningFactor


class ShelterCandidate(BaseModel):
    """A shelter that is reachable and suitable for the active scenario."""

    shelter_id: str
    shelter_name: str
    zone_id: str
    route_distance_km: float = Field(ge=0)
    estimated_travel_time_minutes: float = Field(ge=0)
    available_capacity: int = Field(ge=0)
    flood_risk_score: float = Field(ge=0, le=100)
    suitability_score: float = Field(ge=0, le=100)
    rationale: str = Field(min_length=1)
    reasoning_factors: list[ReasoningFactor] = Field(min_length=1)


class ShelterExclusion(BaseModel):
    """A shelter excluded before final suitability ranking."""

    shelter_id: str
    shelter_name: str
    reason: str


class ShelterRecommendationResponse(BaseModel):
    """Frontend-ready selection, ranking, and exclusions for one incident origin."""

    status: Literal["success", "no_suitable_shelter"]
    start_id: str
    scenario: str
    selected_shelter: ShelterCandidate | None
    ranked_shelters: list[ShelterCandidate]
    excluded_shelters: list[ShelterExclusion]
    explanation: str = Field(min_length=1)
