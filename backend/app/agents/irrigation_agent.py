"""Deterministic irrigation recommendation agent for the farm digital twin."""

from __future__ import annotations

from app.schemas.farm import FarmState, IrrigationRecommendation


def analyze_irrigation(
    farm_state: FarmState,
    farm_id: str | None = None,
    field_id: str | None = None,
) -> IrrigationRecommendation:
    """Generate a simulation-only irrigation recommendation from soil and water state."""
    moisture = farm_state.soil.soil_moisture_percent
    available_liters = farm_state.water.available_liters
    minimum_reserve = farm_state.water.minimum_reserve_liters

    if moisture <= 35 and available_liters >= minimum_reserve + 1800:
        recommendation = "IRRIGATE"
        recommended_duration_minutes = 18
        water_required_liters = 1800
        confidence = 76.0
        rationale = (
            "Simulation/demo irrigation rule: soil moisture is low enough to justify a short "
            "irrigation session, and water availability remains above the minimum reserve."
        )
    else:
        recommendation = "NOT_IRRIGATE"
        recommended_duration_minutes = 0
        water_required_liters = 0
        confidence = 70.0
        rationale = (
            "Simulation/demo logic does not recommend irrigation because reserves are too low or "
            "soil moisture is not critical enough."
        )

    evidence = [
        f"soil_moisture_percent={moisture}",
        f"available_liters={available_liters}",
        f"minimum_reserve_liters={minimum_reserve}",
        "this recommendation is simulation-only and is not a real-world irrigation prescription",
    ]

    return IrrigationRecommendation(
        soil_moisture_percent=moisture,
        recommended_duration_minutes=recommended_duration_minutes,
        recommendation=recommendation,
        water_required_liters=water_required_liters,
        confidence=confidence,
        rationale=rationale,
        evidence=evidence,
        farm_id=farm_id,
        field_id=field_id,
    )
