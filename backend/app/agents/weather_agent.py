"""Deterministic weather recommendation agent for the farm digital twin."""

from __future__ import annotations

from app.schemas.farm import FarmState, WeatherRecommendation


def analyze_weather(
    farm_state: FarmState,
    farm_id: str | None = None,
    field_id: str | None = None,
) -> WeatherRecommendation:
    """Build a weather recommendation based on rain probability and forecast window."""
    rain_probability = farm_state.weather.rain_probability_percent
    forecast_window = farm_state.weather.forecast_window_hours

    if rain_probability >= 70:
        recommendation = "WAIT"
        irrigation_delay_hours = 8 if rain_probability >= 80 else 4
        confidence = 88.0
        rationale = (
            "High rain probability reduces the immediate need for irrigation. "
            "The recommendation is to postpone watering because rainfall is likely to "
            "provide replenishment within the forecast window."
        )
    else:
        recommendation = "IRRIGATE"
        irrigation_delay_hours = 0
        confidence = 72.0
        rationale = (
            "Current rainfall risk is low enough that irrigation may be needed to avoid "
            "soil moisture stress."
        )

    evidence = [
        f"rain_probability_percent={rain_probability}",
        f"forecast_window_hours={forecast_window}",
        "rainfall is expected to offset current irrigation demand",
    ]

    return WeatherRecommendation(
        rain_probability_percent=rain_probability,
        forecast_window_hours=forecast_window,
        recommendation=recommendation,
        irrigation_delay_hours=irrigation_delay_hours,
        confidence=confidence,
        rationale=rationale,
        evidence=evidence,
        farm_id=farm_id,
        field_id=field_id,
    )
