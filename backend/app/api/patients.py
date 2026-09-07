from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from backend.app.database import get_db
from backend.app.models.entities import Patient, Observation, PatientBaseline, RiskAssessment, Alert, Task
from backend.app.schemas.schemas import (
    PatientListItem, PatientDetailResponse, PatientBaselineResponse,
    RiskContributorsResponse, ObservationResponse
)

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("", response_model=List[PatientListItem])
def list_patients(
    skip: int = 0,
    limit: int = 50,
    priority: Optional[str] = None,
    trend: Optional[str] = None,
    has_gap: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "risk_desc",
    db: Session = Depends(get_db)
):
    query = db.query(Patient)

    if priority and priority != "All":
        query = query.filter(Patient.current_priority == priority)
    if trend and trend != "All":
        query = query.filter(Patient.current_trend_direction == trend)
    if has_gap is not None:
        query = query.filter(Patient.has_monitoring_gap == has_gap)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Patient.patient_id.ilike(search_pattern),
                Patient.surgery_type.ilike(search_pattern),
                Patient.assigned_owner.ilike(search_pattern),
                Patient.primary_signal.ilike(search_pattern)
            )
        )

    # Sorting
    if sort_by == "risk_desc":
        query = query.order_by(desc(Patient.current_risk_score))
    elif sort_by == "risk_asc":
        query = query.order_by(asc(Patient.current_risk_score))
    elif sort_by == "post_op_day":
        query = query.order_by(desc(Patient.postoperative_day))
    else:
        query = query.order_by(desc(Patient.current_risk_score))

    return query.offset(skip).limit(limit).all()

@router.get("/{patient_id}", response_model=PatientDetailResponse)
def get_patient_detail(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

    baseline = db.query(PatientBaseline).filter(PatientBaseline.patient_id == patient_id).first()
    latest_assessment = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.patient_id == patient_id)
        .order_by(desc(RiskAssessment.timestamp))
        .first()
    )

    baseline_resp = None
    if baseline:
        baseline_resp = PatientBaselineResponse(
            baseline_pain=baseline.baseline_pain,
            baseline_temperature=baseline.baseline_temperature,
            baseline_wound_score=baseline.baseline_wound_score,
            pain_rolling_std=baseline.pain_rolling_std,
            temp_rolling_std=baseline.temp_rolling_std,
            wound_rolling_std=baseline.wound_rolling_std,
            observation_count=baseline.observation_count,
            last_updated=baseline.last_updated
        )

    risk_contribs = None
    what_changed = None
    why_no_alert = None
    if latest_assessment:
        what_changed = latest_assessment.what_changed_summary
        why_no_alert = latest_assessment.why_no_alert_reason
        risk_contribs = RiskContributorsResponse(
            baseline_deviation=latest_assessment.baseline_deviation_component,
            rate_of_change=latest_assessment.rate_of_change_component,
            persistence=latest_assessment.persistence_component,
            multi_signal=latest_assessment.multi_signal_component,
            symptom_severity=latest_assessment.symptom_severity_component,
            data_quality_adjustment=latest_assessment.data_quality_adjustment,
            total_score=latest_assessment.risk_score
        )

    return PatientDetailResponse(
        patient_id=patient.patient_id,
        age_group=patient.age_group,
        surgery_type=patient.surgery_type,
        surgery_date=patient.surgery_date,
        postoperative_day=patient.postoperative_day,
        recovery_phase=patient.recovery_phase,
        baseline_risk_category=patient.baseline_risk_category,
        comorbidity_count=patient.comorbidity_count,
        preferred_contact_method=patient.preferred_contact_method,
        assigned_care_team=patient.assigned_care_team,
        current_risk_score=patient.current_risk_score,
        current_priority=patient.current_priority,
        current_trend_direction=patient.current_trend_direction,
        latest_data_quality_score=patient.latest_data_quality_score,
        primary_signal=patient.primary_signal,
        assigned_owner=patient.assigned_owner,
        has_monitoring_gap=patient.has_monitoring_gap,
        has_active_escalation=patient.has_active_escalation,
        baseline=baseline_resp,
        what_changed_summary=what_changed,
        why_no_alert_reason=why_no_alert,
        risk_contributors=risk_contribs
    )

@router.get("/{patient_id}/timeline", response_model=List[ObservationResponse])
def get_patient_timeline(patient_id: str, db: Session = Depends(get_db)):
    obs = (
        db.query(Observation)
        .filter(Observation.patient_id == patient_id)
        .order_by(asc(Observation.timestamp))
        .all()
    )
    if not obs:
        raise HTTPException(status_code=404, detail=f"No observations found for patient {patient_id}")
    return obs
