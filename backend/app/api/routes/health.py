"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Response returned by the service health check."""

    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse, summary="Check API health")
def health_check() -> HealthResponse:
    """Return service metadata without contacting external dependencies."""
    return HealthResponse(
        status="ok",
        service=settings.application_name,
        version=settings.api_version,
    )
