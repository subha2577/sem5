from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models.entities import Patient, Observation
from backend.app.ml.model_registry import ModelRegistry

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def get_health_status(db: Session = Depends(get_db)):
    # Check database
    db_connected = False
    patient_count = 0
    obs_count = 0
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
        patient_count = db.query(Patient).count()
        obs_count = db.query(Observation).count()
    except Exception:
        db_connected = False

    active_model = ModelRegistry.get_active_model()

    return {
        "status": "healthy" if db_connected else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": {
            "status": "connected" if db_connected else "disconnected",
            "type": "SQLite / PostgreSQL compatible",
            "patient_records": patient_count,
            "observation_records": obs_count
        },
        "model": {
            "name": active_model.get("model_name") if active_model else "trend-risk-classifier",
            "version": active_model.get("version_tag") if active_model else "v1.0.0",
            "status": "online" if active_model else "ready"
        },
        "disclaimer": "Prototype decision-support system. Outputs require qualified clinical review and must not replace professional medical judgement."
    }
