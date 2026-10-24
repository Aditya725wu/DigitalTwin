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

The demo recording is available as a [GitHub-hosted MP4](CardioTwin-Demo-2026-10-24.mp4) stored with Git LFS. Install Git LFS and pull the LFS objects to download it with a clone. This is a GitHub file link; an Unlisted YouTube URL is not currently available.

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

### Project title

**CardioTwin — Proactive Cardiovascular Digital Twin**

### Problem statement

Cardiovascular risk information is split between historical health records and changing wearable readings. This can make it harder to review a patient's baseline alongside current vital-sign trends and follow up on emerging alerts. CardioTwin demonstrates a unified view that combines synthetic EHR data with simulated wearable telemetry and summarizes risk, trends, and alerts for a prototype workflow.

### Team

- **Manthan Sanap** — Team Leader
- **Aditya Kharade** — Team Member
- **Jay Mapari** — Team Member
- **Aditya Patil** — Team Member

Team name, institution, and public contact details are not specified in the project materials.

### Technical stack

| Area | Technologies |
|---|---|
| Backend API | Python, FastAPI, Pydantic, Uvicorn |
| Data and numeric processing | NumPy, pandas; synthetic EHR and wearable readings |
| Doctor dashboard | Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts, Zustand |
| Patient mobile app | React Native 0.72, Expo SDK 49 |
| App communication | REST/JSON and WebSockets |
| Demo state | In-memory backend data; it resets when the API process restarts |

### AI/ML model and framework details

- **Live API behavior:** the running backend calculates a simplified Framingham-inspired score and uses rule-based thresholds for risk categories, vital-sign alerts, and blood-pressure trends.
- **Optional training utilities:** `backend/heart_disease_models.py` includes a synthetic-data training workflow with scikit-learn's `GradientBoostingClassifier`, `StandardScaler`, and an experimental `RandomForestClassifier` helper. These utilities are separate from the live API prediction path.
- **Arrhythmia demo:** ECG handling uses simplified placeholder logic; it is not a deployed or clinically validated CNN.
- These components are proof-of-concept only. They use synthetic demo data and are not intended for diagnosis, treatment, or clinical decisions.

### Demo, architecture, and presentation

- **Demo MP4:** [CardioTwin-Demo-2026-10-24.mp4](CardioTwin-Demo-2026-10-24.mp4) (Git LFS). The file is hosted in this public repository. An Unlisted YouTube URL is still needed if the submission specifically requires YouTube.
- **Architecture diagram:** [PDF](output/pdf/CardioTwin_Architecture.pdf)
- **Project presentation:** [PowerPoint](output/pptx/CardioTwin_Project_Deck_EndSlideAndBackground_NoTemplateText.pptx)

The repository is public, so the linked repository files can be accessed without additional repository permissions. The demo file uses Git LFS; clone users need Git LFS installed and must pull the LFS objects.

## Open-source license

This project is released under the **MIT License**. See [LICENSE](LICENSE).
