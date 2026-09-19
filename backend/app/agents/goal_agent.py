"""Deterministic goal analysis agent for the Farm Digital Twin."""

from __future__ import annotations

from app.schemas.farm import FarmState, GoalAnalysis


def analyze_goal(
    goal_text: str,
    farm_state: FarmState,
    farm_id: str | None = None,
    field_id: str | None = None,
) -> GoalAnalysis:
    """Convert the user goal into a small deterministic structured objective."""
    normalized = (goal_text or "").lower()

    crop = farm_state.crop.crop.lower() if farm_state.crop else "unknown"
    if "tomato" in normalized:
        crop = "tomato"

    if "maximize" in normalized and "yield" in normalized:
        objective = "maximize_yield"
        target_yield_change_percent = 15
    elif "yield" in normalized:
        objective = "maximize_yield"
        target_yield_change_percent = 10
    else:
        objective = "optimize_productivity"
        target_yield_change_percent = 5

    if "reduce" in normalized and "water" in normalized:
        if "20%" in normalized or "20 percent" in normalized:
            water_reduction_percent = 20
        elif "15%" in normalized or "15 percent" in normalized:
            water_reduction_percent = 15
        else:
            water_reduction_percent = 10
    else:
        water_reduction_percent = (
            farm_state.goal.water_reduction_percent if farm_state.goal else 10
        )

    priority = "high" if "maximize" in normalized or "reduce" in normalized else "medium"

    confidence = 92.0 if crop == "tomato" else 68.0
    rationale = (
        "The goal is mapped to a tomato-focused yield optimization target with a "
        "deterministic water reduction policy suitable for the demo simulation."
    )

    return GoalAnalysis(
        objective=objective,
        crop=crop,
        target_yield_change_percent=target_yield_change_percent,
        water_reduction_percent=water_reduction_percent,
        priority=priority,
        confidence=confidence,
        rationale=rationale,
        farm_id=farm_id,
        field_id=field_id,
    )
