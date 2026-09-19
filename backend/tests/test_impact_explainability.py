from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.routes.approvals import submit_demo_approval
from app.api.routes.planning import planning_demo
from app.schemas.farm import ApprovalRequest, PlanningRequest
from app.services.approval import clear_approval
from app.services.audit import clear_audit_events
from app.services.farm_state import get_demo_farm_state
from app.services.impact import estimate_impact
from app.services.planning import generate_plan
from app.agents.goal_agent import analyze_goal
from app.agents.weather_agent import analyze_weather
from app.agents.irrigation_agent import analyze_irrigation
from app.services.conflict_engine import detect_conflicts
from app.services.verification import verify_plan


DEMO_GOAL = "Maximize tomato yield while reducing water consumption by 20%"


def test_legacy_planning_returns_impact_and_explainability():
    response = planning_demo(PlanningRequest(goal=DEMO_GOAL))

    assert response.plan.status == "awaiting_approval"
    assert response.impact is not None
    assert response.explainability is not None
    assert response.impact.simulation_only is True
    assert response.impact.field_validated is False
    assert response.explainability.simulation_only is True
    assert response.explainability.field_validated is False


def test_field_aware_impact_and_explainability_retain_context_and_evidence():
    response = planning_demo(
        PlanningRequest(
            goal=DEMO_GOAL,
            farm_id="farm-demo-001",
            field_id="field-demo-001",
        )
    )

    assert response.impact.farm_id == "farm-demo-001"
    assert response.impact.field_id == "field-demo-001"
    assert response.explainability.farm_id == "farm-demo-001"
    assert response.explainability.field_id == "field-demo-001"
    assert response.explainability.soil_moisture_percent == 31
    assert response.explainability.rain_probability_percent == 82
    assert response.explainability.water_available_liters == 28400
    assert response.explainability.weather_recommendation == "WAIT"
    assert response.explainability.irrigation_recommendation == "IRRIGATE"
    assert response.explainability.conflict_resolution == ["POSTPONE_IRRIGATION"]
    assert response.explainability.verification_status == "verified"
    assert response.explainability.supporting_stages == [
        "Goal Agent",
        "Weather Agent",
        "Irrigation Agent",
        "Conflict Engine",
        "Verification",
    ]


def test_impact_estimation_is_deterministic():
    farm_state = get_demo_farm_state()
    goal_analysis = analyze_goal(DEMO_GOAL, farm_state)
    weather = analyze_weather(farm_state)
    irrigation = analyze_irrigation(farm_state)
    conflicts = detect_conflicts(weather, irrigation)
    verification = verify_plan(farm_state, goal_analysis, weather, irrigation, conflicts)
    plan = generate_plan(DEMO_GOAL, farm_state)

    first = estimate_impact(farm_state, plan, goal_analysis, weather, irrigation, verification, conflicts)
    second = estimate_impact(farm_state, plan, goal_analysis, weather, irrigation, verification, conflicts)

    assert first == second
    assert first.expected_water_change_percent == -plan.expected_water_reduction_percent
    assert first.expected_yield_change_percent == goal_analysis.target_yield_change_percent
    assert first.risk == "medium"
    assert first.confidence == 88.0


def test_impact_does_not_bypass_approval():
    clear_approval()
    clear_audit_events()
    response = planning_demo(
        PlanningRequest(
            goal=DEMO_GOAL,
            farm_id="farm-demo-001",
            field_id="field-demo-001",
        )
    )

    assert response.plan.status == "awaiting_approval"
    approval = submit_demo_approval(
        ApprovalRequest(decision="approve", plan_id=response.plan.plan_id)
    )
    assert approval.execution.status == "simulation_only"
    assert approval.execution.executed is False
