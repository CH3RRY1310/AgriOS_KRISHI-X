"""Read-only audit endpoint for the approval and replanning workflow."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.farm import AuditEvent
from app.services.audit import get_audit_events

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get(
    "/demo",
    response_model=list[AuditEvent],
    summary="Get the current in-memory audit timeline",
    description="Return the current in-memory audit events recorded for the demo workflow.",
)
def get_demo_audit() -> list[AuditEvent]:
    """Return all recorded in-memory audit events."""
    return get_audit_events()
