from __future__ import annotations

from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.routes.approvals import submit_demo_approval
from app.api.routes.scenarios import apply_demo_event
from app.schemas.farm import ApprovalRequest, ScenarioEventRequest
from app.services.audit import get_audit_events
from app.services.farm_state import get_demo_farm_state, replace_demo_farm_state
from app.services.scenarios import apply_scenario_event


DEMO_GOAL = "Maximize tomato yield while reducing water consumption by 20%"


def test_weather_event_updates_state_and_records_previous_value():
    original = get_demo_farm_state()
    try:
        event, updated = apply_scenario_event(
            ScenarioEventRequest(
                event_type="weather_change",
                attribute="rain_probability_percent",
                new_value=85,
                farm_id="farm-demo-001",
                field_id="field-demo-001",
            )
        )
        assert event.previous_value == original.weather.rain_probability_percent
        assert event.new_value == 85
        assert updated.weather.rain_probability_percent == 85
        assert event.farm_id == "farm-demo-001"
        assert event.field_id == "field-demo-001"
        assert event.simulation_only is True
        assert event.field_validated is False
        assert any(
            audit.event_type == "SCENARIO_EVENT"
            and audit.metadata.get("new_value") == 85
            for audit in get_audit_events()
        )
    finally:
        replace_demo_farm_state(original)


def test_arbitrary_state_mutation_is_rejected():
    with pytest.raises(ValidationError):
        ScenarioEventRequest(
            event_type="weather_change",
            attribute="water_available_liters",
            new_value=0,
        )


def test_field_aware_scenario_rejects_invalid_field():
    with pytest.raises(LookupError, match="field not found"):
        apply_scenario_event(
            ScenarioEventRequest(
                event_type="weather_change",
                attribute="rain_probability_percent",
                new_value=85,
                farm_id="farm-demo-001",
                field_id="field-missing",
            )
        )


def test_scenario_runs_existing_planning_and_preserves_simulation_safety():
    original = get_demo_farm_state()
    try:
        response = apply_demo_event(
            ScenarioEventRequest(
                event_type="weather_change",
                attribute="rain_probability_percent",
                new_value=85,
                farm_id="farm-demo-001",
                field_id="field-demo-001",
                goal=DEMO_GOAL,
            )
        )
        assert response.state.weather.rain_probability_percent == 85
        assert response.planning.weather.rain_probability_percent == 85
        assert response.planning.weather.recommendation == "WAIT"
        assert response.planning.irrigation.recommendation == "IRRIGATE"
        assert response.planning.conflicts[0].resolution == "POSTPONE_IRRIGATION"
        assert response.planning.verification.verified is True
        assert response.planning.impact.field_id == "field-demo-001"
        assert response.planning.impact.simulation_only is True
        assert response.planning.impact.field_validated is False
        assert response.planning.explainability.rain_probability_percent == 85
        assert response.planning.plan.status == "awaiting_approval"

        approval = submit_demo_approval(
            ApprovalRequest(
                decision="approve",
                plan_id=response.planning.plan.plan_id,
                farmer_note="Approve simulated weather scenario",
            )
        )
        assert approval.approval.status == "approved"
        assert approval.execution.status == "simulation_only"
        assert approval.execution.executed is False
    finally:
        replace_demo_farm_state(original)
