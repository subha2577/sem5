from typing import Dict, Any, Tuple, List, Optional

class RiskEngine:
    """
    Computes composite patient risk score (0-100) and risk category.
    Provides transparent explainability breakdown with numerical contributor weights.
    Generates 'What Changed?' and 'Why No Alert?' clinical summaries.
    """

    @classmethod
    def calculate_risk_score(
        cls,
        deviations: Dict[str, float],
        trends: Dict[str, Any],
        current_obs: Dict[str, Any],
        data_quality_score: float = 100.0,
        baseline: Optional[Dict[str, float]] = None
    ) -> Tuple[float, str, Dict[str, float], str, Optional[str]]:
        """
        Calculates composite risk score and explainability strings.
        Returns:
            risk_score (float 0-100)
            risk_category (Stable, Watch, Review, High Priority)
            contributors (dict)
            what_changed_summary (str)
            why_no_alert_reason (str or None)
        """
        # 1. Baseline Deviation Component (0 - 30 pts)
        delta_pain = max(0.0, deviations.get("delta_pain", 0.0))
        delta_temp = max(0.0, deviations.get("delta_temp", 0.0))
        delta_wound = max(0.0, deviations.get("delta_wound", 0.0))

        pain_dev_pts = min(12.0, (delta_pain / 3.0) * 12.0)
        temp_dev_pts = min(10.0, (delta_temp / 1.0) * 10.0)
        wound_dev_pts = min(8.0, (delta_wound / 3.0) * 8.0)
        baseline_deviation_pts = round(pain_dev_pts + temp_dev_pts + wound_dev_pts, 1)

        # 2. Rate of Change Component (0 - 25 pts)
        pain_slope = max(0.0, trends.get("pain_short_slope", 0.0))
        temp_slope = max(0.0, trends.get("temp_short_slope", 0.0))
        wound_slope = max(0.0, trends.get("wound_short_slope", 0.0))

        roc_pts = min(25.0, (pain_slope * 6.0) + (temp_slope * 12.0) + (wound_slope * 8.0))
        rate_of_change_pts = round(roc_pts, 1)

        # 3. Persistence Component (0 - 20 pts)
        persistence_count = trends.get("persistence_count", 0)
        if persistence_count >= 3:
            persistence_pts = 20.0
        elif persistence_count == 2:
            persistence_pts = 14.0
        elif persistence_count == 1:
            persistence_pts = 6.0
        else:
            persistence_pts = 0.0

        # 4. Multi-Signal Agreement (0 - 15 pts)
        agreeing = trends.get("agreeing_signals", [])
        if len(agreeing) >= 3:
            multi_signal_pts = 15.0
        elif len(agreeing) == 2:
            multi_signal_pts = 10.0
        elif len(agreeing) == 1:
            multi_signal_pts = 4.0
        else:
            multi_signal_pts = 0.0

        # 5. Symptom Severity & Concerns (0 - 10 pts)
        concern = current_obs.get("patient_reported_concern", "None")
        concern_pts = 5.0 if concern in ["Severe", "Moderate"] else 0.0
        mobility = float(current_obs.get("mobility_score", 7.0))
        mobility_loss_pts = 3.0 if mobility < 4.0 else 0.0
        fatigue_pts = 2.0 if float(current_obs.get("fatigue_score", 2.0)) >= 8.0 else 0.0
        symptom_severity_pts = min(10.0, concern_pts + mobility_loss_pts + fatigue_pts)

        # 6. Data Quality Adjustment (-5 to 0 pts)
        dq_adjustment = 0.0
        if data_quality_score < 70.0:
            dq_adjustment = -5.0 # Caution penalty due to data ambiguity

        # Composite Sum (0 - 100)
        raw_total = (
            baseline_deviation_pts +
            rate_of_change_pts +
            persistence_pts +
            multi_signal_pts +
            symptom_severity_pts +
            dq_adjustment
        )
        risk_score = round(max(0.0, min(100.0, raw_total)), 1)

        # Risk Categories
        if risk_score >= 75.0:
            risk_category = "High Priority"
        elif risk_score >= 50.0:
            risk_category = "Review"
        elif risk_score >= 25.0:
            risk_category = "Watch"
        else:
            risk_category = "Stable"

        contributors = {
            "baseline_deviation": baseline_deviation_pts,
            "rate_of_change": rate_of_change_pts,
            "persistence": persistence_pts,
            "multi_signal": multi_signal_pts,
            "symptom_severity": symptom_severity_pts,
            "data_quality_adjustment": dq_adjustment,
            "total_score": risk_score
        }

        # Build "What Changed?" Clinical Summary
        change_bullets = []
        if delta_pain >= 1.0:
            b_pain = baseline.get("baseline_pain", 3.0) if baseline else 3.0
            change_bullets.append(f"Pain score elevated by +{delta_pain:.1f} vs personal baseline ({b_pain:.1f}).")
        if delta_temp >= 0.4:
            b_temp = baseline.get("baseline_temperature", 36.8) if baseline else 36.8
            change_bullets.append(f"Temperature increased by +{delta_temp:.1f}°C vs personal baseline ({b_temp:.1f}°C).")
        if delta_wound >= 1.0:
            change_bullets.append(f"Wound concern composite score increased by +{delta_wound:.1f}.")
        if persistence_count >= 2:
            change_bullets.append(f"Concerning trend has persisted across {persistence_count} consecutive readings.")
        if len(agreeing) >= 2:
            change_bullets.append(f"Multiple signals concordantly deteriorating: {', '.join(agreeing)}.")
        if concern in ["Severe", "Moderate"]:
            change_bullets.append(f"Patient explicitly reported {concern.lower()} subjective concern.")

        if not change_bullets:
            what_changed_summary = "Patient measurements remain concordant with expected post-operative recovery baseline."
        else:
            what_changed_summary = "\n".join([f"• {b}" for b in change_bullets])

        # Build "Why No Alert?" Rationale (Crucial differentiator for isolated spikes)
        why_no_alert_reason = None
        cur_pain = float(current_obs.get("pain_score", 0.0))
        cur_temp = float(current_obs.get("temperature", 36.8))
        is_isolated_spike = (cur_pain >= 6.0 or cur_temp >= 37.8) and persistence_count < 2 and len(agreeing) < 2

        if is_isolated_spike and risk_category in ["Stable", "Watch"]:
            reasons = [
                "Abnormal reading detected as an isolated transient spike.",
                "No multi-signal agreement: secondary indicators (temperature/wound) remain within personal baseline.",
                f"Persistence requirement not met (persistence count: {persistence_count} < 2).",
                "Alert suppressed to prevent clinical fatigue while flagged for active watch."
            ]
            why_no_alert_reason = "\n".join([f"✓ {r}" for r in reasons])

        return risk_score, risk_category, contributors, what_changed_summary, why_no_alert_reason
