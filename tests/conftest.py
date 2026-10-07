"""Shared test configuration."""

import os

# The suite issues many requests from one client; disable the demo rate limiter and auth.
os.environ["RESCUETWIN_RATE_LIMIT_PER_MIN"] = "0"
os.environ.pop("RESCUETWIN_API_KEY", None)
os.environ.setdefault("RESCUETWIN_SIGNING_KEY", "test-signing-key")

import pytest


@pytest.fixture(autouse=True)
def _clean_dispatch_ledger():
    from app.services.dispatch_ledger import get_ledger

    get_ledger().clear()
    yield
    get_ledger().clear()
