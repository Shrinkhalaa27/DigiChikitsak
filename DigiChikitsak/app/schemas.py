from pydantic import BaseModel, Field
from typing import Literal

class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=1, le=120)
    gender: Literal["Female", "Male", "Other", "Prefer not to say"] = "Prefer not to say"
    mobile: str | None = Field(default=None, max_length=20)

class AssessmentCreate(BaseModel):
    patient_id: str
    symptoms: list[str] = []
    age: int = Field(ge=1, le=120)
    gender: Literal["Female", "Male", "Other", "Prefer not to say"] = "Prefer not to say"
    temperature_c: float = Field(default=36.8, ge=30, le=45)
    spo2: int = Field(default=98, ge=50, le=100)
    systolic_bp: int = Field(default=118, ge=50, le=300)
    diastolic_bp: int = Field(default=78, ge=30, le=200)
    weight_kg: float = Field(default=65, ge=1, le=400)
    height_cm: float = Field(default=165, ge=40, le=250)
    duration_days: int = Field(default=1, ge=0, le=365)
    fever: bool = False
    cough: bool = False
    fatigue: bool = False
    difficulty_breathing: bool = False
    blood_pressure_label: Literal["Low", "Normal", "High"] = "Normal"
    cholesterol_label: Literal["Low", "Normal", "High"] = "Normal"
