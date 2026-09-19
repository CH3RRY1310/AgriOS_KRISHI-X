"use client";

import { useState } from "react";
import { useAgriOS } from "@/components/providers/agri-os-provider";
import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import { createPlan } from "@/services/api";

export default function GoalsPage() {
  const { setCurrentPlan, setCurrentApproval, setCurrentReplan, planLoading, setPlanLoading, planError, setPlanError, currentPlan } = useAgriOS();
  const [goal, setGoal] = useState("Maximize tomato yield while reducing water consumption by 20%");

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedGoal = goal.trim();

    if (!trimmedGoal) {
      setPlanError("Please enter a farmer goal before generating a plan.");
      return;
    }

    setPlanLoading(true);
    setPlanError(null);

    try {
      const response = await createPlan(trimmedGoal);
      setCurrentPlan(response);
      setCurrentApproval(null);
      setCurrentReplan(null);
    } catch (error) {
      setPlanError(error instanceof Error ? error.message : "Your plan could not be generated. Please try again.");
    } finally {
      setPlanLoading(false);
    }
  };

  return <>
    <header className="page-header"><div><p className="eyebrow">Farmer intent</p><h1 className="page-title">Define a goal.</h1><p className="page-subtitle">Start with the outcome that matters on the farm. The planning network will translate it into coordinated, reviewable actions.</p></div><Badge tone="amber">DEMO / SIMULATION</Badge></header>
    <div className="split-grid">
      <Panel title="Goal input" detail="Create a new planning objective">
        <form onSubmit={handleSubmit}>
          <label className="field-label" htmlFor="goal">Farmer goal</label>
          <textarea className="field-input" id="goal" value={goal} onChange={(event) => setGoal(event.target.value)} rows={5} />
          <div className="form-grid">
            <div>
              <label className="field-label" htmlFor="priority">Priority</label>
              <select className="field-input" id="priority" defaultValue="high"><option value="high">High - protect this outcome</option><option value="medium">Medium - balance with other goals</option><option value="low">Low - explore when possible</option></select>
            </div>
            <div>
              <label className="field-label" htmlFor="horizon">Planning horizon</label>
              <select className="field-input" id="horizon" defaultValue="30"><option value="30">Next 30 days</option><option value="14">Next 14 days</option><option value="90">Next 90 days</option></select>
            </div>
          </div>
          {planError && <p className="empty-note" style={{ color: "#f59e0b" }}>{planError}</p>}
          <button className="button-primary" type="submit" disabled={planLoading}>{planLoading ? "Generating plan…" : "Start planning cycle"}</button>
        </form>
      </Panel>
      <Panel title="Farm context" detail="Context attached to this goal">
        <div className="context-list"><div><span>Farm</span><strong>Shinde Farm / Block A</strong></div><div><span>Crop</span><strong>Tomato - 4.8 hectares</strong></div><div><span>Season</span><strong>Kharif - Week 7</strong></div><div><span>Water constraint</span><strong>20% reduction target</strong></div></div>
        <div className="goal-callout compact"><p className="eyebrow">Why it matters</p><p>Goals keep specialist recommendations aligned to the farmer&apos;s actual priorities, not isolated signals.</p></div>
      </Panel>
    </div>
    {currentPlan && <div className="section-block"><Panel title="Latest plan created" detail="Simulation-only plan result"><div className="stat-line"><span>Plan ID</span><strong>{currentPlan.plan.plan_id}</strong></div><div className="stat-line"><span>Status</span><strong>{currentPlan.plan.status}</strong></div><div className="stat-line"><span>Decision</span><strong>{currentPlan.plan.decision}</strong></div><div className="stat-line"><span>Expected water saved</span><strong>{currentPlan.plan.expected_water_saved_liters} L</strong></div></Panel></div>}
    <p className="empty-note">Simulation Mode: this environment is designed for reviewing recommendations before any physical action.</p>
  </>;
}
