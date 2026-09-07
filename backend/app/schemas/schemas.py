from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ObservationCreate(BaseModel):
    patient_id: str
    postoperative_day: Optional[int] = 1
    pain_score: float = Field(..., ge=0.0, le=10.0)
    temperature: float = Field(..., ge=34.0, le=43.0)
    wound_redness_score: float = Field(0.0, ge=0.0, le=5.0)
    wound_swelling_score: float = Field(0.0, ge=0.0, le=5.0)
    wound_discharge_score: float = Field(0.0, ge=0.0, le=5.0)
    wound_pain_score: float = Field(0.0, ge=0.0, le=5.0)
    fatigue_score: float = Field(2.0, ge=0.0, le=10.0)
    nausea_score: float = Field(0.0, ge=0.0, le=10.0)
    dizziness_score: float = Field(0.0, ge=0.0, le=10.0)
    mobility_score: float = Field(7.0, ge=0.0, le=10.0)
    appetite_score: float = Field(7.0, ge=0.0, le=10.0)
    patient_reported_concern: str = "None"
    medication_adherence: str = "Full"
    sleep_quality: float = Field(7.0, ge=0.0, le=10.0)
    data_source: str = "Mobile App"
    timestamp: Optional[datetime] = None

class ObservationResponse(BaseModel):
    observation_id: str
    patient_id: str
    timestamp: datetime
    postoperative_day: int
    pain_score: float
    temperature: float
    wound_redness_score: float
    wound_swelling_score: float
    wound_discharge_score: float
    wound_pain_score: float
    composite_wound_score: float
    fatigue_score: float
    nausea_score: float
    dizziness_score: float
    mobility_score: float
    appetite_score: float
    patient_reported_concern: str
    medication_adherence: str
    sleep_quality: float
    measurement_quality: str
    is_quarantined: bool
    quarantine_reason: Optional[str] = None

    class Config:
        from_attributes = True

class PatientBaselineResponse(BaseModel):
    baseline_pain: float
    baseline_temperature: float
    baseline_wound_score: float
    pain_rolling_std: float
    temp_rolling_std: float
    wound_rolling_std: float
    observation_count: int
    last_updated: datetime

    class Config:
        from_attributes = True

class RiskContributorsResponse(BaseModel):
    baseline_deviation: float
    rate_of_change: float
    persistence: float
    multi_signal: float
    symptom_severity: float
    data_quality_adjustment: float
    total_score: float

class PatientListItem(BaseModel):
    patient_id: str
    age_group: str
    surgery_type: str
    postoperative_day: int
    recovery_phase: str
    baseline_risk_category: str
    current_risk_score: float
    current_priority: str
    current_trend_direction: str
    latest_data_quality_score: float
    primary_signal: str
    assigned_owner: str
    has_monitoring_gap: bool
    has_active_escalation: bool

    class Config:
        from_attributes = True

class PatientDetailResponse(PatientListItem):
    surgery_date: datetime
    comorbidity_count: int
    preferred_contact_method: str
    assigned_care_team: str
    baseline: Optional[PatientBaselineResponse] = None
    what_changed_summary: Optional[str] = None
    why_no_alert_reason: Optional[str] = None
    risk_contributors: Optional[RiskContributorsResponse] = None

class AlertResponse(BaseModel):
    alert_id: str
    patient_id: str
    observation_id: Optional[str] = None
    timestamp: datetime
    severity: str
    title: str
    explanation: str
    contributing_signals: Optional[str] = None
    episode_id: Optional[str] = None
    is_suppressed: bool
    suppression_reason: Optional[str] = None
    acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    task_id: str
    patient_id: str
    alert_id: Optional[str] = None
    priority: str
    assigned_to: str
    assigned_role: str
    created_at: datetime
    due_at: datetime
    status: str
    escalation_level: int
    resolution_note: Optional[str] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_role: Optional[str] = None
    resolution_note: Optional[str] = None
    escalation_level: Optional[int] = None

class DashboardSummaryResponse(BaseModel):
    total_patients_monitored: int
    active_high_priority_reviews: int
    worsening_trend_count: int
    monitoring_gap_count: int
    unresolved_tasks_count: int
    low_value_alert_reduction_pct: float
    clinically_relevant_detection_rate_pct: float
    average_response_time_minutes: float
    active_model_version: str

class SimulationRequest(BaseModel):
    trajectory_group: str # Group A - J or Demo 1 - 5
    baseline_pain: Optional[float] = 3.0
    baseline_temp: Optional[float] = 36.8
    observation_steps: Optional[int] = 7

class SimulationResponse(BaseModel):
    scenario_name: str
    trajectory_description: str
    observations: List[Dict[str, Any]]
    recoverai_result: Dict[str, Any]
    simple_baseline_result: Dict[str, Any]
    what_changed_summary: str
    why_no_alert_explanation: Optional[str] = None

class StakeholderFeedbackCreate(BaseModel):
    role: str
    understanding_score: int = Field(5, ge=1, le=5)
    explainability_score: int = Field(5, ge=1, le=5)
    alert_reduction_satisfaction: int = Field(5, ge=1, le=5)
    comments: Optional[str] = None

class StakeholderFeedbackResponse(StakeholderFeedbackCreate):
    feedback_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class DataQualityEventResponse(BaseModel):
    event_id: str
    patient_id: str
    observation_id: Optional[str] = None
    timestamp: datetime
    flag_type: str
    severity: str
    description: str
    quarantined: bool

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    log_id: str
    timestamp: datetime
    actor: str
    event_type: str
    entity_id: Optional[str] = None
    description: str
    metadata_json: Optional[str] = None

    class Config:
        from_attributes = True
