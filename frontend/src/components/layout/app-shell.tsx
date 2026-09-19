"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <div className="app-shell">
      <div className={`mobile-overlay ${mobileOpen ? "visible" : ""}`} onClick={() => setMobileOpen(false)} aria-hidden="true" />
      <div className={`sidebar-wrap ${mobileOpen ? "open" : ""}`}><Sidebar onNavigate={() => setMobileOpen(false)} /></div>
      <div className="workspace">
        <Topbar onMenu={() => setMobileOpen(true)} />
        <main className="main-content">{children}</main>
      </div>
    </div>
  );
}
