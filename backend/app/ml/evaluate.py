from typing import Dict, Any, List, Tuple
import numpy as np

class EvaluationEngine:
    """
    Rigorously benchmarks RecoverAI Intelligent Trend Engine against
    a conventional Single-Threshold Baseline on the synthetic cohort.
    """

    @staticmethod
    def is_simple_baseline_alert(obs: Dict[str, Any]) -> bool:
        """
        Conventional monitoring rule:
        Fires an alert if ANY single raw vital crosses a standard threshold.
        """
        pain = float(obs.get("pain_score", 0.0))
        temp = float(obs.get("temperature", 36.8))
        discharge = float(obs.get("wound_discharge_score", 0.0))
        redness = float(obs.get("wound_redness_score", 0.0))

        return (
            pain >= 7.0 or
            temp >= 38.0 or
            discharge >= 3.0 or
            redness >= 3.5
        )

    @classmethod
    def evaluate_cohort(
        cls,
        patient_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates synthetic cohort records.
        Each patient record contains:
          - patient_id
          - trajectory_group
          - observations (list of dicts)
          - ground_truth_escalation ("no_action", "monitor", "review", "urgent_review")
          - recoverai_risk_category
          - recoverai_alert_count
          - recoverai_suppressed_count
        """
        baseline_total_alerts = 0
        baseline_low_value_alerts = 0
        baseline_true_positives = 0
        baseline_false_positives = 0
        baseline_false_negatives = 0

        recoverai_total_alerts = 0
        recoverai_low_value_alerts = 0
        recoverai_true_positives = 0
        recoverai_false_positives = 0
        recoverai_false_negatives = 0

        error_breakdown = {
            "false_positive": 0,
            "false_negative": 0,
            "delayed_detection": 0,
            "data_quality_error": 0,
            "ambiguous_case": 0
        }

        total_patients = len(patient_records)

        for p in patient_records:
            gt = p.get("ground_truth_escalation", "no_action")
            is_clinically_relevant = gt in ["review", "urgent_review"]
            obs_list = p.get("observations", [])

            # --- Simple Baseline Evaluation ---
            # Baseline alerts on every single observation exceeding threshold
            p_baseline_alerts = sum(1 for o in obs_list if cls.is_simple_baseline_alert(o))
            baseline_total_alerts += p_baseline_alerts

            if p_baseline_alerts > 0:
                if is_clinically_relevant:
                    baseline_true_positives += 1
                else:
                    baseline_false_positives += 1
                    baseline_low_value_alerts += p_baseline_alerts
            else:
                if is_clinically_relevant:
                    baseline_false_negatives += 1

            # --- RecoverAI Evaluation ---
            rai_alerts = p.get("recoverai_alert_count", 0)
            rai_cat = p.get("recoverai_risk_category", "Stable")
            rai_flagged = (rai_alerts > 0) or (rai_cat in ["Review", "High Priority"])

            recoverai_total_alerts += rai_alerts

            if rai_flagged:
                if is_clinically_relevant:
                    recoverai_true_positives += 1
                else:
                    recoverai_false_positives += 1
                    recoverai_low_value_alerts += rai_alerts
                    error_breakdown["false_positive"] += 1
            else:
                if is_clinically_relevant:
                    recoverai_false_negatives += 1
                    error_breakdown["false_negative"] += 1

            # Trajectory-specific error taxonomy
            group = p.get("trajectory_group", "Group A")
            if group == "Group H" and not rai_flagged and is_clinically_relevant:
                error_breakdown["data_quality_error"] += 1
            elif group == "Group G" and not rai_flagged and is_clinically_relevant:
                error_breakdown["delayed_detection"] += 1
            elif rai_cat == "Mixed":
                error_breakdown["ambiguous_case"] += 1

        # Metrics calculation
        baseline_precision = baseline_true_positives / max(1, baseline_true_positives + baseline_false_positives)
        baseline_recall = baseline_true_positives / max(1, baseline_true_positives + baseline_false_negatives)
        baseline_f1 = 2 * (baseline_precision * baseline_recall) / max(1e-5, baseline_precision + baseline_recall)

        rai_precision = recoverai_true_positives / max(1, recoverai_true_positives + recoverai_false_positives)
        rai_recall = recoverai_true_positives / max(1, recoverai_true_positives + recoverai_false_negatives)
        rai_f1 = 2 * (rai_precision * rai_recall) / max(1e-5, rai_precision + rai_recall)

        alert_reduction_pct = 0.0
        if baseline_total_alerts > 0:
            alert_reduction_pct = round(((baseline_total_alerts - recoverai_total_alerts) / baseline_total_alerts) * 100.0, 1)

        low_value_reduction_pct = 0.0
        if baseline_low_value_alerts > 0:
            low_value_reduction_pct = round(((baseline_low_value_alerts - recoverai_low_value_alerts) / baseline_low_value_alerts) * 100.0, 1)

        target_achieved = alert_reduction_pct >= 30.0 and rai_recall >= 0.88

        return {
            "total_patients": total_patients,
            "target": "Reduce low-value alerts by at least 30% while maintaining detection >= 88%",
            "target_achieved": target_achieved,
            "alert_reduction_pct": alert_reduction_pct,
            "low_value_reduction_pct": low_value_reduction_pct,
            "simple_baseline": {
                "total_alerts": baseline_total_alerts,
                "low_value_alerts": baseline_low_value_alerts,
                "relevant_cases_surfaced": baseline_true_positives,
                "missed_relevant_cases": baseline_false_negatives,
                "false_alerts": baseline_false_positives,
                "precision": round(float(baseline_precision), 3),
                "recall": round(float(baseline_recall), 3),
                "f1_score": round(float(baseline_f1), 3),
                "avg_alerts_per_patient": round(baseline_total_alerts / max(1, total_patients), 2)
            },
            "recoverai": {
                "total_alerts": recoverai_total_alerts,
                "low_value_alerts": recoverai_low_value_alerts,
                "relevant_cases_surfaced": recoverai_true_positives,
                "missed_relevant_cases": recoverai_false_negatives,
                "false_alerts": recoverai_false_positives,
                "precision": round(float(rai_precision), 3),
                "recall": round(float(rai_recall), 3),
                "f1_score": round(float(rai_f1), 3),
                "avg_alerts_per_patient": round(recoverai_total_alerts / max(1, total_patients), 2)
            },
            "error_breakdown": error_breakdown
        }
