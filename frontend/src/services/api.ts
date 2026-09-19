const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

import type {
  ApprovalRequest,
  ApprovalResponse,
  AuditEvent,
  FarmState,
  HealthResponse,
  PlanSummary,
  PlanningResponse,
} from "@/types";

function getApiBaseUrl() {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  return (configured && configured.length > 0 ? configured : DEFAULT_API_BASE_URL).replace(/\/$/, "");
}

function getErrorMessage(payload: unknown): string {
  if (payload && typeof payload === "object") {
    const record = payload as Record<string, unknown>;
    if (typeof record.detail === "string") return record.detail;
    if (Array.isArray(record.detail) && record.detail.length > 0) {
      const first = record.detail[0];
      if (first && typeof first === "object") {
        const issue = first as Record<string, unknown>;
        if (typeof issue.msg === "string") return issue.msg;
      }
    }
    if (typeof record.message === "string") return record.message;
  }
  return "The AgriOS service request failed.";
}

async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${path}`;

  try {
    const response = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
    });

    const contentType = response.headers.get("content-type") ?? "";

    let payload: unknown = null;
    try {
      payload = contentType.includes("application/json") ? await response.json() : await response.text();
    } catch {
      if (!response.ok) {
        throw new Error("The AgriOS service returned an unreadable response.");
      }
      return undefined as T;
    }

    if (!response.ok) {
      const message = getErrorMessage(payload);
      throw new Error(message || "Unable to reach the AgriOS planning service.");
    }

    if (payload === null || payload === undefined) {
      return undefined as T;
    }

    return payload as T;
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes("Failed to fetch") || error.message.includes("fetch")) {
        throw new Error("Unable to reach the AgriOS planning service.");
      }
      throw error;
    }

    throw new Error("Unable to reach the AgriOS planning service.");
  }
}

export async function getHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/api/health");
}

export async function getFarmState(): Promise<FarmState> {
  return apiRequest<FarmState>("/api/farms/demo/state");
}

export async function createPlan(goal: string): Promise<PlanningResponse> {
  return apiRequest<PlanningResponse>("/api/planning/demo", {
    method: "POST",
    body: JSON.stringify({ goal }),
  });
}

export async function getApproval(): Promise<ApprovalResponse | null> {
  return apiRequest<ApprovalResponse | null>("/api/approvals/demo");
}

export async function submitApproval(request: ApprovalRequest): Promise<ApprovalResponse> {
  return apiRequest<ApprovalResponse>("/api/approvals/demo", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function replan(planId: string): Promise<PlanSummary> {
  return apiRequest<PlanSummary>("/api/replanning/demo", {
    method: "POST",
    body: JSON.stringify({ plan_id: planId }),
  });
}

export async function getAuditEvents(): Promise<AuditEvent[]> {
  return apiRequest<AuditEvent[]>("/api/audit/demo");
}
