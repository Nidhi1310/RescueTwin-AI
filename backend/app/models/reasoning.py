"""Shared models for transparent recommendation scoring."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReasoningFactor(BaseModel):
    """One normalized factor contributing to a recommendation score."""

    factor: str = Field(min_length=1)
    value: str = Field(min_length=1)
    weight: float = Field(ge=0, le=1)
    contribution: float
