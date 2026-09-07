from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, timedelta

class DataQualityEngine:
    """
    Validates, scores, and flags incoming patient observations.
    Ensures physiological plausibility, detects reporting anomalies,
    and isolates corrupted or duplicate data without silent drops.
    """

    @staticmethod
    def calculate_composite_wound_score(redness: float, swelling: float, discharge: float, pain: float) -> float:
        # Sum of wound scores (each 0-5, max 20) scaled to 0-10
        raw_sum = redness + swelling + discharge + pain
        return round((raw_sum / 20.0) * 10.0, 1)

    @classmethod
    def validate_observation(
        cls,
        obs_data: Dict[str, Any],
        previous_obs: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[bool, float, List[Dict[str, Any]], Optional[str]]:
        """
        Validates observation and computes Data Quality Score (0-100).
        Returns:
            is_valid (bool): True if allowed into baseline & trend engines, False if quarantined
            quality_score (float): 0 - 100
            flags (list of dicts): Identified data quality events
            quarantine_reason (str or None)
        """
        flags = []
        deductions = 0.0
        quarantine = False
        quarantine_reasons = []

        pain = float(obs_data.get("pain_score", 0.0))
        temp = float(obs_data.get("temperature", 36.8))
        redness = float(obs_data.get("wound_redness_score", 0.0))
        swelling = float(obs_data.get("wound_swelling_score", 0.0))
        discharge = float(obs_data.get("wound_discharge_score", 0.0))
        wound_pain = float(obs_data.get("wound_pain_score", 0.0))
        timestamp = obs_data.get("timestamp")

        # 1. Physiological Range Validation
        if temp < 34.0 or temp > 42.5:
            quarantine = True
            quarantine_reasons.append(f"Critical invalid temperature: {temp:.1f}°C outside viable physiological range (34-42.5°C)")
            flags.append({
                "flag_type": "RANGE_VIOLATION",
                "severity": "Error",
                "description": f"Physiologically implausible temperature recorded: {temp:.1f}°C."
            })
            deductions += 50.0
        elif temp < 35.5 or temp > 40.5:
            flags.append({
                "flag_type": "EXTREME_PHYSIOLOGICAL_VALUE",
                "severity": "Warning",
                "description": f"Extreme temperature value: {temp:.1f}°C."
            })
            deductions += 15.0

        if pain < 0.0 or pain > 10.0:
            quarantine = True
            quarantine_reasons.append(f"Pain score {pain} outside 0-10 scale")
            flags.append({
                "flag_type": "RANGE_VIOLATION",
                "severity": "Error",
                "description": f"Pain score {pain} invalid."
            })
            deductions += 40.0

        for name, val in [("redness", redness), ("swelling", swelling), ("discharge", discharge), ("wound pain", wound_pain)]:
            if val < 0.0 or val > 5.0:
                flags.append({
                    "flag_type": "RANGE_VIOLATION",
                    "severity": "Warning",
                    "description": f"Wound {name} score {val} outside 0-5 scale."
                })
                deductions += 10.0

        # 2. Contradictory Observation Check
        if pain == 0.0 and (redness >= 4.0 or discharge >= 4.0):
            flags.append({
                "flag_type": "CONTRADICTORY_SIGNALS",
                "severity": "Warning",
                "description": "Reported zero pain despite severe wound erythema or purulent discharge."
            })
            deductions += 15.0

        # 3. Dynamic Checks against Previous Observations
        if previous_obs and len(previous_obs) > 0:
            last_obs = previous_obs[-1]
            last_temp = float(last_obs.get("temperature", 36.8))
            last_pain = float(last_obs.get("pain_score", 0.0))
            last_time = last_obs.get("timestamp")

            # Duplicate timestamp check
            if timestamp and last_time and timestamp == last_time:
                quarantine = True
                quarantine_reasons.append("Duplicate observation submission timestamp detected.")
                flags.append({
                    "flag_type": "DUPLICATE_ENTRY",
                    "severity": "Error",
                    "description": "Identical timestamp received for patient observation."
                })
                deductions += 40.0

            # Sudden unphysiological jump check
            temp_delta = abs(temp - last_temp)
            if temp_delta >= 2.5:
                flags.append({
                    "flag_type": "SUDDEN_JUMP",
                    "severity": "Warning",
                    "description": f"Sudden temperature jump of {temp_delta:.1f}°C from previous reading ({last_temp:.1f}°C -> {temp:.1f}°C)."
                })
                deductions += 20.0

            pain_delta = abs(pain - last_pain)
            if pain_delta >= 6.0:
                flags.append({
                    "flag_type": "SUDDEN_JUMP",
                    "severity": "Warning",
                    "description": f"Abrupt pain change of {pain_delta:.1f} points ({last_pain:.1f} -> {pain:.1f})."
                })
                deductions += 15.0

            # Monitoring gap check (elapsed time)
            if timestamp and last_time and isinstance(timestamp, datetime) and isinstance(last_time, datetime):
                elapsed_hours = (timestamp - last_time).total_seconds() / 3600.0
                if elapsed_hours > 36.0:
                    flags.append({
                        "flag_type": "MONITORING_GAP",
                        "severity": "Warning",
                        "description": f"Monitoring gap of {elapsed_hours:.1f} hours detected between submissions."
                    })
                    deductions += 20.0

        quality_score = max(0.0, round(100.0 - deductions, 1))
        reason_str = "; ".join(quarantine_reasons) if quarantine else None
        return (not quarantine, quality_score, flags, reason_str)
