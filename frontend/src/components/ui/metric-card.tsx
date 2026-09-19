import type { Metric } from "@/types";
import { Badge } from "@/components/ui/badge";

export function MetricCard({ metric }: { metric: Metric }) {
  return <article className="metric-card">
    <div className="metric-top"><span className="metric-label">{metric.label}</span><span className={`metric-signal signal-${metric.tone}`} /></div>
    <strong className="metric-value">{metric.value}</strong>
    <div className="metric-bottom"><span>{metric.detail}</span>{metric.trend && <Badge tone={metric.tone}>{metric.trend}</Badge>}</div>
  </article>;
}
