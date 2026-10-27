"""Authentication, rate limiting, upload limits and audit logging."""

from __future__ import annotations

import hmac
import logging
import os
import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

audit_logger = logging.getLogger("rescuetwin.audit")

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
_MULTIPART_OVERHEAD_BYTES = 64 * 1024


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Require ``X-API-Key`` when ``RESCUETWIN_API_KEY`` is configured (read per request)."""

    expected = os.getenv("RESCUETWIN_API_KEY")
    if not expected:
        return
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Missing or invalid API key.")


def client_ip(request: Request) -> str:
    if os.getenv("RESCUETWIN_TRUST_PROXY") == "1":
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def audit(request: Request, event: str, **fields: object) -> None:
    details = " ".join(f"{key}={value}" for key, value in fields.items())
    audit_logger.info("event=%s client=%s %s", event, client_ip(request), details)


async def read_limited_upload(file: UploadFile, limit: int = MAX_UPLOAD_BYTES) -> bytes:
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(status_code=413, detail=f"Upload exceeds the {limit // (1024 * 1024)} MB limit.")
    return data


class RequestGuardMiddleware(BaseHTTPMiddleware):
    """Reject oversized bodies early and apply a per-client sliding-window rate limit."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._last_prune = time.monotonic()

    async def dispatch(self, request: Request, call_next):
        length = request.headers.get("content-length")
        if length and length.isdigit() and int(length) > MAX_UPLOAD_BYTES + _MULTIPART_OVERHEAD_BYTES:
            return JSONResponse(status_code=413, content={"error": "payload_too_large", "message": "Request body is too large."})

        limit = int(os.getenv("RESCUETWIN_RATE_LIMIT_PER_MIN", "300") or 0)
        if limit > 0 and not request.url.path.endswith("/health"):
            now = time.monotonic()
            window = self._hits[client_ip(request)]
            while window and now - window[0] > 60:
                window.popleft()
            if len(window) >= limit:
                retry = max(1, int(60 - (now - window[0])))
                return JSONResponse(
                    status_code=429,
                    headers={"Retry-After": str(retry)},
                    content={"error": "rate_limited", "message": f"Too many requests. Retry in {retry}s."},
                )
            window.append(now)
            if now - self._last_prune > 300:  # bound memory: drop idle clients
                self._last_prune = now
                for key in [k for k, v in self._hits.items() if not v or now - v[-1] > 60]:
                    del self._hits[key]
        return await call_next(request)
