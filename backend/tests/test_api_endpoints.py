import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "model" in data
    assert "disclaimer" in data

def test_dashboard_summary_endpoint():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_patients_monitored" in data
    assert "low_value_alert_reduction_pct" in data
    assert "clinically_relevant_detection_rate_pct" in data

def test_patients_list_endpoint():
    response = client.get("/api/patients?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "patient_id" in data[0]

def test_patient_detail_demo_rec001():
    response = client.get("/api/patients/REC-001")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == "REC-001"
    assert "baseline" in data
    assert data["baseline"]["baseline_pain"] is not None

def test_patient_timeline_endpoint():
    response = client.get("/api/patients/REC-001/timeline")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "pain_score" in data[0]

def test_alerts_endpoint():
    response = client.get("/api/alerts?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_tasks_endpoint():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_simulation_endpoint():
    payload = {
        "trajectory_group": "Group B - Temporary Variation",
        "baseline_pain": 3.0,
        "baseline_temp": 36.8,
        "observation_steps": 6
    }
    response = client.post("/api/simulation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recoverai_result" in data
    assert "simple_baseline_result" in data
    assert data["scenario_name"] == "Group B - Temporary Variation"
    assert "why_no_alert_explanation" in data
