import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from backend.app.config import settings

class AlertEngine:
    """
    Intelligent alerting with deduplication and alert episode grouping.
    Suppresses low-value repetitive alerts, groups related events, and provides explainability.
    """

    @classmethod
    def evaluate_alert(
        cls,
        patient_id: str,
        observation_id: str,
        risk_score: float,
        risk_category: str,
        trends: Dict[str, Any],
        what_changed_summary: str,
        active_alerts: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluates whether an alert should be created, updated, or suppressed.
        Returns alert payload or None.
        """
        if risk_category == "Stable":
            return None

        # Check for existing active episode within grouping window
        existing_episode = None
        for a in active_alerts:
            if not a.get("is_suppressed", False) and not a.get("acknowledged", False):
                existing_episode = a
                break

        # Check if this is an isolated spike that should be suppressed
        is_isolated_watch = (
            risk_category == "Watch" and
            trends.get("persistence_count", 0) < 2 and
            not trends.get("multi_signal_agreement", False)
        )

        if is_isolated_watch:
            return {
                "alert_id": f"ALT-{uuid.uuid4().hex[:8].upper()}",
                "patient_id": patient_id,
                "observation_id": observation_id,
                "timestamp": datetime.utcnow(),
                "severity": "Watch",
                "title": "Transient Variation Flagged (Alert Suppressed)",
                "explanation": (
                    "• Single non-persistent deviation detected.\n"
                    "• Secondary recovery indicators remain stable.\n"
                    "• Alert suppressed from main queue to prevent clinical alarm fatigue."
                ),
                "contributing_signals": "; ".join(trends.get("agreeing_signals", ["Transient Shift"])),
                "episode_id": existing_episode.get("episode_id") if existing_episode else f"EP-{uuid.uuid4().hex[:6].upper()}",
                "is_suppressed": True,
                "suppression_reason": "Low-value isolated spike: persistence and multi-signal criteria not met.",
                "acknowledged": False
            }

        # For Review or High Priority alerts:
        severity = risk_category
        title = f"{severity.upper()}: Multi-Signal Deterioration Signal" if trends.get("multi_signal_agreement") else f"{severity.upper()}: Significant Trajectory Deviation"

        explanation_lines = [
            f"Risk Score: {risk_score:.0f}/100 ({severity})",
            what_changed_summary
        ]
        if trends.get("multi_signal_agreement"):
            explanation_lines.append(f"• Concordant multi-signal deterioration across: {', '.join(trends.get('agreeing_signals', []))}")
        if trends.get("persistence_count", 0) >= 2:
            explanation_lines.append(f"• Change persisted over {trends.get('persistence_count')} consecutive evaluations.")

        explanation = "\n".join(explanation_lines)

        # Episode Grouping & Deduplication
        if existing_episode:
            # If current severity is higher than existing, escalate the episode
            prev_sev = existing_episode.get("severity", "Review")
            if severity == "High Priority" and prev_sev != "High Priority":
                return {
                    "alert_id": existing_episode.get("alert_id"),
                    "patient_id": patient_id,
                    "observation_id": observation_id,
                    "timestamp": datetime.utcnow(),
                    "severity": "High Priority",
                    "title": f"ESCALATED EPISODE: {title}",
                    "explanation": f"Episode upgraded from {prev_sev} to High Priority.\n{explanation}",
                    "contributing_signals": "; ".join(trends.get("agreeing_signals", [])),
                    "episode_id": existing_episode.get("episode_id"),
                    "is_suppressed": False,
                    "suppression_reason": None,
                    "acknowledged": False,
                    "is_update": True
                }
            else:
                # Same severity ongoing episode: suppress duplicate alert creation
                return {
                    "alert_id": f"ALT-{uuid.uuid4().hex[:8].upper()}",
                    "patient_id": patient_id,
                    "observation_id": observation_id,
                    "timestamp": datetime.utcnow(),
                    "severity": severity,
                    "title": f"Episode Update ({existing_episode.get('episode_id')})",
                    "explanation": explanation,
                    "contributing_signals": "; ".join(trends.get("agreeing_signals", [])),
                    "episode_id": existing_episode.get("episode_id"),
                    "is_suppressed": True,
                    "suppression_reason": f"Deduplicated: Active episode {existing_episode.get('episode_id')} already assigned to care team.",
                    "acknowledged": False,
                    "is_update": True
                }

        # Create fresh episode
        new_episode_id = f"EP-{uuid.uuid4().hex[:6].upper()}"
        return {
            "alert_id": f"ALT-{uuid.uuid4().hex[:8].upper()}",
            "patient_id": patient_id,
            "observation_id": observation_id,
            "timestamp": datetime.utcnow(),
            "severity": severity,
            "title": title,
            "explanation": explanation,
            "contributing_signals": "; ".join(trends.get("agreeing_signals", [])),
            "episode_id": new_episode_id,
            "is_suppressed": False,
            "suppression_reason": None,
            "acknowledged": False
        }
