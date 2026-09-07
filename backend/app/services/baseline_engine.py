from typing import List, Dict, Any, Tuple
import numpy as np

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
                "observation_count": 0
            }

        # Take the most recent 'window_size' unquarantined observations
        valid_history = [o for o in history if not o.get("is_quarantined", False)]
        if not valid_history:
            valid_history = history

        slice_window = valid_history[-window_size:] if len(valid_history) >= window_size else valid_history

        pains = [float(o.get("pain_score", 0.0)) for o in slice_window]
        temps = [float(o.get("temperature", 36.8)) for o in slice_window]
        wounds = [float(o.get("composite_wound_score", 0.0)) for o in slice_window]

        return {
            "baseline_pain": round(float(np.median(pains)), 2),
            "baseline_temperature": round(float(np.median(temps)), 2),
            "baseline_wound_score": round(float(np.median(wounds)), 2),
            "pain_rolling_std": round(float(np.std(pains)) if len(pains) > 1 else 0.5, 2),
            "temp_rolling_std": round(float(np.std(temps)) if len(temps) > 1 else 0.2, 2),
            "wound_rolling_std": round(float(np.std(wounds)) if len(wounds) > 1 else 0.3, 2),
            "observation_count": len(valid_history)
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
