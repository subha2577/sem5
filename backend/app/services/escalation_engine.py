import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from backend.app.config import settings

class EscalationEngine:
    """
    Manages clinical task creation, care team ownership assignment,
    SLA due times, and automatic multi-tier escalation for unresolved tasks.
    """

    ROLE_CARE_COORDINATOR = "Care Coordinator"
    ROLE_NURSE_REVIEWER = "Nurse Reviewer"
    ROLE_CLINICAL_SUPERVISOR = "Clinical Supervisor"
    ROLE_ESCALATION_MANAGER = "Escalation Manager"

    @classmethod
    def create_task_for_alert(
        cls,
        alert: Dict[str, Any],
        patient_care_team: str = "Team Alpha"
    ) -> Optional[Dict[str, Any]]:
        """
        Creates an actionable follow-up task for an unsuppressed alert.
        """
        if alert.get("is_suppressed", False):
            return None

        severity = alert.get("severity", "Review")
        now = datetime.utcnow()

        if severity == "High Priority":
            sla_hours = settings.TASK_DUE_HOURS_HIGH
            role = cls.ROLE_NURSE_REVIEWER
            assigned_to = f"Nurse Sarah (Team {patient_care_team})"
            escalation_level = 1
        elif severity == "Review":
            sla_hours = settings.TASK_DUE_HOURS_REVIEW
            role = cls.ROLE_CARE_COORDINATOR
            assigned_to = f"Coordinator Alex (Team {patient_care_team})"
            escalation_level = 1
        else:
            sla_hours = settings.TASK_DUE_HOURS_WATCH
            role = cls.ROLE_CARE_COORDINATOR
            assigned_to = "Automated Follow-up"
            escalation_level = 1

        due_at = now + timedelta(hours=sla_hours)

        return {
            "task_id": f"TSK-{uuid.uuid4().hex[:8].upper()}",
            "patient_id": alert.get("patient_id"),
            "alert_id": alert.get("alert_id"),
            "priority": severity,
            "assigned_to": assigned_to,
            "assigned_role": role,
            "created_at": now,
            "due_at": due_at,
            "status": "Assigned",
            "escalation_level": escalation_level,
            "resolution_note": None,
            "resolved_at": None
        }

    @classmethod
    def check_and_escalate_overdue_tasks(
        cls,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Scans active tasks and escalates unresolved tasks past due date.
        Level 1 (Care Team) -> Level 2 (Clinical Supervisor) -> Level 3 (Escalation Queue)
        """
        escalated_tasks = []
        now = datetime.utcnow()

        for t in tasks:
            if t.get("status") in ["Resolved", "Closed"]:
                continue

            due_at = t.get("due_at")
            if due_at and now > due_at:
                current_lvl = t.get("escalation_level", 1)
                if current_lvl == 1:
                    t["escalation_level"] = 2
                    t["status"] = "Escalated"
                    t["assigned_role"] = cls.ROLE_CLINICAL_SUPERVISOR
                    t["assigned_to"] = "Dr. Miller (Clinical Supervisor)"
                    # Extend SLA for supervisory review
                    t["due_at"] = now + timedelta(hours=2)
                    escalated_tasks.append(t)
                elif current_lvl == 2:
                    t["escalation_level"] = 3
                    t["status"] = "Escalated"
                    t["assigned_role"] = cls.ROLE_ESCALATION_MANAGER
                    t["assigned_to"] = "Operations Escalation Queue"
                    t["due_at"] = now + timedelta(hours=1)
                    escalated_tasks.append(t)

        return escalated_tasks
