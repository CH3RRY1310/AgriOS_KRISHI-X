"""Explicit orchestration for the first deterministic planning vertical slice."""

from __future__ import annotations

from uuid import uuid4

from app.agents.goal_agent import analyze_goal
from app.agents.irrigation_agent import analyze_irrigation
from app.agents.weather_agent import analyze_weather
from app.schemas.farm import FarmState, PlanSummary
from app.services.audit import record_event
from app.services.conflict_engine import detect_conflicts
from app.services.verification import verify_plan


def generate_plan(
    goal_text: str,
    farm_state: FarmState,
    farm_id: str | None = None,
    field_id: str | None = None,
) -> PlanSummary:
    """Run the goal, weather, irrigation, conflict, and verification sequence deterministically."""
    goal_analysis = analyze_goal(goal_text, farm_state, farm_id, field_id)
    weather_recommendation = analyze_weather(farm_state, farm_id, field_id)
    irrigation_recommendation = analyze_irrigation(farm_state, farm_id, field_id)
    conflicts = detect_conflicts(weather_recommendation, irrigation_recommendation, farm_id, field_id)
    verification = verify_plan(
        farm_state,
        goal_analysis,
        weather_recommendation,
        irrigation_recommendation,
        conflicts,
    )

    if verification.verified and conflicts:
        decision = "POSTPONE_IRRIGATION"
        actions = [
            "postpone irrigation",
            "monitor rainfall",
            "reassess after forecast window",
        ]
        expected_water_saved_liters = max(
            0.0,
            irrigation_recommendation.water_required_liters * 0.9,
        )
        expected_water_reduction_percent = min(
            100.0,
            max(
                0.0,
                goal_analysis.water_reduction_percent,
            ),
        )
        rationale = (
            "Rainfall risk is high enough to defer irrigation, and the deterministic verification "
            "confirms the plan remains safe and simulation-only."
        )
        status = "awaiting_approval"
        confidence = min(99.0, (weather_recommendation.confidence + irrigation_recommendation.confidence + verification.confidence) / 3)
    else:
        decision = "REVIEW_PLAN"
        actions = [
            "reassess irrigation trigger",
            "verify weather forecast",
            "consult farm constraints",
        ]
        expected_water_saved_liters = 0.0
        expected_water_reduction_percent = 0.0
        rationale = (
            "The deterministic safety checks did not approve the current configuration, so the plan is "
            "kept in a review state."
        )
        status = "needs_revision"
        confidence = 0.0

    plan = PlanSummary(
        plan_id=uuid4().hex,
        status=status,
        decision=decision,
        actions=actions,
        expected_water_saved_liters=expected_water_saved_liters,
        expected_water_reduction_percent=expected_water_reduction_percent,
        confidence=confidence,
        rationale=rationale,
        farm_id=farm_id,
        field_id=field_id,
        goal=goal_text,
    )
    record_event(
        "PLAN_CREATED",
        plan.plan_id,
        "Planning workflow created a demo plan.",
        {"goal": goal_text, "farm_id": farm_id, "field_id": field_id},
    )
    return plan
