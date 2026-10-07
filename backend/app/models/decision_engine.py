"""Typed response models for the unified decision engine."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.models.damage_assessment import DamageAssessmentResponse
from app.models.hospital_recommendation import HospitalRecommendationResponse
from app.models.prediction import FloodPredictionResponse
from app.models.routing import RouteResponse
from app.models.shelter_recommendation import ShelterRecommendationResponse
from app.models.simulation import FloodSimulationResult
from app.models.team_allocation import TeamAllocationResponse


class DecisionEngineResponse(BaseModel):
    """The complete decision bundle serving as the single source of truth for the frontend."""

    incident_zone_id: str
    prediction: FloodPredictionResponse
    simulation: FloodSimulationResult
    damage_assessment: DamageAssessmentResponse | None
    hospital_recommendation: HospitalRecommendationResponse
    hospital_route: RouteResponse | None
    shelter_recommendation: ShelterRecommendationResponse
    shelter_route: RouteResponse | None
    team_allocation: TeamAllocationResponse
    team_route: RouteResponse | None
    priority: Literal["routine", "urgent", "critical"] = "urgent"
    incident_isolated: bool = False
    input_basis: Literal["scenario_preset", "user_supplied"] = "scenario_preset"
    dispatch_committed: bool = False
    warnings: list[str] = Field(default_factory=list)
    signature: str | None = Field(
        default=None, description="Server-issued integrity signature required by /generate-report."
    )
