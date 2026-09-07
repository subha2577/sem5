from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(String(64), primary_key=True, index=True)
    age_group = Column(String(32), nullable=False) # e.g. 18-35, 36-50, 51-65, 65+
    surgery_type = Column(String(64), nullable=False) # e.g. Orthopedic, Abdominal, Cardiac, Colorectal
    surgery_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    postoperative_day = Column(Integer, default=1)
    recovery_phase = Column(String(32), default="Early Post-Op") # Early Post-Op, Transition, Late Recovery
    baseline_risk_category = Column(String(32), default="Standard") # Low, Standard, Elevated
    comorbidity_count = Column(Integer, default=0)
    preferred_contact_method = Column(String(32), default="SMS")
    assigned_care_team = Column(String(64), default="Team Alpha")
    
    # Live summary cache fields for fast dashboard queries
    current_risk_score = Column(Float, default=15.0)
    current_priority = Column(String(32), default="Stable") # Stable, Watch, Review, High Priority
    current_trend_direction = Column(String(32), default="Stable") # Improving, Stable, Worsening, Mixed, Unknown
    latest_data_quality_score = Column(Float, default=95.0)
    primary_signal = Column(String(64), default="Normal Recovery")
    assigned_owner = Column(String(64), default="Unassigned")
    has_monitoring_gap = Column(Boolean, default=False)
    has_active_escalation = Column(Boolean, default=False)

    observations = relationship("Observation", back_populates="patient", cascade="all, delete-orphan")
    baselines = relationship("PatientBaseline", back_populates="patient", uselist=False, cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="patient", cascade="all, delete-orphan")


