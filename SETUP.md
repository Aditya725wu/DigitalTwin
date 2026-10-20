# CardioTwin setup guide

This guide is the reproducible local setup for the hackathon prototype. The application has three optional parts: a FastAPI backend, a Next.js doctor dashboard, and a React Native / Expo patient app.

## 1. Install prerequisites

- Python 3.10+
- Node.js 18+ with npm
- Expo Go (optional, for phone testing)

No database, Redis instance, or API key is required for the demo. The current backend uses seeded in-memory synthetic data.

## 2. Backend

Windows:

```bat
cd /d "D:\Digital Twin\backend"
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

macOS / Linux:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Confirm it is running at http://localhost:8000/health. Swagger UI is at http://localhost:8000/docs.

## 3. Web dashboard

In a second terminal:

```bash
cd web-dashboard
npm install
npm run dev
```

Open http://localhost:3000/dashboard. The default API URL is `http://localhost:8000`. To override it, create `web-dashboard/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

For a production build:

```bash
npm run build
npm run start
```

## 4. Mobile app

```bash
cd mobile-app
npm install
npx expo start
```

For a physical device, create `mobile-app/.env` with the LAN address of the backend host:

```env
EXPO_PUBLIC_API_URL=http://YOUR_COMPUTER_LAN_IP:8000
```

Do not use `localhost` from a physical phone; it points to the phone itself.

## 5. Synthetic data and model utilities

The API seeds four safe demo patients automatically. For a separate synthetic dataset or optional model-training experiment:

```bash
python backend/generate_cardiac_data.py
python backend/heart_disease_models.py
```

Generated data and model artifacts are intentionally ignored by Git. They are not required to run the dashboard.

## 6. Troubleshooting

### Dashboard says the API is unavailable

1. Confirm the backend terminal is still running.
2. Open http://localhost:8000/health.
3. Confirm `NEXT_PUBLIC_API_URL` matches the backend address.
4. Restart `npm run dev` after changing `.env.local`.

### Port already in use

Windows:

```bat
netstat -ano | findstr :8000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

macOS / Linux:

```bash
lsof -i :8000
lsof -i :3000
```

### Mobile app cannot reach the backend

Use the computer's LAN IP in `EXPO_PUBLIC_API_URL`, keep both devices on the same Wi-Fi, and allow port 8000 through the local firewall.
