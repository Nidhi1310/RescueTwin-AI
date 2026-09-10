"""FastAPI application entry point for RescueTwin AI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import settings
from app.services.district_service import get_district
from app.services.routing_service import build_routing_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the routing graph in-memory on startup."""
    build_routing_graph(get_district())
    yield


app = FastAPI(
    title="RescueTwin AI API",
    version="0.1.0",
    description="Fictional flood-response decision-support backend.",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Normalize FastAPI validation failures into a stable client-facing shape."""
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "message": "Request validation failed.", "details": exc.errors()},
    )


app.include_router(router, prefix=settings.api_prefix)
