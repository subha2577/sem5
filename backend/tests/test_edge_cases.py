"""
RecoverAI -- Additional Edge Case and Failure Mode Tests
Covers requirements: failure cases, test suite, ownership/due dates, trend summariser
"""
import pytest
from datetime import datetime, timedelta
from backend.app.services.baseline_engine import BaselineEngine, MINIMUM_RELIABLE_BASELINE_OBS
from backend.app.services.trend_engine import TrendEngine
from backend.app.services.risk_engine import RiskEngine
from backend.app.services.alert_engine import AlertEngine
from backend.app.services.escalation_engine import EscalationEngine
from backend.app.services.data_quality_engine import DataQualityEngine


# --- FAILURE CASE 1: INSUFFICIENT BASELINE (NEW PATIENT) ---

def test_insufficient_baseline_flags_uncertain():
    history = [{"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0}]
    baseline = BaselineEngine.calculate_patient_baseline(history)
    assert baseline["baseline_uncertain"] is True
    assert baseline["baseline_uncertainty_note"] is not None
    assert "CAUTION" in baseline["baseline_uncertainty_note"]
    assert baseline["observation_count"] < MINIMUM_RELIABLE_BASELINE_OBS


def test_zero_history_baseline_uncertain():
    baseline = BaselineEngine.calculate_patient_baseline([])
    assert baseline["baseline_uncertain"] is True
    assert baseline["observation_count"] == 0


def test_sufficient_history_not_flagged_uncertain():
    history = [
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0},
        {"pain_score": 3.2, "temperature": 36.9, "composite_wound_score": 1.0},
        {"pain_score": 2.8, "temperature": 36.7, "composite_wound_score": 0.9},
    ]
    baseline = BaselineEngine.calculate_patient_baseline(history)
    assert baseline["baseline_uncertain"] is False
    assert baseline["baseline_uncertainty_note"] is None


# --- FAILURE CASE 2: INVALID DATA / DATA QUALITY ---

def test_invalid_temperature_quarantined():
    obs = {"pain_score": 5.0, "temperature": 44.5, "wound_redness_score": 1.0,
           "wound_swelling_score": 1.0, "wound_discharge_score": 0.0, "wound_pain_score": 0.0}
    is_valid, score, flags, reason = DataQualityEngine.validate_observation(obs)
    assert is_valid is False
    assert any(f["flag_type"] == "RANGE_VIOLATION" for f in flags)


def test_pain_above_scale_quarantined():
    obs = {"pain_score": 12.0, "temperature": 37.0, "wound_redness_score": 0.0,
           "wound_swelling_score": 0.0, "wound_discharge_score": 0.0, "wound_pain_score": 0.0}
    is_valid, score, flags, reason = DataQualityEngine.validate_observation(obs)
    assert is_valid is False


def test_duplicate_observation_quarantined():
    ts = datetime(2024, 1, 15, 10, 0, 0)
    obs = {"pain_score": 3.0, "temperature": 36.8, "wound_redness_score": 0.0,
           "wound_swelling_score": 0.0, "wound_discharge_score": 0.0,
           "wound_pain_score": 0.0, "timestamp": ts}
    prev = [{"temperature": 36.7, "pain_score": 2.8, "timestamp": ts}]
    is_valid, score, flags, reason = DataQualityEngine.validate_observation(obs, prev)
    assert is_valid is False
    assert any(f["flag_type"] == "DUPLICATE_ENTRY" for f in flags)


# --- FAILURE CASE 3: TRANSIENT ABNORMALITY ---

def test_isolated_spike_alert_marked_suppressed():
    trends = {"trajectory_direction": "Stable", "persistence_count": 0,
              "multi_signal_agreement": False, "agreeing_signals": []}
    result = AlertEngine.evaluate_alert(
        patient_id="PAT-B", observation_id="OBS-1", risk_score=28.0,
        risk_category="Watch", trends=trends,
        what_changed_summary="Isolated pain spike.", active_alerts=[])
    assert result is not None
    assert result["is_suppressed"] is True
    assert result["suppression_reason"] is not None


def test_isolated_spike_no_task_created():
    alert = {"alert_id": "ALT-SPIKE", "patient_id": "PAT-S",
             "severity": "Watch", "is_suppressed": True}
    task = EscalationEngine.create_task_for_alert(alert)
    assert task is None


# --- FAILURE CASE 4: DELAYED OBSERVATION / MONITORING GAP ---

def test_monitoring_gap_detected_on_delayed_submission():
    old_ts = datetime(2024, 1, 10, 8, 0, 0)
    new_ts = datetime(2024, 1, 12, 10, 0, 0)  # 50 hours later
    obs = {"pain_score": 3.0, "temperature": 36.8, "wound_redness_score": 0.0,
           "wound_swelling_score": 0.0, "wound_discharge_score": 0.0,
           "wound_pain_score": 0.0, "timestamp": new_ts}
    prev = [{"pain_score": 2.9, "temperature": 36.7, "timestamp": old_ts}]
    _, _, flags, _ = DataQualityEngine.validate_observation(obs, prev)
    assert any(f["flag_type"] == "MONITORING_GAP" for f in flags)


def test_no_monitoring_gap_for_recent_submission():
    old_ts = datetime(2024, 1, 10, 8, 0, 0)
    new_ts = datetime(2024, 1, 10, 20, 0, 0)  # 12 hours later
    obs = {"pain_score": 3.0, "temperature": 36.8, "wound_redness_score": 0.0,
           "wound_swelling_score": 0.0, "wound_discharge_score": 0.0,
           "wound_pain_score": 0.0, "timestamp": new_ts}
    prev = [{"pain_score": 2.9, "temperature": 36.7, "timestamp": old_ts}]
    _, _, flags, _ = DataQualityEngine.validate_observation(obs, prev)
    assert not any(f["flag_type"] == "MONITORING_GAP" for f in flags)


# --- OWNERSHIP AND DUE DATES ---

def test_high_priority_task_has_owner_and_due_date():
    alert = {"alert_id": "ALT-HP", "patient_id": "PAT-HP",
             "severity": "High Priority", "is_suppressed": False}
    task = EscalationEngine.create_task_for_alert(alert, patient_care_team="Beta")
    assert task is not None
    assert task["assigned_to"] is not None
    assert task["assigned_role"] == EscalationEngine.ROLE_NURSE_REVIEWER
    assert task["due_at"] > task["created_at"]
    assert task["status"] == "Assigned"
    assert task["escalation_level"] == 1


def test_review_task_sla_longer_than_high_priority():
    alert_hp = {"alert_id": "ALT-HP2", "patient_id": "PAT-HP2",
                "severity": "High Priority", "is_suppressed": False}
    alert_rv = {"alert_id": "ALT-RV", "patient_id": "PAT-RV",
                "severity": "Review", "is_suppressed": False}
    task_hp = EscalationEngine.create_task_for_alert(alert_hp)
    task_rv = EscalationEngine.create_task_for_alert(alert_rv)
    sla_hp = (task_hp["due_at"] - task_hp["created_at"]).total_seconds()
    sla_rv = (task_rv["due_at"] - task_rv["created_at"]).total_seconds()
    assert sla_rv > sla_hp


def test_resolved_task_not_escalated():
    past_due = datetime.utcnow() - timedelta(hours=3)
    tasks = [{"task_id": "TSK-RES", "patient_id": "PAT-R", "priority": "High Priority",
              "status": "Resolved", "escalation_level": 1, "due_at": past_due,
              "assigned_role": EscalationEngine.ROLE_NURSE_REVIEWER}]
    escalated = EscalationEngine.check_and_escalate_overdue_tasks(tasks)
    assert len(escalated) == 0


def test_unresolved_overdue_escalates_to_supervisor():
    past_due = datetime.utcnow() - timedelta(hours=3)
    tasks = [{"task_id": "TSK-OD", "patient_id": "PAT-OD", "priority": "High Priority",
              "status": "Assigned", "escalation_level": 1, "due_at": past_due,
              "assigned_role": EscalationEngine.ROLE_NURSE_REVIEWER}]
    escalated = EscalationEngine.check_and_escalate_overdue_tasks(tasks)
    assert len(escalated) == 1
    assert escalated[0]["escalation_level"] == 2
    assert escalated[0]["assigned_role"] == EscalationEngine.ROLE_CLINICAL_SUPERVISOR


def test_unresolved_level2_escalates_to_operations_queue():
    past_due = datetime.utcnow() - timedelta(hours=1)
    tasks = [{"task_id": "TSK-L2", "patient_id": "PAT-L2", "priority": "High Priority",
              "status": "Escalated", "escalation_level": 2, "due_at": past_due,
              "assigned_role": EscalationEngine.ROLE_CLINICAL_SUPERVISOR}]
    escalated = EscalationEngine.check_and_escalate_overdue_tasks(tasks)
    assert len(escalated) == 1
    assert escalated[0]["escalation_level"] == 3
    assert escalated[0]["assigned_role"] == EscalationEngine.ROLE_ESCALATION_MANAGER


# --- TREND SUMMARISER ---

def test_trend_summary_high_priority_all_fields_present():
    baseline = {"baseline_pain": 3.0, "baseline_temperature": 36.8,
                "baseline_wound_score": 1.0, "observation_count": 8,
                "baseline_uncertain": False, "baseline_uncertainty_note": None}
    deviations = {"delta_pain": 4.0, "delta_temp": 1.2, "delta_wound": 3.0}
    trends = {"trajectory_direction": "Worsening", "persistence_count": 3,
              "multi_signal_agreement": True,
              "agreeing_signals": ["Pain", "Temperature", "Wound Concern"]}
    summary = BaselineEngine.get_trend_summary(
        baseline=baseline, deviations=deviations, trends=trends,
        risk_score=88.0, risk_category="High Priority",
        what_changed="Pain +4.0, Temp elevated, Wound worsening.",
        owner="Nurse Sarah", due_date="2024-01-15T12:00:00Z",
        escalation_status="Level 1")
    required_fields = ["narrative_summary", "risk_score", "risk_category",
                       "trajectory_direction", "persistence_count",
                       "multi_signal_agreement", "affected_signals",
                       "confidence", "recommended_action", "assigned_owner",
                       "due_date", "escalation_status", "safety_notice"]
    for field in required_fields:
        assert field in summary, f"Missing required field: {field}"
    assert summary["confidence"] == "High"
    assert "Immediate" in summary["recommended_action"]
    assert "concordantly deteriorating" in summary["narrative_summary"]


def test_trend_summary_uncertain_baseline_lowers_confidence():
    baseline = {"baseline_pain": 3.0, "baseline_temperature": 36.8,
                "baseline_wound_score": 1.0, "observation_count": 1,
                "baseline_uncertain": True, "baseline_uncertainty_note": "CAUTION: Only 1 obs."}
    deviations = {"delta_pain": 0.5, "delta_temp": 0.1, "delta_wound": 0.2}
    trends = {"trajectory_direction": "Stable", "persistence_count": 0,
              "multi_signal_agreement": False, "agreeing_signals": []}
    summary = BaselineEngine.get_trend_summary(
        baseline=baseline, deviations=deviations, trends=trends,
        risk_score=15.0, risk_category="Watch", what_changed="Minimal deviation.")
    assert "Low" in summary["confidence"]
    assert summary["baseline_uncertain"] is True


def test_trend_summary_stable_patient():
    baseline = {"baseline_pain": 3.0, "baseline_temperature": 36.8,
                "baseline_wound_score": 1.0, "observation_count": 10,
                "baseline_uncertain": False, "baseline_uncertainty_note": None}
    deviations = {"delta_pain": 0.1, "delta_temp": 0.05, "delta_wound": 0.1}
    trends = {"trajectory_direction": "Stable", "persistence_count": 0,
              "multi_signal_agreement": False, "agreeing_signals": []}
    summary = BaselineEngine.get_trend_summary(
        baseline=baseline, deviations=deviations, trends=trends,
        risk_score=10.0, risk_category="Stable", what_changed="No significant change.")
    assert "routine monitoring" in summary["recommended_action"].lower()
    assert "concordant with expected" in summary["narrative_summary"]


# --- PERSISTENT SINGLE SIGNAL ---

def test_persistent_single_signal_generates_review_alert():
    trends = {"trajectory_direction": "Worsening", "persistence_count": 3,
              "multi_signal_agreement": False, "agreeing_signals": ["Pain"]}
    result = AlertEngine.evaluate_alert(
        patient_id="PAT-PERSIST", observation_id="OBS-P1", risk_score=55.0,
        risk_category="Review", trends=trends,
        what_changed_summary="Pain persistently worsening.", active_alerts=[])
    assert result is not None
    assert result["is_suppressed"] is False


# --- MULTI-SIGNAL HIGH PRIORITY TASK SLA ---

def test_multi_signal_high_priority_task_two_hour_sla():
    alert = {"alert_id": "ALT-MS", "patient_id": "PAT-MS",
             "severity": "High Priority", "is_suppressed": False}
    task = EscalationEngine.create_task_for_alert(alert, patient_care_team="Alpha")
    assert task is not None
    sla_hours = (task["due_at"] - task["created_at"]).total_seconds() / 3600
    assert 1.9 <= sla_hours <= 2.1
