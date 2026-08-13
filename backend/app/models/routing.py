"""Routing API models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from .entities import GeoPoint


class RouteResponse(BaseModel):
    """Result of a safe route computation."""

    status: Literal["success", "no_route_available"]
    distance_km: float
    path: list[GeoPoint]
