"use client";

import { useAgriOS } from "@/components/providers/agri-os-provider";
import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";

export default function MonitoringPage() {
  const { currentReplan } = useAgriOS();

  if (!currentReplan) {
    return <>
      <header className="page-header"><div><p className="eyebrow">Shared farm state</p><h1 className="page-title">Monitoring</h1><p className="page-subtitle">A simulated live view of the signals agents use to reason about the farm and trigger a new planning cycle.</p></div><Badge tone="blue">SIMULATED TELEMETRY</Badge></header>
      <div className="panel"><div className="panel-heading"><div><h3>No replanning result yet</h3><p>Approve a plan and generate an updated plan to see monitoring guidance.</p></div></div></div>
    </>;
  }

  return <>
    <header className="page-header"><div><p className="eyebrow">Shared farm state</p><h1 className="page-title">Monitoring</h1><p className="page-subtitle">A simulated live view of the signals agents use to reason about the farm and trigger a new planning cycle.</p></div><Badge tone="blue">SIMULATION MODE</Badge></header>
    <div className="section-block two-col">
      <Panel title="Monitoring status" detail="Replanning output">
        <div className="stat-line"><span>Status</span><strong>{currentReplan.status}</strong></div>
        <div className="stat-line"><span>Decision</span><strong>{currentReplan.decision}</strong></div>
        <div className="stat-line"><span>Source plan ID</span><strong>{currentReplan.plan_id}</strong></div>
        <div className="stat-line"><span>Next reassessment</span><strong>8 hours</strong></div>
        <div className="stat-line"><span>Simulation only</span><strong>{currentReplan.status === "monitoring" ? "true" : "false"}</strong></div>
        <p className="body-copy">{currentReplan.rationale}</p>
      </Panel>
      <Panel title="Recommended follow-up actions" detail="Monitoring posture">
        <ul className="context-list">{currentReplan.actions.map((action) => <li key={action}>{action}</li>)}</ul>
      </Panel>
    </div>
    <p className="empty-note">Simulation only — no field device action is performed while the plan remains in monitoring.</p>
  </>;
}
