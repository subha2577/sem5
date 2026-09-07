import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.database import get_db
from backend.app.models.entities import (
    Patient, Observation, PatientBaseline, RiskAssessment, Alert, Task, AuditLog, DataQualityEvent
)
from backend.app.schemas.schemas import ObservationCreate, ObservationResponse
from backend.app.services.data_quality_engine import DataQualityEngine
from backend.app.services.baseline_engine import BaselineEngine
from backend.app.services.trend_engine import TrendEngine
from backend.app.services.risk_engine import RiskEngine
from backend.app.services.alert_engine import AlertEngine
from backend.app.services.escalation_engine import EscalationEngine

router = APIRouter(prefix="/observations", tags=["Observations"])

@router.post("", response_model=ObservationResponse)
def create_observation(payload: ObservationCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == payload.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient {payload.patient_id} not found")

    obs_time = payload.timestamp or datetime.utcnow()
    composite_wound = DataQualityEngine.calculate_composite_wound_score(
        payload.wound_redness_score,
        payload.wound_swelling_score,
        payload.wound_discharge_score,
        payload.wound_pain_score
    )

    obs_dict = {
        "observation_id": f"OBS-{uuid.uuid4().hex[:8].upper()}",
        "patient_id": payload.patient_id,
        "timestamp": obs_time,
        "postoperative_day": payload.postoperative_day or patient.postoperative_day,
        "pain_score": payload.pain_score,
        "temperature": payload.temperature,
        "wound_redness_score": payload.wound_redness_score,
        "wound_swelling_score": payload.wound_swelling_score,
        "wound_discharge_score": payload.wound_discharge_score,
        "wound_pain_score": payload.wound_pain_score,
        "composite_wound_score": composite_wound,
        "fatigue_score": payload.fatigue_score,
        "nausea_score": payload.nausea_score,
        "dizziness_score": payload.dizziness_score,
        "mobility_score": payload.mobility_score,
        "appetite_score": payload.appetite_score,
        "patient_reported_concern": payload.patient_reported_concern,
        "medication_adherence": payload.medication_adherence,
        "sleep_quality": payload.sleep_quality,
        "data_source": payload.data_source
    }

    # Fetch recent history for dynamic checks
    recent_obs_entities = (
        db.query(Observation)
        .filter(Observation.patient_id == payload.patient_id)
        .order_by(desc(Observation.timestamp))
        .limit(7)
        .all()
    )
    recent_history = [
        {
            "pain_score": o.pain_score,
            "temperature": o.temperature,
            "composite_wound_score": o.composite_wound_score,
            "timestamp": o.timestamp,
            "is_quarantined": o.is_quarantined
        }
        for o in reversed(recent_obs_entities)
    ]

    # 1. Data Quality Validation
    is_valid, dq_score, dq_flags, quarantine_reason = DataQualityEngine.validate_observation(
        obs_dict, recent_history
    )

    obs_entity = Observation(
        observation_id=obs_dict["observation_id"],
        patient_id=payload.patient_id,
        timestamp=obs_time,
        postoperative_day=obs_dict["postoperative_day"],
        pain_score=payload.pain_score,
        temperature=payload.temperature,
        wound_redness_score=payload.wound_redness_score,
        wound_swelling_score=payload.wound_swelling_score,
        wound_discharge_score=payload.wound_discharge_score,
        wound_pain_score=payload.wound_pain_score,
        composite_wound_score=composite_wound,
        fatigue_score=payload.fatigue_score,
        nausea_score=payload.nausea_score,
        dizziness_score=payload.dizziness_score,
        mobility_score=payload.mobility_score,
        appetite_score=payload.appetite_score,
        patient_reported_concern=payload.patient_reported_concern,
        medication_adherence=payload.medication_adherence,
        sleep_quality=payload.sleep_quality,
        data_source=payload.data_source,
        measurement_quality="Good" if dq_score >= 80 else ("Fair" if dq_score >= 50 else "Poor"),
        is_quarantined=not is_valid,
        quarantine_reason=quarantine_reason
    )
    db.add(obs_entity)

    # Log any DQ flags
    for fl in dq_flags:
        dqe = DataQualityEvent(
            event_id=f"DQE-{uuid.uuid4().hex[:8].upper()}",
            patient_id=payload.patient_id,
            observation_id=obs_entity.observation_id,
            timestamp=obs_time,
            flag_type=fl["flag_type"],
            severity=fl["severity"],
            description=fl["description"],
            quarantined=not is_valid
        )
        db.add(dqe)

    # If valid, run baseline, trend, and risk calculations
    if is_valid:
        patient.has_monitoring_gap = False
        full_window = recent_history + [obs_dict]
        baseline_record = db.query(PatientBaseline).filter(PatientBaseline.patient_id == payload.patient_id).first()
        
        baseline_dict = {
            "baseline_pain": baseline_record.baseline_pain if baseline_record else 3.0,
            "baseline_temperature": baseline_record.baseline_temperature if baseline_record else 36.8,
            "baseline_wound_score": baseline_record.baseline_wound_score if baseline_record else 1.0,
            "pain_rolling_std": baseline_record.pain_rolling_std if baseline_record else 0.5,
            "temp_rolling_std": baseline_record.temp_rolling_std if baseline_record else 0.2,
            "wound_rolling_std": baseline_record.wound_rolling_std if baseline_record else 0.3
        }

        deviations = BaselineEngine.calculate_deviations(obs_dict, baseline_dict)
        trends = TrendEngine.analyze_trends(full_window)
        risk_score, risk_cat, contribs, what_changed, why_no_alert = RiskEngine.calculate_risk_score(
            deviations, trends, obs_dict, data_quality_score=dq_score, baseline=baseline_dict
        )

        # Update patient summary fields
        patient.current_risk_score = risk_score
        patient.current_priority = risk_cat
        patient.current_trend_direction = trends["trajectory_direction"]
        patient.latest_data_quality_score = dq_score
        if trends["agreeing_signals"]:
            patient.primary_signal = f"Deteriorating: {', '.join(trends['agreeing_signals'])}"

        # Save Assessment
        ra = RiskAssessment(
            assessment_id=f"RA-{uuid.uuid4().hex[:8].upper()}",
            patient_id=payload.patient_id,
            timestamp=obs_time,
            risk_score=risk_score,
            risk_category=risk_cat,
            trend_direction=trends["trajectory_direction"],
            baseline_deviation_component=contribs["baseline_deviation"],
            rate_of_change_component=contribs["rate_of_change"],
            persistence_component=contribs["persistence"],
            multi_signal_component=contribs["multi_signal"],
            symptom_severity_component=contribs["symptom_severity"],
            data_quality_adjustment=contribs["data_quality_adjustment"],
            what_changed_summary=what_changed,
            why_no_alert_reason=why_no_alert,
            ml_deterioration_probability=round(risk_score / 100.0, 2)
        )
        db.add(ra)

        # Evaluate Alert
        active_db_alerts = (
            db.query(Alert)
            .filter(Alert.patient_id == payload.patient_id, Alert.acknowledged == False)
            .all()
        )
        active_list = [{"severity": a.severity, "episode_id": a.episode_id, "alert_id": a.alert_id} for a in active_db_alerts]

        alert_dict = AlertEngine.evaluate_alert(
            patient_id=payload.patient_id,
            observation_id=obs_entity.observation_id,
            risk_score=risk_score,
            risk_category=risk_cat,
            trends=trends,
            what_changed_summary=what_changed,
            active_alerts=active_list
        )

        if alert_dict:
            alert_ent = Alert(
                alert_id=alert_dict["alert_id"],
                patient_id=payload.patient_id,
                observation_id=alert_dict.get("observation_id"),
                timestamp=alert_dict["timestamp"],
                severity=alert_dict["severity"],
                title=alert_dict["title"],
                explanation=alert_dict["explanation"],
                contributing_signals=alert_dict.get("contributing_signals"),
                episode_id=alert_dict.get("episode_id"),
                is_suppressed=alert_dict.get("is_suppressed", False),
                suppression_reason=alert_dict.get("suppression_reason"),
                acknowledged=False
            )
            db.add(alert_ent)

            if not alert_ent.is_suppressed:
                task_dict = EscalationEngine.create_task_for_alert(alert_dict, patient.assigned_care_team)
                if task_dict:
                    task_ent = Task(
                        task_id=task_dict["task_id"],
                        patient_id=payload.patient_id,
                        alert_id=alert_ent.alert_id,
                        priority=task_dict["priority"],
                        assigned_to=task_dict["assigned_to"],
                        assigned_role=task_dict["assigned_role"],
                        created_at=task_dict["created_at"],
                        due_at=task_dict["due_at"],
                        status=task_dict["status"],
                        escalation_level=task_dict["escalation_level"]
                    )
                    db.add(task_ent)
                    patient.assigned_owner = task_dict["assigned_to"]

    # Audit log
    audit = AuditLog(
        log_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        timestamp=obs_time,
        actor="Mobile Ingestion Stream",
        event_type="OBSERVATION_INGESTED",
        entity_id=obs_entity.observation_id,
        description=f"Observation received for {payload.patient_id}. Valid: {is_valid}, Quality: {dq_score:.0f}."
    )
    db.add(audit)

    db.commit()
    db.refresh(obs_entity)
    return obs_entity
