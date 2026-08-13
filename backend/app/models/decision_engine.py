"""Typed response models for the unified decision engine."""

from __future__ import annotations

from pydantic import BaseModel

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
