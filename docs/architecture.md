# CardioTwin architecture

```mermaid
flowchart LR
    EHR[Static synthetic EHR
    demographics, history, labs] --> API[FastAPI cardiac API]
    Wearable[Simulated wearable stream
    HR, BP, SpO2, ECG rhythm] --> API
    API --> Twin[Cardiac digital-twin engine
    risk + rhythm + BP trend]
    Twin --> Alerts[Alert and recommendation service]
    Twin --> Dashboard[Next.js clinician dashboard]
    Alerts --> Dashboard
    API --> Mobile[Expo patient app]
    Mobile -->|vitals submission| API
```

## Runtime flow

1. The API seeds synthetic EHR profiles and baseline wearable readings.
2. The dashboard and mobile app request the patient profile and recent telemetry.
3. The prediction endpoint combines static EHR factors with recent vital signs.
4. Threshold checks generate cardiac, arrhythmia, and hypertension alerts.
5. Clinicians acknowledge alerts from the dashboard; the mobile app displays the patient-facing status.

## Data boundary

This proof-of-concept uses synthetic data only. No real patient records, credentials, or production database are included in the repository.
