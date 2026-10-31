"""Train the educational symptom classifier from the supplied CSV.

The source dataset is small and has many disease labels. This is a prototype model,
not a clinically validated diagnostic tool. Run: python train_models.py
"""
from pathlib import Path
import json
import pandas as pd
import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "disease_symptoms.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODEL_DIR / "symptom_model.joblib"
CARD_PATH = MODEL_DIR / "model_card.json"

def _records(frame):
    records = []
    for _, row in frame.iterrows():
        records.append({
            "Fever": str(row["Fever"]).strip().lower(),
            "Cough": str(row["Cough"]).strip().lower(),
            "Fatigue": str(row["Fatigue"]).strip().lower(),
            "Difficulty Breathing": str(row["Difficulty Breathing"]).strip().lower(),
            "Age": f"{min(100, max(0, int(float(row['Age']) // 10) * 10))}s",
            "Gender": str(row["Gender"]).strip().lower(),
            "Blood Pressure": str(row["Blood Pressure"]).strip().lower(),
            "Cholesterol Level": str(row["Cholesterol Level"]).strip().lower(),
        })
    return records

def main():
    df = pd.read_csv(DATA).dropna(subset=["Disease"])
    X = _records(df)
    y = df["Disease"].astype(str).tolist()
    model = Pipeline([("vectorizer", DictVectorizer(sparse=True)), ("classifier", MultinomialNB(alpha=0.5))])
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    unique_rows = len(df.drop_duplicates())
    classes = len(set(y))
    card = {
        "model": "DictVectorizer + Multinomial Naive Bayes",
        "dataset": "Disease_symptom_and_patient_profile_dataset.csv",
        "rows": int(len(df)),
        "unique_rows": int(unique_rows),
        "classes": int(classes),
        "features": ["Fever", "Cough", "Fatigue", "Difficulty Breathing", "Age", "Gender", "Blood Pressure", "Cholesterol Level"],
        "limitations": [
            "Small dataset with many disease classes and sparse examples per class.",
            "Predictions are educational pattern matches, not a diagnosis or calibrated clinical probabilities.",
            "Do not use this model for treatment, triage, or medical decisions."
        ]
    }
    CARD_PATH.write_text(json.dumps(card, indent=2), encoding="utf-8")
    print(f"Trained on {len(df)} rows / {classes} classes. Model: {MODEL_PATH}")
    print("Important: this prototype is not clinically validated.")

if __name__ == "__main__":
    main()
