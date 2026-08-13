"""Explainable team allocation based on availability, specialization, and route distance."""

from __future__ import annotations

from app.models.district import DistrictProfile
from app.models.entities import TeamStatus
from app.models.simulation import RainfallScenario
from app.models.team_allocation import (
    TeamAllocationResponse,
    TeamCandidate,
    TeamExclusion,
)
from app.services.flood_simulation import simulate_flood
from app.services.routing_service import build_routing_graph, find_safe_route

_ESTIMATED_RESPONSE_SPEED_KPH = 40.0


def allocate_team(
    district: DistrictProfile,
    incident_zone_id: str,
    scenario: RainfallScenario,
    required_specialty: str | None = None,
) -> TeamAllocationResponse:
    """Rank available rescue teams for an incident using explicit suitability factors."""

    build_routing_graph(district)
    simulation = simulate_flood(district, scenario)
    blocked_road_ids = {road.road_id for road in simulation.blocked_roads}
    
    candidates: list[TeamCandidate] = []
    exclusions: list[TeamExclusion] = []

    for team in district.rescue_teams:
        if team.status != TeamStatus.AVAILABLE:
            exclusions.append(TeamExclusion(
                team_id=team.id,
                team_name=team.name,
                reason=f"Excluded because current status is '{team.status.value}'.",
            ))
            continue

        route, route_distance_km = find_safe_route(team.id, incident_zone_id, blocked_road_ids)
        if not route:
            exclusions.append(TeamExclusion(
                team_id=team.id,
                team_name=team.name,
                reason="Excluded because no safe route remains after flood-blocked roads are removed.",
            ))
            continue

        travel_time_minutes = round((route_distance_km / _ESTIMATED_RESPONSE_SPEED_KPH) * 60, 1)
        
        # Scoring logic (0 to 100)
        # Distance score: Max 50 points, degrades over distance (e.g., 0 points if > 25km)
        distance_score = max(0.0, 50 - (route_distance_km * 2))
        
        # Specialty score: 30 points if required specialty matches or isn't specified
        specialty_match = False
        if required_specialty:
            specialty_match = required_specialty in team.specialties
            specialty_score = 30.0 if specialty_match else 0.0
        else:
            specialty_match = True
            specialty_score = 30.0
            
        # Personnel score: Up to 20 points for larger teams (max score at 10+ personnel)
        personnel_score = min(20.0, team.personnel_count * 2.0)
        
        suitability_score = round(distance_score + specialty_score + personnel_score, 1)
        
        candidates.append(TeamCandidate(
            team_id=team.id,
            team_name=team.name,
            home_zone_id=team.home_zone_id,
            route_distance_km=round(route_distance_km, 2),
            estimated_travel_time_minutes=travel_time_minutes,
            personnel_count=team.personnel_count,
            specialties=list(team.specialties),
            specialty_match=specialty_match,
            suitability_score=suitability_score,
            rationale=(
                f"Distance is {route_distance_km:.2f} km. "
                f"Specialty match: {'Yes' if specialty_match else 'No'}. "
                f"Personnel available: {team.personnel_count}."
            ),
        ))

    # Rank by suitability, then distance, then ID
    ranked_teams = sorted(
        candidates,
        key=lambda c: (-c.suitability_score, c.route_distance_km, c.team_id),
    )

    if not ranked_teams:
        return TeamAllocationResponse(
            status="no_suitable_team",
            incident_zone_id=incident_zone_id,
            scenario=scenario.value,
            required_specialty=required_specialty,
            selected_team=None,
            ranked_teams=[],
            excluded_teams=exclusions,
            explanation="No available team could be allocated for this incident (all either busy or unreachable).",
        )

    selected = ranked_teams[0]
    return TeamAllocationResponse(
        status="success",
        incident_zone_id=incident_zone_id,
        scenario=scenario.value,
        required_specialty=required_specialty,
        selected_team=selected,
        ranked_teams=ranked_teams,
        excluded_teams=exclusions,
        explanation=(
            f"{selected.team_name} is the highest-ranked available team after considering "
            "distance, safe-route accessibility, personnel count, and operational specialties."
        ),
    )
