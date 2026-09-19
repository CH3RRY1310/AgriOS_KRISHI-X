"""SQLite-backed audit trail for approval and replanning events."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import AuditEventDB, FarmDB, PlanDB
from app.services.farm_state import get_demo_farm_state
from app.schemas.farm import AuditEvent


def record_event(event_type: str, plan_id: str, description: str, metadata: dict | None = None) -> AuditEvent:
    """Persist a new audit event for the current demo session."""
    db = SessionLocal()
    try:
        farm = db.scalar(select(FarmDB).order_by(FarmDB.created_at.asc()))
        plan = db.scalar(select(PlanDB).where(PlanDB.external_plan_id == plan_id))
        event = AuditEventDB(
            farm_id=farm.id if farm else None,
            plan_id=plan.id if plan else None,
            event_type=event_type,
            message=description,
            event_metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return AuditEvent(
            event_id=str(event.id),
            event_type=event_type,
            timestamp=event.created_at,
            plan_id=plan_id,
            description=description,
            metadata=dict(event.event_metadata or {}),
        )
    finally:
        db.close()


def get_audit_events() -> list[AuditEvent]:
    """Return the audit timeline from SQLite."""
    db = SessionLocal()
    try:
        rows = db.execute(select(AuditEventDB).order_by(AuditEventDB.created_at.asc())).scalars().all()
        return [
            AuditEvent(
                event_id=str(row.id),
                event_type=row.event_type,
                timestamp=row.created_at,
                plan_id=row.plan.external_plan_id if row.plan else "",
                description=row.message,
                metadata=dict(row.event_metadata or {}),
            )
            for row in rows
        ]
    finally:
        db.close()


def clear_audit_events() -> None:
    """Reset the audit trail for a fresh demo run."""
    db = SessionLocal()
    try:
        db.query(AuditEventDB).delete()
        db.commit()
    finally:
        db.close()
