<<<<<<< HEAD
# Cardiovascular Digital Twin POC

An educational, simulated monitoring workflow. This prototype flags persistent changes from an individual's own baseline for further attention; it does not diagnose, estimate medical-event risk, or replace clinical care.

## Run the API

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs are at `http://127.0.0.1:8000/docs`. On startup the API creates its SQLite database, generates reproducible synthetic patient-separated training/evaluation data, trains a demo classifier, and prints class-level evaluation metrics. The model is only trained on synthetic labels.

Useful endpoints: `GET /api/patients/demo/dashboard`, `GET /api/patients/demo/baseline`, `POST /api/patients/demo/simulate`, `GET /api/patients/demo/assessment`, `POST /api/patients/demo/what-if`, `PUT /api/patients/demo/family-contact`, `GET /api/patients/demo/alerts`.

## Run the Flutter app

Install Flutter, then run from `mobile/`:

```powershell
flutter create .
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Use `http://127.0.0.1:8000` for a desktop/browser client or your computer's LAN address for a physical device. The initial screen targets the `demo` patient.

## Demo flow

1. Open the dashboard and inspect the simulated measurements and baseline.
2. Generate normal, sustained-deviation, recovery, or incomplete readings from the API docs.
3. Refresh the dashboard to see status, reasons, missing signals, and alert history.
4. Authorize a demo family contact using `PUT /api/patients/demo/family-contact`, then simulate a sustained deviation. Alerts are recorded locally; FCM can be enabled using environment variables documented in `backend/.env.example`.
5. Use the what-if endpoint to assess hypothetical changes without writing them to patient history.

## Safety and data

All readings are simulated. Three consecutive hourly flagged summaries are required for an alert, independently of the classifier score threshold. No real wearable, hospital, or emergency-service integration is included. Do not use this POC for care decisions.
=======
# DigitalTwinChallenge 2,3
>>>>>>> origin/main
