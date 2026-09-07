import pytest
from datetime import datetime, timedelta
from backend.app.services.data_quality_engine import DataQualityEngine

def test_valid_observation_scoring():
    obs = {
        "pain_score": 3.0,
        "temperature": 36.8,
        "wound_redness_score": 1.0,
        "wound_swelling_score": 1.0,
        "wound_discharge_score": 0.0,
        "wound_pain_score": 1.0,
        "timestamp": datetime.utcnow()
    }
    is_valid, score, flags, reason = DataQualityEngine.validate_observation(obs)
    assert is_valid is True
    assert score >= 90.0
    assert len(flags) == 0
    assert reason is None

def test_critical_temperature_quarantine():
    obs = {
        "pain_score": 4.0,
        "temperature": 43.5, # Physiologically impossible
        "wound_redness_score": 1.0,
        "wound_swelling_score": 1.0,
        "wound_discharge_score": 0.0,
        "wound_pain_score": 1.0
    }
    is_valid, score, flags, reason = DataQualityEngine.validate_observation(obs)
    assert is_valid is False
    assert score <= 50.0
    assert "Critical invalid temperature" in reason
    assert any(f["flag_type"] == "RANGE_VIOLATION" for f in flags)

def test_invalid_pain_range_quarantine():
    obs = {
        "pain_score": 14.0, # Outside 0-10 scale
        "temperature": 36.8
    }
    is_valid, score, flags, reason = DataQualityEngine.validate_observation(obs)
    assert is_valid is False
    assert "Pain score 14.0 outside 0-10 scale" in reason

def test_contradictory_signals_warning():
    obs = {
        "pain_score": 0.0,
        "temperature": 36.8,
        "wound_redness_score": 4.5,
        "wound_discharge_score": 4.5
    }
    is_valid, score, flags, reason = DataQualityEngine.validate_observation(obs)
    assert is_valid is True # Non-fatal but warning deduction
    assert score < 90.0
    assert any(f["flag_type"] == "CONTRADICTORY_SIGNALS" for f in flags)

def test_sudden_jump_detection():
    t1 = datetime.utcnow() - timedelta(hours=2)
    t2 = datetime.utcnow()
    prev = [{"pain_score": 2.0, "temperature": 36.6, "timestamp": t1}]
    cur = {
        "pain_score": 9.0, # +7.0 point jump
        "temperature": 39.5, # +2.9°C jump
        "timestamp": t2
    }
    is_valid, score, flags, reason = DataQualityEngine.validate_observation(cur, prev)
    assert is_valid is True
    assert any(f["flag_type"] == "SUDDEN_JUMP" for f in flags)

def test_duplicate_timestamp_quarantine():
    t = datetime.utcnow()
    prev = [{"pain_score": 3.0, "temperature": 36.8, "timestamp": t}]
    cur = {"pain_score": 3.0, "temperature": 36.8, "timestamp": t}
    is_valid, score, flags, reason = DataQualityEngine.validate_observation(cur, prev)
    assert is_valid is False
    assert any(f["flag_type"] == "DUPLICATE_ENTRY" for f in flags)
