import os
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.entities import Patient, Alert

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("")
def get_analytics_summary(db: Session = Depends(get_db)):
    eval_file = "reports/evaluation_results.json"
    eval_data = {}
    if os.path.exists(eval_file):
        try:
            with open(eval_file, "r") as f:
                eval_data = json.load(f)
        except Exception:
            pass

    # Live alerts breakdown by severity
    severity_counts = db.query(Alert.severity, func.count(Alert.alert_id)).group_by(Alert.severity).all()
    sev_map = {sev: cnt for sev, cnt in severity_counts}

    # Surgery type distribution
    surgery_counts = db.query(Patient.surgery_type, func.count(Patient.patient_id)).group_by(Patient.surgery_type).all()
    surgery_dist = [{"surgery": s, "count": c} for s, c in surgery_counts]

    # Suppressed vs Unsuppressed Alerts
    suppressed_count = db.query(Alert).filter(Alert.is_suppressed == True).count()
    active_alert_count = db.query(Alert).filter(Alert.is_suppressed == False).count()

    return {
        "evaluation_metrics": eval_data,
        "live_alert_counts": {
            "High Priority": sev_map.get("High Priority", 0),
            "Review": sev_map.get("Review", 0),
            "Watch": sev_map.get("Watch", 0)
        },
        "suppression_summary": {
            "active_actionable_alerts": active_alert_count,
            "suppressed_fatigue_alerts": suppressed_count,
            "suppression_rate_pct": round((suppressed_count / max(1, suppressed_count + active_alert_count)) * 100.0, 1)
        },
        "surgery_distribution": surgery_dist
    }
