"""Deterministic impact estimation and explainability for planning results."""

from __future__ import annotations

from app.schemas.farm import (
    Conflict,
    Explainability,
    FarmState,
    GoalAnalysis,
    ImpactEstimate,
    IrrigationRecommendation,
    PlanSummary,
    VerificationResult,
    WeatherRecommendation,
)


def _risk_for(verification: VerificationResult, conflicts: list[Conflict]) -> str:
    """Map existing verification evidence to a conservative risk level."""
    if not verification.verified:
        return "high"
    if any(not conflict.resolved for conflict in conflicts):
        return "high"
    if conflicts:
        return "medium"
    return "low"


def estimate_impact(
    farm_state: FarmState,
    plan: PlanSummary,
    goal_analysis: GoalAnalysis,
    weather_recommendation: WeatherRecommendation,
    irrigation_recommendation: IrrigationRecommendation,
    verification: VerificationResult,
    conflicts: list[Conflict],
) -> ImpactEstimate:
    """Estimate deterministic simulated impact from verified pipeline evidence."""
    risk = _risk_for(verification, conflicts)
    expected_water_change_percent = -plan.expected_water_reduction_percent
    expected_yield_change_percent = goal_analysis.target_yield_change_percent if verification.verified else 0.0
    confidence = min(
        99.0,
        max(
            0.0,
            (goal_analysis.confidence + weather_recommendation.confidence + irrigation_recommendation.confidence + verification.confidence) / 4,
        ),
    )
    return ImpactEstimate(
        farm_id=plan.farm_id,
        field_id=plan.field_id,
        water_impact=(
            f"Estimated water use change: {expected_water_change_percent:.0f}% "
            "relative to the current irrigation recommendation."
        ),
        yield_impact=(
            f"Estimated yield change: {expected_yield_change_percent:.0f}% "
            "against the stated goal target."
        ),
        expected_water_change_percent=expected_water_change_percent,
        expected_yield_change_percent=expected_yield_change_percent,
        risk=risk,
        confidence=confidence,
        simulation_only=True,
        field_validated=False,
        rationale=(
            "This is a deterministic simulation estimate derived from the current FarmState, "
            "agent recommendations, conflicts, and verification result. It is not a field-validated "
            "outcome and does not execute any physical action."
        ),
    )


def build_explainability(
    farm_state: FarmState,
    goal_text: str,
    goal_analysis: GoalAnalysis,
    weather_recommendation: WeatherRecommendation,
    irrigation_recommendation: IrrigationRecommendation,
    conflicts: list[Conflict],
    verification: VerificationResult,
    impact: ImpactEstimate,
) -> Explainability:
    """Build traceable explanation data from actual pipeline evidence."""
    return Explainability(
        farm_id=impact.farm_id,
        field_id=impact.field_id,
        goal=goal_text,
        crop=farm_state.crop.crop,
        growth_stage=farm_state.crop.growth_stage,
        soil_moisture_percent=farm_state.soil.soil_moisture_percent,
        temperature_celsius=farm_state.weather.temperature_celsius,
        humidity_percent=farm_state.weather.humidity_percent,
        rain_probability_percent=farm_state.weather.rain_probability_percent,
        water_available_liters=farm_state.water.available_liters,
        pest_risk_percent=farm_state.pest.risk_percent,
        irrigation_recommendation=irrigation_recommendation.recommendation,
        weather_recommendation=weather_recommendation.recommendation,
        conflict_resolution=[conflict.resolution for conflict in conflicts],
        verification_status=verification.status,
        confidence=impact.confidence,
        risk=impact.risk,
        supporting_stages=[
            "Goal Agent",
            "Weather Agent",
            "Irrigation Agent",
            "Conflict Engine",
            "Verification",
        ],
        simulation_only=True,
        field_validated=False,
    )
