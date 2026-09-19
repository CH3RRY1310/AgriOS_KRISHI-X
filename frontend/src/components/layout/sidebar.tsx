"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { navItems } from "@/lib/demo-data";

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="brand-block">
        <Link href="/dashboard" className="brand" onClick={onNavigate}>
          <span className="brand-mark">KX</span>
          <span><strong>AgriOS</strong><small>KRISHI-X / DEMO</small></span>
        </Link>
        <span className="demo-stamp">SIMULATION</span>
      </div>
      <nav className="nav-list">
        <p className="nav-label">Operations</p>
        {navItems.map((item) => {
          const active = pathname === item.href || (item.href === "/dashboard" && pathname === "/");
          return (
            <Link key={item.href} href={item.href} className={`nav-item ${active ? "active" : ""}`} onClick={onNavigate}>
              <span className="nav-code" aria-hidden="true">{item.code}</span>
              <span>{item.label}</span>
              {item.badge && <span className="nav-badge">{item.badge}</span>}
            </Link>
          );
        })}
      </nav>
      <div className="sidebar-footer">
        <div className="operator-dot" />
        <div><strong>Operator console</strong><span>Local demo session</span></div>
      </div>
    </aside>
  );
}
