"use client";

import { useEffect, useState } from "react";
import { useAgriOS } from "@/components/providers/agri-os-provider";
import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import { getApproval, replan, submitApproval } from "@/services/api";

export default function ApprovalsPage() {
  const { currentPlan, currentApproval, setCurrentApproval, approvalLoading, setApprovalLoading, approvalError, setApprovalError, setCurrentReplan, replanLoading, setReplanLoading, replanError, setReplanError } = useAgriOS();
  const [decision, setDecision] = useState<"approve" | "modify" | "reject">("approve");
  const [farmerNote, setFarmerNote] = useState("");
  const [modifiedAction, setModifiedAction] = useState("");

  useEffect(() => {
    let active = true;

    const loadApproval = async () => {
      setApprovalLoading(true);
      setApprovalError(null);
      try {
        const response = await getApproval();
        if (active) {
          setCurrentApproval(response);
        }
      } catch (error) {
        if (active) {
          setApprovalError(error instanceof Error ? error.message : "Approval could not be loaded.");
        }
      } finally {
        if (active) {
          setApprovalLoading(false);
        }
      }
    };

    loadApproval();
    return () => {
      active = false;
    };
  }, [setApprovalError, setApprovalLoading, setCurrentApproval]);

  const planId = currentPlan?.plan.plan_id ?? currentApproval?.approval.plan_id ?? "";

  const handleSubmission = async () => {
    if (!planId) {
      setApprovalError("Create a plan before submitting a farmer approval.");
      return;
    }

    setApprovalLoading(true);
    setApprovalError(null);

    try {
      const response = await submitApproval({
        decision,
        plan_id: planId,
        farmer_note: farmerNote || undefined,
        modified_action: decision === "modify" ? modifiedAction.trim() || undefined : undefined,
      });
      setCurrentApproval(response);
      setCurrentReplan(null);
      setReplanError(null);
    } catch (error) {
      setApprovalError(error instanceof Error ? error.message : "Approval could not be submitted.");
    } finally {
      setApprovalLoading(false);
    }
  };

  const handleGenerateReplan = async () => {
    if (!planId) return;

    setReplanLoading(true);
    setReplanError(null);

    try {
      const response = await replan(planId);
      setCurrentReplan(response);
    } catch (error) {
      setReplanError(error instanceof Error ? error.message : "The updated plan could not be generated.");
    } finally {
      setReplanLoading(false);
    }
  };

  const approvalState = currentApproval?.approval;
  const executionState = currentApproval?.execution;

  return <>
    <header className="page-header"><div><p className="eyebrow">Human in the loop</p><h1 className="page-title">Farmer approvals</h1><p className="page-subtitle">Review the reasoning, expected impact, and evidence before a recommendation can move forward.</p></div><Badge tone="amber">{planId ? "Simulation Mode" : "Awaiting plan"}</Badge></header>
    {approvalError && <p className="empty-note" style={{ color: "#f59e0b" }}>{approvalError}</p>}
    <div className="approval-layout">
      <div className="approval-main">
        <div className="approval-banner"><Badge tone="amber">AI recommendation — awaiting farmer approval</Badge><h2>{currentPlan?.plan?.decision ?? "Plan awaiting review"}</h2><p>{currentPlan?.plan?.rationale ?? "Create or load a plan to review the recommendation."}</p></div>
        <div className="split-grid">
          <Panel title="Recommendation" detail="Deterministic plan summary">
            <div className="stat-line"><span>Plan ID</span><strong>{planId || "—"}</strong></div>
            <div className="stat-line"><span>Expected water saving</span><strong>{currentPlan?.plan?.expected_water_saved_liters ?? 0} L</strong></div>
            <div className="stat-line"><span>Expected water reduction</span><strong>{currentPlan?.plan?.expected_water_reduction_percent ?? 0}%</strong></div>
            <div className="stat-line"><span>Decision</span><strong>{currentPlan?.plan?.decision ?? "pending"}</strong></div>
          </Panel>
          <Panel title="Evidence" detail="Signals supporting this plan">
            <div className="stat-line"><span>Soil moisture</span><strong>{currentPlan?.irrigation.soil_moisture_percent ?? 0}%</strong></div>
            <div className="stat-line"><span>Rain probability</span><strong>{currentPlan?.weather.rain_probability_percent ?? 0}%</strong></div>
            <div className="stat-line"><span>Plan confidence</span><strong>{currentPlan?.plan?.confidence ?? 0}%</strong></div>
          </Panel>
        </div>
        <Panel title="Decision controls" detail="Simulation-only approval gate">
          <div className="approval-actions" style={{ display: "grid", gap: "12px" }}>
            <div className="form-grid"><label className="field-label" htmlFor="decision">Decision</label><select className="field-input" id="decision" value={decision} onChange={(event) => setDecision(event.target.value as "approve" | "modify" | "reject")}><option value="approve">Approve plan</option><option value="modify">Modify recommendation</option><option value="reject">Reject</option></select></div>
            {decision === "modify" && <div><label className="field-label" htmlFor="modified-action">Modification</label><textarea className="field-input" id="modified-action" value={modifiedAction} onChange={(event) => setModifiedAction(event.target.value)} rows={3} placeholder="State the modified action or adjustment required." /></div>}
            {decision === "reject" && <div><label className="field-label" htmlFor="farmer-note">Farmer note</label><textarea className="field-input" id="farmer-note" value={farmerNote} onChange={(event) => setFarmerNote(event.target.value)} rows={3} placeholder="Optional note for the rejection feedback." /></div>}
            <button className="button-primary" type="button" onClick={handleSubmission} disabled={approvalLoading}>{approvalLoading ? "Submitting…" : "Submit decision"}</button>
            {replanError && <p className="empty-note" style={{ color: "#f59e0b" }}>{replanError}</p>}
          </div>
        </Panel>
      </div>
      <Panel title="Decision trace" detail="Why this recommendation exists">
        <div className="trace-step"><span>01</span><div><strong>Goal alignment</strong><p>Supports the water reduction target while keeping crop health in range.</p></div></div>
        <div className="trace-step"><span>02</span><div><strong>Conflict resolved</strong><p>Balances low soil moisture against forecast rainfall and keeps the plan deterministic.</p></div></div>
        <div className="trace-step"><span>03</span><div><strong>Verification</strong><p>Safety checks pass and the environment remains simulation-only.</p></div></div>
      </Panel>
    </div>
    {approvalState && <div className="section-block"><Panel title="Approval result" detail="Submitted farmer response"><div className="stat-line"><span>Status</span><strong>{approvalState.status}</strong></div><div className="stat-line"><span>Decision</span><strong>{approvalState.decision}</strong></div><div className="stat-line"><span>Simulation only</span><strong>{executionState?.executed === false ? "true" : "false"}</strong></div><div className="stat-line"><span>Executed</span><strong>{executionState?.executed ? "true" : "false"}</strong></div><p className="body-copy">Simulation only — no physical action executed.</p>{approvalState.note && <p className="body-copy">{approvalState.note}</p>}<button className="button-secondary" type="button" onClick={handleGenerateReplan} disabled={replanLoading}>{replanLoading ? "Generating updated plan…" : "Generate Updated Plan"}</button></Panel></div>}
    <p className="empty-note">Simulation only — no physical action is executed from this approval step.</p>
  </>;
}
