"""API endpoints for RescueTwin AI operational services."""

from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

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
from app.services.report_generation import generate_incident_report
from app.services.district_service import get_district
from app.services.flood_simulation import simulate_flood
from app.services.flood_prediction import get_prediction_service
from app.services.hospital_recommendation import recommend_hospital
from app.services.routing_service import find_safe_route
from app.services.team_allocation import allocate_team, known_specialties, normalize_specialty
from app.services.decision_engine import InconsistentIncidentInputs
from app.services.dispatch_ledger import get_ledger
from app.services.flood_simulation import SCENARIO_PRESETS
from app.services.hospital_recommendation import known_services
from app.services.report_integrity import verify_decision
from app.security import audit, read_limited_upload, require_api_key

public_router = APIRouter()  # unauthenticated: health only
router = APIRouter(dependencies=[Depends(require_api_key)])


APP_VERSION = "0.2.0"


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str = APP_VERSION


def _ensure_zone(zone_id: str) -> None:
    if not any(zone.id == zone_id for zone in get_district().zones):
        raise HTTPException(status_code=404, detail=f"Unknown zone id: {zone_id}")


def _ensure_location(location_id: str) -> None:
    district = get_district()
    known_ids = {
        item.id
        for item in (
            *district.zones,
            *district.hospitals,
            *district.shelters,
            *district.rescue_teams,
        )
    }
    if location_id not in known_ids:
        raise HTTPException(status_code=404, detail=f"Unknown operational location id: {location_id}")


def _validate_specialty(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = normalize_specialty(value)
    options = known_specialties(get_district())
    if normalized not in options:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown specialty '{value}'. Available specialties: {', '.join(options)}.",
        )
    return normalized


def _validate_service(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    options = known_services(get_district())
    if normalized not in options:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown hospital service '{value}'. Available services: {', '.join(options)}.",
        )
    return normalized


@public_router.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="rescuetwin-api", version=APP_VERSION)


@router.get("/district", response_model=DistrictProfile, tags=["district"])
def district_metadata() -> DistrictProfile:
    return get_district()


@router.get("/simulate", response_model=FloodSimulationResult, tags=["simulation"])
def simulate(scenario: RainfallScenario = RainfallScenario.MODERATE) -> FloodSimulationResult:
    return simulate_flood(get_district(), scenario)


@router.get("/route", response_model=RouteResponse, tags=["routing"])
def calculate_route(
    start_id: str = Query(min_length=1),
    end_id: str = Query(min_length=1),
    scenario: RainfallScenario = RainfallScenario.MODERATE,
) -> RouteResponse:
    _ensure_location(start_id)
    _ensure_location(end_id)
    sim_result = simulate_flood(get_district(), scenario)
    blocked_ids = {road.road_id for road in sim_result.blocked_roads}
    path_coords, distance = find_safe_route(start_id, end_id, blocked_ids)
    if not path_coords:
        return RouteResponse(status="no_route_available", distance_km=0.0, path=[])
    return RouteResponse(status="success", distance_km=round(distance, 2), path=path_coords)


@router.get("/recommendations/hospital", response_model=HospitalRecommendationResponse, tags=["recommendations"])
def recommend_hospital_for_incident(
    start_id: str = Query(min_length=1),
    scenario: RainfallScenario = RainfallScenario.MODERATE,
    required_service: str | None = Query(default=None, min_length=1),
) -> HospitalRecommendationResponse:
    _ensure_location(start_id)
    service = _validate_service(required_service)
    return recommend_hospital(get_district(), start_id, scenario, required_service=service)


@router.get("/recommendations/team", response_model=TeamAllocationResponse, tags=["recommendations"])
def recommend_team_for_incident(
    incident_zone_id: str = Query(min_length=1),
    scenario: RainfallScenario = RainfallScenario.MODERATE,
    required_specialty: str | None = Query(default=None, min_length=1),
) -> TeamAllocationResponse:
    _ensure_zone(incident_zone_id)
    specialty = _validate_specialty(required_specialty)
    reserved = get_ledger().reserved_team_ids(excluding_incident=incident_zone_id)
    return allocate_team(get_district(), incident_zone_id, scenario, specialty, unavailable_team_ids=reserved)


@router.post("/predict", response_model=FloodPredictionResponse, tags=["prediction"])
def predict_flood_severity(request: FloodPredictionRequest) -> FloodPredictionResponse:
    return get_prediction_service().predict(request)


