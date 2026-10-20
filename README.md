# CardioTwin

CardioTwin is a cardiovascular Digital Twin proof-of-concept for the Happiest Health Digital Twin Challenge 2026. It combines a synthetic electronic health record (EHR) with simulated wearable telemetry to help a clinician review cardiac risk, vital-sign trends, and alerts before an adverse event occurs.

> **Prototype notice:** This project uses synthetic demo patients and simplified risk heuristics. It is not a medical device and must not be used for clinical decisions.

## Challenge alignment

The prototype demonstrates the required two-stream fusion:

1. **Static / historical EHR** — age, sex, BMI, smoking, diabetes, hypertension, family history, and cholesterol values.
2. **Dynamic wearable stream** — heart rate, blood pressure, oxygen saturation, ECG rhythm, timestamp, and source.
3. **Digital-twin output** — cardiac-event probability, risk classification, arrhythmia signal, blood-pressure trend, recommendations, and alerts.
4. **Clinical UI** — a responsive doctor dashboard plus a patient-facing Expo mobile app.

## What works

- FastAPI backend with seeded synthetic cardiac patients
- Cardiac prediction endpoint with risk classification
- Arrhythmia and blood-pressure checks
- Alert generation and acknowledgement
- WebSocket endpoint for patient telemetry
- Next.js doctor dashboard with live API data, charts, risk mix, prediction watchlist, and alert queue
- Expo mobile app screens for cardiac status, telemetry, alerts, and profile
- Swagger / OpenAPI documentation at `/docs`

## Repository layout

```text
backend/
  main.py                    FastAPI app and in-memory demo state
  heart_disease_models.py    Optional synthetic model-training utilities
  generate_cardiac_data.py  Synthetic EHR and wearable data generator
  config.py                  Environment and threshold configuration
  requirements.txt           Python dependencies
web-dashboard/               Next.js doctor dashboard
mobile-app/                  React Native / Expo patient app
docs/                        API, deployment, and submission notes
START.bat                    Windows convenience launcher
.env.example                Local environment template
LICENSE                      MIT license
```

## Quick start

### Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer and npm
- Optional: Expo Go for the mobile app

### Windows

Run the following from the repository root (`D:\Digital Twin`):

```bat
cd /d "D:\Digital Twin\backend"
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

cd /d "D:\Digital Twin\web-dashboard"
npm install
```

Then start two terminals.

**Terminal 1 — backend**

```bat
cd /d "D:\Digital Twin\backend"
call venv\Scripts\activate.bat
uvicorn main:app --reload --port 8000
```

**Terminal 2 — web dashboard**

```bat
cd /d "D:\Digital Twin\web-dashboard"
npm run dev
```

Open:

- Dashboard: http://localhost:3000/dashboard
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Alternatively, after installing dependencies, double-click `START.bat`.

### macOS / Linux

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Terminal 1
uvicorn main:app --reload --port 8000

# Terminal 2
cd ../web-dashboard
npm install
npm run dev
```

### Mobile app

```bash
cd mobile-app
npm install
npx expo start
```

For a physical phone, set `EXPO_PUBLIC_API_URL` to the host computer's LAN IP, for example `http://192.168.1.20:8000`, and ensure the phone and computer are on the same network.

## Demo flow for judges

1. Start the backend and dashboard.
2. Open the dashboard and show the four seeded patients.
3. Point out the static EHR risk factors on the patient roster.
4. Show live wearable vitals and the heart-rate / blood-pressure chart.
5. Open the prediction watchlist and compare LOW, MODERATE, HIGH, and CRITICAL profiles.
6. Open the alert queue and acknowledge one alert.
7. Submit a new vital reading through Swagger: `POST /api/patients/{patient_id}/vitals`.
8. Refresh the dashboard and show the new telemetry / alert state.
9. Open the mobile app to show the patient-facing view.

Example vital payload:

```json
{
  "heart_rate_bpm": 128,
  "blood_pressure_systolic": 182,
  "blood_pressure_diastolic": 118,
  "oxygen_saturation": 92,
  "ecg_rhythm": "Tachycardia",
  "ecg_quality": "GOOD",
  "source": "wearable"
}
```

## Verification

```bash
# Backend syntax
python -m py_compile backend/main.py backend/heart_disease_models.py backend/generate_cardiac_data.py

# Web production build
cd web-dashboard
npm run build
```

The backend stores demo state in memory, so seeded patients and newly submitted readings reset when the API process restarts.

## Documentation

- [Setup guide](SETUP.md)
- [API reference](docs/api-reference.md)
- [Deployment notes](docs/deployment.md)
- [Hackathon submission checklist](docs/hackathon-submission.md)

## Team and submission placeholders

Before submitting, replace the placeholders in `docs/hackathon-submission.md` with the team name, college/incubator, team members, demo-video link, architecture PDF/PPT link, and presentation link.

## License

MIT — see [LICENSE](LICENSE).
