from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import ApprovalDB, FarmDB, FieldDB, GoalDB, PlanDB
from app.schemas.farm import (
    ApprovalState,
    CropState,
    Farm,
    FarmState,
    GoalState,
    MarketState,
    NutrientState,
    PestState,
    SoilState,
    WaterState,
    WeatherState,
    PlanSummary,
)

DEMO_FARM_EXTERNAL_ID = "farm-demo-001"


def make_demo_farm_state() -> FarmState:
    """Return the deterministic tomato farm baseline currently used by the app."""
    return FarmState(
        farm=Farm(
            id=DEMO_FARM_EXTERNAL_ID,
            name="Shinde Farm / Block A",
            location="Nashik, Maharashtra",
            area_acres=11.86,
        ),
        crop=CropState(
            crop="tomato",
            variety="Sahyadri",
            growth_stage="flowering",
            health_status="healthy",
        ),
        soil=SoilState(
            soil_moisture_percent=31,
            soil_type="sandy loam",
            temperature_celsius=24.5,
        ),
        weather=WeatherState(
            temperature_celsius=27.0,
            humidity_percent=68,
            rain_probability_percent=82,
            rainfall_mm=3.2,
            forecast_window_hours=48,
            observed_at=datetime(2026, 9, 18, 9, 30, tzinfo=timezone.utc),
        ),
        water=WaterState(
            available_liters=28400,
            minimum_reserve_liters=8000,
            irrigation_available=True,
        ),
        pest=PestState(
            risk_level="low",
            risk_percent=18,
            primary_threat="early blight",
        ),
        nutrient=NutrientState(
            nitrogen_status="adequate",
            phosphorus_status="adequate",
            potassium_status="watch",
        ),
        market=MarketState(
            crop="tomato",
            price_per_kg=36.0,
            currency="INR",
            market_name="Nashik APMC",
            observed_at=datetime(2026, 9, 18, 9, 15, tzinfo=timezone.utc),
        ),
        goal=GoalState(
            objective="Maximize tomato yield while reducing water consumption by 20%",
            crop="tomato",
            target_yield_change_percent=5,
            water_reduction_percent=20,
            priority="high",
        ),
        approval=ApprovalState(
            status="pending",
            decision="approve",
            plan_id="",
            farmer_note="Simulation data; no action is executed.",
            rationale="Simulation data; no action is executed.",
            note="Simulation data; no action is executed.",
        ),
        updated_at=datetime(2026, 9, 18, 9, 30, tzinfo=timezone.utc),
    )


def _build_goal_state(goal_row: GoalDB | None) -> GoalState | None:
    if goal_row is None:
        return None
    return GoalState(
        objective=goal_row.objective or goal_row.text,
        crop=goal_row.crop,
        target_yield_change_percent=goal_row.target_yield_change_percent,
        water_reduction_percent=goal_row.water_reduction_percent,
        priority=goal_row.priority or "high",
        farm_id=goal_row.farm.external_id if goal_row.farm else None,
        field_id=goal_row.field.external_id if goal_row.field else None,
    )


def _build_plan_summary(plan_row: PlanDB | None) -> PlanSummary | None:
    if plan_row is None:
        return None
    return PlanSummary(
        plan_id=plan_row.external_plan_id,
        status=plan_row.status,
        decision=plan_row.decision,
        actions=[],
        expected_water_saved_liters=plan_row.expected_water_saved_liters,
        expected_water_reduction_percent=plan_row.expected_water_reduction_percent,
        confidence=plan_row.confidence,
        rationale=plan_row.rationale or "No rationale stored.",
        farm_id=plan_row.farm.external_id if plan_row.farm else None,
        field_id=plan_row.field.external_id if plan_row.field else None,
        goal=plan_row.goal.text if plan_row.goal else None,
    )


