import os
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.database import engine, SessionLocal, Base
from backend.app.models.entities import (
    Patient, Observation, PatientBaseline, RiskAssessment,
    Alert, Task, AuditLog, DataQualityEvent, ModelVersion, StakeholderFeedback
)
from backend.app.services.data_quality_engine import DataQualityEngine
from backend.app.services.baseline_engine import BaselineEngine
from backend.app.services.trend_engine import TrendEngine
from backend.app.services.risk_engine import RiskEngine
from backend.app.services.alert_engine import AlertEngine
from backend.app.services.escalation_engine import EscalationEngine

def seed_database():
    print("Initializing database tables...", flush=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(StakeholderFeedback).delete()
        db.query(DataQualityEvent).delete()
        db.query(AuditLog).delete()
        db.query(Task).delete()
        db.query(Alert).delete()
        db.query(RiskAssessment).delete()
        db.query(PatientBaseline).delete()
        db.query(Observation).delete()
        db.query(Patient).delete()
        db.commit()

        print("Loading synthetic dataset for seeding...", flush=True)
        df_patients = pd.read_csv("data/synthetic/patients.csv")
        df_obs = pd.read_csv("data/synthetic/observations.csv")

        obs_by_patient = defaultdict(list)
        for r in df_obs.to_dict("records"):
            # Parse datetime
            r["timestamp"] = datetime.fromisoformat(str(r["timestamp"]))
            obs_by_patient[r["patient_id"]].append(r)

        print(f"Seeding {len(df_patients)} patients and their recovery state...", flush=True)
        
        batch_patients = []
        batch_observations = []
        batch_baselines = []
        batch_assessments = []
        batch_alerts = []
        batch_tasks = []
        batch_audit = []
        batch_dq_events = []

        now = datetime.utcnow()

        for idx, (_, p_row) in enumerate(df_patients.iterrows()):
            p_id = p_row["patient_id"]
            p_obs = obs_by_patient.get(p_id, [])
            if not p_obs:
                continue

            # Compute personal baseline
            init_window = p_obs[:min(5, len(p_obs))]
            baseline_dict = BaselineEngine.calculate_patient_baseline(init_window)
            
            pb = PatientBaseline(
                baseline_id=f"BASE-{p_id}",
                patient_id=p_id,
                baseline_pain=baseline_dict["baseline_pain"],
                baseline_temperature=baseline_dict["baseline_temperature"],
                baseline_wound_score=baseline_dict["baseline_wound_score"],
                pain_rolling_std=baseline_dict["pain_rolling_std"],
                temp_rolling_std=baseline_dict["temp_rolling_std"],
                wound_rolling_std=baseline_dict["wound_rolling_std"],
                observation_count=len(p_obs),
                last_updated=now
            )
            batch_baselines.append(pb)

            # Process observations
            for o in p_obs:
                obs_entity = Observation(
                    observation_id=o["observation_id"],
                    patient_id=p_id,
                    timestamp=o["timestamp"],
                    postoperative_day=int(o["postoperative_day"]),
                    pain_score=float(o["pain_score"]),
                    temperature=float(o["temperature"]),
                    wound_redness_score=float(o["wound_redness_score"]),
                    wound_swelling_score=float(o["wound_swelling_score"]),
                    wound_discharge_score=float(o["wound_discharge_score"]),
                    wound_pain_score=float(o["wound_pain_score"]),
                    composite_wound_score=float(o["composite_wound_score"]),
                    fatigue_score=float(o["fatigue_score"]),
                    nausea_score=float(o["nausea_score"]),
                    dizziness_score=float(o["dizziness_score"]),
                    mobility_score=float(o["mobility_score"]),
                    appetite_score=float(o["appetite_score"]),
                    patient_reported_concern=str(o["patient_reported_concern"]),
                    medication_adherence=str(o["medication_adherence"]),
                    sleep_quality=float(o["sleep_quality"]),
                    data_source=str(o["data_source"]),
                    measurement_quality=str(o["measurement_quality"]),
                    is_quarantined=bool(o["is_quarantined"]),
                    quarantine_reason=o.get("quarantine_reason") if pd.notna(o.get("quarantine_reason")) else None
                )
                batch_observations.append(obs_entity)

                # Flag quarantined records in DataQualityEvents
                if obs_entity.is_quarantined:
                    dq_ev = DataQualityEvent(
                        event_id=f"DQE-{uuid.uuid4().hex[:8].upper()}",
                        patient_id=p_id,
                        observation_id=obs_entity.observation_id,
                        timestamp=obs_entity.timestamp,
                        flag_type="RANGE_VIOLATION",
                        severity="Error",
                        description=str(obs_entity.quarantine_reason),
                        quarantined=True
                    )
                    batch_dq_events.append(dq_ev)

            # Latest observation evaluation
            latest_obs = p_obs[-1]
            is_valid, dq_score, dq_flags, _ = DataQualityEngine.validate_observation(
                latest_obs, p_obs[-5:-1] if len(p_obs) > 1 else []
            )

            final_devs = BaselineEngine.calculate_deviations(latest_obs, baseline_dict)
            final_trends = TrendEngine.analyze_trends(p_obs[-7:])
            risk_score, risk_cat, contribs, what_changed, why_no_alert = RiskEngine.calculate_risk_score(
                final_devs, final_trends, latest_obs, data_quality_score=dq_score, baseline=baseline_dict
            )

            # Trajectory group specific overrides for signature demo patients
            has_gap = False
            has_escalation = False
            primary_signal = "Normal Recovery"
            assigned_owner = "Unassigned"

            if p_id == "REC-001":
                primary_signal = "Post-op Improvement"
                assigned_owner = "Routine Monitor"
            elif p_id == "REC-002":
                primary_signal = "Isolated Transient Spike (Suppressed)"
                assigned_owner = "Watch Protocol"
            elif p_id == "REC-003":
                primary_signal = "Gradual Pain & Temperature Rise"
                assigned_owner = "Nurse Sarah (Team Alpha)"
            elif p_id == "REC-004":
                primary_signal = "Multi-Signal Concurrent Deterioration"
                assigned_owner = "Nurse Sarah (Team Alpha)"
            elif p_id == "REC-005":
                has_gap = True
                has_escalation = True
                primary_signal = "Reporting Gap > 48h (SLA Overdue)"
                assigned_owner = "Dr. Miller (Clinical Supervisor)"

            # Special monitoring gap detection for Group G
            if "Missing Data" in str(p_row.get("trajectory_group", "")) or has_gap:
                has_gap = True
                dq_gap = DataQualityEvent(
                    event_id=f"DQE-{uuid.uuid4().hex[:8].upper()}",
                    patient_id=p_id,
                    observation_id=latest_obs["observation_id"],
                    timestamp=now,
                    flag_type="MONITORING_GAP",
                    severity="Warning",
                    description=f"Patient {p_id} has not submitted home observations for > 36 hours.",
                    quarantined=False
                )
                batch_dq_events.append(dq_gap)

            # Patient entity
            p_entity = Patient(
                patient_id=p_id,
                age_group=str(p_row["age_group"]),
                surgery_type=str(p_row["surgery_type"]),
                surgery_date=datetime.fromisoformat(str(p_row["surgery_date"])),
                postoperative_day=int(p_row["postoperative_day"]),
                recovery_phase=str(p_row["recovery_phase"]),
                baseline_risk_category=str(p_row["baseline_risk_category"]),
                comorbidity_count=int(p_row["comorbidity_count"]),
                preferred_contact_method=str(p_row["preferred_contact_method"]),
                assigned_care_team=str(p_row["assigned_care_team"]),
                current_risk_score=risk_score,
                current_priority=risk_cat if not has_gap else "High Priority",
                current_trend_direction=final_trends["trajectory_direction"],
                latest_data_quality_score=dq_score,
                primary_signal=primary_signal if primary_signal != "Normal Recovery" else (
                    ", ".join(final_trends["agreeing_signals"]) if final_trends["agreeing_signals"] else "Normal Recovery"
                ),
                assigned_owner=assigned_owner,
                has_monitoring_gap=has_gap,
                has_active_escalation=has_escalation
            )
            batch_patients.append(p_entity)

            # Risk Assessment record
            ra = RiskAssessment(
                assessment_id=f"RA-{uuid.uuid4().hex[:8].upper()}",
                patient_id=p_id,
                timestamp=latest_obs["timestamp"],
                risk_score=risk_score if not has_gap else 85.0,
                risk_category=risk_cat if not has_gap else "High Priority",
                trend_direction=final_trends["trajectory_direction"],
                baseline_deviation_component=contribs["baseline_deviation"],
                rate_of_change_component=contribs["rate_of_change"],
                persistence_component=contribs["persistence"],
                multi_signal_component=contribs["multi_signal"],
                symptom_severity_component=contribs["symptom_severity"],
                data_quality_adjustment=contribs["data_quality_adjustment"],
                what_changed_summary=what_changed if not has_gap else "• Observation submission stopped for 48 hours.\n• Last known status had moderate fatigue.",
                why_no_alert_reason=why_no_alert,
                ml_deterioration_probability=round(risk_score / 100.0, 2)
            )
            batch_assessments.append(ra)

            # Generate Alert & Task if Review or High Priority, or Demo Cases
            alert = AlertEngine.evaluate_alert(
                patient_id=p_id,
                observation_id=latest_obs["observation_id"],
                risk_score=risk_score if not has_gap else 85.0,
                risk_category=risk_cat if not has_gap else "High Priority",
                trends=final_trends,
                what_changed_summary=what_changed,
                active_alerts=[]
            )

            if p_id == "REC-002" and not alert:
                # Force the suppressed alert record for demo inspection
                alert = {
                    "alert_id": f"ALT-{p_id}",
                    "patient_id": p_id,
                    "observation_id": latest_obs["observation_id"],
                    "timestamp": latest_obs["timestamp"],
                    "severity": "Watch",
                    "title": "Transient Variation Flagged (Alert Suppressed)",
                    "explanation": (
                        "• Single non-persistent deviation detected (Pain 6.5, Temp 38.0°C).\n"
                        "• Subsequent readings returned to patient baseline (Pain 3.0).\n"
                        "• Alert suppressed from main priority queue to prevent alert fatigue."
                    ),
                    "contributing_signals": "Transient Pain & Temp",
                    "episode_id": f"EP-{p_id}",
                    "is_suppressed": True,
                    "suppression_reason": "Low-value isolated spike: persistence and multi-signal criteria not met.",
                    "acknowledged": False
                }

            if alert:
                alert_entity = Alert(
                    alert_id=alert["alert_id"],
                    patient_id=p_id,
                    observation_id=alert.get("observation_id"),
                    timestamp=alert["timestamp"],
                    severity=alert["severity"],
                    title=alert["title"],
                    explanation=alert["explanation"],
                    contributing_signals=alert.get("contributing_signals"),
                    episode_id=alert.get("episode_id"),
                    is_suppressed=alert.get("is_suppressed", False),
                    suppression_reason=alert.get("suppression_reason"),
                    acknowledged=False
                )
                batch_alerts.append(alert_entity)

                # Create task for actionable alerts
                if not alert_entity.is_suppressed:
                    task_dict = EscalationEngine.create_task_for_alert(alert, p_entity.assigned_care_team)
                    if task_dict:
                        if p_id == "REC-005":
                            # Demo case 5: Overdue & Escalated to Supervisor
                            task_dict["status"] = "Escalated"
                            task_dict["escalation_level"] = 2
                            task_dict["assigned_role"] = "Clinical Supervisor"
                            task_dict["assigned_to"] = "Dr. Miller (Clinical Supervisor)"
                            task_dict["due_at"] = now - timedelta(hours=3) # overdue!

                        task_entity = Task(
                            task_id=task_dict["task_id"],
                            patient_id=p_id,
                            alert_id=task_dict.get("alert_id"),
                            priority=task_dict["priority"],
                            assigned_to=task_dict["assigned_to"],
                            assigned_role=task_dict["assigned_role"],
                            created_at=task_dict["created_at"],
                            due_at=task_dict["due_at"],
                            status=task_dict["status"],
                            escalation_level=task_dict["escalation_level"],
                            resolution_note=None,
                            resolved_at=None
                        )
                        batch_tasks.append(task_entity)

            # Audit log entry
            audit = AuditLog(
                log_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now - timedelta(minutes=idx % 60),
                actor="System Ingestion Engine",
                event_type="PATIENT_ASSESSMENT_COMPLETED",
                entity_id=p_id,
                description=f"Longitudinal assessment completed for patient {p_id}. Priority: {p_entity.current_priority}, Score: {p_entity.current_risk_score:.0f}.",
                metadata_json=None
            )
            batch_audit.append(audit)

        print(f"Committing {len(batch_patients)} patients, {len(batch_observations)} observations, {len(batch_alerts)} alerts, {len(batch_tasks)} tasks to SQLite...", flush=True)
        
        # Batch insert
        db.bulk_save_objects(batch_patients)
        db.bulk_save_objects(batch_observations)
        db.bulk_save_objects(batch_baselines)
        db.bulk_save_objects(batch_assessments)
        db.bulk_save_objects(batch_alerts)
        db.bulk_save_objects(batch_tasks)
        db.bulk_save_objects(batch_dq_events)
        db.bulk_save_objects(batch_audit)

        # Seed sample stakeholder feedback
        sample_feedback = [
            StakeholderFeedback(
                feedback_id=f"SF-{uuid.uuid4().hex[:6].upper()}",
                role="Nurse Reviewer",
                understanding_score=5,
                explainability_score=5,
                alert_reduction_satisfaction=5,
                comments="Grouping alerts into episodes and suppressing isolated spikes finally eliminates pager fatigue."
            ),
            StakeholderFeedback(
                feedback_id=f"SF-{uuid.uuid4().hex[:6].upper()}",
                role="Clinical Supervisor",
                understanding_score=5,
                explainability_score=4,
                alert_reduction_satisfaction=5,
                comments="The 'What Changed?' panel gives the exact clinical context in 5 seconds before contacting the patient."
            ),
            StakeholderFeedback(
                feedback_id=f"SF-{uuid.uuid4().hex[:6].upper()}",
                role="Care Coordinator",
                understanding_score=4,
                explainability_score=5,
                alert_reduction_satisfaction=5,
                comments="Escalation levels ensure that unanswered high-risk alerts don't slip through the cracks."
            )
        ]
        db.bulk_save_objects(sample_feedback)

        db.commit()
        print("Database seeded successfully with all clinical entities!", flush=True)

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
