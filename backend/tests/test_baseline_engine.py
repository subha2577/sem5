import pytest
from backend.app.services.baseline_engine import BaselineEngine

def test_patient_baseline_calculation():
    history = [
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0},
        {"pain_score": 3.5, "temperature": 36.9, "composite_wound_score": 1.2},
        {"pain_score": 3.0, "temperature": 36.7, "composite_wound_score": 1.0},
        {"pain_score": 2.5, "temperature": 36.8, "composite_wound_score": 0.8},
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0}
    ]
    baseline = BaselineEngine.calculate_patient_baseline(history)
    assert baseline["baseline_pain"] == 3.0
    assert baseline["baseline_temperature"] == 36.8
    assert baseline["baseline_wound_score"] == 1.0
    assert baseline["observation_count"] == 5

def test_empty_history_fallback():
    baseline = BaselineEngine.calculate_patient_baseline([])
    assert baseline["baseline_pain"] == 3.0
    assert baseline["baseline_temperature"] == 36.8
    assert baseline["observation_count"] == 0

def test_quarantined_observations_excluded_from_baseline():
    history = [
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0, "is_quarantined": False},
        {"pain_score": 14.0, "temperature": 43.8, "composite_wound_score": 8.0, "is_quarantined": True},
        {"pain_score": 3.2, "temperature": 36.7, "composite_wound_score": 1.0, "is_quarantined": False}
    ]
    baseline = BaselineEngine.calculate_patient_baseline(history)
    assert baseline["baseline_pain"] < 5.0 # The quarantined 14.0 is ignored
    assert baseline["observation_count"] == 2

def test_baseline_deviations():
    baseline = {
        "baseline_pain": 3.0,
        "baseline_temperature": 36.8,
        "baseline_wound_score": 1.0,
        "pain_rolling_std": 0.5,
        "temp_rolling_std": 0.2,
        "wound_rolling_std": 0.3
    }
    cur = {"pain_score": 6.0, "temperature": 37.8, "composite_wound_score": 2.5}
    devs = BaselineEngine.calculate_deviations(cur, baseline)
    assert devs["delta_pain"] == 3.0
    assert devs["delta_temp"] == 1.0
    assert devs["delta_wound"] == 1.5
    assert devs["z_pain"] == 6.0
    assert devs["z_temp"] == 5.0

def test_negative_deviations_for_improving_patient():
    baseline = {
        "baseline_pain": 4.0,
        "baseline_temperature": 37.0,
        "baseline_wound_score": 2.0
    }
    cur = {"pain_score": 2.0, "temperature": 36.7, "composite_wound_score": 1.0}
    devs = BaselineEngine.calculate_deviations(cur, baseline)
    assert devs["delta_pain"] == -2.0
    assert devs["delta_temp"] == -0.3
    assert devs["delta_wound"] == -1.0
