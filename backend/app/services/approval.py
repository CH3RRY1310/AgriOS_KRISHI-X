"""SQLite-backed approval gate for the simulation-only farmer review workflow."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import ApprovalDB, PlanDB
from app.schemas.farm import ApprovalRequest, ApprovalState
from app.services.audit import record_event


def submit_approval(approval_request: ApprovalRequest, plan) -> ApprovalState:
    """Persist the farmer's explicit approval decision in SQLite for this demo."""
    if approval_request.decision not in {"approve", "modify", "reject"}:
        raise ValueError("approval decision must be approve, modify, or reject")

    if approval_request.decision == "modify" and not approval_request.modified_action:
        raise ValueError("modified_action is required when decision is modify")

    if plan is None:
        raise ValueError("plan is required to submit approval")

    if approval_request.plan_id and approval_request.plan_id != plan.plan_id:
        raise ValueError("plan_id does not match the current demo plan")

    if approval_request.decision == "approve":
        status = "approved"
        rationale = "Farmer approved the simulation plan and requested that monitoring continue."
    elif approval_request.decision == "modify":
        status = "modified"
        rationale = (
            "Farmer requested a modification to the current simulation plan; "
            "the modified action is recorded but no physical action is executed."
        )
    else:
        status = "rejected"
        rationale = "Farmer rejected the simulation plan; no physical action will be executed."

    db = SessionLocal()
    try:
        plan_row = db.scalar(select(PlanDB).where(PlanDB.external_plan_id == plan.plan_id))
        if plan_row is None:
            raise ValueError("plan not found in persistence layer")
        approval_row = db.scalar(select(ApprovalDB).where(ApprovalDB.plan_id == plan_row.id))
        if approval_row is None:
            approval_row = ApprovalDB(plan_id=plan_row.id)
            db.add(approval_row)

        approval_row.decision = approval_request.decision
        approval_row.status = status
        approval_row.execution_mode = "simulation_only"
        approval_row.executed = False
        approval_row.farmer_note = approval_request.farmer_note
        approval_row.modified_action = approval_request.modified_action
        approval_row.rationale = rationale
        approval_row.created_at = datetime.now(timezone.utc)
        db.commit()
        approval = ApprovalState(
            status=status,
            decision=approval_request.decision,
            plan_id=plan.plan_id,
            farmer_note=approval_request.farmer_note,
            modified_action=approval_request.modified_action,
            decided_at=approval_row.created_at,
            approved_by="farmer",
            rationale=rationale,
            note=approval_request.farmer_note,
        )
    finally:
        db.close()

    record_event(
        "APPROVAL_SUBMITTED",
        approval.plan_id,
        f"Farmer {approval.decision} the demo plan.",
        {"decision": approval.decision, "executed": False},
    )
    return approval


def get_current_approval() -> ApprovalState | None:
    """Return the current approval decision persisted in SQLite."""
    db = SessionLocal()
    try:
        row = db.execute(select(ApprovalDB).order_by(ApprovalDB.created_at.desc())).scalars().first()
        if row is None:
            return None
        plan_row = db.get(PlanDB, row.plan_id)
        return ApprovalState(
            status=row.status,
            decision=row.decision,
            plan_id=plan_row.external_plan_id if plan_row else row.plan_id.__str__(),
            farmer_note=row.farmer_note,
            modified_action=row.modified_action,
            decided_at=row.created_at,
            approved_by="farmer",
            rationale=row.rationale or "Simulation data; no action is executed.",
            note=row.farmer_note,
        )
    finally:
        db.close()


def clear_approval() -> None:
    """Reset the in-database approval state for a fresh demo run."""
    db = SessionLocal()
    try:
        db.query(ApprovalDB).delete()
        db.commit()
    finally:
        db.close()
