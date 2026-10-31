import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import DB_PATH

@pytest.fixture()
def client():
    # Tests use the app database path; delete it for isolated test setup.
    if DB_PATH.exists():
        DB_PATH.unlink()
    with TestClient(app) as c:
        yield c
    if DB_PATH.exists():
        DB_PATH.unlink()

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_patient_and_assessment(client):
    patient = client.post("/api/patients", json={
        "name":"Demo Patient","age":27,"gender":"Female","mobile":None
    })
    assert patient.status_code == 201
    pid = patient.json()["patient_id"]
    response = client.post("/api/assessments", json={
        "patient_id":pid,"age":27,"gender":"Female","symptoms":["Fever","Cough"],
        "temperature_c":38.2,"spo2":98,"systolic_bp":118,"diastolic_bp":78,
        "weight_kg":65,"height_cm":165,"duration_days":2,"fever":True,"cough":True,
        "fatigue":False,"difficulty_breathing":False,"blood_pressure_label":"Normal","cholesterol_label":"Normal"
    })
    assert response.status_code == 201
    assert response.json()["result"]["bmi"] == 23.9
    detail = client.get(f"/api/patients/{pid}")
    assert detail.status_code == 200
    assert len(detail.json()["assessments"]) == 1

def test_safety_flags(client):
    patient = client.post("/api/patients", json={"name":"Sample Person","age":40,"gender":"Other"})
    pid = patient.json()["patient_id"]
    response = client.post("/api/assessments", json={
        "patient_id":pid,"age":40,"gender":"Other","symptoms":["Difficulty breathing"],
        "temperature_c":40.1,"spo2":88,"systolic_bp":190,"diastolic_bp":125,
        "weight_kg":70,"height_cm":170,"duration_days":0,"fever":True,"cough":False,
        "fatigue":False,"difficulty_breathing":True,"blood_pressure_label":"High","cholesterol_label":"Normal"
    })
    assert response.status_code == 201
    flags = response.json()["result"]["safety_flags"]
    assert any(f["level"] == "critical" for f in flags)
