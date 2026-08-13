"""Typed response models for rescue team allocation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TeamCandidate(BaseModel):
    """A rescue team that is available and reachable."""

    team_id: str
    team_name: str
    home_zone_id: str
    route_distance_km: float = Field(ge=0)
    estimated_travel_time_minutes: float = Field(ge=0)
    personnel_count: int = Field(gt=0)
    specialties: list[str]
    specialty_match: bool
    suitability_score: float = Field(ge=0, le=100)
    rationale: str


class TeamExclusion(BaseModel):
    """A rescue team excluded before final suitability ranking."""

    team_id: str
    team_name: str
    reason: str


class TeamAllocationResponse(BaseModel):
    """Frontend-ready selection, ranking, and exclusions for team dispatch."""

    status: Literal["success", "no_suitable_team"]
    incident_zone_id: str
    scenario: str
    required_specialty: str | None
    selected_team: TeamCandidate | None
    ranked_teams: list[TeamCandidate]
    excluded_teams: list[TeamExclusion]
    explanation: str
