"""Explainable hospital selection using capacity, flood risk, and safe routing."""

from __future__ import annotations

from app.models.district import DistrictProfile
from app.models.hospital_recommendation import (
    HospitalCandidate,
    HospitalExclusion,
    HospitalRecommendationResponse,
)
from app.models.reasoning import ReasoningFactor
from app.models.simulation import RainfallScenario
from app.services.flood_simulation import simulate_flood
from app.services.routing_service import build_routing_graph, find_safe_route

_MAX_SAFE_HOSPITAL_FLOOD_RISK = 75.0
_ESTIMATED_RESPONSE_SPEED_KPH = 30.0


def recommend_hospital(
    district: DistrictProfile,
    start_id: str,
    scenario: RainfallScenario,
) -> HospitalRecommendationResponse:
    """Rank reachable hospitals for a scenario using explicit suitability factors."""

    build_routing_graph(district)
    simulation = simulate_flood(district, scenario)
    flood_risk_by_zone = {impact.zone_id: impact.severity_score for impact in simulation.zone_impacts}
    blocked_road_ids = {road.road_id for road in simulation.blocked_roads}
    candidates: list[HospitalCandidate] = []
    exclusions: list[HospitalExclusion] = []

    for hospital in district.hospitals:
        available_capacity = hospital.capacity - hospital.current_occupancy
        if available_capacity <= 0:
            exclusions.append(HospitalExclusion(hospital_id=hospital.id, hospital_name=hospital.name, reason="Excluded because no staffed bed capacity is currently available."))
            continue

        flood_risk = flood_risk_by_zone[hospital.zone_id]
        if flood_risk >= _MAX_SAFE_HOSPITAL_FLOOD_RISK:
            exclusions.append(HospitalExclusion(
                hospital_id=hospital.id,
                hospital_name=hospital.name,
                reason=f"Excluded because local flood risk is {flood_risk:.1f}/100, above the {_MAX_SAFE_HOSPITAL_FLOOD_RISK:.0f} safety threshold.",
            ))
            continue

        route = find_safe_route(start_id, hospital.id, blocked_road_ids)
        if not route[0]:
            exclusions.append(HospitalExclusion(hospital_id=hospital.id, hospital_name=hospital.name, reason="Excluded because no safe route remains after flood-blocked roads are removed."))
            continue

        route_distance_km = route[1]
        travel_time_minutes = round((route_distance_km / _ESTIMATED_RESPONSE_SPEED_KPH) * 60, 1)
        capacity_ratio = available_capacity / hospital.capacity
        safety_score = (1 - flood_risk / 100) * 45
        capacity_score = capacity_ratio * 35
        distance_score = max(0.0, 20 - (route_distance_km * 4))
        suitability_score = round(safety_score + capacity_score + distance_score, 1)
        candidates.append(HospitalCandidate(
            hospital_id=hospital.id,
            hospital_name=hospital.name,
            zone_id=hospital.zone_id,
            route_distance_km=round(route_distance_km, 2),
            estimated_travel_time_minutes=travel_time_minutes,
            available_capacity=available_capacity,
            flood_risk_score=flood_risk,
            suitability_score=suitability_score,
            rationale=(f"Safe route is {route_distance_km:.2f} km; {available_capacity} beds are available; local flood risk is {flood_risk:.1f}/100."),
            reasoning_factors=[
                ReasoningFactor(factor="Flood safety", value=f"{flood_risk:.1f}/100 risk", weight=0.45, contribution=safety_score),
                ReasoningFactor(factor="Available capacity", value=f"{available_capacity} / {hospital.capacity} beds", weight=0.35, contribution=capacity_score),
                ReasoningFactor(factor="Safe-route distance", value=f"{route_distance_km:.2f} km", weight=0.20, contribution=distance_score),
            ],
        ))

    ranked_hospitals = sorted(candidates, key=lambda candidate: (-candidate.suitability_score, candidate.route_distance_km, candidate.hospital_id))
    if not ranked_hospitals:
        return HospitalRecommendationResponse(status="no_suitable_hospital", start_id=start_id, scenario=scenario.value, selected_hospital=None, ranked_hospitals=[], excluded_hospitals=exclusions, explanation="No hospital satisfies the current capacity, flood-risk, and safe-route constraints.")

    selected = ranked_hospitals[0]
    top_factor = max(selected.reasoning_factors, key=lambda factor: factor.contribution)
    return HospitalRecommendationResponse(
        status="success",
        start_id=start_id,
        scenario=scenario.value,
        selected_hospital=selected,
        ranked_hospitals=ranked_hospitals,
        excluded_hospitals=exclusions,
        explanation=(f"{selected.hospital_name} is selected with a {selected.suitability_score:.1f}/100 suitability score. "
                     f"The strongest score contribution is {top_factor.factor.lower()} ({top_factor.contribution:.1f} points), "
                     f"supported by a {selected.route_distance_km:.2f} km safe route and {selected.available_capacity} available beds."),
    )
