from pathlib import Path
import json
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .db import init_db, connect
from .schemas import PatientCreate, AssessmentCreate
from .ml import predict, safety_flags

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
app = FastAPI(
    title="DigiChikitsak API",
    description="Educational digital-health kiosk prototype. Not a medical device or diagnostic service.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")

@app.get("/staff")
def staff():
    return FileResponse(STATIC / "staff.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "DigiChikitsak", "mode": "educational prototype"}

@app.post("/api/patients", status_code=201)
def create_patient(data: PatientCreate):
    patient_id = "DC-" + uuid.uuid4().hex[:8].upper()
    with connect() as conn:
        conn.execute(
            "INSERT INTO patients(patient_id,name,age,gender,mobile) VALUES(?,?,?,?,?)",
            (patient_id, data.name.strip(), data.age, data.gender, data.mobile)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
    return dict(row)

@app.get("/api/patients")
def list_patients(q: str = ""):
    with connect() as conn:
        rows = conn.execute(
            """SELECT p.*, COUNT(a.id) AS assessment_count,
               MAX(a.created_at) AS last_visit
               FROM patients p LEFT JOIN assessments a ON p.patient_id=a.patient_id
               WHERE p.name LIKE ? OR p.patient_id LIKE ?
               GROUP BY p.patient_id ORDER BY p.created_at DESC LIMIT 200""",
            (f"%{q}%", f"%{q}%")
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/patients/lookup")
def lookup_patient(identifier: str):
    """Look up an existing demo patient by patient ID or mobile number. OTP is simulated in the kiosk UI."""
    key = identifier.strip()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM patients WHERE upper(patient_id)=upper(?) OR mobile=? ORDER BY id DESC LIMIT 1",
            (key, key)
        ).fetchone()
    if not row:
        raise HTTPException(404, "Patient not found. Register a new patient first.")
    return dict(row)

@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: str):
    with connect() as conn:
        patient = conn.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
        if not patient:
            raise HTTPException(404, "Patient not found")
        assessments = conn.execute("SELECT * FROM assessments WHERE patient_id=? ORDER BY id DESC", (patient_id,)).fetchall()
    result = dict(patient)
    result["assessments"] = [
        {**dict(a), "symptoms": json.loads(a["symptoms_json"]), "vitals": json.loads(a["vitals_json"]), "result": json.loads(a["result_json"])}
        for a in assessments
    ]
    return result

@app.post("/api/assessments", status_code=201)
def create_assessment(data: AssessmentCreate):
    payload = data.model_dump()
    with connect() as conn:
        patient = conn.execute("SELECT patient_id FROM patients WHERE patient_id=?", (data.patient_id,)).fetchone()
        if not patient:
            raise HTTPException(404, "Patient not found. Register the patient first.")
        model_result = predict(payload)
        flags = safety_flags(payload)
        bmi = round(data.weight_kg / ((data.height_cm / 100) ** 2), 1)
        health_score = max(0, min(100, int(100 - max(0, data.temperature_c - 37) * 9 - max(0, 95-data.spo2)*3 - max(0, data.systolic_bp-120)*0.15 - len(data.symptoms)*2)))
        result = {
            "matches": model_result["matches"],
            "model_available": model_result["available"],
            "model_note": model_result["model_note"],
            "safety_flags": flags,
            "bmi": bmi,
            "health_score": health_score,
            "recommendation": "Seek urgent care now" if any(f["level"] == "critical" for f in flags) else ("Contact a healthcare professional for assessment" if flags else "Use this summary as a discussion aid with a healthcare professional."),
            "forecast": "No validated recovery forecast is available. Monitor symptoms and follow professional advice."
        }
        vitals = {
            "temperature_c": data.temperature_c, "spo2": data.spo2,
            "systolic_bp": data.systolic_bp, "diastolic_bp": data.diastolic_bp,
            "weight_kg": data.weight_kg, "height_cm": data.height_cm,
            "bmi": bmi, "duration_days": data.duration_days
        }
        cur = conn.execute(
            "INSERT INTO assessments(patient_id,symptoms_json,vitals_json,result_json) VALUES(?,?,?,?)",
            (data.patient_id, json.dumps(data.symptoms), json.dumps(vitals), json.dumps(result))
        )
        conn.commit()
        assessment_id = cur.lastrowid
    return {"id": assessment_id, "patient_id": data.patient_id, "vitals": vitals, "symptoms": data.symptoms, "result": result}

@app.get("/api/assessments/{assessment_id}")
def get_assessment(assessment_id: int):
    with connect() as conn:
        row = conn.execute(
            """SELECT a.*, p.name, p.age, p.gender FROM assessments a
               JOIN patients p ON p.patient_id=a.patient_id WHERE a.id=?""",
            (assessment_id,)
        ).fetchone()
    if not row:
        raise HTTPException(404, "Assessment not found")
    result = dict(row)
    result["symptoms"] = json.loads(result.pop("symptoms_json"))
    result["vitals"] = json.loads(result.pop("vitals_json"))
    result["result"] = json.loads(result.pop("result_json"))
    return result

@app.get("/api/stats")
def stats():
    with connect() as conn:
        patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        assessments = conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
        today = conn.execute("SELECT COUNT(*) FROM assessments WHERE date(created_at)=date('now','localtime')").fetchone()[0]
        flags = conn.execute("SELECT result_json FROM assessments").fetchall()
    critical = 0
    for row in flags:
        try:
            result = json.loads(row["result_json"])
            if any(f.get("level") == "critical" for f in result.get("safety_flags", [])):
                critical += 1
        except Exception:
            pass
    return {"patients": patients, "assessments": assessments, "today": today, "flagged_assessments": critical}

@app.get("/api/model-card")
def model_card():
    path = ROOT.parent / "models" / "model_card.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"model": "Not trained", "limitations": ["Run python train_models.py to create the prototype model."]}
