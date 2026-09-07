from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from backend.app.database import get_db
from backend.app.models.entities import Task, Patient, AuditLog
from backend.app.schemas.schemas import TaskResponse, TaskUpdate
from backend.app.services.escalation_engine import EscalationEngine

router = APIRouter(prefix="/tasks", tags=["Tasks & Escalations"])

@router.get("", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    if status and status != "All":
        query = query.filter(Task.status == status)
    if priority and priority != "All":
        query = query.filter(Task.priority == priority)
    if role and role != "All":
        query = query.filter(Task.assigned_role == role)

    return query.order_by(desc(Task.created_at)).all()

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if payload.status is not None:
        task.status = payload.status
        if payload.status in ["Resolved", "Closed"]:
            task.resolved_at = datetime.utcnow()
    if payload.assigned_to is not None:
        task.assigned_to = payload.assigned_to
    if payload.assigned_role is not None:
        task.assigned_role = payload.assigned_role
    if payload.resolution_note is not None:
        task.resolution_note = payload.resolution_note
    if payload.escalation_level is not None:
        task.escalation_level = payload.escalation_level

    audit = AuditLog(
        log_id=f"AUD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        actor=task.assigned_to,
        event_type="TASK_UPDATED",
        entity_id=task_id,
        description=f"Task {task_id} updated. Status: {task.status}, Escalation Level: {task.escalation_level}."
    )
    db.add(audit)
    db.commit()
    db.refresh(task)
    return task

@router.post("/check-escalations")
def trigger_escalation_check(db: Session = Depends(get_db)):
    active_tasks = db.query(Task).filter(Task.status.notin_(["Resolved", "Closed"])).all()
    task_dicts = [
        {
            "task_id": t.task_id,
            "patient_id": t.patient_id,
            "priority": t.priority,
            "status": t.status,
            "due_at": t.due_at,
            "escalation_level": t.escalation_level,
            "assigned_role": t.assigned_role,
            "assigned_to": t.assigned_to
        }
        for t in active_tasks
    ]

    escalated = EscalationEngine.check_and_escalate_overdue_tasks(task_dicts)

    for esc in escalated:
        t = db.query(Task).filter(Task.task_id == esc["task_id"]).first()
        if t:
            t.status = esc["status"]
            t.escalation_level = esc["escalation_level"]
            t.assigned_role = esc["assigned_role"]
            t.assigned_to = esc["assigned_to"]
            t.due_at = esc["due_at"]

            # Update patient escalation flag
            p = db.query(Patient).filter(Patient.patient_id == t.patient_id).first()
            if p:
                p.has_active_escalation = True
                p.assigned_owner = esc["assigned_to"]

            audit = AuditLog(
                log_id=f"AUD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                actor="Escalation SLA Engine",
                event_type="TASK_AUTO_ESCALATED",
                entity_id=t.task_id,
                description=f"Task {t.task_id} auto-escalated to Level {t.escalation_level} ({t.assigned_role}). Due time expired."
            )
            db.add(audit)

    db.commit()
    return {"status": "success", "escalated_count": len(escalated), "escalated_tasks": [e["task_id"] for e in escalated]}
