from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "symptom_model.joblib"
CARD_PATH = ROOT / "models" / "model_card.json"

def get_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)

def predict(payload: dict):
    model = get_model()
    if model is None:
        return {"available": False, "matches": [], "model_note": "Model not trained yet. Run python train_models.py."}
    age_band = f"{min(100, max(0, int(payload.get('age', 30) // 10) * 10))}s"
    record = {
        "Fever": "yes" if payload.get("fever") else "no",
        "Cough": "yes" if payload.get("cough") else "no",
        "Fatigue": "yes" if payload.get("fatigue") else "no",
        "Difficulty Breathing": "yes" if payload.get("difficulty_breathing") else "no",
        "Age": age_band,
        "Gender": str(payload.get("gender", "Other")).lower(),
        "Blood Pressure": str(payload.get("blood_pressure_label", "Normal")).lower(),
        "Cholesterol Level": str(payload.get("cholesterol_label", "Normal")).lower(),
    }
    probs = model.predict_proba([record])[0]
    classes = model.classes_
    top = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)[:3]
    return {
        "available": True,
        "matches": [{"condition": str(name), "score": round(float(score) * 100, 1)} for name, score in top],
        "model_note": "Scores are relative model outputs, not medical probabilities or diagnoses."
    }

def safety_flags(payload: dict):
    flags = []
    if payload.get("spo2", 98) < 90:
        flags.append({"level": "critical", "message": "Oxygen reading is very low. Seek urgent medical care now."})
    elif payload.get("spo2", 98) < 94:
        flags.append({"level": "warning", "message": "Oxygen reading is below typical range. Recheck and contact a healthcare professional promptly."})
    if payload.get("systolic_bp", 118) >= 180 or payload.get("diastolic_bp", 78) >= 120:
        flags.append({"level": "critical", "message": "Blood pressure reading is severely high. Seek urgent medical advice; emergency symptoms require emergency services."})
    if payload.get("temperature_c", 36.8) >= 40:
        flags.append({"level": "critical", "message": "Very high temperature recorded. Seek urgent medical advice."})
    if payload.get("difficulty_breathing"):
        flags.append({"level": "warning", "message": "Breathing difficulty can be serious. Seek urgent care if severe, sudden, or worsening."})
    return flags
