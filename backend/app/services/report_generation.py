"""Service for generating comprehensive, human-readable incident reports."""

from __future__ import annotations

import textwrap

from app.models.decision_engine import DecisionEngineResponse
from app.models.report_generation import IncidentReportResponse


def generate_incident_report(decision: DecisionEngineResponse) -> IncidentReportResponse:
    """Generate a deterministic incident report from decision-engine output."""
    severity_score = decision.prediction.predicted_flood_severity
    confidence = decision.prediction.confidence.upper()
    scenario = decision.simulation.scenario.upper()
    affected_zones_count = len(decision.simulation.zone_impacts)
    blocked_roads_count = len(decision.simulation.blocked_roads)
    blocked_roads_list = ", ".join(r.road_id for r in decision.simulation.blocked_roads) or "None"

    damage_str = ""
    if decision.damage_assessment:
        dmg = decision.damage_assessment
        damage_str = (
            f"### Damage Assessment (from {dmg.filename})\n"
            f"- **Level**: {dmg.damage_level.value.upper()}\n"
            f"- **Confidence**: {dmg.confidence}%\n"
            f"- **Rationale**: {dmg.rationale}\n\n"
        )

    hosp_rec = decision.hospital_recommendation
    hosp_str = "No hospital available."
    if hosp_rec.status == "success" and hosp_rec.selected_hospital:
        h = hosp_rec.selected_hospital
        hosp_str = (
            f"**{h.hospital_name}**\n"
            f"  - Distance: {h.route_distance_km} km\n"
            f"  - Estimated Travel: {h.estimated_travel_time_minutes} mins\n"
            f"  - Capacity: {h.available_capacity} available\n"
            f"  - Reasoning: {h.rationale}\n"
        )

    shelt_rec = decision.shelter_recommendation
    shelt_str = "No shelter available."
    if shelt_rec.status == "success" and shelt_rec.selected_shelter:
        s = shelt_rec.selected_shelter
        shelt_str = (
            f"**{s.shelter_name}**\n"
            f"  - Distance: {s.route_distance_km} km\n"
            f"  - Estimated Travel: {s.estimated_travel_time_minutes} mins\n"
            f"  - Capacity: {s.available_capacity} spots\n"
            f"  - Reasoning: {s.rationale}\n"
        )

    team_rec = decision.team_allocation
    team_str = "No team available."
    if team_rec.status == "success" and team_rec.selected_team:
        t = team_rec.selected_team
        specs = ", ".join(t.specialties) if t.specialties else "None"
        team_str = (
            f"**{t.team_name}** (Specialty: {specs})\n"
            f"  - Distance from incident: {t.route_distance_km} km\n"
            f"  - Estimated Arrival: {t.estimated_travel_time_minutes} mins\n"
            f"  - Reasoning: {t.rationale}\n"
        )

    report = textwrap.dedent(f"""\
        RescueTwin AI Incident Report
        **Incident Zone:** {decision.incident_zone_id}

        ## Situation Summary
        Based on real-time metrics, the predicted flood severity is **{severity_score}/100** ({confidence} confidence), resulting in a **{scenario}** flood scenario.
        - **Affected Zones:** {affected_zones_count}
        - **Blocked Roads:** {blocked_roads_count} ({blocked_roads_list})

        {damage_str}## Operational Recommendations

        ### 1. Recommended Hospital
        {hosp_str}
        ### 2. Recommended Shelter
        {shelt_str}
        ### 3. Rescue Team Assignment
        {team_str}
        ---
        *Report generated automatically by RescueTwin AI Decision Engine.*
    """).strip()

    return IncidentReportResponse(report_content=report)