class Observation(Base):
    __tablename__ = "observations"

    observation_id = Column(String(64), primary_key=True, index=True)
    patient_id = Column(String(64), ForeignKey("patients.patient_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    postoperative_day = Column(Integer, default=1)
    
    # Core Vitals & Wound observations
    pain_score = Column(Float, nullable=False) # 0 - 10
    temperature = Column(Float, nullable=False) # Celsius (e.g. 36.5 - 39.5)
    wound_redness_score = Column(Float, default=0.0) # 0 - 5
    wound_swelling_score = Column(Float, default=0.0) # 0 - 5
    wound_discharge_score = Column(Float, default=0.0) # 0 - 5
    wound_pain_score = Column(Float, default=0.0) # 0 - 5
    composite_wound_score = Column(Float, default=0.0) # normalized 0 - 10
    
    # Symptoms & Wellness indicators
    fatigue_score = Column(Float, default=2.0) # 0 - 10
    nausea_score = Column(Float, default=0.0) # 0 - 10
    dizziness_score = Column(Float, default=0.0) # 0 - 10
    mobility_score = Column(Float, default=7.0) # 0 - 10 (higher is better)
    appetite_score = Column(Float, default=7.0) # 0 - 10 (higher is better)
    patient_reported_concern = Column(String(64), default="None") # None, Mild, Moderate, Severe
    medication_adherence = Column(String(32), default="Full") # Full, Missed Dose, Stopped
    sleep_quality = Column(Float, default=7.0) # 0 - 10
    
    # Ingestion & Quality metadata
    data_source = Column(String(32), default="Mobile App") # Mobile App, Smart Patch, Manual Entry
    measurement_quality = Column(String(32), default="Good") # Good, Fair, Poor
    is_quarantined = Column(Boolean, default=False)
    quarantine_reason = Column(String(256), nullable=True)

    patient = relationship("Patient", back_populates="observations")


class PatientBaseline(Base):
    __tablename__ = "patient_baselines"

    baseline_id = Column(String(64), primary_key=True)
    patient_id = Column(String(64), ForeignKey("patients.patient_id"), unique=True, nullable=False, index=True)
    baseline_pain = Column(Float, default=3.0)
    baseline_temperature = Column(Float, default=36.8)
    baseline_wound_score = Column(Float, default=1.0)
    pain_rolling_std = Column(Float, default=0.5)
    temp_rolling_std = Column(Float, default=0.2)
    wound_rolling_std = Column(Float, default=0.3)
    observation_count = Column(Integer, default=5)
    last_updated = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="baselines")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    assessment_id = Column(String(64), primary_key=True, index=True)
    patient_id = Column(String(64), ForeignKey("patients.patient_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    risk_score = Column(Float, nullable=False) # 0 - 100
    risk_category = Column(String(32), nullable=False) # Stable, Watch, Review, High Priority
    trend_direction = Column(String(32), default="Stable")
    
    # Explainable Contributor Weights
    baseline_deviation_component = Column(Float, default=0.0)
    rate_of_change_component = Column(Float, default=0.0)
    persistence_component = Column(Float, default=0.0)
    multi_signal_component = Column(Float, default=0.0)
    symptom_severity_component = Column(Float, default=0.0)
    data_quality_adjustment = Column(Float, default=0.0)
    
    # Signature Explainability Strings
    what_changed_summary = Column(Text, nullable=True)
    why_no_alert_reason = Column(Text, nullable=True)
    ml_deterioration_probability = Column(Float, default=0.0)

    patient = relationship("Patient", back_populates="risk_assessments")


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(64), primary_key=True, index=True)
    patient_id = Column(String(64), ForeignKey("patients.patient_id"), nullable=False, index=True)
    observation_id = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    severity = Column(String(32), nullable=False) # Watch, Review, High Priority
    title = Column(String(128), nullable=False)
    explanation = Column(Text, nullable=False) # Detailed bullet points
    contributing_signals = Column(Text, nullable=True) # JSON or semicolon separated
    
    episode_id = Column(String(64), index=True) # Grouping identifier for deduplication
    is_suppressed = Column(Boolean, default=False)
    suppression_reason = Column(String(256), nullable=True)
    
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(64), nullable=True)

    patient = relationship("Patient", back_populates="alerts")


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(String(64), primary_key=True, index=True)
    patient_id = Column(String(64), ForeignKey("patients.patient_id"), nullable=False, index=True)
    alert_id = Column(String(64), nullable=True, index=True)
    
    priority = Column(String(32), default="Review") # Watch, Review, High Priority
    assigned_to = Column(String(64), default="Nurse Reviewer")
    assigned_role = Column(String(64), default="Nurse Reviewer") # Care Coordinator, Nurse Reviewer, Clinical Supervisor, Escalation Manager
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    due_at = Column(DateTime, nullable=False, index=True)
    status = Column(String(32), default="New") # New, Assigned, Acknowledged, In Review, Resolved, Escalated, Closed
    escalation_level = Column(Integer, default=1) # 1: Team, 2: Supervisor, 3: Escalation Queue
    
    resolution_note = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    patient = relationship("Patient", back_populates="tasks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    actor = Column(String(64), default="System Engine")
    event_type = Column(String(64), nullable=False) # e.g. OBSERVATION_INGESTED, ALERT_TRIGGERED, TASK_ESCALATED
    entity_id = Column(String(64), nullable=True)
    description = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)


class DataQualityEvent(Base):
    __tablename__ = "data_quality_events"

    event_id = Column(String(64), primary_key=True, index=True)
    patient_id = Column(String(64), nullable=False, index=True)
    observation_id = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    flag_type = Column(String(64), nullable=False) # RANGE_VIOLATION, SUDDEN_JUMP, DUPLICATE_ENTRY, CONTRADICTORY_SIGNALS, MONITORING_GAP
    severity = Column(String(32), default="Warning") # Info, Warning, Error
    description = Column(Text, nullable=False)
    quarantined = Column(Boolean, default=False)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    version_id = Column(String(64), primary_key=True)
    model_name = Column(String(64), default="trend-risk-engine")
    version_tag = Column(String(32), default="v1.0.0")
    trained_at = Column(DateTime, default=datetime.utcnow)
    metrics_json = Column(Text, nullable=False)
    feature_importance_json = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)


class StakeholderFeedback(Base):
    __tablename__ = "stakeholder_feedback"

    feedback_id = Column(String(64), primary_key=True)
    role = Column(String(64), nullable=False)
    understanding_score = Column(Integer, default=5) # 1-5
    explainability_score = Column(Integer, default=5) # 1-5
    alert_reduction_satisfaction = Column(Integer, default=5) # 1-5
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
