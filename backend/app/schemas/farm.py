"""Typed Farm Digital Twin state models."""

from datetime import date, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class Farm(BaseModel):
    """Identity and physical size of a farm."""

    id: str
    name: str
    location: str
    area_acres: float = Field(gt=0)


class CropState(BaseModel):
    """Current crop and growth information for the farm."""

    crop: str
    variety: str | None = None
    growth_stage: str
    health_status: str
    planting_date: date | None = None


class SoilState(BaseModel):
    """Current soil observations represented in the shared farm state."""

    soil_moisture_percent: float = Field(ge=0, le=100)
    soil_type: str | None = None
    temperature_celsius: float | None = None


class WeatherState(BaseModel):
    """Observed and forecast weather conditions."""

    temperature_celsius: float
    humidity_percent: float = Field(ge=0, le=100)
    rain_probability_percent: float = Field(ge=0, le=100)
    rainfall_mm: float = Field(ge=0)
    forecast_window_hours: int = Field(ge=0)
    observed_at: datetime


class WaterState(BaseModel):
    """Water availability and irrigation status."""

    available_liters: float = Field(ge=0)
    minimum_reserve_liters: float = Field(ge=0)
    irrigation_available: bool


class PestState(BaseModel):
    """Current pest risk summary."""

    risk_level: str
    risk_percent: float = Field(ge=0, le=100)
    primary_threat: str | None = None


class NutrientState(BaseModel):
    """Qualitative nutrient status from the shared farm state."""

    nitrogen_status: str
    phosphorus_status: str
    potassium_status: str


class MarketState(BaseModel):
    """Latest simulated market information for the selected crop."""

    crop: str
    price_per_kg: float = Field(ge=0)
    currency: str
    market_name: str
    observed_at: datetime


class GoalState(BaseModel):
    """Farmer objective currently associated with the farm."""

    objective: str
    crop: str | None = None
    target_yield_change_percent: float | None = Field(default=None, ge=0)
    water_reduction_percent: float | None = Field(default=None, ge=0, le=100)
    priority: str
    farm_id: str | None = None
    field_id: str | None = None


class GoalAnalysis(BaseModel):
    """Structured output from the goal analysis agent."""

    objective: str
    crop: str
    target_yield_change_percent: float = Field(ge=0)
    water_reduction_percent: float = Field(ge=0, le=100)
    priority: str
    confidence: float = Field(ge=0, le=100)
    rationale: str
    farm_id: str | None = None
    field_id: str | None = None


class WeatherRecommendation(BaseModel):
    """Structured output from the weather recommendation agent."""

    rain_probability_percent: float = Field(ge=0, le=100)
    forecast_window_hours: int = Field(ge=0)
    recommendation: Literal["WAIT", "IRRIGATE", "NOT_IRRIGATE"]
    irrigation_delay_hours: int = Field(ge=0)
    confidence: float = Field(ge=0, le=100)
    rationale: str
    evidence: list[str]
    farm_id: str | None = None
    field_id: str | None = None


class IrrigationRecommendation(BaseModel):
    """Structured output from the irrigation recommendation agent."""

    soil_moisture_percent: float = Field(ge=0, le=100)
    recommended_duration_minutes: int = Field(ge=0)
    recommendation: Literal["IRRIGATE", "NOT_IRRIGATE", "WAIT"]
    water_required_liters: float = Field(ge=0)
    confidence: float = Field(ge=0, le=100)
    rationale: str
    evidence: list[str]
    farm_id: str | None = None
    field_id: str | None = None


class AgentOutput(BaseModel):
    """Optional placeholder for a future agent recommendation."""

    agent_name: str
    summary: str
    confidence_percent: float | None = Field(default=None, ge=0, le=100)
    created_at: datetime


class Conflict(BaseModel):
    """Deterministic conflict record emitted by the conflict engine."""

    conflict_type: str
    agents_involved: list[str]
    description: str
    severity: Literal["low", "medium", "high"]
    resolution: str
    rationale: str
    resolved: bool = False
    farm_id: str | None = None
    field_id: str | None = None


class PlanSummary(BaseModel):
    """Coordinated decision summary for the first planning vertical slice."""

    plan_id: str = Field(default_factory=lambda: uuid4().hex)
    status: Literal["awaiting_approval", "approved", "rejected", "needs_revision", "monitoring"]
    decision: str
    actions: list[str]
    expected_water_saved_liters: float = Field(ge=0)
    expected_water_reduction_percent: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    rationale: str
    farm_id: str | None = None
    field_id: str | None = None
    goal: str | None = None


class VerificationResult(BaseModel):
    """Safety verification for the generated plan."""

    status: Literal["verified", "failed"]
    verified: bool
    confidence: float = Field(ge=0, le=100)
    safety_checks: dict[str, bool]
    rationale: str
    summary: str
    farm_id: str | None = None
    field_id: str | None = None


class ImpactEstimate(BaseModel):
    """Deterministic simulated impact estimate shown before farmer approval."""

    farm_id: str | None = None
    field_id: str | None = None
    water_impact: str
    yield_impact: str
    expected_water_change_percent: float
    expected_yield_change_percent: float
    risk: Literal["low", "medium", "high"]
    confidence: float = Field(ge=0, le=100)
    simulation_only: bool = True
    field_validated: bool = False
    rationale: str


