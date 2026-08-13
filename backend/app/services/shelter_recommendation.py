"""Explainable shelter selection using capacity, flood risk, and safe routing."""

from __future__ import annotations

from app.models.district import DistrictProfile
from app.models.entities import FacilityType
from app.models.shelter_recommendation import (
    ShelterCandidate,
    ShelterExclusion,
    ShelterRecommendationResponse,
)
from app.models.simulation import RainfallScenario
from app.services.flood_simulation import simulate_flood
from app.services.routing_service import build_routing_graph, find_safe_route

_MAX_SAFE_SHELTER_FLOOD_RISK = 50.0
_ESTIMATED_EVAC_SPEED_KPH = 15.0


def recommend_shelter(
    district: DistrictProfile,
    start_id: str,
    scenario: RainfallScenario,
) -> ShelterRecommendationResponse:
    """Rank reachable shelters for an evacuation using explicit suitability factors."""

    build_routing_graph(district)
    simulation = simulate_flood(district, scenario)
    flood_risk_by_zone = {impact.zone_id: impact.severity_score for impact in simulation.zone_impacts}
    blocked_road_ids = {road.road_id for road in simulation.blocked_roads}
    
    candidates: list[ShelterCandidate] = []
    exclusions: list[ShelterExclusion] = []

    for facility in district.shelters:
        if facility.type != FacilityType.SHELTER:
            continue
            
        available_capacity = facility.capacity - facility.current_occupancy
        if available_capacity <= 0:
            exclusions.append(ShelterExclusion(
                shelter_id=facility.id,
                shelter_name=facility.name,
                reason="Excluded because no capacity is currently available.",
            ))
            continue

        flood_risk = flood_risk_by_zone[facility.zone_id]
        if flood_risk >= _MAX_SAFE_SHELTER_FLOOD_RISK:
            exclusions.append(ShelterExclusion(
                shelter_id=facility.id,
                shelter_name=facility.name,
                reason=(
                    f"Excluded because local flood risk is {flood_risk:.1f}/100, above the "
                    f"{_MAX_SAFE_SHELTER_FLOOD_RISK:.0f} safety threshold."
                ),
            ))
            continue

        route, route_distance_km = find_safe_route(start_id, facility.id, blocked_road_ids)
        if not route:
            exclusions.append(ShelterExclusion(
                shelter_id=facility.id,
                shelter_name=facility.name,
                reason="Excluded because no safe route remains after flood-blocked roads are removed.",
            ))
            continue

        travel_time_minutes = round((route_distance_km / _ESTIMATED_EVAC_SPEED_KPH) * 60, 1)
        capacity_ratio = available_capacity / facility.capacity
        safety_score = (1 - flood_risk / 100) * 50
        capacity_score = capacity_ratio * 30
        distance_score = max(0.0, 20 - (route_distance_km * 3))
        suitability_score = round(safety_score + capacity_score + distance_score, 1)
        
        candidates.append(ShelterCandidate(
            shelter_id=facility.id,
            shelter_name=facility.name,
            zone_id=facility.zone_id,
            route_distance_km=round(route_distance_km, 2),
            estimated_travel_time_minutes=travel_time_minutes,
            available_capacity=available_capacity,
            flood_risk_score=flood_risk,
            suitability_score=suitability_score,
            rationale=(
                f"Safe route is {route_distance_km:.2f} km; {available_capacity} spots are available; "
                f"local flood risk is {flood_risk:.1f}/100."
            ),
        ))

    ranked_shelters = sorted(
        candidates,
        key=lambda c: (-c.suitability_score, c.route_distance_km, c.shelter_id),
    )
    
    if not ranked_shelters:
        return ShelterRecommendationResponse(
            status="no_suitable_shelter",
            start_id=start_id,
            scenario=scenario.value,
            selected_shelter=None,
            ranked_shelters=[],
            excluded_shelters=exclusions,
            explanation="No shelter satisfies the current capacity, flood-risk, and safe-route constraints.",
        )

    selected = ranked_shelters[0]
    return ShelterRecommendationResponse(
        status="success",
        start_id=start_id,
        scenario=scenario.value,
        selected_shelter=selected,
        ranked_shelters=ranked_shelters,
        excluded_shelters=exclusions,
        explanation=(
            f"{selected.shelter_name} is the highest-ranked suitable shelter after considering "
            "safe-route distance, local flood risk, and available capacity."
        ),
    )
