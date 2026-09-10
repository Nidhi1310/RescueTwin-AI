"""FastAPI application entry point for RescueTwin AI."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import router
from app.services.district_service import get_district
from app.services.observability import REQUEST_ID_HEADER, create_request_id, get_logger, now
from app.services.routing_service import build_routing_graph


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the routing graph in-memory on startup."""
    build_routing_graph(get_district())
    app.state.ready = True
    yield
    app.state.ready = False


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    """Attach request IDs and emit one structured request-completion log."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or create_request_id()
        request.state.request_id = request_id
        started = now()
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = round((now() - started) * 1000, 2)
            logger.exception(
                "request_failed method=%s path=%s request_id=%s duration_ms=%s",
                request.method,
                request.url.path,
                request_id,
                elapsed_ms,
            )
            raise
        elapsed_ms = round((now() - started) * 1000, 2)
        response.headers[REQUEST_ID_HEADER] = request_id
        logger.info(
            "request_complete method=%s path=%s status=%s request_id=%s duration_ms=%s",
            request.method,
            request.url.path,
            response.status_code,
            request_id,
            elapsed_ms,
        )
        return response


app = FastAPI(
    title="RescueTwin AI API",
    version="0.1.0",
    description="Fictional flood-response decision-support backend.",
    lifespan=lifespan,
)
app.add_middleware(RequestObservabilityMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return a stable, client-friendly payload for malformed requests."""
    details = [
        {
            "location": list(error.get("loc", ())),
            "message": error.get("msg", "Invalid value."),
            "type": error.get("type", "validation_error"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed.",
            "details": details,
        },
    )


@app.get("/api/v1/readiness", tags=["system"])
def readiness_check() -> dict[str, str]:
    """Report whether startup initialization has completed."""
    if not getattr(app.state, "ready", False):
        return {"status": "not_ready"}
    return {"status": "ready"}


app.include_router(router, prefix="/api/v1")
