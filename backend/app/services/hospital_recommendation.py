"""Explainable hospital selection using capacity, flood risk, and safe routing."""

from __future__ import annotations

from app.models.district import DistrictProfile
from app.models.hospital_recommendation import (
    HospitalCandidate,
    HospitalExclusion,
    HospitalRecommendationResponse,
)
from app.models.reasoning import FallbackOption
from app.models.simulation import RainfallScenario
from app.services.flood_simulation import simulate_flood
from app.services.routing_service import find_safe_route, location_of, straight_line_km
from app.services.severity import clamp_severity

_MAX_SAFE_HOSPITAL_FLOOD_RISK = 75.0
_ESTIMATED_RESPONSE_SPEED_KPH = 30.0


def known_services(district: DistrictProfile) -> list[str]:
    return sorted({service.lower() for hospital in district.hospitals for service in hospital.services})


def _fallback_hospital(
    district: DistrictProfile, start_id: str, required_service: str | None, flood_risk_by_zone: dict[str, float]
) -> FallbackOption | None:
    """Nearest hospital with free capacity, ignoring road closures and flood threshold (informational)."""

    origin = location_of(start_id, district)
    if origin is None:
        return None
    options = [
        h for h in district.hospitals
        if h.capacity - h.current_occupancy > 0
        and (not required_service or required_service in {x.lower() for x in h.services})
    ]
    if not options:
        return None
    hospital = min(options, key=lambda h: straight_line_km(origin, h.location))
    distance = straight_line_km(origin, hospital.location)
    risk = flood_risk_by_zone.get(hospital.zone_id, 0.0)
    return FallbackOption(
        target_id=hospital.id,
        target_name=hospital.name,
        straight_line_km=round(distance, 2),
        advice=(
            f"No hospital is reachable by a safe road. {hospital.name} is {distance:.1f} km away in a straight "
            f"line with {hospital.capacity - hospital.current_occupancy} free beds (local flood risk "
            f"{risk:.0f}/100). Consider air or boat transfer; this is NOT a routed path."
        ),
    )


def recommend_hospital(
    district: DistrictProfile,
    start_id: str,
    scenario: RainfallScenario,
    incident_severity: float | None = None,
    required_service: str | None = None,
) -> HospitalRecommendationResponse:
    """Rank reachable hospitals for a scenario using explicit suitability factors.

    Higher ``incident_severity`` shifts weight from bed capacity toward travel
    distance (time-critical care).  ``required_service`` is a hard constraint.
    """

    service = required_service.strip().lower() if required_service else None
    severity = clamp_severity(incident_severity)
    distance_max = 10.0 + 0.2 * severity
    safety_max = 45.0
    capacity_max = 100.0 - safety_max - distance_max
    simulation = simulate_flood(district, scenario)
    flood_risk_by_zone = {impact.zone_id: impact.severity_score for impact in simulation.zone_impacts}
    blocked_road_ids = {road.road_id for road in simulation.blocked_roads}
    candidates: list[HospitalCandidate] = []
    exclusions: list[HospitalExclusion] = []

    for hospital in district.hospitals:
        available_capacity = hospital.capacity - hospital.current_occupancy
        if service and service not in {x.lower() for x in hospital.services}:
            exclusions.append(HospitalExclusion(
                hospital_id=hospital.id,
                hospital_name=hospital.name,
                reason=f"Excluded because it does not offer the required service '{service}'.",
            ))
            continue
        if available_capacity <= 0:
            exclusions.append(HospitalExclusion(
                hospital_id=hospital.id,
                hospital_name=hospital.name,
                reason="Excluded because no staffed bed capacity is currently available.",
            ))
            continue

        flood_risk = flood_risk_by_zone[hospital.zone_id]
        if flood_risk >= _MAX_SAFE_HOSPITAL_FLOOD_RISK:
            exclusions.append(HospitalExclusion(
                hospital_id=hospital.id,
                hospital_name=hospital.name,
                reason=(
                    f"Excluded because local flood risk is {flood_risk:.1f}/100, above the "
                    f"{_MAX_SAFE_HOSPITAL_FLOOD_RISK:.0f} safety threshold."
                ),
            ))
            continue

        route = find_safe_route(start_id, hospital.id, blocked_road_ids, district)
        if not route[0]:
            exclusions.append(HospitalExclusion(
                hospital_id=hospital.id,
                hospital_name=hospital.name,
                reason="Excluded because no safe route remains after flood-blocked roads are removed.",
            ))
            continue

        route_distance_km = route[1]
        travel_time_minutes = round((route_distance_km / _ESTIMATED_RESPONSE_SPEED_KPH) * 60, 1)
        capacity_ratio = available_capacity / hospital.capacity
        safety_score = (1 - flood_risk / 100) * safety_max
        capacity_score = capacity_ratio * capacity_max
        distance_score = max(0.0, distance_max - route_distance_km * 4 * (distance_max / 20.0))
        suitability_score = round(safety_score + capacity_score + distance_score, 1)

        reasoning_factors = [
            {
                "factor": "Flood safety",
                "value": f"{flood_risk:.1f}/100 local risk",
                "weight": round(safety_max / 100, 2),
                "contribution": round(safety_score, 1),
            },
            {
                "factor": "Available capacity",
                "value": f"{available_capacity} beds",
                "weight": round(capacity_max / 100, 2),
                "contribution": round(capacity_score, 1),
            },
            {
                "factor": "Safe-route distance",
                "value": f"{route_distance_km:.2f} km",
                "weight": round(distance_max / 100, 2),
                "contribution": round(distance_score, 1),
            },
        ]
        candidates.append(HospitalCandidate(
            hospital_id=hospital.id,
            hospital_name=hospital.name,
            zone_id=hospital.zone_id,
            route_distance_km=round(route_distance_km, 2),
            estimated_travel_time_minutes=travel_time_minutes,
            available_capacity=available_capacity,
            flood_risk_score=flood_risk,
            suitability_score=suitability_score,
            rationale=(
                f"Safe route is {route_distance_km:.2f} km; {available_capacity} beds are available; "
                f"local flood risk is {flood_risk:.1f}/100."
            ),
            reasoning_factors=reasoning_factors,
        ))

    ranked_hospitals = sorted(
        candidates,
        key=lambda candidate: (-candidate.suitability_score, candidate.route_distance_km, candidate.hospital_id),
    )
    if not ranked_hospitals:
        fallback = _fallback_hospital(district, start_id, service, flood_risk_by_zone)
        return HospitalRecommendationResponse(
            status="no_suitable_hospital",
            start_id=start_id,
            scenario=scenario.value,
            selected_hospital=None,
            ranked_hospitals=[],
            excluded_hospitals=exclusions,
            explanation=(
                "No hospital satisfies the current capacity, flood-risk, service, and safe-route constraints."
                + (" " + fallback.advice if fallback else " Request external air/boat medical evacuation.")
            ),
            required_service=service,
            fallback=fallback,
        )

    selected = ranked_hospitals[0]
    top_factor = max(selected.reasoning_factors, key=lambda factor: factor.contribution)
    return HospitalRecommendationResponse(
        status="success",
        start_id=start_id,
        scenario=scenario.value,
        selected_hospital=selected,
        ranked_hospitals=ranked_hospitals,
        excluded_hospitals=exclusions,
        explanation=(
            f"{selected.hospital_name} is the highest-ranked suitable hospital with a "
            f"{selected.suitability_score:.1f}/100 suitability score. The strongest contributing "
            f"factor is {top_factor.factor.lower()} ({top_factor.value}); safe-route distance is "
            f"{selected.route_distance_km:.2f} km."
        ),
        required_service=service,
    )
