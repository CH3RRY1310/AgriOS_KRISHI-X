"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import { getAuditEvents } from "@/services/api";
import type { AuditEvent } from "@/types";

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const loadEvents = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await getAuditEvents();
        if (active) {
          setEvents(response);
        }
      } catch (loadError) {
        if (active) {
          setError(loadError instanceof Error ? loadError.message : "Unable to load the audit timeline.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadEvents();
    return () => {
      active = false;
    };
  }, []);

  return <><header className="page-header"><div><p className="eyebrow">Traceability</p><h1 className="page-title">Audit timeline</h1><p className="page-subtitle">A chronological record of the decisions, evidence, conflicts, and human gates behind the current plan.</p></div><Badge tone="slate">DEMO EVENT LOG</Badge></header>{error && <p className="empty-note" style={{ color: "#f59e0b" }}>{error}</p>}{loading ? <p className="empty-note">Loading audit events…</p> : <Panel title="Decision history" detail="Current planning and approval flow"><div className="audit-list">{events.length === 0 ? <p className="empty-note">No audit events recorded yet.</p> : [...events].reverse().map((event) => <div className="audit-row" key={event.event_id}><span className="audit-time">{new Date(event.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span><span className={`audit-node node-${event.event_type.toLowerCase()}`} /><div><strong>{event.event_type}</strong><p>{event.description}</p></div><Badge tone={event.event_type === "PLAN_REPLANNED" ? "blue" : event.event_type === "APPROVAL_SUBMITTED" ? "amber" : "slate"}>{event.event_type}</Badge></div>)}</div></Panel>}<div className="section-block three-col"><Panel title="Audit coverage" detail="Current planning cycle"><div className="stat-line"><span>Events recorded</span><strong>{events.length}</strong></div><div className="stat-line"><span>Plan events</span><strong>{events.filter((event) => event.event_type === "PLAN_CREATED").length}</strong></div><div className="stat-line"><span>Approval events</span><strong>{events.filter((event) => event.event_type === "APPROVAL_SUBMITTED").length}</strong></div></Panel><Panel title="Trace integrity" detail="Demo status"><Badge tone="green">Complete chain</Badge><p className="body-copy">Each simulated decision is connected to the goal, farm state, and final approval gate.</p></Panel><Panel title="Data provenance" detail="Current sources"><p className="body-copy">All signals are synthetic demo values. External weather, sensor, market, and imagery sources are not connected.</p></Panel></div></>;
}
