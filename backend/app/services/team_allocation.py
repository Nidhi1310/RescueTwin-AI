"""Explainable team allocation based on availability, specialization, route distance and severity."""

from __future__ import annotations

from app.models.district import DistrictProfile
from app.models.entities import TeamStatus
from app.models.reasoning import FallbackOption
from app.models.simulation import RainfallScenario
from app.models.team_allocation import (
    TeamAllocationResponse,
    TeamCandidate,
    TeamExclusion,
)
from app.services.flood_simulation import simulate_flood
from app.services.routing_service import find_safe_route, location_of, straight_line_km
from app.services.severity import clamp_severity

_ESTIMATED_RESPONSE_SPEED_KPH = 40.0
_WATER_SPECIALTIES = frozenset({"boat_rescue", "swift_water", "air_rescue"})


def normalize_specialty(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def known_specialties(district: DistrictProfile) -> list[str]:
    return sorted({normalize_specialty(s) for team in district.rescue_teams for s in team.specialties})


def _fallback_team(
    district: DistrictProfile,
    incident_zone_id: str,
    required: str | None,
    reserved: frozenset[str],
) -> FallbackOption | None:
    """Nearest available water/air-capable team, ignoring road closures (informational only)."""

    incident_location = location_of(incident_zone_id, district)
    if incident_location is None:
        return None
    best: tuple[float, object] | None = None
    for team in district.rescue_teams:
        specialties = {normalize_specialty(s) for s in team.specialties}
        if team.status != TeamStatus.AVAILABLE or team.id in reserved:
            continue
        if not specialties & _WATER_SPECIALTIES:
            continue
        if required and required not in specialties:
            continue
        distance = straight_line_km(team.location, incident_location)
        if best is None or distance < best[0]:
            best = (distance, team)
    if best is None:
        return None
    distance, team = best
    return FallbackOption(
        target_id=team.id,
        target_name=team.name,
        straight_line_km=round(distance, 2),
        advice=(
            f"No team can reach {incident_zone_id} by road. {team.name} has water-rescue capability and is "
            f"{distance:.1f} km away in a straight line. This is NOT a routed path: confirm boat/air access "
            "before dispatching."
        ),
    )


def allocate_team(
    district: DistrictProfile,
    incident_zone_id: str,
    scenario: RainfallScenario,
    required_specialty: str | None = None,
    incident_severity: float | None = None,
    unavailable_team_ids: frozenset[str] = frozenset(),
) -> TeamAllocationResponse:
    """Rank available rescue teams for an incident using explicit suitability factors.

    ``incident_severity`` (0-100, normally the ML prediction) shifts weight from
    travel distance toward team size as severity rises.  The three weights always
    total 100.  ``required_specialty`` is a hard constraint.
    """

    simulation = simulate_flood(district, scenario)
    blocked_road_ids = {road.road_id for road in simulation.blocked_roads}
    required = normalize_specialty(required_specialty) if required_specialty else None
    severity = clamp_severity(incident_severity)
    distance_max = 60.0 - 0.2 * severity
    personnel_max = 10.0 + 0.2 * severity
    specialty_max = 30.0

    candidates: list[TeamCandidate] = []
    exclusions: list[TeamExclusion] = []

    for team in district.rescue_teams:
        specialties = {normalize_specialty(s) for s in team.specialties}
        if team.id in unavailable_team_ids:
            exclusions.append(TeamExclusion(
                team_id=team.id, team_name=team.name,
                reason="Excluded because it is already committed to another incident.",
            ))
            continue
        if team.status != TeamStatus.AVAILABLE:
            exclusions.append(TeamExclusion(
                team_id=team.id, team_name=team.name,
                reason=f"Excluded because current status is '{team.status.value}'.",
            ))
            continue
        if required and required not in specialties:
            exclusions.append(TeamExclusion(
                team_id=team.id, team_name=team.name,
                reason=f"Excluded because it lacks the required specialty '{required}'.",
            ))
            continue

        route, route_distance_km = find_safe_route(team.id, incident_zone_id, blocked_road_ids, district)
        if not route:
            exclusions.append(TeamExclusion(
                team_id=team.id, team_name=team.name,
                reason="Excluded because no safe route remains after flood-blocked roads are removed.",
            ))
            continue

        travel_time_minutes = round((route_distance_km / _ESTIMATED_RESPONSE_SPEED_KPH) * 60, 1)
        distance_score = max(0.0, distance_max - route_distance_km * 2)
        specialty_score = specialty_max
        personnel_score = min(personnel_max, team.personnel_count * 2.0 * personnel_max / 20.0)
        suitability_score = round(distance_score + specialty_score + personnel_score, 1)

        reasoning_factors = [
            {
                "factor": "Safe-route distance",
                "value": f"{route_distance_km:.2f} km",
                "weight": round(distance_max / 100, 2),
                "contribution": round(distance_score, 1),
            },
            {
                "factor": "Specialty match",
                "value": f"Matched ({required})" if required else "No specialty required",
                "weight": round(specialty_max / 100, 2),
                "contribution": round(specialty_score, 1),
            },
            {
                "factor": "Personnel availability",
                "value": f"{team.personnel_count} personnel",
                "weight": round(personnel_max / 100, 2),
                "contribution": round(personnel_score, 1),
            },
        ]
        candidates.append(TeamCandidate(
            team_id=team.id,
            team_name=team.name,
            home_zone_id=team.home_zone_id,
            route_distance_km=round(route_distance_km, 2),
            estimated_travel_time_minutes=travel_time_minutes,
            personnel_count=team.personnel_count,
            specialties=list(team.specialties),
            specialty_match=True,
            suitability_score=suitability_score,
            rationale=(
                f"Distance is {route_distance_km:.2f} km. "
                f"Specialty requirement: {required or 'none'}. "
                f"Personnel available: {team.personnel_count}. "
                f"Incident severity {severity:.0f}/100 weights team size at {personnel_max:.0f}% of the score."
            ),
            reasoning_factors=reasoning_factors,
        ))

    ranked_teams = sorted(candidates, key=lambda c: (-c.suitability_score, c.route_distance_km, c.team_id))

    if not ranked_teams:
        fallback = _fallback_team(district, incident_zone_id, required, unavailable_team_ids)
        if required and required not in known_specialties(district):
            reason = (
                f"No team in the district offers the specialty '{required}'. "
                f"Available specialties: {', '.join(known_specialties(district))}."
            )
        else:
            reason = "No available team could be allocated for this incident (all busy, committed, lacking the required specialty, or unreachable by road)."
        if fallback:
            reason += " " + fallback.advice
        else:
            reason += " Request external boat/air rescue assets."
        return TeamAllocationResponse(
            status="no_suitable_team",
            incident_zone_id=incident_zone_id,
            scenario=scenario.value,
            required_specialty=required,
            incident_severity=incident_severity,
            selected_team=None,
            ranked_teams=[],
            excluded_teams=exclusions,
            explanation=reason,
            fallback=fallback,
        )

    selected = ranked_teams[0]
    top_factor = max(selected.reasoning_factors, key=lambda factor: factor.contribution)
    return TeamAllocationResponse(
        status="success",
        incident_zone_id=incident_zone_id,
        scenario=scenario.value,
        required_specialty=required,
        incident_severity=incident_severity,
        selected_team=selected,
        ranked_teams=ranked_teams,
        excluded_teams=exclusions,
        explanation=(
            f"{selected.team_name} is the highest-ranked available team with a "
            f"{selected.suitability_score:.1f}/100 suitability score. The strongest contributing "
            f"factor is {top_factor.factor.lower()} ({top_factor.value})."
        ),
    )
