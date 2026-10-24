# CardioTwin API reference

Base URL: `http://localhost:8000`. All records and predictions are synthetic.

## Health and demo state

- `GET /health` — service status and heuristic model availability.
- `POST /api/reset` — stop simulators and restore the seeded in-memory demo records.
- `GET /api/statistics` — patient, risk, alert, and average-heart-rate counts.

## Patients and EHR

- `GET /api/patients` — roster.
- `GET /api/patients/{patient_id}` — one EHR record, including `flag_streak` (0–3).
- `POST /api/patients` — create a patient.
- `PUT /api/patients/{patient_id}` — replace editable EHR fields.
- `DELETE /api/patients/{patient_id}` — remove patient, vitals, alerts, family records, and simulator.
- `GET /api/patients/{patient_id}/export` — patient, vitals, alerts, family contact, notification log, and streak as JSON.
- `GET /api/patients/{patient_id}/summary` — deterministic template-based summary of latest reading and current estimate.

Create and edit use the same EHR body. Name, age, gender, email, phone, and BMI are required; risk factors and lipid values have defaults.

```json
{
  "name": "Asha Rao", "age": 52, "gender": "F", "email": "asha@example.com",
  "phone": "+91-9000000000", "bmi": 26.4, "height_cm": 163, "weight_kg": 70,
  "smoker": false, "diabetes": false, "hypertension": true,
  "family_history_cvd": true, "family_history_hypertension": false,
  "total_cholesterol": 220, "hdl_cholesterol": 45, "ldl_cholesterol": 140,
  "medications": ["example medication"], "medical_history": ["example history"]
}
```

## Vitals and baseline

- `POST /api/patients/{patient_id}/vitals` — record a reading through the common ingestion path.
- `GET /api/patients/{patient_id}/vitals?limit=100` — recent readings (`limit` 1–1000).
- `GET /api/patients/{patient_id}/vitals/latest` — latest reading.
- `GET /api/patients/{patient_id}/baseline` — history averages, latest reading, per-signal percentage deviation, and `large_deviation` flag.

Heart rate is validated from 20–250 bpm, systolic BP 50–300 mmHg, diastolic BP 30–200 mmHg, and SpO2 50–100%.

```json
{
  "heart_rate_bpm": 78, "blood_pressure_systolic": 128,
  "blood_pressure_diastolic": 82, "oxygen_saturation": 97,
  "ecg_rhythm": "Normal sinus rhythm", "ecg_quality": "GOOD", "source": "wearable"
}
```

## Predictions

- `POST /api/patients/{patient_id}/predict/cardiac` — active deterministic prediction with probability, classification, rhythm and BP analysis, and recommended actions.
- `POST /api/patients/{patient_id}/whatif` — accepts optional vital and EHR overrides; returns a prediction with `what_if_only: true` and `history_unchanged: true`. It never saves overrides.
- `GET /api/patients/{patient_id}/explain` — factor points, `total_points`, divisor 45, probability, and final class using the same simplified Framingham points as the active scorer.

Risk explanation includes age, gender, systolic BP, total and HDL cholesterol, smoking, and diabetes contributions. Overall class also uses the active arrhythmia and BP-risk rules.

## Alerts and simulated family contact

- `GET /api/alerts?severity=CRITICAL&limit=50` — recent alerts, optionally filtered by severity.
- `GET /api/patients/{patient_id}/alerts?limit=20` — one patient's alerts.
- `POST /api/alerts/{alert_id}/acknowledge` — acknowledge an alert.
- `GET /api/patients/{patient_id}/family-contact` — saved contact, simulated notification log, and flag streak.
- `POST /api/patients/{patient_id}/family-contact` — save `{ "name": "...", "phone": "..." }`.

The streak counts distinct hourly summary buckets (0–3), not multiple readings from the same hour; a non-flagged summary resets it. The simulator advances its synthetic summary clock once per three-second reading while keeping the displayed reading timestamp current. A critical alert with a saved family contact creates a clearly labelled `simulated_queued` log entry. It becomes `simulated_sent` only when three consecutive hourly summaries are flagged. No real message is sent.

## Simulator and WebSocket

- `POST /api/simulate/{patient_id}/start` — start a background simulator producing a synthetic reading every 3 seconds.
- `POST /api/simulate/{patient_id}/stop` — stop it.
- `WS /ws/patient/{patient_id}` — send `{"type":"subscribe"}` to join the patient's stream. Events include `vitals`, `alert`, and `prediction_update`. Sending `{"type":"vitals","data":{...}}` ingests a reading through the same path and broadcasts the update.

The simulator has occasional abnormal spikes. Vitals and alerts are stored in memory by default and are cleared when the process restarts.

## CORS and errors

The API allows localhost web (`3000`), Expo web (`19006`), loopback, and private LAN origins. Validation errors use FastAPI's `422` response; unknown patients or alerts return `404`, for example:

```json
{"detail":"Patient not found"}
```

This prototype uses synthetic demo data. It is not a medical device and is not for clinical decisions.
