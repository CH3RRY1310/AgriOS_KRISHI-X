import type { Tone } from "@/types";

type BadgeProps = {
  children: React.ReactNode;
  tone?: Tone;
};

export function Badge({ children, tone = "slate" }: BadgeProps) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
