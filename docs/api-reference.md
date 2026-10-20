# CardioTwin API reference

Base URL: `http://localhost:8000`

All examples use synthetic demo data.

## Health

### `GET /health`

Returns service and heuristic-model availability.

## Patients

### `GET /api/patients`

Returns the current synthetic patient roster.

### `GET /api/patients/{patient_id}`

Returns one patient EHR profile.

### `POST /api/patients`

Registers a patient. Required fields:

```json
{
  "name": "Asha Rao",
  "age": 52,
  "gender": "F",
  "email": "asha@example.com",
  "phone": "+91-9000000000",
  "bmi": 26.4,
  "hypertension": true,
  "diabetes": false,
  "smoker": false,
  "family_history_cvd": true,
  "total_cholesterol": 220,
  "hdl_cholesterol": 45,
  "ldl_cholesterol": 140
}
```

## Wearable vitals

### `POST /api/patients/{patient_id}/vitals`

```json
{
  "heart_rate_bpm": 78,
  "blood_pressure_systolic": 128,
  "blood_pressure_diastolic": 82,
  "oxygen_saturation": 97,
  "ecg_rhythm": "Normal sinus rhythm",
  "ecg_quality": "GOOD",
  "source": "wearable"
}
```

### `GET /api/patients/{patient_id}/vitals?limit=100`

Returns recent wearable readings.

### `GET /api/patients/{patient_id}/vitals/latest`

Returns the latest reading.

## Predictions

### `POST /api/patients/{patient_id}/predict/cardiac`

Combines the patient EHR with stored vitals and returns:

- `cardiac_event_probability`
- `risk_classification` (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`)
- `arrhythmia_risk`
- `blood_pressure_trend`
- `bp_risk_level`
- `recommended_actions`

## Alerts

### `GET /api/alerts`

Returns recent alerts. Optional query parameters: `severity`, `limit`.

### `GET /api/patients/{patient_id}/alerts`

Returns alerts for one patient.

### `POST /api/alerts/{alert_id}/acknowledge`

Marks an alert as acknowledged.

## Analytics

### `GET /api/statistics`

Returns patient count, alert count, risk counts, unacknowledged alerts, and average heart rate.

## Real-time stream

### `WS /ws/patient/{patient_id}`

Send `{"type":"subscribe"}` to subscribe. Send `{"type":"vitals","data":{...}}` to ingest a vital reading and receive alert / prediction updates.

## Error format

```json
{"detail":"Patient not found"}
```
