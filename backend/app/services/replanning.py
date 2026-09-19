"""Deterministic replanning service for approval-driven monitoring scenarios."""

from __future__ import annotations

from app.schemas.farm import ApprovalState, FarmState, PlanSummary
from app.services.audit import record_event


def replan_after_approval(
    farm_state: FarmState,
    original_plan: PlanSummary,
    approval: ApprovalState,
) -> PlanSummary:
    """Create the follow-up simulation-only plan after a farmer decision."""
    if approval.plan_id != original_plan.plan_id:
        raise ValueError("approval plan_id must match the original plan")

    if approval.decision == "approve":
        status = "monitoring"
        decision = "MONITOR_APPROVED_PLAN"
        actions = [
            "monitor rainfall trend",
            "reassess soil moisture after 8 hours",
            "keep simulation state unchanged",
        ]
        rationale = (
            "Farmer approved the original plan. The simulation enters a monitoring-only state; "
            "no physical action is executed."
        )
    elif approval.decision == "modify":
        status = "monitoring"
        decision = "MONITOR_MODIFIED_PLAN"
        actions = [
            "incorporate farmer modification",
            "reassess soil moisture after 8 hours",
            "continue simulation-only review",
        ]
        rationale = (
            "Farmer modification was incorporated into the plan, but the system remains simulation-only and does not execute field actions."
        )
        if approval.modified_action:
            actions.insert(0, approval.modified_action)
    elif approval.decision == "reject":
        status = "rejected"
        decision = "SAFE_FOLLOW_UP"
        actions = [
            "retain conservative monitoring mode",
            "do not execute irrigation plan",
            "schedule reassessment after 8 hours",
        ]
        rationale = (
            "Farmer rejected the current plan. The follow-up state is a safe monitoring-only alternative without physical execution."
        )
    else:
        raise ValueError("unsupported approval decision")

    replanned = PlanSummary(
        plan_id=original_plan.plan_id,
        status=status,
        decision=decision,
        actions=actions,
        expected_water_saved_liters=original_plan.expected_water_saved_liters,
        expected_water_reduction_percent=original_plan.expected_water_reduction_percent,
        confidence=min(99.0, max(50.0, original_plan.confidence - 5.0)),
        rationale=rationale,
        farm_id=original_plan.farm_id,
        field_id=original_plan.field_id,
        goal=original_plan.goal,
    )
    record_event(
        "PLAN_REPLANNED",
        replanned.plan_id,
        "Plan changed into monitoring state after the farmer decision.",
        {"decision": approval.decision, "status": replanned.status, "executed": False},
    )
    return replanned
