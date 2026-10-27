"""Orchestrates all decision-making engines into a single bundle."""

from __future__ import annotations

from app.models.damage_assessment import DamageAssessmentResponse
from app.models.decision_engine import DecisionEngineResponse
from app.models.district import DistrictProfile
from app.models.prediction import FloodPredictionRequest
from app.models.routing import RouteResponse
from app.models.simulation import RainfallScenario
from app.services.damage_assessment import assess_image_damage
from app.services.dispatch_ledger import get_ledger
from app.services.flood_prediction import get_prediction_service
from app.services.flood_simulation import SCENARIO_PRESETS, scenario_for_rainfall, simulate_flood
from app.services.hospital_recommendation import recommend_hospital
from app.services.report_integrity import sign_decision
from app.services.routing_service import find_safe_route, is_zone_isolated
from app.services.severity import priority_band
from app.services.shelter_recommendation import recommend_shelter
from app.services.team_allocation import allocate_team

_PREDICTION_DISAGREEMENT_POINTS = 25.0
_ELEVATION_TOLERANCE_M = 0.5


class InconsistentIncidentInputs(ValueError):
    """Raised when supplied inputs contradict each other or the district data."""


def _build_route(
    district: DistrictProfile, start_id: str, end_id: str, blocked_road_ids: set[str]
) -> RouteResponse:
    path, distance = find_safe_route(start_id, end_id, blocked_road_ids, district)
    if not path:
        return RouteResponse(status="no_route_available", distance_km=0.0, path=[])
    return RouteResponse(status="success", distance_km=round(distance, 2), path=path)


def resolve_inputs(
    district: DistrictProfile,
    incident_zone_id: str,
    rainfall_mm: float | None,
    elevation_m: float | None,
    drainage_score: int | None,
    previous_water_level_m: float | None,
    scenario_override: RainfallScenario | None,
) -> tuple[RainfallScenario, float, float, int, float, str]:
    """Make the server authoritative for incident inputs.

    Zone elevation/drainage always come from district data (a caller may echo
    them but not contradict them).  Rainfall and water level come from the
    caller if given, else from the selected scenario's preset.  A scenario and
    a rainfall value that fall in different bands are rejected.
    """

    zone = next((z for z in district.zones if z.id == incident_zone_id), None)
    if zone is None:
        raise InconsistentIncidentInputs(f"Unknown zone id: {incident_zone_id}")
    if elevation_m is not None and abs(elevation_m - zone.elevation_m) > _ELEVATION_TOLERANCE_M:
        raise InconsistentIncidentInputs(
            f"elevation_m={elevation_m} contradicts {zone.id} ({zone.elevation_m} m). Omit it to use district data."
        )
    if drainage_score is not None and drainage_score != zone.drainage_score:
        raise InconsistentIncidentInputs(
            f"drainage_score={drainage_score} contradicts {zone.id} ({zone.drainage_score}). Omit it to use district data."
        )
    if rainfall_mm is None and scenario_override is None:
        raise InconsistentIncidentInputs("Provide a scenario or rainfall_mm.")

    if rainfall_mm is not None:
        derived = scenario_for_rainfall(rainfall_mm)
        if scenario_override is not None and scenario_override != derived:
            raise InconsistentIncidentInputs(
                f"rainfall_mm={rainfall_mm} falls in the '{derived.value}' band but scenario='{scenario_override.value}'."
            )
        scenario = derived
        source = "user_supplied"
        rainfall = rainfall_mm
        water = previous_water_level_m if previous_water_level_m is not None else round(min(4.0, rainfall / 160.0), 2)
    else:
        assert scenario_override is not None
        scenario = scenario_override
        preset = SCENARIO_PRESETS[scenario]
        rainfall = preset.rainfall_mm
        water = previous_water_level_m if previous_water_level_m is not None else preset.previous_water_level_m
        source = "user_supplied" if previous_water_level_m is not None else "scenario_preset"
    return scenario, rainfall, zone.elevation_m, zone.drainage_score, water, source


