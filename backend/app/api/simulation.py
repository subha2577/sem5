from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter
from backend.app.schemas.schemas import SimulationRequest, SimulationResponse
from backend.app.services.baseline_engine import BaselineEngine
from backend.app.services.trend_engine import TrendEngine
from backend.app.services.risk_engine import RiskEngine
from backend.app.services.alert_engine import AlertEngine
from backend.app.services.data_quality_engine import DataQualityEngine
from backend.app.ml.evaluate import EvaluationEngine

router = APIRouter(prefix="/simulation", tags=["Simulation"])

@router.post("", response_model=SimulationResponse)
def run_recovery_simulation(payload: SimulationRequest):
    scenario = payload.trajectory_group
    base_p = payload.baseline_pain or 3.0
    base_t = payload.baseline_temp or 36.8
    steps = max(5, payload.observation_steps or 7)

    observations = []
    now = datetime.utcnow()

    # Generate scenario-specific synthetic observation series
    for step in range(steps):
        t_time = now - timedelta(hours=(steps - step) * 12)
        p_day = 1 + int(step / 2)

        if "Temporary" in scenario or "Isolated" in scenario or scenario == "Group B":
            desc = "Temporary Variation: Isolated spike followed by rapid return to baseline."
            if step == 3:
                pain = base_p + 3.8
                temp = 38.1
                redness, swelling, discharge = 1.0, 1.0, 0.0
                concern = "Mild"
            elif step > 3:
                pain = max(1.0, base_p - 0.5)
                temp = base_t
                redness, swelling, discharge = 0.5, 0.5, 0.0
                concern = "None"
            else:
                pain = base_p
                temp = base_t
                redness, swelling, discharge = 1.0, 1.0, 0.0
                concern = "None"

        elif "Gradual" in scenario or scenario == "Group C":
            desc = "Gradual Deterioration: Steady upward trend in pain and wound inflammation across multiple days."
            if step < 2:
                pain = base_p
                temp = base_t
                redness, swelling, discharge = 1.0, 1.0, 0.0
                concern = "None"
            else:
                pain = min(9.5, base_p + (step - 1) * 1.3)
                temp = min(39.0, base_t + (step - 1) * 0.35)
                redness = min(4.5, 1.0 + (step - 1) * 0.8)
                swelling = min(4.0, 1.0 + (step - 1) * 0.7)
                discharge = min(3.0, (step - 1) * 0.5)
                concern = "Moderate" if step < 4 else "Severe"

        elif "Wound" in scenario or scenario == "Group D":
            desc = "Wound-Dominant Deterioration: Temperature remains normal (afebrile), but surgical site redness, swelling, and purulent discharge rapidly worsen."
            temp = base_t
            if step < 2:
                pain = base_p
                redness, swelling, discharge = 1.0, 1.0, 0.0
                concern = "None"
            else:
                pain = min(8.0, base_p + (step - 1) * 0.9)
                redness = min(5.0, 1.5 + (step - 1) * 0.9)
                swelling = min(5.0, 1.5 + (step - 1) * 0.8)
                discharge = min(5.0, 0.5 + (step - 1) * 1.0)
                concern = "Moderate"

        elif "Multi-Signal" in scenario or scenario == "Group F":
            desc = "Multi-Signal Deterioration: High-priority clinical state where pain, temperature, and wound symptoms deteriorate simultaneously."
            if step < 2:
                pain = base_p
                temp = base_t
                redness, swelling, discharge = 1.0, 1.0, 0.0
                concern = "None"
            else:
                pain = min(10.0, base_p + (step - 1) * 1.5)
                temp = min(39.6, base_t + (step - 1) * 0.55)
                redness = min(5.0, 1.5 + (step - 1) * 0.9)
                swelling = min(5.0, 1.5 + (step - 1) * 0.8)
                discharge = min(5.0, 1.0 + (step - 1) * 0.9)
                concern = "Severe"

        elif "Gap" in scenario or scenario == "Group G":
            desc = "Monitoring Gap: Patient abruptly discontinues submitting readings after initial post-op days."
            pain = base_p
            temp = base_t
            redness, swelling, discharge = 1.0, 1.0, 0.0
            concern = "None"

        else: # Default: Stable Normal Recovery
            desc = "Normal Recovery: Post-operative indicators steadily improve toward baseline with expected healing progression."
            pain = max(1.0, base_p - (step * 0.4))
            temp = base_t
            redness = max(0.5, 1.5 - (step * 0.2))
            swelling = max(0.5, 1.5 - (step * 0.2))
            discharge = 0.0
            concern = "None"

        comp_wound = DataQualityEngine.calculate_composite_wound_score(redness, swelling, discharge, min(5.0, pain / 2.0))
        observations.append({
            "observation_id": f"SIM-{step + 1}",
            "timestamp": t_time.isoformat(),
            "postoperative_day": p_day,
            "pain_score": round(pain, 1),
            "temperature": round(temp, 1),
            "wound_redness_score": round(redness, 1),
            "wound_swelling_score": round(swelling, 1),
            "wound_discharge_score": round(discharge, 1),
            "wound_pain_score": round(min(5.0, pain / 2.0), 1),
            "composite_wound_score": comp_wound,
            "patient_reported_concern": concern
        })

    # Run RecoverAI Engine on simulated series
    baseline = BaselineEngine.calculate_patient_baseline(observations[:3] if len(observations) >= 3 else observations)
    latest = observations[-1]
    devs = BaselineEngine.calculate_deviations(latest, baseline)
    trends = TrendEngine.analyze_trends(observations)
    r_score, r_cat, contribs, what_changed, why_no_alert = RiskEngine.calculate_risk_score(
        devs, trends, latest, data_quality_score=100.0, baseline=baseline
    )

    alert_dict = AlertEngine.evaluate_alert(
        patient_id="SIM-PATIENT",
        observation_id=latest["observation_id"],
        risk_score=r_score,
        risk_category=r_cat,
        trends=trends,
        what_changed_summary=what_changed,
        active_alerts=[]
    )

    # Simple Baseline evaluation
    baseline_alerts_count = sum(1 for o in observations if EvaluationEngine.is_simple_baseline_alert(o))

    recoverai_result = {
        "risk_score": r_score,
        "risk_category": r_cat,
        "trend_direction": trends["trajectory_direction"],
        "persistence_count": trends["persistence_count"],
        "multi_signal_agreement": trends["multi_signal_agreement"],
        "agreeing_signals": trends["agreeing_signals"],
        "alert_triggered": bool(alert_dict and not alert_dict.get("is_suppressed", False)),
        "alert_severity": alert_dict.get("severity") if alert_dict else "None",
        "is_suppressed": alert_dict.get("is_suppressed", False) if alert_dict else True,
        "suppression_reason": alert_dict.get("suppression_reason") if alert_dict else "Risk score within stable limits",
        "contributors": contribs
    }

    simple_baseline_result = {
        "total_alerts_triggered": baseline_alerts_count,
        "alert_fatigue_risk": "High (Floods care team on isolated variations)" if baseline_alerts_count > 0 and r_cat in ["Stable", "Watch"] else "Moderate",
        "rule_description": "Triggers alert whenever Pain >= 7.0 OR Temp >= 38.0°C OR Discharge >= 3.0"
    }

    return SimulationResponse(
        scenario_name=scenario,
        trajectory_description=desc,
        observations=observations,
        recoverai_result=recoverai_result,
        simple_baseline_result=simple_baseline_result,
        what_changed_summary=what_changed,
        why_no_alert_explanation=why_no_alert
    )
