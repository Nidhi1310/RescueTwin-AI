"""Orchestrates all decision-making engines into a single bundle."""

from __future__ import annotations

from app.models.decision_engine import DecisionEngineResponse
from app.models.district import DistrictProfile
from app.models.prediction import FloodPredictionRequest
from app.models.routing import RouteResponse
from app.models.simulation import RainfallScenario
from app.services.damage_assessment import assess_image_damage
from app.services.flood_prediction import get_prediction_service
from app.services.flood_simulation import simulate_flood
from app.services.hospital_recommendation import recommend_hospital
from app.services.routing_service import build_routing_graph, find_safe_route
from app.services.shelter_recommendation import recommend_shelter
from app.services.team_allocation import allocate_team


def _build_route(start_id: str, end_id: str, blocked_road_ids: set[str]) -> RouteResponse:
    """Convert the routing service tuple into the API response contract."""
    path, distance = find_safe_route(start_id, end_id, blocked_road_ids)
    return RouteResponse(status="success", distance_km=round(distance, 2), path=path)


def generate_decision_bundle(
    district: DistrictProfile,
    incident_zone_id: str,
    rainfall_mm: float,
    elevation_m: float,
    drainage_score: int,
    previous_water_level_m: float,
    required_specialty: str | None = None,
    image_bytes: bytes | None = None,
    image_filename: str | None = None,
) -> DecisionEngineResponse:
    """Generate the unified decision bundle for the frontend."""

    prediction_req = FloodPredictionRequest(
        rainfall_mm=rainfall_mm,
        elevation_m=elevation_m,
        drainage_score=drainage_score,
        previous_water_level_m=previous_water_level_m,
    )
    prediction = get_prediction_service().predict(prediction_req)

    severity = prediction.predicted_flood_severity
    if severity >= 75:
        scenario = RainfallScenario.EXTREME
    elif severity >= 40:
        scenario = RainfallScenario.SEVERE
    else:
        scenario = RainfallScenario.MODERATE

    simulation = simulate_flood(district, scenario)
    blocked_road_ids = {road.road_id for road in simulation.blocked_roads}

    hospital_rec = recommend_hospital(district, incident_zone_id, scenario)
    hospital_route = (
        _build_route(incident_zone_id, hospital_rec.selected_hospital.hospital_id, blocked_road_ids)
        if hospital_rec.status == "success" and hospital_rec.selected_hospital
        else None
    )

    shelter_rec = recommend_shelter(district, incident_zone_id, scenario)
    shelter_route = (
        _build_route(incident_zone_id, shelter_rec.selected_shelter.shelter_id, blocked_road_ids)
        if shelter_rec.status == "success" and shelter_rec.selected_shelter
        else None
    )

    team_rec = allocate_team(district, incident_zone_id, scenario, required_specialty)
    team_route = (
        _build_route(team_rec.selected_team.team_id, incident_zone_id, blocked_road_ids)
        if team_rec.status == "success" and team_rec.selected_team
        else None
    )

    damage_assessment = None
    if image_bytes and image_filename:
        try:
            damage_assessment = assess_image_damage(image_bytes, image_filename)
        except ValueError:
            damage_assessment = None

    return DecisionEngineResponse(
        incident_zone_id=incident_zone_id,
        prediction=prediction,
        simulation=simulation,
        damage_assessment=damage_assessment,
        hospital_recommendation=hospital_rec,
        hospital_route=hospital_route,
        shelter_recommendation=shelter_rec,
        shelter_route=shelter_route,
        team_allocation=team_rec,
        team_route=team_route,
    )
