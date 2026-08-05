"""District-level API models."""

from __future__ import annotations

from pydantic import Field

from .entities import DomainModel, Facility, FloodZone, GeoPoint, RescueTeam, Road


class DistrictMetadata(DomainModel):
    """Static identity and map context for the fictional district."""

    id: str
    name: str
    region: str
    country: str
    timezone: str
    center: GeoPoint
    description: str


class DistrictProfile(DomainModel):
    """Complete static district data returned by the district endpoint."""

    metadata: DistrictMetadata
    zones: tuple[FloodZone, ...] = Field(min_length=1)
    roads: tuple[Road, ...] = Field(min_length=1)
    hospitals: tuple[Facility, ...]
    shelters: tuple[Facility, ...]
    rescue_teams: tuple[RescueTeam, ...]
