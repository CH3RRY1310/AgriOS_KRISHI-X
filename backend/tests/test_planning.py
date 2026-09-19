"""Executable validation for the deterministic planning workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.farm import Conflict, FarmState
from app.services.conflict_engine import detect_conflicts
from app.services.farm_state import get_demo_farm_state
from app.services.planning import generate_plan
from app.services.verification import verify_plan
from app.agents.goal_agent import analyze_goal
from app.agents.weather_agent import analyze_weather
from app.agents.irrigation_agent import analyze_irrigation


def main() -> None:
    """Run deterministic planning assertions without pytest."""
    farm_state = get_demo_farm_state()

    goal_analysis = analyze_goal(
        "Maximize tomato yield while reducing water consumption by 20%.",
        farm_state,
    )
    assert goal_analysis.objective == "maximize_yield"
    assert goal_analysis.crop == "tomato"
    assert goal_analysis.target_yield_change_percent == 15
    assert goal_analysis.water_reduction_percent == 20
    assert goal_analysis.priority == "high"

    weather = analyze_weather(farm_state)
    assert weather.recommendation == "WAIT"
    assert weather.irrigation_delay_hours == 8

    irrigation = analyze_irrigation(farm_state)
    assert irrigation.recommendation == "IRRIGATE"
    assert irrigation.recommended_duration_minutes == 18

    conflicts = detect_conflicts(weather, irrigation)
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == "weather_irrigation"
    assert conflicts[0].severity == "medium"
    assert conflicts[0].resolution == "POSTPONE_IRRIGATION"
    assert conflicts[0].resolved is True

    verification = verify_plan(
        farm_state,
        goal_analysis,
        weather,
        irrigation,
        conflicts,
    )
    assert verification.verified is True
    assert verification.status == "verified"

    plan = generate_plan(
        "Maximize tomato yield while reducing water consumption by 20%.",
        farm_state,
    )
    assert plan.status == "awaiting_approval"
    assert plan.decision == "POSTPONE_IRRIGATION"

    unsafe_state = farm_state.model_copy(deep=True)
    unsafe_state.water.available_liters = -5
    unsafe_verification = verify_plan(
        unsafe_state,
        goal_analysis,
        weather,
        irrigation,
        conflicts,
    )
    assert unsafe_verification.verified is False

    json_text = json.dumps(plan.model_dump())
    payload = json.loads(json_text)
    assert payload["decision"] == "POSTPONE_IRRIGATION"

    assert isinstance(Conflict.model_validate({
        "conflict_type": "weather_irrigation",
        "agents_involved": ["Weather Agent", "Irrigation Agent"],
        "description": "Rain probability is high while soil moisture is low.",
        "severity": "medium",
        "resolution": "POSTPONE_IRRIGATION",
        "rationale": "High rain probability should take precedence.",
        "resolved": True,
    }), Conflict)

    print("planning workflow checks passed")


if __name__ == "__main__":
    main()
