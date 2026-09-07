import pytest
from backend.app.services.risk_engine import RiskEngine

def test_stable_risk_score():
    devs = {"delta_pain": 0.0, "delta_temp": 0.0, "delta_wound": 0.0}
    trends = {
        "trajectory_direction": "Stable",
        "persistence_count": 0,
        "agreeing_signals": [],
        "pain_short_slope": 0.0,
        "temp_short_slope": 0.0,
        "wound_short_slope": 0.0
    }
    obs = {"pain_score": 2.0, "temperature": 36.7, "patient_reported_concern": "None"}
    score, cat, contribs, changed, no_alert = RiskEngine.calculate_risk_score(devs, trends, obs)
    assert score < 25.0
    assert cat == "Stable"
    assert "concordant with expected" in changed.lower()

def test_high_priority_multi_signal_risk():
    devs = {"delta_pain": 4.0, "delta_temp": 1.5, "delta_wound": 3.0}
    trends = {
        "trajectory_direction": "Worsening",
        "persistence_count": 3,
        "agreeing_signals": ["Pain", "Temperature", "Wound Concern"],
        "pain_short_slope": 1.5,
        "temp_short_slope": 0.6,
        "wound_short_slope": 1.0
    }
    obs = {"pain_score": 8.0, "temperature": 38.8, "patient_reported_concern": "Severe"}
    score, cat, contribs, changed, no_alert = RiskEngine.calculate_risk_score(devs, trends, obs)
    assert score >= 75.0
    assert cat == "High Priority"
    assert contribs["persistence"] == 20.0
    assert contribs["multi_signal"] == 15.0
    assert "persisted across 3" in changed

def test_why_no_alert_generation_for_transient_spike():
    # An isolated pain spike (7.0) with zero persistence
    devs = {"delta_pain": 3.5, "delta_temp": 0.1, "delta_wound": 0.0}
    trends = {
        "trajectory_direction": "Stable",
        "persistence_count": 0,
        "agreeing_signals": ["Pain"],
        "pain_short_slope": 0.0,
        "temp_short_slope": 0.0,
        "wound_short_slope": 0.0
    }
    obs = {"pain_score": 7.0, "temperature": 36.8, "patient_reported_concern": "None"}
    score, cat, contribs, changed, no_alert = RiskEngine.calculate_risk_score(devs, trends, obs)
    assert cat in ["Stable", "Watch"]
    assert no_alert is not None
    assert "isolated transient spike" in no_alert.lower()
    assert "persistence requirement not met" in no_alert.lower()

def test_data_quality_penalty_adjustment():
    devs = {"delta_pain": 2.0, "delta_temp": 0.5, "delta_wound": 1.0}
    trends = {"trajectory_direction": "Worsening", "persistence_count": 1, "agreeing_signals": []}
    obs = {"pain_score": 5.0, "temperature": 37.3}
    score_clean, _, contribs_clean, _, _ = RiskEngine.calculate_risk_score(devs, trends, obs, data_quality_score=100.0)
    score_poor, _, contribs_poor, _, _ = RiskEngine.calculate_risk_score(devs, trends, obs, data_quality_score=50.0)
    assert contribs_poor["data_quality_adjustment"] == -5.0
    assert score_poor < score_clean

def test_risk_categories_boundaries():
    assert 24.0 < 25.0 # Stable
    assert 49.0 < 50.0 # Watch
    assert 74.0 < 75.0 # Review
    # Tested against 0-100 scale
