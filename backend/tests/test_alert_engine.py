import pytest
from backend.app.services.alert_engine import AlertEngine

def test_stable_patient_no_alert():
    trends = {"persistence_count": 0, "multi_signal_agreement": False, "agreeing_signals": []}
    alert = AlertEngine.evaluate_alert(
        patient_id="PAT-TEST",
        observation_id="OBS-1",
        risk_score=15.0,
        risk_category="Stable",
        trends=trends,
        what_changed_summary="Stable",
        active_alerts=[]
    )
    assert alert is None

def test_isolated_spike_suppressed():
    trends = {"persistence_count": 1, "multi_signal_agreement": False, "agreeing_signals": ["Pain"]}
    alert = AlertEngine.evaluate_alert(
        patient_id="PAT-TEST",
        observation_id="OBS-2",
        risk_score=35.0,
        risk_category="Watch",
        trends=trends,
        what_changed_summary="Pain spiked",
        active_alerts=[]
    )
    assert alert is not None
    assert alert["is_suppressed"] is True
    assert "Low-value isolated spike" in alert["suppression_reason"]

def test_high_priority_alert_generation():
    trends = {"persistence_count": 3, "multi_signal_agreement": True, "agreeing_signals": ["Pain", "Temperature"]}
    alert = AlertEngine.evaluate_alert(
        patient_id="PAT-TEST",
        observation_id="OBS-3",
        risk_score=85.0,
        risk_category="High Priority",
        trends=trends,
        what_changed_summary="Multiple indicators rising",
        active_alerts=[]
    )
    assert alert is not None
    assert alert["is_suppressed"] is False
    assert alert["severity"] == "High Priority"
    assert "HIGH PRIORITY" in alert["title"]
    assert alert["episode_id"] is not None

def test_alert_deduplication_into_episode():
    # Existing active episode
    active = [{
        "alert_id": "ALT-1",
        "episode_id": "EP-100",
        "severity": "Review",
        "acknowledged": False,
        "is_suppressed": False
    }]
    trends = {"persistence_count": 2, "multi_signal_agreement": False, "agreeing_signals": ["Pain"]}
    alert = AlertEngine.evaluate_alert(
        patient_id="PAT-TEST",
        observation_id="OBS-4",
        risk_score=60.0,
        risk_category="Review",
        trends=trends,
        what_changed_summary="Ongoing pain",
        active_alerts=active
    )
    # Deduplicated into the same episode
    assert alert["episode_id"] == "EP-100"
    assert alert["is_suppressed"] is True
    assert "Deduplicated" in alert["suppression_reason"]

def test_alert_episode_escalation():
    # Previous was Review, now deteriorates to High Priority
    active = [{
        "alert_id": "ALT-1",
        "episode_id": "EP-100",
        "severity": "Review",
        "acknowledged": False,
        "is_suppressed": False
    }]
    trends = {"persistence_count": 3, "multi_signal_agreement": True, "agreeing_signals": ["Pain", "Temperature"]}
    alert = AlertEngine.evaluate_alert(
        patient_id="PAT-TEST",
        observation_id="OBS-5",
        risk_score=88.0,
        risk_category="High Priority",
        trends=trends,
        what_changed_summary="Escalating fever and pain",
        active_alerts=active
    )
    # Upgrades the episode severity to High Priority
    assert alert["severity"] == "High Priority"
    assert alert["is_suppressed"] is False
    assert "ESCALATED EPISODE" in alert["title"]
    assert alert["episode_id"] == "EP-100"
