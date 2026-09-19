"""Deterministic Scenario/Event Engine for controlled Farm Digital Twin simulation."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.database.connection import SessionLocal
from app.schemas.farm import FarmState, ScenarioEvent, ScenarioEventRequest
from app.services.audit import record_event
from app.services.fields import resolve_planning_scope
from app.services.farm_state import get_demo_farm_state, replace_demo_farm_state

DEMO_WEATHER_SCENARIO_ID = "scenario-demo-weather"


def apply_scenario_event(request: ScenarioEventRequest) -> tuple[ScenarioEvent, FarmState]:
    """Apply one explicitly supported event and persist the simulated FarmState."""
    if request.event_type != "weather_change" or request.attribute != "rain_probability_percent":
        raise ValueError("unsupported scenario event")

    db = SessionLocal()
    try:
        try:
            resolved_farm_id, selected_field = resolve_planning_scope(
                request.farm_id,
                request.field_id,
                db,
            )
        except (LookupError, ValueError):
            raise
    finally:
        db.close()

    if resolved_farm_id != "farm-demo-001":
        raise LookupError("FarmState simulation is only available for the demo farm")

    current_state = get_demo_farm_state()
    previous_value = current_state.weather.rain_probability_percent
    updated_weather = current_state.weather.model_copy(
        update={"rain_probability_percent": request.new_value}
    )
    updated_state = current_state.model_copy(update={"weather": updated_weather})
    persisted_state = replace_demo_farm_state(updated_state)

    field_id = selected_field.id if selected_field is not None else None
    event = ScenarioEvent(
        scenario_id=DEMO_WEATHER_SCENARIO_ID,
        event_id=f"event-{uuid4().hex[:12]}",
        event_type="weather_change",
        description=(
            "Simulated weather change updated rain probability in the Farm Digital Twin; "
            "no physical sensor or field condition was changed."
        ),
        attribute="rain_probability_percent",
        previous_value=previous_value,
        new_value=request.new_value,
        simulation_order=1,
        timestamp=datetime.now(UTC),
        farm_id=resolved_farm_id,
        field_id=field_id,
        simulation_only=True,
        field_validated=False,
    )
    record_event(
        "SCENARIO_EVENT",
        "",
        "Scenario event changed simulated rain probability.",
        {
            "scenario_id": event.scenario_id,
            "event_id": event.event_id,
            "attribute": event.attribute,
            "previous_value": event.previous_value,
            "new_value": event.new_value,
            "farm_id": event.farm_id,
            "field_id": event.field_id,
            "simulation_only": True,
            "field_validated": False,
        },
    )
    return event, persisted_state
