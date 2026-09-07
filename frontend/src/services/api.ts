import {
  PatientListItem, PatientDetail, Observation, Alert, Task,
  DashboardSummary, SimulationResponse, AuditLog
} from "../types";

const API_BASE = "/api";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Health
  getHealth: () => fetchJson<any>(`${API_BASE}/health`),

  // Dashboard
  getDashboardSummary: () => fetchJson<DashboardSummary>(`${API_BASE}/dashboard/summary`),
  getPriorityBreakdown: () => fetchJson<Record<string, number>>(`${API_BASE}/dashboard/priority-breakdown`),
  getTrendBreakdown: () => fetchJson<Record<string, number>>(`${API_BASE}/dashboard/trend-breakdown`),
  getRecentAlerts: () => fetchJson<Alert[]>(`${API_BASE}/dashboard/recent-alerts`),

  // Patients
  getPatients: (params?: {
    priority?: string;
    trend?: string;
    has_gap?: boolean;
    search?: string;
    limit?: number;
    sort_by?: string;
  }) => {
    const q = new URLSearchParams();
    if (params?.priority && params.priority !== "All") q.append("priority", params.priority);
    if (params?.trend && params.trend !== "All") q.append("trend", params.trend);
    if (params?.has_gap !== undefined) q.append("has_gap", String(params.has_gap));
    if (params?.search) q.append("search", params.search);
    if (params?.limit) q.append("limit", String(params.limit));
    if (params?.sort_by) q.append("sort_by", params.sort_by);
    return fetchJson<PatientListItem[]>(`${API_BASE}/patients?${q.toString()}`);
  },

  getPatientDetail: (id: string) => fetchJson<PatientDetail>(`${API_BASE}/patients/${id}`),
  getPatientTimeline: (id: string) => fetchJson<Observation[]>(`${API_BASE}/patients/${id}/timeline`),

  // Observations Ingestion
  createObservation: (obs: any) =>
    fetchJson<Observation>(`${API_BASE}/observations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(obs)
    }),

  // Alerts
  getAlerts: (severity?: string, includeSuppressed: boolean = false) => {
    const q = new URLSearchParams();
    if (severity && severity !== "All") q.append("severity", severity);
    if (includeSuppressed) q.append("include_suppressed", "true");
    return fetchJson<Alert[]>(`${API_BASE}/alerts?${q.toString()}`);
  },

  acknowledgeAlert: (alertId: string, clinicianName: string = "Nurse Reviewer") =>
    fetchJson<any>(`${API_BASE}/alerts/${alertId}/acknowledge?clinician_name=${encodeURIComponent(clinicianName)}`, {
      method: "POST"
    }),

  // Tasks
  getTasks: (status?: string, priority?: string) => {
    const q = new URLSearchParams();
    if (status && status !== "All") q.append("status", status);
    if (priority && priority !== "All") q.append("priority", priority);
    return fetchJson<Task[]>(`${API_BASE}/tasks?${q.toString()}`);
  },

  updateTask: (taskId: string, update: { status?: string; resolution_note?: string; escalation_level?: number }) =>
    fetchJson<Task>(`${API_BASE}/tasks/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(update)
    }),

  checkEscalations: () => fetchJson<any>(`${API_BASE}/tasks/check-escalations`, { method: "POST" }),

  // Simulation
  runSimulation: (req: { trajectory_group: string; baseline_pain?: number; baseline_temp?: number; observation_steps?: number }) =>
    fetchJson<SimulationResponse>(`${API_BASE}/simulation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req)
    }),

  // Analytics & Model
  getAnalytics: () => fetchJson<any>(`${API_BASE}/analytics`),
  getModelPerformance: () => fetchJson<any>(`${API_BASE}/model/performance`),

  // Data Quality
  getDataQualitySummary: () => fetchJson<any>(`${API_BASE}/data-quality/summary`),
  getDataQualityEvents: () => fetchJson<any[]>(`${API_BASE}/data-quality/events`),

  // Audit
  getAuditLogs: () => fetchJson<AuditLog[]>(`${API_BASE}/audit`),

  // Stakeholder
  getStakeholderSummary: () => fetchJson<any>(`${API_BASE}/stakeholder-feedback/summary`),
  submitStakeholderFeedback: (fb: { role: string; understanding_score: number; explainability_score: number; alert_reduction_satisfaction: number; comments?: string }) =>
    fetchJson<any>(`${API_BASE}/stakeholder-feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(fb)
    })
};
