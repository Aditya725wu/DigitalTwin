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

- FastAPI backend with editable synthetic patient EHRs, validated vitals, deterministic risk explanations and summaries, baseline deviation, JSON export, and reset
- Alert generation, acknowledgement, three-strike flag tracking, and clearly labelled simulated family-notification logs
- Three-second synthetic live simulator with WebSocket vital, alert, and prediction updates
- Next.js doctor dashboard with patient search/filter/sort, add/edit/delete, vital entry, what-if scenarios, risk breakdowns, family contacts, trend charts, timeline replay, JSON export, and print view
- Expo SDK 49 patient app with patient selection, live shared patient data, vital entry, alert acknowledgement, EHR/family editing, local medication and appointment reminders, dark mode, language switch, and emergency card
- Swagger / OpenAPI documentation at `/docs`

The backend stores demo data in memory by default. The apps display: “Synthetic demo data. Not a medical device. Not for clinical decisions.”

## Demo recording

The CardioTwin walkthrough recorded on 2026-10-24 is available as [an MP4 video](CardioTwin-Demo-2026-10-24.mp4) in the repository root. The video is stored with Git LFS; install Git LFS and pull the LFS objects to download it with a clone.

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
CardioTwin-Demo-2026-10-24.mp4  Root-level project demo recording (Git LFS)
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

Run the following from the repository root (`D:\DigitalTwin\DigitalTwin`):

```bat
cd /d "D:\DigitalTwin\DigitalTwin\backend"
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

cd /d "D:\DigitalTwin\DigitalTwin\web-dashboard"
npm install
```

Then start three terminals.

**Terminal 1 — backend**

```bat
cd /d "D:\DigitalTwin\DigitalTwin\backend"
call venv\Scripts\activate.bat
uvicorn main:app --reload --port 8000
```

**Terminal 2 — web dashboard**

```bat
cd /d "D:\DigitalTwin\DigitalTwin\web-dashboard"
npm run dev
```

**Terminal 3 — Expo app**

```bat
cd /d "D:\DigitalTwin\DigitalTwin\mobile-app"
npx expo start
```

Open:

- Dashboard: http://localhost:3000/dashboard
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` for the web dashboard and `EXPO_PUBLIC_API_URL=http://localhost:8000` for a local mobile emulator. For a physical phone, use the computer's LAN address for the Expo variable, e.g. `http://192.168.1.20:8000`. The API CORS policy permits localhost and private LAN origins. Expo remains on SDK 49.

Alternatively, after installing dependencies, double-click `START.bat` to launch the backend and web dashboard.

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

AsyncStorage is pinned to the SDK 49 compatible version by `npx expo install @react-native-async-storage/async-storage`. The Android application ID is `com.aditya.cardiotwin`.

For a physical phone, set `EXPO_PUBLIC_API_URL` to the host computer's LAN IP, for example `http://192.168.1.20:8000`, and ensure the phone and computer are on the same network.

## Demo flow for judges

1. Start the backend and dashboard.
2. Open the dashboard and show the four seeded patients.
3. Point out the static EHR risk factors on the patient roster.
4. Show live wearable vitals and the heart-rate / blood-pressure chart.
5. Open the prediction watchlist and compare LOW, MODERATE, HIGH, and CRITICAL profiles.
6. Open the alert queue and acknowledge one alert.
7. Add a patient and submit a vital reading from the dashboard or Swagger. HR `128`, BP `182/118`, and SpO2 `92` generates a CRITICAL BP alert.
8. Open the factor explanation, run a what-if, start live monitoring, and acknowledge the alert.
9. Select that same patient in the mobile app; the shared patient API and WebSocket update its vitals and alert feed.

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

# Expo SDK 49 bundle check
cd ../mobile-app
npx expo export --platform android --output-dir dist
```

Demo notice: Synthetic demo data. Not a medical device. Not for clinical decisions.

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
