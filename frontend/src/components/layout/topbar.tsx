"use client";

export function Topbar({ onMenu }: { onMenu: () => void }) {
  return (
    <header className="topbar">
      <button className="menu-button" type="button" onClick={onMenu} aria-label="Open navigation menu">MENU</button>
      <div className="farm-context"><span className="context-kicker">CURRENT FARM</span><strong>Shinde Farm / Block A</strong><span className="context-location">Nashik, Maharashtra</span></div>
      <div className="topbar-actions">
        <span className="status-chip"><span className="status-pulse" /> Systems nominal</span>
        <span className="topbar-divider" />
        <button className="icon-button" type="button" aria-label="View notifications">ALERT <span className="alert-count">1</span></button>
        <button className="operator-button" type="button" aria-label="Open operator menu"><span>AS</span><strong>Operator</strong></button>
      </div>
    </header>
  );
}