class Explainability(BaseModel):
    """Traceable evidence used to explain a deterministic planning decision."""

    farm_id: str | None = None
    field_id: str | None = None
    goal: str
    crop: str
    growth_stage: str
    soil_moisture_percent: float
    temperature_celsius: float
    humidity_percent: float
    rain_probability_percent: float
    water_available_liters: float
    pest_risk_percent: float
    irrigation_recommendation: str
    weather_recommendation: str
    conflict_resolution: list[str]
    verification_status: str
    confidence: float = Field(ge=0, le=100)
    risk: Literal["low", "medium", "high"]
    supporting_stages: list[str]
    simulation_only: bool = True
    field_validated: bool = False


class ApprovalRequest(BaseModel):
    """Farmer input for the approval gate."""

    decision: Literal["approve", "modify", "reject"]
    plan_id: str
    farmer_note: str | None = None
    modified_action: str | None = None


class ApprovalState(BaseModel):
    """Structured farmer approval state for simulation-only execution gating."""

    status: Literal["pending", "approved", "rejected", "modified"] = "pending"
    decision: Literal["approve", "modify", "reject"] | None = "approve"
    plan_id: str = ""
    farmer_note: str | None = None
    modified_action: str | None = None
    decided_at: datetime | None = None
    approved_by: str = "farmer"
    rationale: str = "Simulation data; no action is executed."
    note: str | None = None


class ExecutionState(BaseModel):
    """Explicit simulation-only execution flag used by approval and replanning responses."""

    status: Literal["simulation_only"]
    executed: bool = False


class ApprovalResponse(BaseModel):
    """Approval response with explicit simulation-only execution state."""

    approval: ApprovalState
    execution: ExecutionState


class MonitoringState(BaseModel):
    """Monitoring metadata used after an approval decision."""

    status: Literal["monitoring"]
    next_reassessment_hours: int = Field(ge=0)
    reason: str
    source_plan_id: str


class PlanningRequest(BaseModel):
    """Request payload for the deterministic planning workflow."""

    goal: str
    farm_id: str | None = None
    field_id: str | None = None


class PlanningContext(BaseModel):
    """Explicit farm and field scope carried with a planning response."""

    farm_id: str
    field_id: str | None = None
    field_name: str | None = None
    crop: str | None = None
    variety: str | None = None
    growth_stage: str | None = None
    area_acres: float | None = Field(default=None, gt=0)


class PlanningResponse(BaseModel):
    """Structured response produced by the deterministic planning workflow."""

    goal_analysis: GoalAnalysis
    weather: WeatherRecommendation
    irrigation: IrrigationRecommendation
    conflicts: list[Conflict]
    verification: VerificationResult
    plan: PlanSummary
    context: PlanningContext | None = None
    impact: ImpactEstimate
    explainability: Explainability


class ScenarioEventRequest(BaseModel):
    """Validated request for a supported deterministic simulation event."""

    event_type: Literal["weather_change"]
    attribute: Literal["rain_probability_percent"]
    new_value: float = Field(ge=0, le=100)
    farm_id: str = "farm-demo-001"
    field_id: str | None = None
    goal: str | None = None


class ScenarioEvent(BaseModel):
    """Recorded simulated change applied to the Farm Digital Twin."""

    scenario_id: str
    event_id: str
    event_type: Literal["weather_change"]
    description: str
    attribute: Literal["rain_probability_percent"]
    previous_value: float
    new_value: float
    simulation_order: int = Field(ge=1)
    timestamp: datetime
    farm_id: str
    field_id: str | None = None
    simulation_only: bool = True
    field_validated: bool = False


class PlanReplanningRequest(BaseModel):
    """Request payload for replanning after an approval action."""

    plan_id: str


class AuditEvent(BaseModel):
    """In-memory audit record used for observability and review."""

    event_id: str = Field(default_factory=lambda: uuid4().hex)
    event_type: Literal["PLAN_CREATED", "APPROVAL_SUBMITTED", "PLAN_REPLANNED", "SCENARIO_EVENT"]
    timestamp: datetime
    plan_id: str
    description: str
    metadata: dict[str, str | bool | int | float | None] = Field(default_factory=dict)


class FarmState(BaseModel):
    """Complete shared state for the Farm Digital Twin."""

    model_config = ConfigDict(title="FarmState")

    farm: Farm
    crop: CropState
    soil: SoilState
    weather: WeatherState
    water: WaterState
    pest: PestState
    nutrient: NutrientState
    market: MarketState
    goal: GoalState | None = None
    agent_outputs: list[AgentOutput] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    plan: PlanSummary | None = None
    verification: VerificationResult | None = None
    approval: ApprovalState | None = None
    updated_at: datetime


class ScenarioEventResponse(BaseModel):
    """Result of applying a simulated event and running existing planning."""

    event: ScenarioEvent
    state: FarmState
    planning: PlanningResponse
