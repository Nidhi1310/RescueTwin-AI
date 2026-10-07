"""HMAC signing so reports can only be generated from bundles this server issued."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import secrets

from app.models.decision_engine import DecisionEngineResponse

logger = logging.getLogger("rescuetwin.security")

_configured_key = os.getenv("RESCUETWIN_SIGNING_KEY")
if not _configured_key:
    logger.warning(
        "RESCUETWIN_SIGNING_KEY is not set: using a random per-process key. "
        "Decision bundles will not verify after a restart or on another worker."
    )
_KEY = _configured_key.encode() if _configured_key else secrets.token_bytes(32)


def _canonical(decision: DecisionEngineResponse) -> bytes:
    payload = decision.model_dump(mode="json", exclude={"signature"})
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def sign_decision(decision: DecisionEngineResponse) -> str:
    return hmac.new(_KEY, _canonical(decision), hashlib.sha256).hexdigest()


def verify_decision(decision: DecisionEngineResponse) -> bool:
    if not decision.signature:
        return False
    return hmac.compare_digest(decision.signature, sign_decision(decision))
