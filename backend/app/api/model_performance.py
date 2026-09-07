import os
import json
from fastapi import APIRouter
from backend.app.ml.model_registry import ModelRegistry

router = APIRouter(prefix="/model", tags=["Model Performance"])

@router.get("/performance")
def get_model_performance():
    active_model = ModelRegistry.get_active_model()
    eval_file = "reports/evaluation_results.json"
    eval_data = {}
    if os.path.exists(eval_file):
        try:
            with open(eval_file, "r") as f:
                eval_data = json.load(f)
        except Exception:
            pass

    return {
        "model_version": active_model.get("version_tag", "v1.0.0") if active_model else "v1.0.0",
        "model_name": active_model.get("model_name", "trend-risk-classifier") if active_model else "trend-risk-classifier",
        "trained_at": active_model.get("trained_at") if active_model else None,
        "ml_metrics": active_model.get("metrics", {}) if active_model else {},
        "feature_importance": active_model.get("feature_importance", {}) if active_model else {},
        "cohort_evaluation": eval_data,
        "disclaimer": "Performance is evaluated on synthetic post-operative scenarios and should not be interpreted as clinical validation."
    }
