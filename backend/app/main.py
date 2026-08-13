"""FastAPI application entry point for RescueTwin AI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
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
app.include_router(router, prefix="/api/v1")
