# DigiChikitsak Demo Video Script (15–20 minutes)

**Team:** TeamDiamonds — Shrinkhala Anand and Vaidik Gupta  
**Required submission field:** Add the real unlisted YouTube URL to the README after uploading. This document is a recording plan, not a video link.

## Recording outline

| Time | Segment | What to demonstrate |
|---|---|---|
| 0:00–1:30 | Introduction | Team, project title, problem statement, intended community-health use case, PoC disclaimer |
| 1:30–3:30 | Welcome UI | Show the teal-and-white interface, female doctor illustration, healthcare feature tiles, theme/large-text controls, privacy notice |
| 3:30–5:00 | Patient access | Show Patient Login, New Registration, guest flow, patient ID lookup, and explain OTP is simulated |
| 5:00–7:00 | Profile and symptoms | Enter demo name/age/gender, select symptoms, and add optional free text |
| 7:00–10:00 | Guided kiosk | Walk through the main health-kiosk phases, vitals, symptom duration, review/verification, and simulated values |
| 10:00–12:00 | Assessment result | Submit the assessment, explain the exploratory model result and separate rule-based safety flags; do not describe it as diagnosis |
| 12:00–13:30 | Report | Show the visit summary and print flow |
| 13:30–15:00 | Staff dashboard | Search for the demo patient, open visit history, and explain local SQLite persistence |
| 15:00–17:00 | Technical architecture | Show FastAPI `/docs`, health endpoint, project tree, model files, and architecture diagram |
| 17:00–18:30 | Limitations and roadmap | Explain simulated OTP/device data, prototype dataset, lack of clinical validation, security requirements, and next steps |
| 18:30–19:00 | Closing | Summarise the intended value and repeat the safety boundary |

## Recording checklist

- Use fictional patient details only.
- Keep the browser window readable and hide private notifications.
- Show the API docs and architecture PDF briefly.
- Avoid claiming clinical accuracy, measured outcomes, real device integration, or SMS delivery.
- Upload the finished video as **Unlisted**, test access in a private browser, then replace `ADD_REAL_UNLISTED_YOUTUBE_URL_HERE` in `README.md`.
