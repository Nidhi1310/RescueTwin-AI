"""FastAPI application entry point for RescueTwin AI."""

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="RescueTwin AI API",
    version="0.1.0",
    description="Fictional flood-response decision-support backend.",
)
app.include_router(router, prefix="/api/v1")
