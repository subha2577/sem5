from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from backend.app.database import get_db
from backend.app.models.entities import DataQualityEvent, Patient, Observation
from backend.app.schemas.schemas import DataQualityEventResponse

router = APIRouter(prefix="/data-quality", tags=["Data Quality"])

@router.get("/events", response_model=List[DataQualityEventResponse])
def get_data_quality_events(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(DataQualityEvent).order_by(desc(DataQualityEvent.timestamp)).limit(limit).all()

@router.get("/summary")
def get_data_quality_summary(db: Session = Depends(get_db)):
    total_events = db.query(DataQualityEvent).count()
    quarantined = db.query(DataQualityEvent).filter(DataQualityEvent.quarantined == True).count()
    monitoring_gaps = db.query(DataQualityEvent).filter(DataQualityEvent.flag_type == "MONITORING_GAP").count()
    sudden_jumps = db.query(DataQualityEvent).filter(DataQualityEvent.flag_type == "SUDDEN_JUMP").count()
    range_violations = db.query(DataQualityEvent).filter(DataQualityEvent.flag_type == "RANGE_VIOLATION").count()

    # Patient data quality score buckets
    good_count = db.query(Patient).filter(Patient.latest_data_quality_score >= 80.0).count()
    fair_count = db.query(Patient).filter(Patient.latest_data_quality_score >= 50.0, Patient.latest_data_quality_score < 80.0).count()
    poor_count = db.query(Patient).filter(Patient.latest_data_quality_score < 50.0).count()

    return {
        "total_flagged_events": total_events,
        "quarantined_records": quarantined,
        "monitoring_gaps": monitoring_gaps,
        "sudden_jumps": sudden_jumps,
        "range_violations": range_violations,
        "score_distribution": {
            "Good (80-100)": good_count,
            "Fair (50-79)": fair_count,
            "Poor (<50)": poor_count
        }
    }
