from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.database import get_db
from backend.app.models.entities import Alert, AuditLog
from backend.app.schemas.schemas import AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    skip: int = 0,
    limit: int = 50,
    severity: Optional[str] = None,
    include_suppressed: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if not include_suppressed:
        query = query.filter(Alert.is_suppressed == False)
    if severity and severity != "All":
        query = query.filter(Alert.severity == severity)

    return query.order_by(desc(Alert.timestamp)).offset(skip).limit(limit).all()

@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: str,
    clinician_name: str = "Nurse Reviewer",
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = clinician_name

    audit = AuditLog(
        log_id=f"AUD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        actor=clinician_name,
        event_type="ALERT_ACKNOWLEDGED",
        entity_id=alert_id,
        description=f"Alert {alert_id} acknowledged by {clinician_name}."
    )
    db.add(audit)
    db.commit()
    return {"status": "success", "alert_id": alert_id, "acknowledged": True}
