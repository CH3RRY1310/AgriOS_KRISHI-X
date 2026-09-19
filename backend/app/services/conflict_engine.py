"""Conflict detection for the first deterministic planning vertical slice."""

from __future__ import annotations

from app.schemas.farm import Conflict, IrrigationRecommendation, WeatherRecommendation


def detect_conflicts(
    weather_recommendation: WeatherRecommendation,
    irrigation_recommendation: IrrigationRecommendation,
    farm_id: str | None = None,
    field_id: str | None = None,
) -> list[Conflict]:
    """Capture deterministic conflicts between weather and irrigation recommendations."""
    if (
        weather_recommendation.recommendation == "WAIT"
        and irrigation_recommendation.recommendation == "IRRIGATE"
    ):
        return [
            Conflict(
                conflict_type="weather_irrigation",
                agents_involved=["Weather Agent", "Irrigation Agent"],
                description=(
                    "Weather recommends delaying irrigation because rain probability is high, "
                    "while irrigation recommends immediate watering based on low soil moisture."
                ),
                severity="medium",
                resolution="POSTPONE_IRRIGATION",
                rationale=(
                    "High rain probability should take precedence in this demo because rainfall "
                    "is expected to replenish soil moisture during the report window."
                ),
                resolved=True,
                farm_id=farm_id,
                field_id=field_id,
            )
        ]

    if (
        weather_recommendation.recommendation == "IRRIGATE"
        and irrigation_recommendation.recommendation == "WAIT"
    ):
        return [
            Conflict(
                conflict_type="weather_irrigation",
                agents_involved=["Weather Agent", "Irrigation Agent"],
                description=(
                    "Weather recommends irrigation while irrigation logic is waiting for more evidence."
                ),
                severity="low",
                resolution="REVIEW_FORECAST",
                rationale=(
                    "The recommendation is kept conservative until the forecast is re-evaluated."
                ),
                resolved=True,
                farm_id=farm_id,
                field_id=field_id,
            )
        ]

    return []
