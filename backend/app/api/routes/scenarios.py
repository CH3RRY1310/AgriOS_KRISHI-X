"""Controlled deterministic Scenario/Event Engine routes."""

from fastapi import APIRouter, HTTPException, status

from app.api.routes.planning import planning_demo
from app.schemas.farm import PlanningRequest, ScenarioEventRequest, ScenarioEventResponse
from app.services.scenarios import apply_scenario_event

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("/demo/events", response_model=ScenarioEventResponse)
def apply_demo_event(request: ScenarioEventRequest) -> ScenarioEventResponse:
    """Apply a supported demo event and run the existing planning pipeline."""
    try:
        event, state = apply_scenario_event(request)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    goal = request.goal or (state.goal.objective if state.goal is not None else "Maximize tomato yield while reducing water consumption by 20%")
    planning = planning_demo(
        PlanningRequest(
            goal=goal,
            farm_id=event.farm_id,
            field_id=event.field_id,
        )
    )
    return ScenarioEventResponse(event=event, state=state, planning=planning)
