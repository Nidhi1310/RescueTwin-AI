"""FastAPI application entry point for RescueTwin AI."""

from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import public_router, router
from app.security import RequestGuardMiddleware
from app.services.district_service import get_district
from app.services.flood_prediction import get_prediction_service
from app.services.routing_service import build_routing_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("rescuetwin")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the routing graph and load/verify the ML artifact at startup (fail fast)."""
    build_routing_graph(get_district())
    get_prediction_service()
    if "*" in cors_origins:
        logger.warning("CORS allows every origin ('*'). Set RESCUETWIN_CORS_ORIGINS to your frontend URL in production.")
    if not os.getenv("RESCUETWIN_API_KEY"):
        logger.warning("RESCUETWIN_API_KEY is not set: the API is unauthenticated (acceptable for the demo only).")
    yield


cors_origins = [origin.strip() for origin in os.getenv("RESCUETWIN_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",") if origin.strip()]

app = FastAPI(
    title="RescueTwin AI API",
    version="0.1.0",
    description="Fictional flood-response decision-support backend.",
    lifespan=lifespan,
)


app.add_middleware(RequestGuardMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-API-Key"],
)


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


app.include_router(public_router, prefix="/api/v1")
app.include_router(router, prefix="/api/v1")
