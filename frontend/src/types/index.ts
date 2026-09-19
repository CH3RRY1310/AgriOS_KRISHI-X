export type Tone = "green" | "amber" | "red" | "blue" | "slate";

export type Metric = {
  label: string;
  value: string;
  detail: string;
  tone: Tone;
  trend?: string;
};

export type Agent = {
  name: string;
  role: string;
  status: "Active" | "Standby" | "Review";
  activity: string;
  confidence: string;
};

export type DemoAuditEvent = {
  time: string;
  title: string;
  description: string;
  type: "goal" | "state" | "decision" | "conflict" | "verification" | "approval";
};

export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

export type FarmState = {
  farm: {
    id: string;
    name: string;
    location: string;
    area_acres: number;
  };
  crop: {
    crop: string;
    variety: string | null;
    growth_stage: string;
    health_status: string;
    planting_date: string | null;
  };
  soil: {
    soil_moisture_percent: number;
    soil_type: string | null;
    temperature_celsius: number | null;
  };
  weather: {
    temperature_celsius: number;
    humidity_percent: number;
    rain_probability_percent: number;
    rainfall_mm: number;
    forecast_window_hours: number;
    observed_at: string;
  };
  water: {
    available_liters: number;
    minimum_reserve_liters: number;
    irrigation_available: boolean;
  };
  pest: {
    risk_level: string;
    risk_percent: number;
    primary_threat: string | null;
  };
  nutrient: {
    nitrogen_status: string;
    phosphorus_status: string;
    potassium_status: string;
  };
  market: {
    crop: string;
    price_per_kg: number;
    currency: string;
    market_name: string;
    observed_at: string;
  };
  goal: {
    objective: string;
    crop: string | null;
    target_yield_change_percent: number | null;
    water_reduction_percent: number | null;
    priority: string;
  } | null;
  agent_outputs: Array<{
    agent_name: string;
    summary: string;
    confidence_percent: number | null;
    created_at: string;
  }>;
  conflicts: Conflict[];
  plan: PlanSummary | null;
  verification: VerificationResult | null;
  approval: ApprovalState | null;
  updated_at: string;
};

export type GoalAnalysis = {
  objective: string;
  crop: string;
  target_yield_change_percent: number;
  water_reduction_percent: number;
  priority: string;
  confidence: number;
  rationale: string;
};

export type WeatherRecommendation = {
  rain_probability_percent: number;
  forecast_window_hours: number;
  recommendation: "WAIT" | "IRRIGATE" | "NOT_IRRIGATE";
  irrigation_delay_hours: number;
  confidence: number;
  rationale: string;
  evidence: string[];
};

export type IrrigationRecommendation = {
  soil_moisture_percent: number;
  recommended_duration_minutes: number;
  recommendation: "IRRIGATE" | "NOT_IRRIGATE" | "WAIT";
  water_required_liters: number;
  confidence: number;
  rationale: string;
  evidence: string[];
};

export type Conflict = {
  conflict_type: string;
  agents_involved: string[];
  description: string;
  severity: "low" | "medium" | "high";
  resolution: string;
  rationale: string;
  resolved: boolean;
};

export type VerificationResult = {
  status: "verified" | "failed";
  verified: boolean;
  confidence: number;
  safety_checks: Record<string, boolean>;
  rationale: string;
  summary: string;
};

export type PlanSummary = {
  plan_id: string;
  status: "awaiting_approval" | "approved" | "rejected" | "needs_revision" | "monitoring";
  decision: string;
  actions: string[];
  expected_water_saved_liters: number;
  expected_water_reduction_percent: number;
  confidence: number;
  rationale: string;
};

export type PlanningResponse = {
  goal_analysis: GoalAnalysis;
  weather: WeatherRecommendation;
  irrigation: IrrigationRecommendation;
  conflicts: Conflict[];
  verification: VerificationResult;
  plan: PlanSummary;
};

export type ApprovalRequest = {
  decision: "approve" | "modify" | "reject";
  plan_id: string;
  farmer_note?: string | null;
  modified_action?: string | null;
};

export type ApprovalState = {
  status: "pending" | "approved" | "rejected" | "modified";
  decision: "approve" | "modify" | "reject" | null;
  plan_id: string;
  farmer_note: string | null;
  modified_action: string | null;
  decided_at: string | null;
  approved_by: string;
  rationale: string;
  note: string | null;
};

export type ExecutionState = {
  status: "simulation_only";
  executed: boolean;
};

export type ApprovalResponse = {
  approval: ApprovalState;
  execution: ExecutionState;
};

export type AuditEntry = {
  event_id: string;
  event_type: "PLAN_CREATED" | "APPROVAL_SUBMITTED" | "PLAN_REPLANNED";
  timestamp: string;
  plan_id: string;
  description: string;
  metadata: Record<string, string | boolean | number | null>;
};

export type ReplanningResponse = PlanSummary;

export type AuditEvent = AuditEntry;

