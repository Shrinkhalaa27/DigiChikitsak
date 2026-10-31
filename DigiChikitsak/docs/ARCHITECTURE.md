# Architecture Notes

DigiChikitsak is a local educational proof of concept maintained by **TeamDiamonds** (Shrinkhala Anand and Vaidik Gupta).

## Request flow

1. The welcome/login overlay supports patient lookup, new registration, guest access, age and symptom intake.
2. The entry flow calls `GET /api/patients/lookup` for existing patient lookup and `POST /api/patients` for a new/guest demo profile.
3. The selected age, symptoms, and patient record are passed to the main kiosk via a browser custom event. The main kiosk pre-populates its patient state and begins the pre-check stage.
4. The kiosk guides the patient through vitals, symptom duration, verification, exploratory assessment, care information, and report.
5. Assessment submission is persisted through `POST /api/assessments`; patient and assessment data are stored in local SQLite.
6. The staff dashboard queries the FastAPI endpoints to find patient records and assessment history.

## Main components

- `app/static/index.html`: kiosk UI, welcome/login overlay, multilingual patient journey, inline client-side state and rendering.
- `app/static/assets/doctor-lady.png`: female doctor illustration used in the welcome screen.
- `app/main.py`: FastAPI routes for health, patients, lookup, assessment, and static pages.
- `app/schemas.py`: Pydantic request models and field constraints.
- `app/db.py`: SQLite schema and connection helpers.
- `app/ml.py`: model loading/prediction and rule-based safety flags.
- `train_models.py`: trains/rebuilds the prototype model from included data.
- `app/static/staff.html` and `app/static/staff.js`: staff-facing demo dashboard.

## Data flow and safety

Patient registration and assessments are stored locally in SQLite. The ML result is exploratory; safety flags are rule-based and separate. OTP is not actually delivered, QR scanning uses a patient-ID prompt as a demo fallback, and readings may be simulated or entered manually. The application is not clinically validated and must not be used for diagnosis or treatment decisions.

See `architecture_diagram.pdf` for a diagram and `../README.md` for setup and API details.
