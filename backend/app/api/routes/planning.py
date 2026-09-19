"""Planning workflow endpoint for the first deterministic agentic vertical slice."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from datetime import datetime, timezone

from app.agents.goal_agent import analyze_goal
from app.agents.irrigation_agent import analyze_irrigation
from app.agents.weather_agent import analyze_weather
from app.database.connection import SessionLocal
from app.schemas.farm import GoalState, PlanningContext, PlanningRequest, PlanningResponse
from app.services.conflict_engine import detect_conflicts
from app.services.farm_state import get_demo_farm_state, replace_demo_farm_state
from app.services.impact import build_explainability, estimate_impact
from app.services.planning import generate_plan
from app.services.verification import verify_plan
from app.services.fields import resolve_planning_scope

router = APIRouter(prefix="/planning", tags=["planning"])


@router.post(
    "/demo",
    response_model=PlanningResponse,
    summary="Run the deterministic planning workflow for the demo farm",
    description="Execute the goal, weather, irrigation, conflict detection, verification, and plan summary flow.",
)
def planning_demo(request: PlanningRequest) -> PlanningResponse:
    """Generate the structured vertical-slice planning output for the deterministic demo state."""
    db = SessionLocal()
    try:
        try:
            resolved_farm_id, selected_field = resolve_planning_scope(request.farm_id, request.field_id, db)
        except LookupError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    finally:
        db.close()

    farm_state = get_demo_farm_state()
    selected_field_id = selected_field.id if selected_field else None
    goal_analysis = analyze_goal(request.goal, farm_state, resolved_farm_id, selected_field_id)
    weather = analyze_weather(farm_state, resolved_farm_id, selected_field_id)
    irrigation = analyze_irrigation(farm_state, resolved_farm_id, selected_field_id)
    conflicts = detect_conflicts(weather, irrigation, resolved_farm_id, selected_field_id)
    verification = verify_plan(
        farm_state,
        goal_analysis,
        weather,
        irrigation,
        conflicts,
    )
    plan = generate_plan(request.goal, farm_state, resolved_farm_id, selected_field_id)
    impact = estimate_impact(
        farm_state,
        plan,
        goal_analysis,
        weather,
        irrigation,
        verification,
        conflicts,
    )
    explainability = build_explainability(
        farm_state,
        request.goal,
        goal_analysis,
        weather,
        irrigation,
        conflicts,
        verification,
        impact,
    )
    goal_state = farm_state.goal or GoalState(
        objective=request.goal,
        crop=goal_analysis.crop,
        target_yield_change_percent=goal_analysis.target_yield_change_percent,
        water_reduction_percent=goal_analysis.water_reduction_percent,
        priority=goal_analysis.priority,
    )
    stored_state = farm_state.model_copy(
        update={
            "goal": goal_state.model_copy(
                update={"farm_id": resolved_farm_id, "field_id": selected_field_id}
            ),
            "plan": plan,
            "verification": verification,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    replace_demo_farm_state(stored_state)

    return PlanningResponse(
        goal_analysis=goal_analysis,
        weather=weather,
        irrigation=irrigation,
        conflicts=conflicts,
        verification=verification,
        plan=plan,
        impact=impact,
        explainability=explainability,
        context=(
            PlanningContext(
                farm_id=resolved_farm_id,
                field_id=selected_field.id,
                field_name=selected_field.name,
                crop=selected_field.crop,
                variety=selected_field.variety,
                growth_stage=selected_field.growth_stage,
                area_acres=selected_field.area_acres,
            )
            if selected_field is not None
            else None
        ),
    )
