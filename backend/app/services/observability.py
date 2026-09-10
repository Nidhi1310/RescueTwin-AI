"""Structured request observability helpers for RescueTwin AI."""

from __future__ import annotations

import logging
import time
from uuid import uuid4

REQUEST_ID_HEADER = "X-Request-ID"
LOGGER_NAME = "rescuetwin.api"


def get_logger() -> logging.Logger:
    """Return the application logger used by API observability."""
    return logging.getLogger(LOGGER_NAME)


def create_request_id() -> str:
    """Create a short, traceable identifier for one HTTP request."""
    return uuid4().hex


def now() -> float:
    """Return a monotonic timestamp suitable for latency measurements."""
    return time.perf_counter()
