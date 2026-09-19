"use client";

import { useAgriOS } from "@/components/providers/agri-os-provider";
import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";

export default function ConflictsPage() {
  const { currentPlan } = useAgriOS();
  const firstConflict = currentPlan?.conflicts[0];

  if (!firstConflict) {
    return <>
      <header className="page-header"><div><p className="eyebrow">Decision quality</p><h1 className="page-title">Conflicts</h1><p className="page-subtitle">Make competing recommendations visible. The coordinator documents evidence before resolving a disagreement.</p></div><Badge tone="amber">NO CONFLICTS</Badge></header>
      <div className="panel"><div className="panel-heading"><div><h3>No conflict loaded</h3><p>Generate a plan to populate the backend conflict output.</p></div></div></div>
    </>;
  }

  return <>
    <header className="page-header"><div><p className="eyebrow">Decision quality</p><h1 className="page-title">Conflicts</h1><p className="page-subtitle">Make competing recommendations visible. The coordinator documents evidence before resolving a disagreement.</p></div><Badge tone="amber">SIMULATION MODE</Badge></header>
    <div className="conflict-card">
      <div className="conflict-header"><div><Badge tone={firstConflict.severity === "high" ? "red" : firstConflict.severity === "medium" ? "amber" : "green"}>{firstConflict.severity} severity</Badge><h2>{firstConflict.conflict_type}</h2><p>Agents: {firstConflict.agents_involved.join(", ")}</p></div><Badge tone="green">{firstConflict.resolved ? "Resolved" : "Open"}</Badge></div>
      <div className="split-grid">
        <Panel title="Weather" detail="Recommendation A"><div className="recommendation"><strong>WAIT</strong><p>{currentPlan?.weather.rationale}</p><Badge tone="blue">Confidence {currentPlan?.weather.confidence ?? 0}%</Badge></div></Panel>
        <Panel title="Irrigation" detail="Recommendation B"><div className="recommendation"><strong>IRRIGATE</strong><p>{currentPlan?.irrigation.rationale}</p><Badge tone="blue">Confidence {currentPlan?.irrigation.confidence ?? 0}%</Badge></div></Panel>
      </div>
      <div className="resolution"><div><p className="eyebrow">Coordinator resolution</p><strong>{firstConflict.resolution}</strong><p>{firstConflict.description}</p></div><Badge tone="green">Verified by Resource</Badge></div>
    </div>
    <div className="section-block three-col">
      <Panel title="Evidence" detail="Shared farm state"><div className="stat-line"><span>Soil moisture</span><strong>{currentPlan?.irrigation.soil_moisture_percent ?? 0}%</strong></div><div className="stat-line"><span>Rain probability</span><strong>{currentPlan?.weather.rain_probability_percent ?? 0}%</strong></div><div className="stat-line"><span>Water reserve</span><strong>{Math.round(currentPlan?.weather.rain_probability_percent ?? 0)}%</strong></div></Panel>
      <Panel title="Resolution status" detail="Safety checks"><div className="stat-line"><span>Goal alignment</span><Badge tone="green">Pass</Badge></div><div className="stat-line"><span>Crop safety</span><Badge tone="green">Pass</Badge></div><div className="stat-line"><span>Water goal</span><Badge tone="green">Pass</Badge></div></Panel>
      <Panel title="Operator note" detail="Demo explanation"><p className="body-copy">{firstConflict.rationale}</p></Panel>
    </div>
    <p className="empty-note">Simulation Mode: no physical irrigation command is executed from this conflict resolution.</p>
  </>;
}
