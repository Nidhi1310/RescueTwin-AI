"""Initial API endpoints for service health and static district data."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.district import DistrictProfile
from app.models.prediction import FloodPredictionRequest, FloodPredictionResponse
from app.models.simulation import FloodSimulationResult, RainfallScenario
from app.services.district_service import get_district
from app.services.flood_simulation import simulate_flood
from app.services.flood_prediction import get_prediction_service

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    """Confirm the API process is ready to serve requests."""

    return HealthResponse(status="ok", service="rescuetwin-api")


@router.get("/district", response_model=DistrictProfile, tags=["district"])
def district_metadata() -> DistrictProfile:
    """Return all static operational data for Sundarpur District."""

    return get_district()


@router.get("/simulate", response_model=FloodSimulationResult, tags=["simulation"])
def simulate(scenario: RainfallScenario = RainfallScenario.MODERATE) -> FloodSimulationResult:
    """Return deterministic zone impacts and road closures for a rainfall scenario."""

    return simulate_flood(get_district(), scenario)


@router.post("/predict", response_model=FloodPredictionResponse, tags=["prediction"])
def predict_flood_severity(request: FloodPredictionRequest) -> FloodPredictionResponse:
    """Predict flood severity using the persisted XGBoost baseline artifact."""

    return get_prediction_service().predict(request)
