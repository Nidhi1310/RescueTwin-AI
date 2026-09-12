"""Request and response contracts for flood-severity predictions."""

from typing import Literal

from pydantic import BaseModel, Field


class FloodPredictionRequest(BaseModel):
    """Validated environmental inputs for a flood-severity prediction."""

    rainfall_mm: float = Field(ge=0, le=320)
    elevation_m: float = Field(ge=55, le=110)
    drainage_score: int = Field(ge=1, le=10)
    previous_water_level_m: float = Field(ge=0, le=4)


class FloodPredictionResponse(BaseModel):
    """A model prediction with confidence and a human-readable explanation."""

    predicted_flood_severity: float = Field(ge=0, le=100)
    confidence: Literal["low", "medium", "high"]
    explanation: str
