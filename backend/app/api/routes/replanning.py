"""Replanning endpoint for the simulation-only approval flow."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.farm import PlanReplanningRequest, PlanSummary
from app.services.approval import get_current_approval
from app.services.farm_state import get_demo_farm_state
from app.services.replanning import replan_after_approval

router = APIRouter(prefix="/replanning", tags=["replanning"])


@router.post(
    "/demo",
    response_model=PlanSummary,
    summary="Create the follow-up plan after a farmer decision",
    description="Validate the approval, compare with the requested plan, and generate a monitoring or safe follow-up plan.",
)
def replan_demo(request: PlanReplanningRequest) -> PlanSummary:
    """Generate a monitoring or safe follow-up plan after an approval decision."""
    farm_state = get_demo_farm_state()
    if farm_state.plan is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No current plan exists; create one first with POST /api/planning/demo.",
        )

    if request.plan_id != farm_state.plan.plan_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested plan_id does not match the current demo plan.",
        )

    approval = get_current_approval()
    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No approval exists for the requested plan; submit approval before replanning.",
        )

    if approval.plan_id != request.plan_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval does not belong to the requested plan.",
        )

    replanned = replan_after_approval(farm_state, farm_state.plan, approval)
    updated_state = farm_state.model_copy(update={"plan": replanned, "updated_at": farm_state.updated_at})
    from app.services.farm_state import replace_demo_farm_state

    replace_demo_farm_state(updated_state)
    return replanned
