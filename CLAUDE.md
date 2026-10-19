# DiabetesTwin - Digital Twin for Type 2 Diabetes Management

## Project Overview

A comprehensive Digital Twin healthcare application for the Happiest Health Digital Twin Challenge 2026. This project creates a dynamic, virtual replica of a diabetic patient that continuously monitors health status and predicts adverse events 2-4 hours in advance.

## Tech Stack

### Backend (Python)
- FastAPI for REST API
- SQLite/PostgreSQL for data storage
- Scikit-learn/XGBoost for ML models
- WebSockets for real-time updates

### Frontend (Next.js)
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- Recharts for visualizations
- Zustand for state management

### Mobile App (React Native/Expo)
- React Native with Expo
- React Navigation
- Victory Native for charts
- Socket.io for real-time updates

## Project Structure

```
digital-twin/
├── backend/               # FastAPI backend
│   ├── main.py           # API endpoints
│   ├── train_models.py   # ML model training
│   ├── generate_synthetic_data.py
│   ├── config.py         # Configuration
│   └── requirements.txt
├── web-dashboard/        # Next.js doctor dashboard
│   ├── src/
│   │   ├── app/         # Pages
│   │   ├── lib/         # Utilities
│   │   └── store/       # State management
│   └── package.json
├── mobile-app/          # React Native patient app
│   ├── src/
│   │   ├── screens/    # App screens
│   │   └── services/   # API services
│   └── App.js
├── docs/               # Documentation
├── data/               # Synthetic datasets
├── models/             # Trained ML models
├── README.md
└── LICENSE
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
# or: source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python generate_synthetic_data.py
python train_models.py
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd web-dashboard
npm install
npm run dev
```

### Mobile App Setup
```bash
cd mobile-app
npm install
npx expo start
```

## Features

### Patient Mobile App
- Real-time glucose monitoring
- Predictive alerts (2 hours advance warning)
- Medication reminders
- Activity tracking
- Personal health trends

### Doctor Dashboard
- Multi-patient monitoring
- Risk stratification
- Interactive visualizations
- Real-time alert feed
- Historical analysis

## API Endpoints

- `GET /health` - Health check
- `POST /api/patients` - Register patient
- `GET /api/patients` - List patients
- `GET /api/patients/{id}` - Get patient
- `POST /api/patients/{id}/predict` - Get prediction
- `GET /api/patients/{id}/alerts` - Get alerts
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert

## ML Models

### Glucose Spike Predictor
- Type: Gradient Boosting (XGBoost) + LSTM
- Input: CGM data, heart rate, activity
- Output: Probability of spike in 2 hours

### Cardiovascular Risk Model
- Type: Random Forest
- Input: Patient demographics, lab results, sensor data
- Output: Risk score (0-100)

## Security

- JWT authentication
- Role-based access control
- Data encryption
- HIPAA-compliant architecture

## License

MIT License - See LICENSE file