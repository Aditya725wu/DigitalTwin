# Hackathon submission checklist

Use this file as the final handoff checklist before submitting the public repository.

## Required team details

- Team name: **TODO**
- College / incubator: **TODO**
- Team leader: **TODO**
- Team members (1–4): **TODO**
- Contact email and phone: submit only through the official platform, not in source code

## Project

- Title: **CardioTwin — Proactive Cardiovascular Digital Twin**
- Use case: early cardiac-risk and hypertension/arrhythmia monitoring using synthetic EHR + wearable telemetry
- License: MIT (`LICENSE`)

## Technical evidence

- Backend: FastAPI, Pydantic, NumPy, synthetic cardiac heuristics
- Dashboard: Next.js 14, TypeScript, Tailwind CSS, Recharts, Zustand
- Mobile: React Native / Expo
- Data: synthetic seeded EHR and wearable readings; no real patient data
- API contract: [`docs/api-reference.md`](api-reference.md)
- Setup: [`SETUP.md`](../SETUP.md)

## Required external deliverables

- 20+ minute demo video: **TODO — add unlisted YouTube / Drive link**
- Architecture diagram PDF/PPT: **TODO — add public link or place final file in `docs/`**
- Presentation PDF/PPT: **TODO — add public link or place final file in `docs/`**
- Public GitHub repository: `https://github.com/Aditya725wu/DigitalTwin`

## Suggested demo sequence

1. Start the API and dashboard.
2. Show static EHR factors for four synthetic patients.
3. Show wearable heart rate, BP, SpO₂, and ECG status.
4. Compare model outputs across risk levels.
5. Trigger a high BP / tachycardia reading in Swagger.
6. Show the new alert and acknowledge it from the dashboard.
7. Explain privacy, limitations, and the path to real validation.

## Final pre-submission checks

```bash
python -m py_compile backend/main.py backend/heart_disease_models.py backend/generate_cardiac_data.py
cd web-dashboard && npm run build
```

Confirm that no `.env`, credential, local virtual environment, `node_modules`, `.next`, `.expo`, generated dataset, or model artifact is committed.
