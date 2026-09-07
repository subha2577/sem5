import os
import sys
from collections import defaultdict
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.services.baseline_engine import BaselineEngine
from backend.app.services.trend_engine import TrendEngine
from backend.app.ml.feature_engineering import FeatureEngineer
from backend.app.ml.train import train_risk_model
from backend.app.ml.model_registry import ModelRegistry

def run_training_pipeline():
    print("Loading synthetic observations and patient records for model training...", flush=True)
    df_patients = pd.read_csv("data/synthetic/patients.csv")
    df_obs = pd.read_csv("data/synthetic/observations.csv")

    X_list = []
    y_list = []

    gt_map = {
        "no_action": 0,
        "monitor": 0,
        "review": 1,
        "urgent_review": 1
    }

    # Group records into dict in single pass (fast)
    print("Grouping observations by patient...", flush=True)
    obs_by_patient = defaultdict(list)
    for r in df_obs.to_dict("records"):
        obs_by_patient[r["patient_id"]].append(r)

    print(f"Processing {len(df_patients)} patients...", flush=True)
    for _, p in df_patients.iterrows():
        p_id = p["patient_id"]
        gt = p["ground_truth_escalation"]
        target = gt_map.get(gt, 0)

        p_obs = obs_by_patient.get(p_id, [])
        if not p_obs:
            continue

        # Compute baseline and trends
        baseline = BaselineEngine.calculate_patient_baseline(p_obs)
        trends = TrendEngine.analyze_trends(p_obs)
        
        # Extract features
        feat_vec = FeatureEngineer.extract_features_from_patient_obs(
            p_obs, baseline, trends, data_quality_score=95.0
        )

        X_list.append(feat_vec)
        y_list.append(target)

    X = np.array(X_list)
    y = np.array(y_list)

    print(f"Dataset prepared: {X.shape[0]} samples, {X.shape[1]} features. Class balance: {np.bincount(y)}", flush=True)
    
    print("Training Random Forest Classifier...", flush=True)
    metrics = train_risk_model(X, y)

    # Register in Model Registry
    reg_entry = ModelRegistry.register_model(
        version_tag="v1.0.0",
        metrics=metrics,
        feature_importance=metrics["feature_importance"],
        is_active=True
    )

    print("\n--- Model Training Results ---", flush=True)
    print(f"Precision: {metrics['precision']:.4f}", flush=True)
    print(f"Recall:    {metrics['recall']:.4f}", flush=True)
    print(f"F1 Score:  {metrics['f1_score']:.4f}", flush=True)
    print(f"ROC-AUC:   {metrics['roc_auc']:.4f}", flush=True)
    print(f"Top 5 Features: {list(metrics['feature_importance'].items())[:5]}", flush=True)
    print("Model artifact and registry saved successfully.", flush=True)
    return metrics

if __name__ == "__main__":
    run_training_pipeline()
