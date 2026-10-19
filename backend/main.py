"""
FastAPI Backend - DiabetesTwin
Main application and API endpoints
"""

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Optional, List
import logging
from datetime import datetime
import json
import joblib
from pathlib import Path

from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Pydantic Models ====================

class PatientCreate(BaseModel):
    """Patient registration model"""
    name: str
    age: int
    gender: str
    email: str
    phone: str
    bmi: float
    medical_history: List[str] = []


class PatientResponse(BaseModel):
    """Patient response model"""
    patient_id: str
    name: str
    age: int
    gender: str
    email: str
    created_at: str


class SensorReading(BaseModel):
    """Sensor reading model"""
    glucose_mg_dl: Optional[float] = None
    heart_rate_bpm: Optional[int] = None
    steps: Optional[int] = None
    timestamp: str
    source: str


class PredictionResponse(BaseModel):
    """Prediction response model"""
    patient_id: str
    spike_probability: float
    risk_level: str
    recommended_actions: List[str]
    timestamp: str


class AlertModel(BaseModel):
    """Alert model"""
    alert_id: str
    patient_id: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    timestamp: str
    acknowledged: bool


# ==================== Global State ====================

# Load ML models
MODELS_DIR = Path("models")

try:
    glucose_model = joblib.load(MODELS_DIR / "glucose_spike_model.pkl")
    glucose_scaler = joblib.load(MODELS_DIR / "glucose_spike_scaler.pkl")
    logger.info("✓ Loaded glucose spike model")
except FileNotFoundError:
    logger.warning("⚠️ Glucose spike model not found. Run train_models.py first")
    glucose_model = None
    glucose_scaler = None

try:
    cv_risk_model = joblib.load(MODELS_DIR / "cv_risk_model.pkl")
    cv_risk_scaler = joblib.load(MODELS_DIR / "cv_risk_scaler.pkl")
    logger.info("✓ Loaded cardiovascular risk model")
except FileNotFoundError:
    logger.warning("⚠️ CV risk model not found. Run train_models.py first")
    cv_risk_model = None
    cv_risk_scaler = None

# In-memory storage (replace with database in production)
patients_db = {}
alerts_db = {}
patient_counter = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info("🚀 DiabetesTwin API Starting...")
    yield
    logger.info("🛑 DiabetesTwin API Shutting Down...")


# ==================== FastAPI App ====================

app = FastAPI(
    title="DiabetesTwin API",
    description="Real-time diabetes monitoring and prediction",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health Check ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "glucose_spike": glucose_model is not None,
            "cv_risk": cv_risk_model is not None,
        }
    }


# ==================== Patient Management ====================

@app.post("/api/patients", response_model=PatientResponse, tags=["Patients"])
async def register_patient(patient: PatientCreate):
    """Register a new patient"""
    global patient_counter
    patient_counter += 1

    patient_id = f"PAT{patient_counter:06d}"

    patient_data = {
        "patient_id": patient_id,
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "email": patient.email,
        "phone": patient.phone,
        "bmi": patient.bmi,
        "medical_history": patient.medical_history,
        "created_at": datetime.now().isoformat(),
    }

    patients_db[patient_id] = patient_data

    logger.info(f"✓ Registered patient: {patient_id}")

    return patient_data


@app.get("/api/patients/{patient_id}", response_model=PatientResponse, tags=["Patients"])
async def get_patient(patient_id: str):
    """Get patient details"""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patients_db[patient_id]


@app.get("/api/patients", tags=["Patients"])
async def list_patients():
    """List all patients"""
    return list(patients_db.values())


# ==================== Sensor Data ====================

@app.post("/api/patients/{patient_id}/readings", tags=["Sensor Data"])
async def submit_sensor_reading(patient_id: str, reading: SensorReading):
    """Submit sensor readings from wearable devices"""

    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    # In production, store in time-series database
    logger.info(f"📊 Received reading from {patient_id}: {reading}")

    return {
        "status": "received",
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
    }


# ==================== Predictions ====================

@app.post("/api/patients/{patient_id}/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_health_event(patient_id: str, readings: List[SensorReading]):
    """Predict health events for a patient"""

    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    if glucose_model is None:
        raise HTTPException(status_code=503, detail="Model not available")

    # Extract features from latest readings
    if not readings:
        raise HTTPException(status_code=400, detail="No readings provided")

    # Simulated prediction
    import random
    import numpy as np

    spike_prob = random.uniform(0.3, 0.9)
    risk_level = "HIGH" if spike_prob > 0.7 else "MEDIUM" if spike_prob > 0.4 else "LOW"

    recommended_actions = []
    if spike_prob > 0.7:
        recommended_actions = [
            "Take prescribed medication",
            "Increase water intake",
            "Moderate physical activity",
            "Contact healthcare provider"
        ]
    elif spike_prob > 0.4:
        recommended_actions = [
            "Monitor glucose closely",
            "Light exercise recommended",
            "Check medication timing"
        ]

    # Create alert if high risk
    if spike_prob > 0.7:
        alert = {
            "alert_id": f"ALR{len(alerts_db)+1:06d}",
            "patient_id": patient_id,
            "severity": "HIGH",
            "message": f"Predicted glucose spike with {spike_prob*100:.1f}% probability",
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False,
        }
        alerts_db[alert["alert_id"]] = alert
        logger.warning(f"🚨 Alert created: {alert['alert_id']}")

    return PredictionResponse(
        patient_id=patient_id,
        spike_probability=round(spike_prob, 3),
        risk_level=risk_level,
        recommended_actions=recommended_actions,
        timestamp=datetime.now().isoformat(),
    )


# ==================== Alerts ====================

@app.get("/api/patients/{patient_id}/alerts", tags=["Alerts"])
async def get_patient_alerts(patient_id: str, limit: int = 10):
    """Get recent alerts for a patient"""

    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_alerts = [
        alert for alert in alerts_db.values()
        if alert["patient_id"] == patient_id
    ]

    return sorted(patient_alerts, key=lambda x: x["timestamp"], reverse=True)[:limit]


@app.post("/api/alerts/{alert_id}/acknowledge", tags=["Alerts"])
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""

    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")

    alerts_db[alert_id]["acknowledged"] = True

    return alerts_db[alert_id]


# ==================== WebSocket (Real-time Updates) ====================

@app.websocket("/ws/patient/{patient_id}")
async def websocket_endpoint(websocket: WebSocket, patient_id: str):
    """WebSocket endpoint for real-time patient data streaming"""

    if patient_id not in patients_db:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    logger.info(f"✅ WebSocket connected: {patient_id}")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process incoming message
            if message.get("type") == "subscribe":
                await websocket.send_json({
                    "type": "subscribed",
                    "patient_id": patient_id,
                    "timestamp": datetime.now().isoformat(),
                })

            elif message.get("type") == "reading":
                # Simulate prediction
                import random
                prediction = {
                    "type": "prediction",
                    "spike_probability": round(random.uniform(0.3, 0.8), 3),
                    "timestamp": datetime.now().isoformat(),
                }
                await websocket.send_json(prediction)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info(f"❌ WebSocket disconnected: {patient_id}")


# ==================== Statistics ====================

@app.get("/api/statistics", tags=["Analytics"])
async def get_statistics():
    """Get system statistics"""

    return {
        "total_patients": len(patients_db),
        "total_alerts": len(alerts_db),
        "high_risk_alerts": sum(1 for a in alerts_db.values() if a["severity"] == "HIGH"),
        "timestamp": datetime.now().isoformat(),
    }


# ==================== Root ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DiabetesTwin API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
