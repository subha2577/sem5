import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any

class FeatureEngineer:
    """
    Extracts clinical trend, baseline delta, and persistence features from observation series.
    """

    FEATURE_NAMES = [
        "current_pain",
        "current_temp",
        "current_wound_score",
        "delta_pain",
        "delta_temp",
        "delta_wound",
        "pain_short_slope",
        "temp_short_slope",
        "wound_short_slope",
        "persistence_count",
        "multi_signal_flag",
        "fatigue_score",
        "mobility_score",
        "data_quality_score"
    ]

    @classmethod
    def extract_features_from_patient_obs(
        cls,
        observations: List[Dict[str, Any]],
        baseline: Dict[str, float],
        trends: Dict[str, Any],
        data_quality_score: float
    ) -> np.ndarray:
        """
        Builds a single feature vector for model inference.
        """
        if not observations:
            return np.zeros(len(cls.FEATURE_NAMES))

        latest = observations[-1]
        pain = float(latest.get("pain_score", 0.0))
        temp = float(latest.get("temperature", 36.8))
        wound = float(latest.get("composite_wound_score", 0.0))

        delta_pain = pain - baseline.get("baseline_pain", 3.0)
        delta_temp = temp - baseline.get("baseline_temperature", 36.8)
        delta_wound = wound - baseline.get("baseline_wound_score", 1.0)

        vec = [
            pain,
            temp,
            wound,
            delta_pain,
            delta_temp,
            delta_wound,
            trends.get("pain_short_slope", 0.0),
            trends.get("temp_short_slope", 0.0),
            trends.get("wound_short_slope", 0.0),
            float(trends.get("persistence_count", 0)),
            1.0 if trends.get("multi_signal_agreement", False) else 0.0,
            float(latest.get("fatigue_score", 2.0)),
            float(latest.get("mobility_score", 7.0)),
            data_quality_score
        ]
        return np.array(vec, dtype=float)
