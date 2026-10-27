from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ReasoningFactor(BaseModel):
    """One score component explaining a recommendation."""

    factor: str = Field(min_length=1)
    value: str = Field(min_length=1)
    weight: float = Field(ge=0, le=1)
    contribution: float


class FallbackOption(BaseModel):
    """Non-road option offered when no road-accessible resource exists.

    Straight-line distance is informational only; it is not a routable path.
    """

    mode: Literal["water_or_air_access"] = "water_or_air_access"
    target_id: str
    target_name: str
    straight_line_km: float = Field(ge=0)
    advice: str = Field(min_length=1)
