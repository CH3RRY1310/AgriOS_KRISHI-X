"""Farmer approval endpoint for the simulation-only decision gate."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.farm import ApprovalRequest, ApprovalResponse, ExecutionState
from app.services.approval import get_current_approval, submit_approval
from app.services.farm_state import get_demo_farm_state
from app.services.planning import generate_plan

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post(
    "/demo",
    response_model=ApprovalResponse,
    summary="Submit a farmer approval decision",
    description="Store the simulation-only approval state and ensure the request is valid before returning the result.",
)
def submit_demo_approval(request: ApprovalRequest) -> ApprovalResponse:
    """Validate and store a farmer approval decision for the current demo plan."""
    farm_state = get_demo_farm_state()
    current_plan = farm_state.plan
    if current_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current demo plan exists; create one via POST /api/planning/demo first.",
        )

    if request.plan_id != current_plan.plan_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested plan_id does not match the current demo plan.",
        )

    if request.decision == "modify" and not request.modified_action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="modified_action is required when decision is modify.",
        )

    approval = submit_approval(request, current_plan)
    return ApprovalResponse(
        approval=approval,
        execution=ExecutionState(status="simulation_only", executed=False),
    )


@router.get(
    "/demo",
    response_model=ApprovalResponse | None,
    summary="Read the current demo approval state",
    description="Read the most recent approval decision for the current demo plan.",
)
def get_demo_approval() -> ApprovalResponse | None:
    """Return the most recent approval state as a simulation-only execution response."""
    approval = get_current_approval()
    if approval is None:
        return None
    return ApprovalResponse(
        approval=approval,
        execution=ExecutionState(status="simulation_only", executed=False),
    )
