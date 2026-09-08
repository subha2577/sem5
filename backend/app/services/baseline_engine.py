from typing import List, Dict, Any, Tuple, Optional
import numpy as np

MINIMUM_RELIABLE_BASELINE_OBS = 3  # Minimum observations before baseline is considered reliable

class BaselineEngine:
    """
    Computes patient-specific recovery baselines rather than relying on
    static one-size-fits-all population cutoffs.
    """

    @staticmethod
    def calculate_patient_baseline(
        history: List[Dict[str, Any]],
        window_size: int = 5
    ) -> Dict[str, float]:
        """
        Derives rolling baseline metrics from valid prior observations.
        If history is smaller than window_size, computes baseline from available data.
        """
        if not history:
            return {
                "baseline_pain": 3.0,
                "baseline_temperature": 36.8,
                "baseline_wound_score": 1.0,
                "pain_rolling_std": 0.5,
                "temp_rolling_std": 0.2,
                "wound_rolling_std": 0.3,
                "observation_count": 0,
                "baseline_uncertain": True,
                "baseline_uncertainty_note": (
                    f"CAUTION: Baseline derived from only 0 observation(s). "
                    f"A minimum of {MINIMUM_RELIABLE_BASELINE_OBS} valid observations are required for a reliable "
                    "patient-specific baseline. Population defaults are partially applied — deviations "
                    "should be interpreted conservatively until more history is available."
                )
            }

        # Take the most recent 'window_size' unquarantined observations
        valid_history = [o for o in history if not o.get("is_quarantined", False)]
        if not valid_history:
            valid_history = history

        slice_window = valid_history[-window_size:] if len(valid_history) >= window_size else valid_history

        pains = [float(o.get("pain_score", 0.0)) for o in slice_window]
        temps = [float(o.get("temperature", 36.8)) for o in slice_window]
        wounds = [float(o.get("composite_wound_score", 0.0)) for o in slice_window]

        obs_count = len(valid_history)
        # Flag baseline as uncertain when fewer than the minimum reliable count
        baseline_uncertain = obs_count < MINIMUM_RELIABLE_BASELINE_OBS

        return {
            "baseline_pain": round(float(np.median(pains)), 2),
            "baseline_temperature": round(float(np.median(temps)), 2),
            "baseline_wound_score": round(float(np.median(wounds)), 2),
            "pain_rolling_std": round(float(np.std(pains)) if len(pains) > 1 else 0.5, 2),
            "temp_rolling_std": round(float(np.std(temps)) if len(temps) > 1 else 0.2, 2),
            "wound_rolling_std": round(float(np.std(wounds)) if len(wounds) > 1 else 0.3, 2),
            "observation_count": obs_count,
            "baseline_uncertain": baseline_uncertain,
            "baseline_uncertainty_note": (
                f"CAUTION: Baseline derived from only {obs_count} observation(s). "
                f"A minimum of {MINIMUM_RELIABLE_BASELINE_OBS} valid observations are required for a reliable "
                "patient-specific baseline. Population defaults are partially applied — deviations "
                "should be interpreted conservatively until more history is available."
            ) if baseline_uncertain else None
        }

    @classmethod
    def calculate_deviations(
        cls,
        current_obs: Dict[str, Any],
        baseline: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculates difference between current observation and personal baseline.
        """
        cur_pain = float(current_obs.get("pain_score", 0.0))
        cur_temp = float(current_obs.get("temperature", 36.8))
        cur_wound = float(current_obs.get("composite_wound_score", 0.0))

        delta_pain = cur_pain - baseline["baseline_pain"]
        delta_temp = cur_temp - baseline["baseline_temperature"]
        delta_wound = cur_wound - baseline["baseline_wound_score"]

        # Z-score deviations (capped to prevent division by near zero)
        std_pain = max(baseline.get("pain_rolling_std", 0.5), 0.2)
        std_temp = max(baseline.get("temp_rolling_std", 0.2), 0.1)
        std_wound = max(baseline.get("wound_rolling_std", 0.3), 0.1)

        z_pain = delta_pain / std_pain
        z_temp = delta_temp / std_temp
        z_wound = delta_wound / std_wound

        return {
            "delta_pain": round(delta_pain, 2),
            "delta_temp": round(delta_temp, 2),
            "delta_wound": round(delta_wound, 2),
            "z_pain": round(z_pain, 2),
            "z_temp": round(z_temp, 2),
            "z_wound": round(z_wound, 2)
        }

    @staticmethod
    def get_trend_summary(
        baseline: Dict[str, Any],
        deviations: Dict[str, float],
        trends: Dict[str, Any],
        risk_score: float,
        risk_category: str,
        what_changed: str,
        owner: Optional[str] = None,
        due_date: Optional[str] = None,
        escalation_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Produces a structured, human-readable trend summary for every patient episode.
        Satisfies the Trend Summariser requirement (Section 5 of problem statement).
        Covers: current state, baseline, direction, persistence, affected signals,
        severity, confidence, reason for prioritisation, recommended action,
        owner, due date, escalation status.
        """
        direction = trends.get("trajectory_direction", "Stable")
        persistence = trends.get("persistence_count", 0)
        signals = trends.get("agreeing_signals", [])
        multi_signal = trends.get("multi_signal_agreement", False)
        obs_count = baseline.get("observation_count", 0)
        baseline_uncertain = baseline.get("baseline_uncertain", False)

        # Confidence: lower when baseline is uncertain or few signals
        if baseline_uncertain:
            confidence = "Low (insufficient baseline history — conservative interpretation required)"
        elif risk_score >= 75:
            confidence = "High"
        elif risk_score >= 50:
            confidence = "Moderate-High"
        elif risk_score >= 25:
            confidence = "Moderate"
        else:
            confidence = "Low"

        # Recommended action
        if risk_category == "High Priority":
            recommended_action = (
                "Immediate clinical review required. "
                "Contact patient and assess for acute post-operative complication."
            )
        elif risk_category == "Review":
            recommended_action = (
                "Schedule clinical review within SLA window. "
                "Validate patient status by telephone or patient portal."
            )
        elif risk_category == "Watch":
            recommended_action = (
                "Monitor for further deterioration. "
                "No immediate action required unless trajectory continues to worsen."
            )
        else:
            recommended_action = (
                "Continue routine monitoring. "
                "Patient recovery trajectory is consistent with expected post-operative baseline."
            )

        # Narrative prose summary (human-readable, not a diagnosis)
        if direction == "Worsening" and multi_signal:
            narrative = (
                f"Multiple recovery signals are concordantly deteriorating "
                f"({', '.join(signals) if signals else 'pain, temperature and/or wound'}). "
                f"This persistent multi-signal deviation (across {persistence} consecutive reading(s)) "
                f"represents a meaningful departure from this patient's personal recovery baseline "
                f"and has been prioritised for clinical review. "
                f"This tool is for decision-support only and requires qualified human clinical review."
            )
        elif direction == "Worsening" and persistence >= 2:
            signal_name = signals[0] if signals else "a key recovery metric"
            narrative = (
                f"{signal_name} has shown sustained worsening across {persistence} consecutive "
                f"readings relative to this patient's personal baseline. "
                f"Persistent single-signal deterioration has been escalated for review. "
                f"This tool is for decision-support only and requires qualified human clinical review."
            )
        elif direction == "Improving":
            narrative = (
                "Patient recovery trajectory is showing improvement relative to personal baseline. "
                "Continue monitoring per standard protocol."
            )
        elif risk_category == "Watch":
            narrative = (
                "An isolated transient variation was detected but does not meet the persistence "
                "or multi-signal concordance criteria for a high-priority alert. "
                "Flagged for active monitoring only. No clinical action required at this time."
            )
        else:
            narrative = (
                "Patient measurements remain concordant with expected post-operative recovery baseline. "
                "No clinically meaningful change detected in this evaluation window."
            )

        return {
            "narrative_summary": narrative,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "trajectory_direction": direction,
            "persistence_count": persistence,
            "multi_signal_agreement": multi_signal,
            "affected_signals": signals,
            "baseline_pain": baseline.get("baseline_pain"),
            "baseline_temperature": baseline.get("baseline_temperature"),
            "baseline_wound_score": baseline.get("baseline_wound_score"),
            "delta_pain_from_baseline": deviations.get("delta_pain"),
            "delta_temp_from_baseline": deviations.get("delta_temp"),
            "delta_wound_from_baseline": deviations.get("delta_wound"),
            "baseline_observation_count": obs_count,
            "baseline_uncertain": baseline_uncertain,
            "baseline_uncertainty_note": baseline.get("baseline_uncertainty_note"),
            "confidence": confidence,
            "recommended_action": recommended_action,
            "assigned_owner": owner,
            "due_date": due_date,
            "escalation_status": escalation_status,
            "what_changed_detail": what_changed,
            "safety_notice": (
                "This prototype does not provide medical diagnosis or autonomous treatment recommendations. "
                "All outputs require qualified clinical review."
            )
        }
