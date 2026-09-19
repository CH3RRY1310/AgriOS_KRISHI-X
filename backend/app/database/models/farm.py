from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FarmDB(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    external_id: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    area: Mapped[float] = mapped_column(nullable=False)
    crop: Mapped[str] = mapped_column(String(120), nullable=False)
    variety: Mapped[str | None] = mapped_column(String(120), nullable=True)
    growth_stage: Mapped[str] = mapped_column(String(120), nullable=False, default="unknown")
    health_status: Mapped[str] = mapped_column(String(80), nullable=False, default="healthy")
    soil_moisture_percent: Mapped[float] = mapped_column(nullable=False, default=0.0)
    soil_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    soil_temperature_celsius: Mapped[float | None] = mapped_column(nullable=True)
    weather_temperature_celsius: Mapped[float] = mapped_column(nullable=False, default=0.0)
    humidity_percent: Mapped[float] = mapped_column(nullable=False, default=0.0)
    rain_probability_percent: Mapped[float] = mapped_column(nullable=False, default=0.0)
    rainfall_mm: Mapped[float] = mapped_column(nullable=False, default=0.0)
    forecast_window_hours: Mapped[int] = mapped_column(nullable=False, default=0)
    weather_observed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    water_available_liters: Mapped[float] = mapped_column(nullable=False, default=0.0)
    minimum_reserve_liters: Mapped[float] = mapped_column(nullable=False, default=0.0)
    irrigation_available: Mapped[bool] = mapped_column(nullable=False, default=True)
    pest_risk_level: Mapped[str] = mapped_column(String(40), nullable=False, default="low")
    pest_risk_percent: Mapped[float] = mapped_column(nullable=False, default=0.0)
    primary_threat: Mapped[str | None] = mapped_column(String(120), nullable=True)
    nitrogen_status: Mapped[str] = mapped_column(String(50), nullable=False, default="adequate")
    phosphorus_status: Mapped[str] = mapped_column(String(50), nullable=False, default="adequate")
    potassium_status: Mapped[str] = mapped_column(String(50), nullable=False, default="watch")
    market_price_per_kg: Mapped[float] = mapped_column(nullable=False, default=0.0)
    market_currency: Mapped[str] = mapped_column(String(20), nullable=False, default="INR")
    market_name: Mapped[str] = mapped_column(String(120), nullable=False, default="Nashik APMC")
    market_observed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    goal_objective: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    goal_crop: Mapped[str | None] = mapped_column(String(120), nullable=True)
    goal_target_yield_change_percent: Mapped[float | None] = mapped_column(nullable=True)
    goal_water_reduction_percent: Mapped[float | None] = mapped_column(nullable=True)
    goal_priority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    goals: Mapped[list["GoalDB"]] = relationship(back_populates="farm", cascade="all, delete-orphan")
    plans: Mapped[list["PlanDB"]] = relationship(back_populates="farm", cascade="all, delete-orphan")
    audit_events: Mapped[list["AuditEventDB"]] = relationship(back_populates="farm", cascade="all, delete-orphan")
    fields: Mapped[list["FieldDB"]] = relationship(back_populates="farm", cascade="all, delete-orphan")
