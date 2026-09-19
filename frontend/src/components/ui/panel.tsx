type PanelProps = { title: string; detail?: string; children: React.ReactNode; className?: string };

export function Panel({ title, detail, children, className = "" }: PanelProps) {
  return <section className={`panel ${className}`}><div className="panel-heading"><div><h3>{title}</h3>{detail && <p>{detail}</p>}</div></div>{children}</section>;
}
