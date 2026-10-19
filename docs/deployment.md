# Digital Twin Challenge 2026 - Deployment Guide

## Quick Start

### 1. Backend (FastAPI)
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python generate_synthetic_data.py

# Train ML models
python train_models.py

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Web Dashboard (Next.js)
```bash
cd web-dashboard

# Install dependencies
npm install

# Start development server
npm run dev
# Access at http://localhost:3000
```

### 3. Mobile App (React Native/Expo)
```bash
cd mobile-app

# Install dependencies
npm install

# Start Expo
npx expo start

# Run on Android
npx expo run:android

# Run on iOS
npx expo run:ios
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/digitaltwin
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

### Web Dashboard (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Mobile App (.env)
```
EXPO_PUBLIC_API_URL=http://your-server-ip:8000
```

## Docker Deployment

### Backend
```bash
cd backend
docker build -t diabetestwin-api .
docker run -p 8000:8000 diabetestwin-api
```

### With Docker Compose
```bash
docker-compose up --build
```

## Production Deployment

### Backend
- Use Gunicorn with multiple workers
- Enable HTTPS
- Configure PostgreSQL
- Set up Redis for caching

### Frontend
- Build for production: `npm run build`
- Deploy to Vercel/Netlify
- Configure environment variables

### Mobile App
- Build with EAS Build
- Publish to App Store/Play Store

## API Documentation

Once the backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd web-dashboard
npm test
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port 8000
   netstat -ano | findstr :8000
   # Kill process
   taskkill /PID <PID> /F
   ```

2. **Module not found**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

3. **Database connection issues**
   - Check PostgreSQL is running
   - Verify DATABASE_URL
   - Run migrations

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Metrics
- API endpoint: `/api/statistics`
- WebSocket: `/ws/patient/{patient_id}`