def generate_decision_bundle(
    district: DistrictProfile,
    incident_zone_id: str,
    rainfall_mm: float | None = None,
    elevation_m: float | None = None,
    drainage_score: int | None = None,
    previous_water_level_m: float | None = None,
    required_specialty: str | None = None,
    scenario_override: RainfallScenario | None = None,
    image_bytes: bytes | None = None,
    image_filename: str | None = None,
    required_service: str | None = None,
    commit_dispatch: bool = False,
) -> DecisionEngineResponse:
    """Generate one internally consistent decision bundle for the selected incident."""

    scenario, rainfall, elevation, drainage, water_level, source = resolve_inputs(
        district, incident_zone_id, rainfall_mm, elevation_m, drainage_score, previous_water_level_m, scenario_override
    )
    prediction = get_prediction_service().predict(FloodPredictionRequest(
        rainfall_mm=rainfall,
        elevation_m=elevation,
        drainage_score=drainage,
        previous_water_level_m=water_level,
    ))
    severity = prediction.predicted_flood_severity
    priority = priority_band(severity)

    simulation = simulate_flood(district, scenario)
    blocked_road_ids = {road.road_id for road in simulation.blocked_roads}
    isolated = is_zone_isolated(incident_zone_id, blocked_road_ids, district)

    hospital_rec = recommend_hospital(district, incident_zone_id, scenario, severity, required_service)
    shelter_rec = recommend_shelter(district, incident_zone_id, scenario)

    ledger = get_ledger()
    committed = False

    def _allocate(reserved: frozenset[str]):
        return allocate_team(district, incident_zone_id, scenario, required_specialty, severity, reserved)

    if commit_dispatch:
        team_rec, committed = ledger.commit_allocation(
            incident_zone_id, _allocate,
            lambda r: r.selected_team.team_id if r.status == "success" and r.selected_team else None,
        )
    else:
        team_rec = _allocate(ledger.reserved_team_ids(excluding_incident=incident_zone_id))

    hospital_route = (
        _build_route(district, incident_zone_id, hospital_rec.selected_hospital.hospital_id, blocked_road_ids)
        if hospital_rec.status == "success" and hospital_rec.selected_hospital else None
    )
    shelter_route = (
        _build_route(district, incident_zone_id, shelter_rec.selected_shelter.shelter_id, blocked_road_ids)
        if shelter_rec.status == "success" and shelter_rec.selected_shelter else None
    )
    team_route = (
        _build_route(district, team_rec.selected_team.team_id, incident_zone_id, blocked_road_ids)
        if team_rec.status == "success" and team_rec.selected_team else None
    )

    warnings: list[str] = []
    damage: DamageAssessmentResponse | None = None
    if image_bytes and image_filename:
        try:
            damage = assess_image_damage(image_bytes, image_filename)
        except ValueError as exc:
            warnings.append(f"Incident image was rejected and NOT assessed: {exc}")

    if source == "scenario_preset":
        warnings.append(
            f"Environmental inputs are the '{scenario.value}' scenario preset (rainfall {rainfall:.0f} mm), "
            "not live sensor data."
        )
    if isolated:
        warnings.append(
            f"{incident_zone_id} is cut off: every access road is flood-blocked. Road dispatch is not possible; "
            "see the fallback options."
        )
    zone_severity = next(i.severity_score for i in simulation.zone_impacts if i.zone_id == incident_zone_id)
    if abs(zone_severity - severity) > _PREDICTION_DISAGREEMENT_POINTS:
        warnings.append(
            f"ML prediction ({severity:.0f}/100) and scenario simulation for {incident_zone_id} "
            f"({zone_severity:.0f}/100) disagree by more than {_PREDICTION_DISAGREEMENT_POINTS:.0f} points. "
            "Treat both with caution."
        )
    if prediction.out_of_support_inputs:
        warnings.append(
            "Prediction inputs are outside or at the edge of the model's training range: "
            + ", ".join(prediction.out_of_support_inputs) + "."
        )
    affected_ids = {impact.zone_id for impact in simulation.affected_zones}
    affected_pop = sum(z.population for z in district.zones if z.id in affected_ids)
    shelter_free = sum(s.capacity - s.current_occupancy for s in district.shelters)
    beds_free = sum(h.capacity - h.current_occupancy for h in district.hospitals)
    if affected_pop and shelter_free < affected_pop:
        warnings.append(
            f"Capacity gap: {shelter_free:,} free shelter spaces cover {100 * shelter_free / affected_pop:.1f}% of the "
            f"{affected_pop:,} residents in flood-affected zones; {beds_free:,} hospital beds are free district-wide."
        )

    response = DecisionEngineResponse(
        incident_zone_id=incident_zone_id,
        prediction=prediction,
        simulation=simulation,
        damage_assessment=damage,
        hospital_recommendation=hospital_rec,
        hospital_route=hospital_route,
        shelter_recommendation=shelter_rec,
        shelter_route=shelter_route,
        team_allocation=team_rec,
        team_route=team_route,
        priority=priority,
        incident_isolated=isolated,
        input_basis="scenario_preset" if source == "scenario_preset" else "user_supplied",
        dispatch_committed=committed,
        warnings=warnings,
    )
    return response.model_copy(update={"signature": sign_decision(response)})
