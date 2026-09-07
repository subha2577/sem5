import pytest
from datetime import datetime, timedelta
from backend.app.services.escalation_engine import EscalationEngine

def test_task_creation_for_high_priority_alert():
    alert = {
        "alert_id": "ALT-TEST-1",
        "patient_id": "PAT-TEST",
        "severity": "High Priority",
        "is_suppressed": False
    }
    task = EscalationEngine.create_task_for_alert(alert, patient_care_team="Alpha")
    assert task is not None
    assert task["priority"] == "High Priority"
    assert task["assigned_role"] == EscalationEngine.ROLE_NURSE_REVIEWER
    assert task["escalation_level"] == 1
    # 2 hour SLA
    assert task["due_at"] > task["created_at"]

def test_no_task_for_suppressed_alert():
    alert = {
        "alert_id": "ALT-TEST-2",
        "patient_id": "PAT-TEST",
        "severity": "Watch",
        "is_suppressed": True
    }
    task = EscalationEngine.create_task_for_alert(alert)
    assert task is None

def test_overdue_task_auto_escalation_level_2():
    past_due = datetime.utcnow() - timedelta(hours=1)
    tasks = [{
        "task_id": "TSK-100",
        "patient_id": "PAT-TEST",
        "priority": "High Priority",
        "status": "Assigned",
        "escalation_level": 1,
        "due_at": past_due,
        "assigned_role": EscalationEngine.ROLE_NURSE_REVIEWER
    }]
    escalated = EscalationEngine.check_and_escalate_overdue_tasks(tasks)
    assert len(escalated) == 1
    assert escalated[0]["escalation_level"] == 2
    assert escalated[0]["assigned_role"] == EscalationEngine.ROLE_CLINICAL_SUPERVISOR
    assert escalated[0]["status"] == "Escalated"

def test_overdue_task_auto_escalation_level_3():
    past_due = datetime.utcnow() - timedelta(hours=1)
    tasks = [{
        "task_id": "TSK-200",
        "patient_id": "PAT-TEST",
        "priority": "High Priority",
        "status": "Escalated",
        "escalation_level": 2,
        "due_at": past_due,
        "assigned_role": EscalationEngine.ROLE_CLINICAL_SUPERVISOR
    }]
    escalated = EscalationEngine.check_and_escalate_overdue_tasks(tasks)
    assert len(escalated) == 1
    assert escalated[0]["escalation_level"] == 3
    assert escalated[0]["assigned_role"] == EscalationEngine.ROLE_ESCALATION_MANAGER
