export interface PatientListItem {
  patient_id: string;
  age_group: string;
  surgery_type: string;
  postoperative_day: number;
  recovery_phase: string;
  baseline_risk_category: string;
  current_risk_score: number;
  current_priority: "Stable" | "Watch" | "Review" | "High Priority";
  current_trend_direction: "Improving" | "Stable" | "Worsening" | "Mixed" | "Unknown";
  latest_data_quality_score: number;
  primary_signal: string;
  assigned_owner: string;
  has_monitoring_gap: boolean;
  has_active_escalation: boolean;
}

export interface PatientBaseline {
  baseline_pain: number;
  baseline_temperature: number;
  baseline_wound_score: number;
  pain_rolling_std: number;
  temp_rolling_std: number;
  wound_rolling_std: number;
  observation_count: number;
  last_updated: string;
}

export interface RiskContributors {
  baseline_deviation: number;
  rate_of_change: number;
  persistence: number;
  multi_signal: number;
  symptom_severity: number;
  data_quality_adjustment: number;
  total_score: number;
}

export interface PatientDetail extends PatientListItem {
  surgery_date: string;
  comorbidity_count: number;
  preferred_contact_method: string;
  assigned_care_team: string;
  baseline?: PatientBaseline;
  what_changed_summary?: string;
  why_no_alert_reason?: string;
  risk_contributors?: RiskContributors;
}

export interface Observation {
  observation_id: string;
  patient_id: string;
  timestamp: string;
  postoperative_day: number;
  pain_score: number;
  temperature: number;
  wound_redness_score: number;
  wound_swelling_score: number;
  wound_discharge_score: number;
  wound_pain_score: number;
  composite_wound_score: number;
  fatigue_score: number;
  nausea_score: number;
  dizziness_score: number;
  mobility_score: number;
  appetite_score: number;
  patient_reported_concern: string;
  medication_adherence: string;
  sleep_quality: number;
  measurement_quality: string;
  is_quarantined: boolean;
  quarantine_reason?: string;
}

export interface Alert {
  alert_id: string;
  patient_id: string;
  observation_id?: string;
  timestamp: string;
  severity: "Watch" | "Review" | "High Priority";
  title: string;
  explanation: string;
  contributing_signals?: string;
  episode_id?: string;
  is_suppressed: boolean;
  suppression_reason?: string;
  acknowledged: boolean;
  acknowledged_at?: string;
  acknowledged_by?: string;
}

export interface Task {
  task_id: string;
  patient_id: string;
  alert_id?: string;
  priority: "Watch" | "Review" | "High Priority";
  assigned_to: string;
  assigned_role: string;
  created_at: string;
  due_at: string;
  status: "New" | "Assigned" | "Acknowledged" | "In Review" | "Resolved" | "Escalated" | "Closed";
  escalation_level: number;
  resolution_note?: string;
  resolved_at?: string;
}

export interface DashboardSummary {
  total_patients_monitored: number;
  active_high_priority_reviews: number;
  worsening_trend_count: number;
  monitoring_gap_count: number;
  unresolved_tasks_count: number;
  low_value_alert_reduction_pct: number;
  clinically_relevant_detection_rate_pct: number;
  average_response_time_minutes: number;
  active_model_version: string;
}

export interface SimulationResponse {
  scenario_name: string;
  trajectory_description: string;
  observations: any[];
  recoverai_result: {
    risk_score: number;
    risk_category: string;
    trend_direction: string;
    persistence_count: number;
    multi_signal_agreement: boolean;
    agreeing_signals: string[];
    alert_triggered: boolean;
    alert_severity: string;
    is_suppressed: boolean;
    suppression_reason: string;
    contributors: Record<string, number>;
  };
  simple_baseline_result: {
    total_alerts_triggered: number;
    alert_fatigue_risk: string;
    rule_description: string;
  };
  what_changed_summary: string;
  why_no_alert_explanation?: string;
}

export interface AuditLog {
  log_id: string;
  timestamp: string;
  actor: string;
  event_type: string;
  entity_id?: string;
  description: string;
  metadata_json?: string;
}