@router.post("/assess-damage", response_model=DamageAssessmentResponse, tags=["damage"])
async def evaluate_incident_image(file: UploadFile = File(...)) -> DamageAssessmentResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename not provided.")
    content = await read_limited_upload(file)
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
    try:
        return assess_image_damage(content, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/decision-engine", response_model=DecisionEngineResponse, tags=["decision-engine"])
async def decision_engine(
    request: Request,
    incident_zone_id: str = Form(..., min_length=1),
    scenario: RainfallScenario | None = Form(None),
    rainfall_mm: float | None = Form(None, ge=0, le=320),
    elevation_m: float | None = Form(None, ge=55, le=110),
    drainage_score: int | None = Form(None, ge=1, le=10),
    previous_water_level_m: float | None = Form(None, ge=0, le=4),
    required_specialty: str | None = Form(None, min_length=1),
    required_service: str | None = Form(None, min_length=1),
    commit: bool = Form(False),
    file: UploadFile | None = File(None),
) -> DecisionEngineResponse:
    """Run the full decision workflow.

    The server is authoritative: zone elevation/drainage come from district data
    (echoing them is allowed, contradicting them is rejected) and, if only a
    scenario is given, rainfall/water level come from that scenario's preset.
    By default this is a what-if preview; pass ``commit=true`` to reserve the team.
    """

    _ensure_zone(incident_zone_id)
    specialty = _validate_specialty(required_specialty)
    service = _validate_service(required_service)
    image_bytes = None
    image_filename = None
    if file and file.filename:
        image_bytes = await read_limited_upload(file)
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
        image_filename = file.filename
    try:
        decision = await run_in_threadpool(
            generate_decision_bundle,
            district=get_district(),
            incident_zone_id=incident_zone_id,
            rainfall_mm=rainfall_mm,
            elevation_m=elevation_m,
            drainage_score=drainage_score,
            previous_water_level_m=previous_water_level_m,
            required_specialty=specialty,
            scenario_override=scenario,
            image_bytes=image_bytes,
            image_filename=image_filename,
            required_service=service,
            commit_dispatch=commit,
        )
    except InconsistentIncidentInputs as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    team = decision.team_allocation.selected_team
    audit(
        request, "decision_engine",
        zone=incident_zone_id, scenario=decision.simulation.scenario.value, priority=decision.priority,
        team=team.team_id if team else None, committed=decision.dispatch_committed,
        isolated=decision.incident_isolated,
    )
    return decision


@router.post("/generate-report", response_model=IncidentReportResponse, tags=["report"])
def generate_report(decision: DecisionEngineResponse) -> IncidentReportResponse:
    """Generate a report from a decision bundle previously issued (and signed) by this server."""

    if not verify_decision(decision):
        raise HTTPException(
            status_code=400,
            detail="Decision bundle failed its integrity check: it was modified or was not issued by this server.",
        )
    return generate_incident_report(decision)


class DispatchAssignment(BaseModel):
    team_id: str
    incident_zone_id: str


class DispatchState(BaseModel):
    assignments: list[DispatchAssignment]


@router.get("/dispatch", response_model=DispatchState, tags=["dispatch"])
def list_dispatch() -> DispatchState:
    """Teams currently committed to incidents."""

    return DispatchState(assignments=[
        DispatchAssignment(team_id=team, incident_zone_id=zone) for team, zone in sorted(get_ledger().snapshot().items())
    ])


@router.delete("/dispatch/{incident_zone_id}", response_model=DispatchState, tags=["dispatch"])
def release_dispatch(request: Request, incident_zone_id: str) -> DispatchState:
    """Release every team committed to an incident, making them available again."""

    _ensure_zone(incident_zone_id)
    released = get_ledger().release_incident(incident_zone_id)
    if not released:
        raise HTTPException(status_code=404, detail=f"No team is committed to {incident_zone_id}.")
    audit(request, "dispatch_release", zone=incident_zone_id, teams=",".join(released))
    return list_dispatch()


@router.get("/scenarios", tags=["simulation"])
def scenario_presets() -> dict[str, dict[str, float]]:
    """Representative inputs used when only a scenario is selected (not live data)."""

    return {
        scenario.value: {
            "rainfall_mm": preset.rainfall_mm,
            "previous_water_level_m": preset.previous_water_level_m,
        }
        for scenario, preset in SCENARIO_PRESETS.items()
    }
