"""Initial API endpoints for service health and static district data."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.district import DistrictProfile
from app.models.prediction import FloodPredictionRequest, FloodPredictionResponse
from app.models.simulation import FloodSimulationResult, RainfallScenario
from app.models.routing import RouteResponse
from app.services.district_service import get_district
from app.services.flood_simulation import simulate_flood
from app.services.flood_prediction import get_prediction_service
from app.services.routing_service import find_safe_route

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


@router.get("/route", response_model=RouteResponse, tags=["routing"])
def calculate_route(start_id: str, end_id: str, scenario: RainfallScenario = RainfallScenario.MODERATE) -> RouteResponse:
    """Calculate the safest route avoiding roads blocked by the given scenario."""
    sim_result = simulate_flood(get_district(), scenario)
    blocked_ids = {road.road_id for road in sim_result.blocked_roads}
    
    path_coords, distance = find_safe_route(start_id, end_id, blocked_ids)
    
    if not path_coords:
        return RouteResponse(status="no_route_available", distance_km=0.0, path=[])
        
    return RouteResponse(status="success", distance_km=round(distance, 2), path=path_coords)


@router.post("/predict", response_model=FloodPredictionResponse, tags=["prediction"])
def predict_flood_severity(request: FloodPredictionRequest) -> FloodPredictionResponse:
    """Predict flood severity using the persisted XGBoost baseline artifact."""

    return get_prediction_service().predict(request)
