from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.database import get_db
from backend.app.models.entities import AuditLog
from backend.app.schemas.schemas import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(limit: int = 100, event_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AuditLog)
    if event_type and event_type != "All":
        query = query.filter(AuditLog.event_type == event_type)
    return query.order_by(desc(AuditLog.timestamp)).limit(limit).all()
