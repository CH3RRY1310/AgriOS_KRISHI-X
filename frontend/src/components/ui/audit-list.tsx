import { auditEvents } from "@/lib/demo-data";
import { Badge } from "@/components/ui/badge";

export function AuditList({ limit }: { limit?: number }) {
  const events = limit ? auditEvents.slice(-limit).reverse() : auditEvents.slice().reverse();
  return <div className="audit-list">{events.map((event) => <div className="audit-row" key={`${event.time}-${event.title}`}><span className="audit-time">{event.time}</span><span className={`audit-node node-${event.type}`} /><div><strong>{event.title}</strong><p>{event.description}</p></div><Badge tone={event.type === "conflict" ? "amber" : event.type === "approval" ? "blue" : "slate"}>{event.type}</Badge></div>)}</div>;
}
