"""FastAPI application entry point for AgriOS KRISHI-X."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.approvals import router as approvals_router
from app.api.routes.audit import router as audit_router
from app.api.routes.farms import router as farms_router
from app.api.routes.fields import router as fields_router
from app.api.routes.health import router as health_router
from app.api.routes.planning import router as planning_router
from app.api.routes.replanning import router as replanning_router
from app.api.routes.scenarios import router as scenarios_router
from app.core.config import settings
from app.database.connection import init_db

app = FastAPI(
    title=settings.application_name,
    description="Backend foundation for the AgriOS KRISHI-X agricultural operations platform.",
    version=settings.api_version,
)


@app.on_event("startup")
def startup_event() -> None:
    """Initialize the local SQLite schema and demo data when the API boots."""
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(farms_router, prefix="/api")
app.include_router(fields_router, prefix="/api")
app.include_router(planning_router, prefix="/api")
app.include_router(approvals_router, prefix="/api")
app.include_router(replanning_router, prefix="/api")
app.include_router(scenarios_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
