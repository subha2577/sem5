import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.entities import StakeholderFeedback
from backend.app.schemas.schemas import StakeholderFeedbackCreate, StakeholderFeedbackResponse

router = APIRouter(prefix="/stakeholder-feedback", tags=["Stakeholder Feedback"])

@router.get("", response_model=List[StakeholderFeedbackResponse])
def get_all_feedback(db: Session = Depends(get_db)):
    return db.query(StakeholderFeedback).order_by(StakeholderFeedback.created_at.desc()).all()

@router.get("/summary")
def get_feedback_summary(db: Session = Depends(get_db)):
    feedbacks = db.query(StakeholderFeedback).all()
    if not feedbacks:
        return {
            "total_responses": 0,
            "avg_understanding": 5.0,
            "avg_explainability": 5.0,
            "avg_satisfaction": 5.0
        }

    total = len(feedbacks)
    avg_und = sum(f.understanding_score for f in feedbacks) / total
    avg_exp = sum(f.explainability_score for f in feedbacks) / total
    avg_sat = sum(f.alert_reduction_satisfaction for f in feedbacks) / total

    return {
        "total_responses": total,
        "avg_understanding": round(avg_und, 2),
        "avg_explainability": round(avg_exp, 2),
        "avg_satisfaction": round(avg_sat, 2)
    }

@router.post("", response_model=StakeholderFeedbackResponse)
def submit_feedback(payload: StakeholderFeedbackCreate, db: Session = Depends(get_db)):
    fb = StakeholderFeedback(
        feedback_id=f"SF-{uuid.uuid4().hex[:6].upper()}",
        role=payload.role,
        understanding_score=payload.understanding_score,
        explainability_score=payload.explainability_score,
        alert_reduction_satisfaction=payload.alert_reduction_satisfaction,
        comments=payload.comments,
        created_at=datetime.utcnow()
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
