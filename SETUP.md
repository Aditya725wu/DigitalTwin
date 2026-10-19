# DiabetesTwin - Complete Setup Guide

## Project Structure Overview

```
digital-twin/
├── backend/                    # FastAPI REST API + ML Models
│   ├── main.py                # Main application
│   ├── config.py              # Configuration
│   ├── database.py            # SQLAlchemy models
│   ├── utils.py               # Utility functions
│   ├── train_models.py        # ML model training
│   ├── generate_synthetic_data.py
│   └── requirements.txt
├── web-dashboard/             # Next.js Doctor Dashboard
│   ├── src/
│   │   ├── app/              # Pages and layouts
│   │   ├── lib/              # API client
│   │   └── store/            # State management
│   └── package.json
├── mobile-app/               # React Native Patient App
│   ├── src/
│   │   ├── screens/         # App screens
│   │   └── services/        # API integration
│   ├── App.js               # App entry point
│   └── package.json
├── docs/                     # Documentation
│   ├── api-reference.md
│   └── deployment.md
├── demo_alerts.py           # Alert system demo
├── README.md
├── LICENSE
└── docker-compose.yml       # Docker orchestration
```

## Quick Start (5 minutes)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Or (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python generate_synthetic_data.py

# Train ML models
python train_models.py

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

### 2. Web Dashboard Setup

```bash
cd web-dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

Dashboard available at: **http://localhost:3000**

### 3. Mobile App Setup

```bash
cd mobile-app

# Install dependencies
npm install

# Start Expo
npx expo start

# Scan QR code with Expo Go app (iOS/Android)
# Or press 'i' for iOS simulator / 'a' for Android emulator
```

## Running the Demo

### Demo Alert System

```bash
python demo_alerts.py
```

This generates sample alerts and saves them to `demo_alerts.json`

### Generate Synthetic Data

```bash
cd backend
python generate_synthetic_data.py
```

Creates realistic patient data in `data/` directory

### Train Models

```bash
cd backend
python train_models.py
```

Trains ML models and saves to `models/` directory

## Environment Configuration

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/digitaltwin

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# API
API_TITLE=DiabetesTwin API
API_VERSION=1.0.0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Mobile (.env)

```env
EXPO_PUBLIC_API_URL=http://your-machine-ip:8000
```

## Docker Deployment

### Run with Docker Compose

```bash
docker-compose up --build
```

This starts:
- PostgreSQL database
- Redis cache
- FastAPI backend (port 8000)
- Next.js frontend (port 3000)

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Register Patient
```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "age": 45,
    "gender": "M",
    "email": "john@example.com",
    "phone": "+1234567890",
    "bmi": 27.5
  }'
```

### List Patients
```bash
curl http://localhost:8000/api/patients
```

### Get Predictions
```bash
curl -X POST http://localhost:8000/api/patients/PAT000001/predict \
  -H "Content-Type: application/json" \
  -d '[{
    "glucose_mg_dl": 145.5,
    "heart_rate_bpm": 72,
    "timestamp": "2026-10-19T12:00:00Z",
    "source": "wearable"
  }]'
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd web-dashboard
npm test
```

### Run All Tests
```bash
python -m pytest backend/tests/
```

## Features Implemented

### Backend (FastAPI)
✅ Patient registration and management
✅ Sensor data ingestion
✅ ML model predictions
✅ Real-time alerts
✅ WebSocket support
✅ REST API with Swagger docs
✅ Synthetic data generation
✅ ML model training

### Web Dashboard (Next.js)
✅ Patient monitoring dashboard
✅ Real-time glucose trends
✅ Risk stratification
✅ Alert management
✅ Multi-patient view
✅ Interactive visualizations
✅ Responsive design

### Mobile App (React Native)
✅ Real-time glucose monitoring
✅ Personal health dashboard
✅ Alert notifications
✅ Medication tracking
✅ Activity integration
✅ Sleep monitoring
✅ User profile management

## Security Features

- JWT authentication
- HTTPS/WSS support
- CORS configuration
- Input validation
- SQL injection prevention
- XSS protection
- Rate limiting ready
- HIPAA-compliant architecture

## Performance Optimization

- WebSocket real-time updates
- Redis caching
- Database indexing
- Lazy loading in frontend
- Code splitting in Next.js
- Optimized ML inference

## Troubleshooting

### Port Already in Use
```bash
# Find process on port 8000
netstat -ano | findstr :8000
# Kill process
taskkill /PID <PID> /F
```

### Database Connection Error
```bash
# Check PostgreSQL is running
# Verify DATABASE_URL
# Check credentials
```

### Models Not Loaded
```bash
# Ensure models/ directory exists
# Run: python train_models.py
# Check model files: models/*.pkl
```

### Mobile App Connection Issues
```bash
# Check EXPO_PUBLIC_API_URL
# Ensure backend is running
# Check firewall settings
# Use machine IP instead of localhost
```

## Next Steps

1. **Customize Models**: Update ML models in `backend/train_models.py`
2. **Add Database**: Connect to PostgreSQL for production
3. **Deploy**: Use Docker or cloud platforms (AWS, GCP, Azure)
4. **Integrate EHR**: Add hospital EHR system integration
5. **Scale**: Implement load balancing and caching

## Support & Documentation

- API Reference: `docs/api-reference.md`
- Deployment Guide: `docs/deployment.md`
- Main README: `README.md`

## License

MIT License - See LICENSE file

## Team

**DiabetesTwin Team**
- Project for Happiest Health Digital Twin Challenge 2026
- Location: Bengaluru, India
