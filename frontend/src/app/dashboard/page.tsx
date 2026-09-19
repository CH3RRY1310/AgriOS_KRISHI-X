"use client";

import Link from "next/link";
import { useEffect, useMemo } from "react";
import { useAgriOS } from "@/components/providers/agri-os-provider";
import { Badge } from "@/components/ui/badge";
import { MetricCard } from "@/components/ui/metric-card";
import { Panel } from "@/components/ui/panel";
import { SectionHeading } from "@/components/ui/section-heading";
import { getFarmState } from "@/services/api";
import type { Metric } from "@/types";

export default function DashboardPage() {
  const { farmState, setFarmState, farmLoading, setFarmLoading, farmError, setFarmError } = useAgriOS();

  useEffect(() => {
    let active = true;

    const loadState = async () => {
      setFarmLoading(true);
      setFarmError(null);
      try {
        const response = await getFarmState();
        if (active) {
          setFarmState(response);
        }
      } catch (error) {
        if (active) {
          setFarmError(error instanceof Error ? error.message : "Unable to load the current farm state.");
        }
      } finally {
        if (active) {
          setFarmLoading(false);
        }
      }
    };

    loadState();
    return () => {
      active = false;
    };
  }, [setFarmError, setFarmLoading, setFarmState]);

  const metrics = useMemo<Metric[]>(() => {
    if (!farmState) {
      return [];
    }

    return [
      { label: "Crop", value: `${farmState.crop.crop} / ${farmState.crop.growth_stage}`, detail: `${farmState.crop.variety ?? "Field mix"} · health ${farmState.crop.health_status}`, tone: "green" },
      { label: "Soil moisture", value: `${Math.round(farmState.soil.soil_moisture_percent)}%`, detail: `Target band: ${farmState.soil.soil_type ?? "sandy loam"}`, tone: farmState.soil.soil_moisture_percent < 40 ? "amber" : "green" },
      { label: "Temperature", value: `${farmState.weather.temperature_celsius.toFixed(1)}°C`, detail: `Humidity ${farmState.weather.humidity_percent}%`, tone: "blue" },
      { label: "Rain probability", value: `${Math.round(farmState.weather.rain_probability_percent)}%`, detail: `${farmState.weather.forecast_window_hours} hour window`, tone: "blue" },
      { label: "Water availability", value: `${Math.round(farmState.water.available_liters).toLocaleString()} L`, detail: `Reserve ${Math.round(farmState.water.minimum_reserve_liters).toLocaleString()} L`, tone: "green" },
      { label: "Pest risk", value: farmState.pest.risk_level, detail: `${farmState.pest.risk_percent}% risk · ${farmState.pest.primary_threat ?? "monitoring"}`, tone: farmState.pest.risk_percent > 30 ? "amber" : "green" },
      { label: "Market price", value: `${farmState.market.currency} ${farmState.market.price_per_kg.toFixed(0)} / kg`, detail: `${farmState.market.market_name}`, tone: "blue" },
    ];
  }, [farmState]);

  const goalText = farmState?.goal?.objective ?? "No active farmer goal is currently loaded.";
  const planConfidence = farmState?.plan?.confidence ?? 0;

  if (farmLoading) {
    return <><header className="page-header"><div><p className="eyebrow">Mission control</p><h1 className="page-title">Loading farm state…</h1></div><Badge tone="amber">Simulation Mode</Badge></header><p className="empty-note">Connecting to the AgriOS demo backend.</p></>;
  }

  if (farmError) {
    return <><header className="page-header"><div><p className="eyebrow">Mission control</p><h1 className="page-title">Farm state unavailable</h1></div><Badge tone="red">Simulation Mode</Badge></header><div className="panel"><div className="panel-heading"><div><h3>Unable to load current data</h3><p>{farmError}</p></div></div></div></>;
  }

  return <>
    <header className="page-header"><div><p className="eyebrow">Mission control / 18 Sep 2026</p><h1 className="page-title">Good morning, operator.</h1><p className="page-subtitle">A high-level view of what is changing across Shinde Farm, what the agent network recommends, and where human judgment is needed.</p></div><Badge tone="amber">DEMO / SIMULATION</Badge></header>
    <section className="goal-callout" aria-labelledby="active-goal"><p className="eyebrow">Active farmer goal</p><p id="active-goal">{goalText}</p><div className="goal-meta"><Badge tone="green">In planning</Badge><Badge tone="slate">Priority: {farmState?.goal?.priority ?? "high"}</Badge><Badge tone="slate">{farmState?.crop.crop ?? "Tomato"} / {farmState?.farm.area_acres ?? "4.8"} ha</Badge></div><div className="progress-track"><div className="progress-value" style={{ width: `${Math.min(planConfidence, 100)}%` }} /></div><div className="progress-label"><span>Plan confidence</span><strong>{Math.round(planConfidence)}%</strong></div></section>
    <section className="section-block" aria-labelledby="farm-signals"><SectionHeading eyebrow="Shared farm state" title="Signals at a glance" detail="Simulated readings from the current operating window." /><div className="dashboard-grid" id="farm-signals">{metrics.map((metric) => <MetricCard key={metric.label} metric={metric} />)}</div></section>
    <section className="section-block two-col"><Panel title="Current AI plan" detail={farmState?.plan ? `Plan ${farmState.plan.plan_id.slice(0, 8)} · ${farmState.plan.status}` : "No active plan yet"}><div className="decision-row"><span className="decision-code">01</span><div><strong>{farmState?.plan?.decision ?? "Awaiting planning"}</strong><p>{farmState?.plan?.rationale ?? "Generate a goal to create the first deterministic planning result."}</p></div><Badge tone={farmState?.plan ? "green" : "slate"}>{farmState?.plan ? "Verified" : "Pending"}</Badge></div><div className="progress-track"><div className="progress-value" style={{ width: `${farmState?.plan ? Math.min(farmState.plan.confidence, 100) : 0}%` }} /></div><div className="progress-label"><span>Constraint coverage</span><strong>{farmState?.plan ? `${Math.round(farmState.plan.confidence)}%` : "0%"}</strong></div><Link className="button-secondary" style={{ display: "inline-block", marginTop: "18px" }} href="/planning">Open plan studio</Link></Panel><Panel title="Pending farmer approval" detail={farmState?.approval ? `Status: ${farmState.approval.status}` : "Review the plan when it is ready"}><div className="decision-row"><span className="decision-code">IR</span><div><strong>{farmState?.plan?.decision ?? "No recommendation yet"}</strong><p>{farmState?.plan ? `Expected water saving: ${farmState.plan.expected_water_saved_liters.toFixed(0)} L` : "Generate a plan to see the recommendation."}</p></div></div><div className="goal-meta"><Badge tone="blue">{farmState?.plan ? `Confidence ${Math.round(farmState.plan.confidence)}%` : "Awaiting input"}</Badge><Badge tone={farmState?.approval?.status === "approved" ? "green" : "amber"}>{farmState?.approval?.status ? farmState.approval.status : "Review needed"}</Badge></div><Link className="button-primary" style={{ display: "inline-block", marginTop: "18px" }} href="/approvals">Review recommendation</Link></Panel></section>
    <p className="empty-note">Simulation Mode: all values on this page are generated by the deterministic AgriOS demo backend and not live field telemetry.</p>
  </>;
}
