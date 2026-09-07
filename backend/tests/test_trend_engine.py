import pytest
from backend.app.services.trend_engine import TrendEngine

def test_stable_trajectory():
    history = [
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0},
        {"pain_score": 3.1, "temperature": 36.8, "composite_wound_score": 1.0},
        {"pain_score": 2.9, "temperature": 36.7, "composite_wound_score": 1.1},
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0}
    ]
    trends = TrendEngine.analyze_trends(history)
    assert trends["trajectory_direction"] == "Stable"
    assert trends["persistence_count"] == 0
    assert trends["multi_signal_agreement"] is False

def test_worsening_trajectory():
    history = [
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0},
        {"pain_score": 4.5, "temperature": 37.2, "composite_wound_score": 1.8},
        {"pain_score": 6.0, "temperature": 37.8, "composite_wound_score": 2.6},
        {"pain_score": 7.5, "temperature": 38.4, "composite_wound_score": 3.5}
    ]
    trends = TrendEngine.analyze_trends(history)
    assert trends["trajectory_direction"] == "Worsening"
    assert trends["persistence_count"] >= 3
    assert trends["multi_signal_agreement"] is True
    assert "Pain" in trends["agreeing_signals"]
    assert "Temperature" in trends["agreeing_signals"]

def test_improving_trajectory():
    history = [
        {"pain_score": 6.0, "temperature": 37.2, "composite_wound_score": 3.0},
        {"pain_score": 4.5, "temperature": 36.9, "composite_wound_score": 2.2},
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.5},
        {"pain_score": 2.0, "temperature": 36.7, "composite_wound_score": 1.0}
    ]
    trends = TrendEngine.analyze_trends(history)
    assert trends["trajectory_direction"] == "Improving"
    assert trends["multi_signal_agreement"] is False

def test_isolated_abnormality_trend():
    history = [
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0},
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0},
        {"pain_score": 7.5, "temperature": 38.0, "composite_wound_score": 1.0}, # Spike
        {"pain_score": 3.2, "temperature": 36.8, "composite_wound_score": 1.0}  # Returned
    ]
    trends = TrendEngine.analyze_trends(history)
    # Because it immediately recovered on latest, persistence is 0
    assert trends["persistence_count"] == 0

def test_multi_signal_concordance():
    history = [
        {"pain_score": 3.0, "temperature": 36.8, "composite_wound_score": 1.0},
        {"pain_score": 5.5, "temperature": 37.8, "composite_wound_score": 2.5}
    ]
    trends = TrendEngine.analyze_trends(history)
    assert trends["multi_signal_agreement"] is True
    assert len(trends["agreeing_signals"]) >= 2

def test_closed_form_slope_accuracy():
    # Linear slope: y = 2x + 1 -> slope should be 2.0
    values = [1.0, 3.0, 5.0, 7.0]
    slope = TrendEngine._calculate_slope(values)
    assert round(slope, 2) == 2.0
