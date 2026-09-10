"""HTTP API endpoints for RescueTwin AI."""

from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.models.damage_assessment import DamageAssessmentResponse
from app.models.decision_engine import DecisionEngineResponse
from app.models.district import DistrictProfile
from app.models.hospital_recommendation import HospitalRecommendationResponse
from app.models.prediction import FloodPredictionRequest, FloodPredictionResponse
from app.models.report_generation import IncidentReportResponse
from app.models.simulation import FloodSimulationResult, RainfallScenario
from app.models.routing import RouteResponse
from app.models.team_allocation import TeamAllocationResponse
from app.services.damage_assessment import assess_image_damage
from app.services.decision_engine import generate_decision_bundle
from app.services.district_service import get_district
from app.services.flood_prediction import get_prediction_service
from app.services.flood_simulation import simulate_flood
from app.services.hospital_recommendation import recommend_hospital
from app.services.report_generation import generate_incident_report
from app.services.routing_service import find_safe_route
from app.services.team_allocation import allocate_team

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: object | None = None


def _ensure_zone(zone_id: str, district: DistrictProfile) -> None:
    if not any(zone.id == zone_id for zone in district.zones):
        raise HTTPException(status_code=404, detail=f"Unknown incident zone '{zone_id}'.")


def _ensure_location(location_id: str, district: DistrictProfile) -> None:
    known_ids = {z.id for z in district.zones}
    known_ids.update(f.id for f in district.hospitals)
    known_ids.update(f.id for f in district.shelters)
    known_ids.update(t.id for t in district.rescue_teams)
    if location_id not in known_ids:
        raise HTTPException(status_code=404, detail=f"Unknown district location '{location_id}'.")


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="rescuetwin-api")


@router.get("/district", response_model=DistrictProfile, tags=["district"])
def district_metadata() -> DistrictProfile:
    return get_district()


@router.get("/simulate", response_model=FloodSimulationResult, tags=["simulation"])
def simulate(scenario: RainfallScenario = RainfallScenario.MODERATE) -> FloodSimulationResult:
    return simulate_flood(get_district(), scenario)


@router.get("/route", response_model=RouteResponse, tags=["routing"], responses={404: {"model": ErrorResponse}})
def calculate_route(start_id: str = Field(min_length=1), end_id: str = Field(min_length=1), scenario: RainfallScenario = RainfallScenario.MODERATE) -> RouteResponse:
    district = get_district()
    _ensure_location(start_id, district)
    _ensure_location(end_id, district)
    sim_result = simulate_flood(district, scenario)
    blocked_ids = {road.road_id for road in sim_result.blocked_roads}
    path_coords, distance = find_safe_route(start_id, end_id, blocked_ids)
    if not path_coords:
        return RouteResponse(status="no_route_available", distance_km=0.0, path=[])
    return RouteResponse(status="success", distance_km=round(distance, 2), path=path_coords)


@router.get("/recommendations/hospital", response_model=HospitalRecommendationResponse, tags=["recommendations"])
def recommend_hospital_for_incident(start_id: str = Field(min_length=1), scenario: RainfallScenario = RainfallScenario.MODERATE) -> HospitalRecommendationResponse:
    district = get_district()
    _ensure_location(start_id, district)
    return recommend_hospital(district, start_id, scenario)


@router.get("/recommendations/team", response_model=TeamAllocationResponse, tags=["recommendations"])
def recommend_team_for_incident(incident_zone_id: str = Field(min_length=1), scenario: RainfallScenario = RainfallScenario.MODERATE, required_specialty: str | None = None) -> TeamAllocationResponse:
    district = get_district()
    _ensure_zone(incident_zone_id, district)
    return allocate_team(district, incident_zone_id, scenario, required_specialty)


@router.post("/predict", response_model=FloodPredictionResponse, tags=["prediction"])
def predict_flood_severity(request: FloodPredictionRequest) -> FloodPredictionResponse:
    return get_prediction_service().predict(request)


@router.post("/assess-damage", response_model=DamageAssessmentResponse, tags=["damage"])
async def evaluate_incident_image(file: UploadFile = File(...)) -> DamageAssessmentResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename not provided.")
    try:
        content = await file.read()
        if not content:
            raise ValueError("Uploaded image is empty.")
        return assess_image_damage(content, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/decision-engine", response_model=DecisionEngineResponse, tags=["decision-engine"])
async def decision_engine(
    incident_zone_id: str = Form(..., min_length=1),
    rainfall_mm: float = Form(..., ge=0),
    elevation_m: float = Form(..., ge=0),
    drainage_score: int = Form(..., ge=0, le=10),
    previous_water_level_m: float = Form(..., ge=0),
    required_specialty: str | None = Form(None),
    file: UploadFile | None = File(None),
) -> DecisionEngineResponse:
    district = get_district()
    _ensure_zone(incident_zone_id, district)
    image_bytes = None
    image_filename = None
    if file and file.filename:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded image is empty.")
        image_filename = file.filename
    return generate_decision_bundle(district=district, incident_zone_id=incident_zone_id, rainfall_mm=rainfall_mm, elevation_m=elevation_m, drainage_score=drainage_score, previous_water_level_m=previous_water_level_m, required_specialty=required_specialty, image_bytes=image_bytes, image_filename=image_filename)


@router.post("/generate-report", response_model=IncidentReportResponse, tags=["report"])
def generate_report(decision: DecisionEngineResponse) -> IncidentReportResponse:
    return generate_incident_report(decision)
