type SectionHeadingProps = {
  eyebrow?: string;
  title: string;
  detail?: string;
  action?: React.ReactNode;
};

export function SectionHeading({ eyebrow, title, detail, action }: SectionHeadingProps) {
  return (
    <div className="section-heading">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2>{title}</h2>
        {detail && <p className="section-detail">{detail}</p>}
      </div>
      {action}
    </div>
  );
}
