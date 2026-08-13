"""Typed response models for the incident report generation API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class IncidentReportResponse(BaseModel):
    """The generated incident report and metadata."""

    report_content: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
