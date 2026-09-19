import type { Agent, DemoAuditEvent, Metric } from "@/types";

export const navItems = [
  { label: "Dashboard", href: "/dashboard", code: "DB" },
  { label: "Goals", href: "/goals", code: "GO" },
  { label: "AI Planning", href: "/planning", code: "PL" },
  { label: "Conflicts", href: "/conflicts", code: "CF", badge: "1" },
  { label: "Approvals", href: "/approvals", code: "AP", badge: "1" },
  { label: "Monitoring", href: "/monitoring", code: "MO" },
  { label: "Agent Control", href: "/agents", code: "AG" },
  { label: "Audit Timeline", href: "/audit", code: "AU" },
];

export const dashboardMetrics: Metric[] = [
  { label: "Crop health", value: "84 / 100", detail: "Healthy canopy signal", tone: "green", trend: "+4.2%" },
  { label: "Soil moisture", value: "38%", detail: "Field average · target 42%", tone: "amber", trend: "-3% today" },
  { label: "Rain probability", value: "62%", detail: "Next 48 hours", tone: "blue" },
  { label: "Pest risk", value: "Low", detail: "No threshold breach", tone: "green" },
  { label: "Market price", value: "Rs 36 / kg", detail: "Tomato · Nashik mandi", tone: "blue", trend: "+8% week" },
  { label: "Water availability", value: "71%", detail: "Reservoir + borewell", tone: "green", trend: "14 days cover" },
];

export const agents: Agent[] = [
  { name: "Coordinator", role: "Plan orchestration", status: "Active", activity: "Reconciling irrigation and rainfall signals", confidence: "96%" },
  { name: "Weather", role: "Forecast intelligence", status: "Active", activity: "Updated 48-hour precipitation window", confidence: "91%" },
  { name: "Irrigation", role: "Water scheduling", status: "Review", activity: "Proposed 18% shorter cycle", confidence: "88%" },
  { name: "Crop Health", role: "Canopy analysis", status: "Active", activity: "Vegetation index within healthy range", confidence: "94%" },
  { name: "Pest", role: "Threat detection", status: "Standby", activity: "Monitoring for early blight indicators", confidence: "83%" },
  { name: "Nutrient", role: "Soil balance", status: "Standby", activity: "No corrective application required", confidence: "86%" },
  { name: "Resource", role: "Constraint planning", status: "Active", activity: "Validated water reserve against goal", confidence: "98%" },
  { name: "Market", role: "Price intelligence", status: "Active", activity: "Flagged favorable harvest window", confidence: "89%" },
];

export const auditEvents: DemoAuditEvent[] = [
  { time: "09:42", title: "Farmer goal created", description: "Yield target and 20% water reduction constraint added by operator.", type: "goal" },
  { time: "09:44", title: "Farm state observed", description: "Soil, weather, crop health, inventory, and market signals synchronized.", type: "state" },
  { time: "09:45", title: "Agent decisions received", description: "Eight specialist agents returned recommendations to the Coordinator.", type: "decision" },
  { time: "09:46", title: "Conflict detected", description: "Irrigation timing overlapped with Weather agent rainfall window.", type: "conflict" },
  { time: "09:48", title: "Conflict resolved", description: "Plan shifted irrigation to a shorter pre-dawn cycle.", type: "verification" },
  { time: "09:49", title: "Verification complete", description: "Resource and crop constraints passed the plan safety check.", type: "verification" },
  { time: "09:50", title: "Approval requested", description: "Farmer review opened for the recommended irrigation adjustment.", type: "approval" },
];

export const planSteps = [
  { label: "Goal", detail: "Yield + water efficiency", status: "complete" },
  { label: "Farm State", detail: "6 signals synchronized", status: "complete" },
  { label: "Weather", detail: "48-hour forecast checked", status: "complete" },
  { label: "Irrigation", detail: "Cycle adjustment proposed", status: "complete" },
  { label: "Conflict Detection", detail: "1 conflict resolved", status: "complete" },
  { label: "Verification", detail: "Constraint checks passed", status: "complete" },
  { label: "Farmer Approval", detail: "Awaiting operator decision", status: "current" },
];
