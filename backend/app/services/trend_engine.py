from typing import List, Dict, Any, Tuple
import numpy as np

class TrendEngine:
    """
    Evaluates temporal trends, rate of change, persistence, and multi-signal agreement.
    Distinguishes sustained deterioration from isolated spikes.
    """

    @staticmethod
    def _calculate_slope(values: List[float]) -> float:
        """Calculates closed-form linear regression slope without SVD overhead."""
        n = len(values)
        if n < 2:
            return 0.0
        sum_x = n * (n - 1) / 2.0
        sum_x2 = (n - 1) * n * (2 * n - 1) / 6.0
        sum_y = sum(values)
        sum_xy = sum(i * y for i, y in enumerate(values))
        denom = (n * sum_x2) - (sum_x ** 2)
        if denom == 0:
            return 0.0
        return float((n * sum_xy - sum_x * sum_y) / denom)

    @classmethod
    def analyze_trends(
        cls,
        history: List[Dict[str, Any]],
        short_window: int = 3,
        medium_window: int = 7
    ) -> Dict[str, Any]:
        """
        Analyzes short-term and medium-term trajectories for pain, temperature, and wound scores.
        """
        valid_obs = [o for o in history if not o.get("is_quarantined", False)]
        if not valid_obs:
            return {
                "trajectory_direction": "Stable",
                "persistence_count": 0,
                "multi_signal_agreement": False,
                "pain_short_slope": 0.0,
                "temp_short_slope": 0.0,
                "wound_short_slope": 0.0,
                "pain_med_slope": 0.0,
                "temp_med_slope": 0.0,
                "wound_med_slope": 0.0,
                "agreeing_signals": []
            }

        pains = [float(o.get("pain_score", 0.0)) for o in valid_obs]
        temps = [float(o.get("temperature", 36.8)) for o in valid_obs]
        wounds = [float(o.get("composite_wound_score", 0.0)) for o in valid_obs]

        # Short-term trends
        short_pains = pains[-short_window:] if len(pains) >= short_window else pains
        short_temps = temps[-short_window:] if len(temps) >= short_window else temps
        short_wounds = wounds[-short_window:] if len(wounds) >= short_window else wounds

        pain_short_slope = round(cls._calculate_slope(short_pains), 2)
        temp_short_slope = round(cls._calculate_slope(short_temps), 2)
        wound_short_slope = round(cls._calculate_slope(short_wounds), 2)

        # Medium-term trends
        med_pains = pains[-medium_window:] if len(pains) >= medium_window else pains
        med_temps = temps[-medium_window:] if len(temps) >= medium_window else temps
        med_wounds = wounds[-medium_window:] if len(wounds) >= medium_window else wounds

        pain_med_slope = round(cls._calculate_slope(med_pains), 2)
        temp_med_slope = round(cls._calculate_slope(med_temps), 2)
        wound_med_slope = round(cls._calculate_slope(med_wounds), 2)

        # Persistence Counter: Consecutive observations showing worsening relative to previous
        persistence_count = 0
        if len(valid_obs) >= 2:
            for i in range(len(valid_obs) - 1, 0, -1):
                cur = valid_obs[i]
                prev = valid_obs[i - 1]
                # Check if pain or wound or temp worsened
                worsening = (
                    float(cur.get("pain_score", 0)) > float(prev.get("pain_score", 0)) + 0.3 or
                    float(cur.get("temperature", 36.8)) > float(prev.get("temperature", 36.8)) + 0.2 or
                    float(cur.get("composite_wound_score", 0)) > float(prev.get("composite_wound_score", 0)) + 0.3
                )
                if worsening:
                    persistence_count += 1
                else:
                    break

        # Multi-signal agreement: check which signals are worsening
        agreeing_signals = []
        if pain_short_slope > 0.3 or (len(short_pains) >= 2 and short_pains[-1] - short_pains[0] >= 1.0):
            agreeing_signals.append("Pain")
        if temp_short_slope > 0.15 or (len(short_temps) >= 2 and short_temps[-1] - short_temps[0] >= 0.4):
            agreeing_signals.append("Temperature")
        if wound_short_slope > 0.25 or (len(short_wounds) >= 2 and short_wounds[-1] - short_wounds[0] >= 0.8):
            agreeing_signals.append("Wound Concern")

        multi_signal_agreement = len(agreeing_signals) >= 2

        # Overall Trajectory Classification
        worsening_signals_count = len(agreeing_signals)
        improving_count = sum([
            1 for s in [pain_short_slope, wound_short_slope, temp_short_slope] if s < -0.2
        ])

        if worsening_signals_count >= 1 and persistence_count >= 1:
            if improving_count >= 1:
                trajectory_direction = "Mixed"
            else:
                trajectory_direction = "Worsening"
        elif improving_count >= 1 and worsening_signals_count == 0:
            trajectory_direction = "Improving"
        else:
            trajectory_direction = "Stable"

        return {
            "trajectory_direction": trajectory_direction,
            "persistence_count": persistence_count,
            "multi_signal_agreement": multi_signal_agreement,
            "agreeing_signals": agreeing_signals,
            "pain_short_slope": pain_short_slope,
            "temp_short_slope": temp_short_slope,
            "wound_short_slope": wound_short_slope,
            "pain_med_slope": pain_med_slope,
            "temp_med_slope": temp_med_slope,
            "wound_med_slope": wound_med_slope,
        }