def _build_approval_state(approval_row: ApprovalDB | None) -> ApprovalState | None:
    if approval_row is None:
        return None
    return ApprovalState(
        status=approval_row.status,
        decision=approval_row.decision,
        plan_id=str(approval_row.plan_id),
        farmer_note=approval_row.farmer_note,
        modified_action=approval_row.modified_action,
        decided_at=approval_row.created_at,
        approved_by="farmer",
        rationale=approval_row.rationale or "Simulation data; no action is executed.",
        note=approval_row.farmer_note,
    )


def ensure_demo_farm_exists(session: Session | None = None) -> FarmDB:
    """Create the deterministic demo farm only once for local SQLite development."""
    owns_session = session is None
    db = session or SessionLocal()
    try:
        existing = db.scalar(select(FarmDB).where(FarmDB.external_id == DEMO_FARM_EXTERNAL_ID))
        if existing is not None:
            return existing

        state = make_demo_farm_state()
        farm = FarmDB(
            external_id=state.farm.id,
            name=state.farm.name,
            location=state.farm.location,
            area=state.farm.area_acres,
            crop=state.crop.crop,
            variety=state.crop.variety,
            growth_stage=state.crop.growth_stage,
            health_status=state.crop.health_status,
            soil_moisture_percent=state.soil.soil_moisture_percent,
            soil_type=state.soil.soil_type,
            soil_temperature_celsius=state.soil.temperature_celsius,
            weather_temperature_celsius=state.weather.temperature_celsius,
            humidity_percent=state.weather.humidity_percent,
            rain_probability_percent=state.weather.rain_probability_percent,
            rainfall_mm=state.weather.rainfall_mm,
            forecast_window_hours=state.weather.forecast_window_hours,
            weather_observed_at=state.weather.observed_at,
            water_available_liters=state.water.available_liters,
            minimum_reserve_liters=state.water.minimum_reserve_liters,
            irrigation_available=state.water.irrigation_available,
            pest_risk_level=state.pest.risk_level,
            pest_risk_percent=state.pest.risk_percent,
            primary_threat=state.pest.primary_threat,
            nitrogen_status=state.nutrient.nitrogen_status,
            phosphorus_status=state.nutrient.phosphorus_status,
            potassium_status=state.nutrient.potassium_status,
            market_price_per_kg=state.market.price_per_kg,
            market_currency=state.market.currency,
            market_name=state.market.market_name,
            market_observed_at=state.market.observed_at,
            goal_objective=state.goal.objective if state.goal else None,
            goal_crop=state.goal.crop if state.goal else None,
            goal_target_yield_change_percent=state.goal.target_yield_change_percent if state.goal else None,
            goal_water_reduction_percent=state.goal.water_reduction_percent if state.goal else None,
            goal_priority=state.goal.priority if state.goal else None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
        return farm
    finally:
        if owns_session:
            db.close()


def load_demo_farm_state(session: Session | None = None) -> FarmState:
    """Read the current persisted demo farm state from SQLite as an API-safe FarmState."""
    owns_session = session is None
    db = session or SessionLocal()
    try:
        farm_row = ensure_demo_farm_exists(db)
        goal_row = db.scalar(
            select(GoalDB).where(GoalDB.farm_id == farm_row.id).order_by(GoalDB.created_at.desc())
        )
        plan_row = db.scalar(
            select(PlanDB).where(PlanDB.farm_id == farm_row.id).order_by(PlanDB.created_at.desc())
        )
        approval_row = None
        if plan_row is not None:
            approval_row = db.scalar(
                select(ApprovalDB).where(ApprovalDB.plan_id == plan_row.id).order_by(ApprovalDB.created_at.desc())
            )

        state = make_demo_farm_state()
        rebuilt = state.model_copy(
            update={
                "farm": Farm(
                    id=farm_row.external_id or str(farm_row.id),
                    name=farm_row.name,
                    location=farm_row.location,
                    area_acres=farm_row.area,
                ),
                "crop": CropState(
                    crop=farm_row.crop,
                    variety=farm_row.variety,
                    growth_stage=farm_row.growth_stage,
                    health_status=farm_row.health_status,
                ),
                "soil": SoilState(
                    soil_moisture_percent=farm_row.soil_moisture_percent,
                    soil_type=farm_row.soil_type,
                    temperature_celsius=farm_row.soil_temperature_celsius,
                ),
                "weather": WeatherState(
                    temperature_celsius=farm_row.weather_temperature_celsius,
                    humidity_percent=farm_row.humidity_percent,
                    rain_probability_percent=farm_row.rain_probability_percent,
                    rainfall_mm=farm_row.rainfall_mm,
                    forecast_window_hours=farm_row.forecast_window_hours,
                    observed_at=farm_row.weather_observed_at or state.weather.observed_at,
                ),
                "water": WaterState(
                    available_liters=farm_row.water_available_liters,
                    minimum_reserve_liters=farm_row.minimum_reserve_liters,
                    irrigation_available=farm_row.irrigation_available,
                ),
                "pest": PestState(
                    risk_level=farm_row.pest_risk_level,
                    risk_percent=farm_row.pest_risk_percent,
                    primary_threat=farm_row.primary_threat,
                ),
                "nutrient": NutrientState(
                    nitrogen_status=farm_row.nitrogen_status,
                    phosphorus_status=farm_row.phosphorus_status,
                    potassium_status=farm_row.potassium_status,
                ),
                "market": MarketState(
                    crop=farm_row.crop,
                    price_per_kg=farm_row.market_price_per_kg,
                    currency=farm_row.market_currency,
                    market_name=farm_row.market_name,
                    observed_at=farm_row.market_observed_at or state.market.observed_at,
                ),
                "goal": _build_goal_state(goal_row),
                "approval": _build_approval_state(approval_row),
                "plan": _build_plan_summary(plan_row),
                "updated_at": farm_row.updated_at or datetime.now(timezone.utc),
            }
        )
        return rebuilt
    finally:
        if owns_session:
            db.close()


def persist_demo_farm_state(state: FarmState, session: Session | None = None) -> FarmState:
    """Persist the current demo farm state to SQLite and return the stored state."""
    owns_session = session is None
    db = session or SessionLocal()
    try:
        farm_row = ensure_demo_farm_exists(db)

        farm_row.name = state.farm.name
        farm_row.location = state.farm.location
        farm_row.area = state.farm.area_acres
        farm_row.crop = state.crop.crop
        farm_row.variety = state.crop.variety
        farm_row.growth_stage = state.crop.growth_stage
        farm_row.health_status = state.crop.health_status
        farm_row.soil_moisture_percent = state.soil.soil_moisture_percent
        farm_row.soil_type = state.soil.soil_type
        farm_row.soil_temperature_celsius = state.soil.temperature_celsius
        farm_row.weather_temperature_celsius = state.weather.temperature_celsius
        farm_row.humidity_percent = state.weather.humidity_percent
        farm_row.rain_probability_percent = state.weather.rain_probability_percent
        farm_row.rainfall_mm = state.weather.rainfall_mm
        farm_row.forecast_window_hours = state.weather.forecast_window_hours
        farm_row.weather_observed_at = state.weather.observed_at
        farm_row.water_available_liters = state.water.available_liters
        farm_row.minimum_reserve_liters = state.water.minimum_reserve_liters
        farm_row.irrigation_available = state.water.irrigation_available
        farm_row.pest_risk_level = state.pest.risk_level
        farm_row.pest_risk_percent = state.pest.risk_percent
        farm_row.primary_threat = state.pest.primary_threat
        farm_row.nitrogen_status = state.nutrient.nitrogen_status
        farm_row.phosphorus_status = state.nutrient.phosphorus_status
        farm_row.potassium_status = state.nutrient.potassium_status
        farm_row.market_price_per_kg = state.market.price_per_kg
        farm_row.market_currency = state.market.currency
        farm_row.market_name = state.market.market_name
        farm_row.market_observed_at = state.market.observed_at
        farm_row.goal_objective = state.goal.objective if state.goal else None
        farm_row.goal_crop = state.goal.crop if state.goal else None
        farm_row.goal_target_yield_change_percent = state.goal.target_yield_change_percent if state.goal else None
        farm_row.goal_water_reduction_percent = state.goal.water_reduction_percent if state.goal else None
        farm_row.goal_priority = state.goal.priority if state.goal else None
        farm_row.updated_at = datetime.now(timezone.utc)

        if state.goal is not None:
            goal_row = db.scalar(select(GoalDB).where(GoalDB.farm_id == farm_row.id).order_by(GoalDB.created_at.desc()))
            if goal_row is None:
                goal_row = GoalDB(farm_id=farm_row.id, text=state.goal.objective)
                db.add(goal_row)
            goal_row.text = state.goal.objective
            goal_row.objective = state.goal.objective
            goal_row.crop = state.goal.crop
            goal_row.target_yield_change_percent = state.goal.target_yield_change_percent
            goal_row.water_reduction_percent = state.goal.water_reduction_percent
            goal_row.priority = state.goal.priority
            goal_row.status = "active"
            goal_row.field_id = None
            if state.goal.field_id:
                field_row = db.scalar(select(FieldDB).where(FieldDB.external_id == state.goal.field_id))
                if field_row is not None and field_row.farm_id == farm_row.id:
                    goal_row.field_id = field_row.id

        if state.plan is not None:
            plan_row = db.scalar(select(PlanDB).where(PlanDB.farm_id == farm_row.id).order_by(PlanDB.created_at.desc()))
            if plan_row is None:
                plan_row = PlanDB(
                    farm_id=farm_row.id,
                    external_plan_id=state.plan.plan_id,
                    goal_id=db.scalar(select(GoalDB.id).where(GoalDB.farm_id == farm_row.id).order_by(GoalDB.created_at.desc())),
                )
                db.add(plan_row)
            plan_row.external_plan_id = state.plan.plan_id
            plan_row.status = state.plan.status
            plan_row.decision = state.plan.decision
            plan_row.confidence = state.plan.confidence
            plan_row.rationale = state.plan.rationale
            plan_row.expected_water_saved_liters = state.plan.expected_water_saved_liters
            plan_row.expected_water_reduction_percent = state.plan.expected_water_reduction_percent
            plan_row.updated_at = datetime.now(timezone.utc)
            plan_row.field_id = None
            if state.plan.field_id:
                field_row = db.scalar(select(FieldDB).where(FieldDB.external_id == state.plan.field_id))
                if field_row is not None and field_row.farm_id == farm_row.id:
                    plan_row.field_id = field_row.id
            if plan_row.goal_id is None:
                latest_goal = db.scalar(select(GoalDB).where(GoalDB.farm_id == farm_row.id).order_by(GoalDB.created_at.desc()))
                plan_row.goal_id = latest_goal.id if latest_goal else None

        if state.approval is not None:
            plan_row = db.scalar(select(PlanDB).where(PlanDB.farm_id == farm_row.id).order_by(PlanDB.created_at.desc()))
            if plan_row is not None:
                approval_row = db.scalar(select(ApprovalDB).where(ApprovalDB.plan_id == plan_row.id))
                if approval_row is None:
                    approval_row = ApprovalDB(plan_id=plan_row.id)
                    db.add(approval_row)
                approval_row.decision = state.approval.decision or "approve"
                approval_row.status = state.approval.status
                approval_row.execution_mode = "simulation_only"
                approval_row.executed = False
                approval_row.farmer_note = state.approval.farmer_note
                approval_row.modified_action = state.approval.modified_action
                approval_row.rationale = state.approval.rationale
                approval_row.created_at = datetime.now(timezone.utc)

        db.commit()
        return load_demo_farm_state(db)
    finally:
        if owns_session:
            db.close()
