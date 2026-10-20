# CardioTwin deployment notes

## Local demo

Use the commands in [SETUP.md](../SETUP.md). The recommended demo deployment is two processes:

- FastAPI on port 8000
- Next.js on port 3000

## Frontend hosting

Build the dashboard with:

```bash
cd web-dashboard
npm run build
npm run start
```

Set `NEXT_PUBLIC_API_URL` to a reachable HTTPS backend URL.

## Backend hosting

Run the API behind a production process manager / reverse proxy:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Set `ALLOWED_ORIGINS` to the exact dashboard and mobile origins. Use HTTPS in any non-local environment.

## Important prototype limitations

- Storage is in memory; restart resets the demo state.
- Patient data is synthetic and seeded in `backend/main.py`.
- Risk scoring is a simplified heuristic for demonstration, not a validated clinical model.
- Authentication, authorization, audit logging, and production database persistence are not implemented in this PoC.
