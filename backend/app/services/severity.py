"""Shared helpers that translate a severity score into operational priority."""

from __future__ import annotations

from typing import Literal

Priority = Literal["routine", "urgent", "critical"]

NEUTRAL_SEVERITY = 50.0  # reproduces the original fixed scoring weights


def priority_band(severity: float) -> Priority:
    """Map a 0-100 severity score to an operational priority band."""

    if severity < 35:
        return "routine"
    if severity < 65:
        return "urgent"
    return "critical"


def clamp_severity(severity: float | None) -> float:
    if severity is None:
        return NEUTRAL_SEVERITY
    return max(0.0, min(100.0, severity))
