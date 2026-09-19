"use client";

import { createContext, useContext, useMemo, useState } from "react";
import type { ApprovalResponse, FarmState, PlanSummary, PlanningResponse } from "@/types";

type AgriOSContextValue = {
  farmState: FarmState | null;
  setFarmState: (state: FarmState | null) => void;
  farmLoading: boolean;
  setFarmLoading: (loading: boolean) => void;
  farmError: string | null;
  setFarmError: (error: string | null) => void;
  currentPlan: PlanningResponse | null;
  setCurrentPlan: (plan: PlanningResponse | null) => void;
  planLoading: boolean;
  setPlanLoading: (loading: boolean) => void;
  planError: string | null;
  setPlanError: (error: string | null) => void;
  currentApproval: ApprovalResponse | null;
  setCurrentApproval: (approval: ApprovalResponse | null) => void;
  approvalLoading: boolean;
  setApprovalLoading: (loading: boolean) => void;
  approvalError: string | null;
  setApprovalError: (error: string | null) => void;
  currentReplan: PlanSummary | null;
  setCurrentReplan: (plan: PlanSummary | null) => void;
  replanLoading: boolean;
  setReplanLoading: (loading: boolean) => void;
  replanError: string | null;
  setReplanError: (error: string | null) => void;
};

const AgriOSContext = createContext<AgriOSContextValue | undefined>(undefined);

export function AgriOSProvider({ children }: { children: React.ReactNode }) {
  const [farmState, setFarmState] = useState<FarmState | null>(null);
  const [farmLoading, setFarmLoading] = useState(false);
  const [farmError, setFarmError] = useState<string | null>(null);

  const [currentPlan, setCurrentPlan] = useState<PlanningResponse | null>(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);

  const [currentApproval, setCurrentApproval] = useState<ApprovalResponse | null>(null);
  const [approvalLoading, setApprovalLoading] = useState(false);
  const [approvalError, setApprovalError] = useState<string | null>(null);

  const [currentReplan, setCurrentReplan] = useState<PlanSummary | null>(null);
  const [replanLoading, setReplanLoading] = useState(false);
  const [replanError, setReplanError] = useState<string | null>(null);

  const value = useMemo<AgriOSContextValue>(
    () => ({
      farmState,
      setFarmState,
      farmLoading,
      setFarmLoading,
      farmError,
      setFarmError,
      currentPlan,
      setCurrentPlan,
      planLoading,
      setPlanLoading,
      planError,
      setPlanError,
      currentApproval,
      setCurrentApproval,
      approvalLoading,
      setApprovalLoading,
      approvalError,
      setApprovalError,
      currentReplan,
      setCurrentReplan,
      replanLoading,
      setReplanLoading,
      replanError,
      setReplanError,
    }),
    [approvalError, approvalLoading, currentApproval, currentPlan, currentReplan, farmError, farmLoading, farmState, planError, planLoading, replanError, replanLoading],
  );

  return <AgriOSContext.Provider value={value}>{children}</AgriOSContext.Provider>;
}

export function useAgriOS() {
  const context = useContext(AgriOSContext);
  if (!context) {
    throw new Error("useAgriOS must be used within an AgriOSProvider");
  }

  return context;
}
