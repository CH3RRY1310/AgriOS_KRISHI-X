"""Deterministic verification service for the planning workflow."""

from __future__ import annotations

from app.schemas.farm import (
    Conflict,
    FarmState,
    GoalAnalysis,
    IrrigationRecommendation,
    VerificationResult,
    WeatherRecommendation,
)


def verify_plan(
    farm_state: FarmState,
    goal_analysis: GoalAnalysis,
    weather_recommendation: WeatherRecommendation,
    irrigation_recommendation: IrrigationRecommendation,
    conflicts: list[Conflict],
) -> VerificationResult:
    """Check safety constraints for the generated plan and fail closed if violated."""
    safety_checks: dict[str, bool] = {}

    safety_checks["farm_state_complete"] = all(
        [
            farm_state is not None,
            farm_state.farm is not None,
            farm_state.crop is not None,
            farm_state.soil is not None,
            farm_state.weather is not None,
            farm_state.water is not None,
            goal_analysis is not None,
        ]
    )
    safety_checks["water_availability_non_negative"] = farm_state.water.available_liters >= 0
    if irrigation_recommendation.recommendation == "IRRIGATE":
        irrigation_water_need = irrigation_recommendation.water_required_liters
        safety_checks["water_reserve_safe"] = (
            farm_state.water.available_liters - irrigation_water_need >= farm_state.water.minimum_reserve_liters
        )
    else:
        safety_checks["water_reserve_safe"] = (
            farm_state.water.available_liters >= farm_state.water.minimum_reserve_liters
        )
    safety_checks["conflicts_resolved"] = all(conflict.resolved for conflict in conflicts)
    safety_checks["weather_data_available"] = bool(
        farm_state.weather.rain_probability_percent is not None
        and farm_state.weather.forecast_window_hours is not None
    )
    safety_checks["simulation_only"] = True

    verified = all(safety_checks.values())
    status = "verified" if verified else "failed"
    confidence = 96.0 if verified else 36.0

    rationale = (
        "The plan passes deterministic safety checks for farm completeness, reserve policy, "
        "weather availability, and conflict resolution. The recommendation remains simulation-only "
        "and does not execute any real farm action."
    )
    if not verified:
        rationale = (
            "The plan fails a deterministic safety check, so the recommendation is not approved for execution. "
            "This is a fail-safe path, not a real-world action trigger."
        )

    return VerificationResult(
        status=status,
        verified=verified,
        confidence=confidence,
        safety_checks=safety_checks,
        rationale=rationale,
        summary=("Plan verified and simulation-only." if verified else "Plan failed verification."),
        farm_id=goal_analysis.farm_id,
        field_id=goal_analysis.field_id,
    )
