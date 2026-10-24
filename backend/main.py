"""
FastAPI Backend - CardioTwin
Main application and API endpoints for cardiac digital twin
"""

from fastapi import FastAPI, HTTPException, Query, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Set
import logging
from datetime import datetime, timedelta, timezone
import json
import numpy as np
import uuid
import asyncio
import random
import re

from pydantic import BaseModel, Field, field_validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Pydantic Models ====================

class PatientCreate(BaseModel):
    """Patient registration model for cardiac monitoring"""
    name: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=18, le=120)
    gender: str = Field(min_length=1, max_length=40)
    email: str = Field(min_length=5, max_length=254)
    phone: str = Field(min_length=5, max_length=40)
    bmi: float = Field(gt=0, le=100)
    height_cm: Optional[float] = Field(default=None, ge=30, le=250)
    weight_kg: Optional[float] = Field(default=None, gt=1, le=500)
    # Cardiac risk factors
    smoker: bool = False
    diabetes: bool = False
    hypertension: bool = False
    family_history_cvd: bool = False
    family_history_hypertension: bool = False
    total_cholesterol: float = Field(default=200, ge=50, le=600)
    hdl_cholesterol: float = Field(default=50, ge=10, le=150)
    ldl_cholesterol: float = Field(default=120, ge=10, le=500)
    medications: List[str] = Field(default_factory=list)
    medical_history: List[str] = Field(default_factory=list)

    @field_validator("name", "gender", "email", "phone")
    @classmethod
    def strip_text_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field cannot be empty")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not re.fullmatch(r"[+0-9() .-]{5,40}", value) or sum(character.isdigit() for character in value) < 5:
            raise ValueError("Enter a valid phone number")
        return value


class PatientResponse(BaseModel):
    """Patient response model"""
    patient_id: str
    name: str
    age: int
    gender: str
    email: str
    risk_level: Optional[str] = "LOW"
    flag_streak: int = 0
    created_at: str


class VitalSigns(BaseModel):
    """Vital signs model for cardiac monitoring"""
    heart_rate_bpm: Optional[int] = Field(default=None, ge=20, le=250)
    blood_pressure_systolic: Optional[int] = Field(default=None, ge=50, le=300)
    blood_pressure_diastolic: Optional[int] = Field(default=None, ge=30, le=200)
    oxygen_saturation: Optional[float] = Field(default=None, ge=50, le=100)
    ecg_rhythm: Optional[str] = None
    ecg_quality: Optional[str] = None
    timestamp: Optional[str] = None
    source: str = "wearable"


class WhatIfRequest(BaseModel):
    heart_rate_bpm: Optional[int] = Field(default=None, ge=20, le=250)
    blood_pressure_systolic: Optional[int] = Field(default=None, ge=50, le=300)
    blood_pressure_diastolic: Optional[int] = Field(default=None, ge=30, le=200)
    oxygen_saturation: Optional[float] = Field(default=None, ge=50, le=100)
    smoker: Optional[bool] = None
    diabetes: Optional[bool] = None
    hypertension: Optional[bool] = None
    family_history_cvd: Optional[bool] = None
    age: Optional[int] = Field(default=None, ge=18, le=120)
    gender: Optional[str] = None
    total_cholesterol: Optional[float] = Field(default=None, ge=50, le=600)
    hdl_cholesterol: Optional[float] = Field(default=None, ge=10, le=150)
    ldl_cholesterol: Optional[float] = Field(default=None, ge=10, le=500)


class FamilyContact(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=5, max_length=40)


class CardiacPredictionResponse(BaseModel):
    """Cardiac prediction response model"""
    patient_id: str
    cardiac_event_probability: float
    arrhythmia_risk: str
    blood_pressure_trend: str
    bp_risk_level: str
    risk_classification: str
    framingham_score: float
    recommended_actions: List[str]
    timestamp: str


class AlertModel(BaseModel):
    """Alert model"""
    alert_id: str
    patient_id: str
    severity: str
    alert_type: str
    message: str
    timestamp: str
    acknowledged: bool
    vital_signs: Optional[dict] = None


# ==================== Cardiac ML Helper Functions ====================

def calculate_framingham_risk(features: dict) -> float:
    """Calculate simplified Framingham Risk Score"""
    score = 0

    # Age scoring
    age = features.get('age') or 50
    if age >= 55:
        score += 8
    elif age >= 45:
        score += 6
    elif age >= 35:
        score += 4

    # Gender
    if features.get('gender_male', 0) == 1:
        score += 3

    # Blood pressure
    systolic = features.get('systolic_bp') or 120
    if systolic >= 140:
        score += 7
    elif systolic >= 130:
        score += 5
    elif systolic >= 120:
        score += 3

    # Cholesterol
    total_chol = features.get('cholesterol_total') or 200
    if total_chol >= 240:
        score += 5
    elif total_chol >= 200:
        score += 3

    # HDL cholesterol (inverse)
    hdl = features.get('cholesterol_hdl') or 50
    if hdl < 40:
        score += 4
    elif hdl < 50:
        score += 2

    # Smoking
    if features.get('smoker', 0) == 1:
        score += 4

    # Diabetes
    if features.get('diabetes', 0) == 1:
        score += 3

    # Convert to probability
    probability = min(score / 45, 0.99)
    return probability


def framingham_factors(features: dict) -> List[dict]:
    """Return the point contributions used by calculate_framingham_risk."""
    factors = []
    age = features.get('age') or 50
    age_points = 8 if age >= 55 else 6 if age >= 45 else 4 if age >= 35 else 0
    factors.append({"factor": "Age", "points": age_points})
    gender_points = 3 if features.get('gender_male', 0) == 1 else 0
    factors.append({"factor": "Gender", "points": gender_points})
    systolic = features.get('systolic_bp') or 120
    bp_points = 7 if systolic >= 140 else 5 if systolic >= 130 else 3 if systolic >= 120 else 0
    factors.append({"factor": "Systolic BP", "points": bp_points})
    total_chol = features.get('cholesterol_total') or 200
    cholesterol_points = 5 if total_chol >= 240 else 3 if total_chol >= 200 else 0
    factors.append({"factor": "Total cholesterol", "points": cholesterol_points})
    hdl = features.get('cholesterol_hdl') or 50
    hdl_points = 4 if hdl < 40 else 2 if hdl < 50 else 0
    factors.append({"factor": "HDL cholesterol", "points": hdl_points})
    factors.append({"factor": "Smoking", "points": 4 if features.get('smoker', 0) == 1 else 0})
    factors.append({"factor": "Diabetes", "points": 3 if features.get('diabetes', 0) == 1 else 0})
    return factors


def prediction_snapshot(patient: dict, history: List[dict]) -> dict:
    """Compute a prediction without changing state or creating an alert."""
    features = prepare_cardiac_features(patient, history)
    probability = calculate_framingham_risk(features)
    arrhythmia_risk = "Normal sinus rhythm"
    arrhythmia_severity = "NORMAL"
    if history:
        result = detect_arrhythmia(history[-1].get('heart_rate_bpm') or 72, history[-1].get('ecg_rhythm'))
        arrhythmia_risk = result['rhythm_status']
        arrhythmia_severity = result['severity']
    bp_data = [
        {'systolic': v.get('blood_pressure_systolic', 120), 'diastolic': v.get('blood_pressure_diastolic', 80)}
        for v in history if v.get('blood_pressure_systolic') is not None
    ]
    bp = predict_bp_trend(bp_data) if bp_data else {'trend': 'STABLE', 'risk_level': 'NORMAL'}
    risk = "CRITICAL" if probability > 0.85 or bp['risk_level'] == "CRITICAL" else (
        "HIGH" if probability > 0.7 or arrhythmia_severity == "HIGH" or bp['risk_level'] == "HIGH" else (
            "MODERATE" if probability > 0.4 or arrhythmia_severity != "NORMAL" or bp['risk_level'] == "ELEVATED" else "LOW"
        )
    )
    return {
        "cardiac_event_probability": round(probability, 3),
        "arrhythmia_risk": arrhythmia_risk,
        "blood_pressure_trend": bp['trend'],
        "bp_risk_level": bp['risk_level'],
        "risk_classification": risk,
        "framingham_score": round(probability, 3),
        "recommended_actions": get_cardiac_recommendations(risk, arrhythmia_risk, bp['risk_level']),
        "timestamp": datetime.now().isoformat(),
    }


def _is_flagged(vitals: dict) -> bool:
    return bool(
        (vitals.get('heart_rate_bpm') is not None and (vitals['heart_rate_bpm'] > 120 or vitals['heart_rate_bpm'] < 50))
        or (vitals.get('blood_pressure_systolic') is not None and vitals['blood_pressure_systolic'] >= 160)
        or (vitals.get('blood_pressure_diastolic') is not None and vitals['blood_pressure_diastolic'] >= 100)
        or (vitals.get('oxygen_saturation') is not None and vitals['oxygen_saturation'] < 90)
        or vitals.get('ecg_rhythm') in ['AFib', 'PVC', 'ST Elevation', 'T Wave Inversion']
    )


def _update_flag_streak(patient_id: str, vitals: dict) -> int:
    flagged = _is_flagged(vitals)
    summary_timestamp = vitals.get("summary_timestamp") or vitals.get("timestamp") or datetime.now().isoformat()
    try:
        parsed_time = datetime.fromisoformat(str(summary_timestamp).replace("Z", "+00:00"))
        if parsed_time.utcoffset() is not None:
            parsed_time = parsed_time.astimezone(timezone.utc).replace(tzinfo=None)
        bucket = parsed_time.replace(minute=0, second=0, microsecond=0)
    except ValueError:
        bucket = datetime.now().replace(minute=0, second=0, microsecond=0)
    bucket_key = bucket.isoformat()
    previous_key = patient_flag_hour_keys.get(patient_id)
    previous_flagged = patient_flag_hour_status.get(patient_id, False)
    current_streak = patient_flag_streaks.get(patient_id, 0)
    if previous_key == bucket_key:
        streak = current_streak if flagged == previous_flagged else 1 if flagged else 0
    elif previous_key:
        previous_bucket = datetime.fromisoformat(previous_key)
        consecutive_hour = (bucket - previous_bucket) == timedelta(hours=1)
        streak = min(3, current_streak + 1) if flagged and previous_flagged and consecutive_hour else 1 if flagged else 0
    else:
        streak = 1 if flagged else 0
    patient_flag_hour_keys[patient_id] = bucket_key
    patient_flag_hour_status[patient_id] = flagged
    patient_flag_streaks[patient_id] = streak
    if patient_id in patients_db:
        patients_db[patient_id]["flag_streak"] = streak
    return streak


def _record_critical_family_event(patient_id: str, alert: dict, streak: int) -> None:
    """Log a simulated notice; it is only marked sent after the three-strike gate."""
    if alert.get('severity') != 'CRITICAL':
        return
    contact = family_contacts.get(patient_id)
    if not contact:
        return
    log = family_notifications.setdefault(patient_id, [])
    if any(item.get('alert_id') == alert['alert_id'] for item in log):
        return
    log.append({
        "notification_id": f"SIM{uuid.uuid4().hex[:10].upper()}",
        "patient_id": patient_id,
        "alert_id": alert['alert_id'],
        "recipient_name": contact['name'],
        "recipient_phone": contact['phone'],
        "message": f"Simulated critical alert for {patients_db[patient_id]['name']}: {alert['message']}",
        "status": "simulated_sent" if streak >= 3 else "simulated_queued",
        "simulated": True,
        "timestamp": datetime.now().isoformat(),
    })


def _advance_queued_family_events(patient_id: str, streak: int) -> None:
    if streak < 3:
        return
    for notification in family_notifications.get(patient_id, []):
        if notification['status'] == 'simulated_queued':
            notification['status'] = 'simulated_sent'
            notification['timestamp'] = datetime.now().isoformat()


def _store_vital(patient_id: str, vitals: VitalSigns, summary_timestamp: Optional[str] = None) -> tuple:
    reading = vitals.model_dump()
    reading['timestamp'] = reading.get('timestamp') or datetime.now().isoformat()
    reading['received_at'] = datetime.now().isoformat()
    if summary_timestamp:
        reading['summary_timestamp'] = summary_timestamp
    readings = patient_vitals.setdefault(patient_id, [])
    readings.append(reading)
    if len(readings) > 1000:
        del readings[:-1000]
    streak = _update_flag_streak(patient_id, reading)
    alert_vitals = vitals.model_copy(update={"timestamp": reading["timestamp"]})
    alerts = check_cardiac_alerts(patient_id, alert_vitals)
    for alert in alerts:
        alerts_db[alert['alert_id']] = alert
        _record_critical_family_event(patient_id, alert, streak)
    _advance_queued_family_events(patient_id, streak)
    return reading, alerts, streak


async def _broadcast(patient_id: str, message: dict) -> None:
    clients = list(websocket_clients.get(patient_id, set()))
    for client in clients:
        try:
            await client.send_json(message)
        except Exception:
            websocket_clients.get(patient_id, set()).discard(client)


async def _ingest_and_broadcast(patient_id: str, vitals: VitalSigns, summary_timestamp: Optional[str] = None) -> dict:
    reading, alerts, streak = _store_vital(patient_id, vitals, summary_timestamp)
    snapshot = prediction_snapshot(patients_db[patient_id], patient_vitals[patient_id])
    await _broadcast(patient_id, {"type": "vitals", "data": reading, "flag_streak": streak})
    for alert in alerts:
        await _broadcast(patient_id, {"type": "alert", "data": alert})
    await _broadcast(patient_id, {"type": "prediction_update", **snapshot, "flag_streak": streak})
    return {"status": "received", "patient_id": patient_id, "alerts_generated": len(alerts), "flag_streak": streak, "timestamp": datetime.now().isoformat()}


def detect_arrhythmia(heart_rate: Optional[int], ecg_rhythm: Optional[str] = None) -> dict:
    """Detect arrhythmias from heart rate and ECG"""
    heart_rate = heart_rate or 72
    if heart_rate > 100:
        rhythm_status = "Tachycardia"
        severity = "HIGH" if heart_rate > 120 else "MODERATE"
    elif heart_rate < 60:
        rhythm_status = "Bradycardia"
        severity = "HIGH" if heart_rate < 50 else "MODERATE"
    else:
        rhythm_status = "Normal sinus rhythm"
        severity = "NORMAL"

    if ecg_rhythm and ecg_rhythm in ['AFib', 'PVC', 'ST Elevation', 'T Wave Inversion']:
        rhythm_status = ecg_rhythm
        severity = "HIGH"

    return {'rhythm_status': rhythm_status, 'severity': severity}


def predict_bp_trend(bp_history: List[dict]) -> dict:
    """Predict blood pressure trend"""
    if not bp_history:
        return {'trend': 'STABLE', 'risk_level': 'NORMAL'}

    systolics = [bp.get('systolic') or 120 for bp in bp_history[-10:]]
    diastolics = [bp.get('diastolic') or 80 for bp in bp_history[-10:]]
    mean_systolic = np.mean(systolics)
    mean_diastolic = np.mean(diastolics)

    if len(systolics) < 2:
        trend = "STABLE"
    else:
        recent_avg = np.mean(systolics[-3:])
        older_avg = np.mean(systolics[:3])

        if recent_avg > older_avg + 10:
            trend = "RISING"
        elif recent_avg < older_avg - 10:
            trend = "FALLING"
        else:
            trend = "STABLE"

    if mean_systolic >= 180 or mean_diastolic >= 120:
        risk_level = "CRITICAL"
    elif mean_systolic >= 140 or mean_diastolic >= 90:
        risk_level = "HIGH"
    elif mean_systolic >= 130 or mean_diastolic >= 80:
        risk_level = "ELEVATED"
    else:
        risk_level = "NORMAL"

    return {'trend': trend, 'risk_level': risk_level}


def get_cardiac_recommendations(risk_classification: str, arrhythmia_risk: str, bp_risk: str) -> List[str]:
    """Get cardiac-specific recommendations"""
    actions = []

    if risk_classification == "CRITICAL":
        actions.extend([
            "CALL EMERGENCY SERVICES IMMEDIATELY",
            "Take aspirin 325mg if not allergic",
            "Stay calm and rest",
            "Have someone stay with you",
        ])
    elif risk_classification == "HIGH":
        actions.extend([
            "Contact cardiologist immediately",
            "Take prescribed cardiac medications",
            "Monitor blood pressure every 30 minutes",
            "Avoid physical exertion",
            "Reduce sodium intake",
        ])
    elif risk_classification == "MODERATE":
        actions.extend([
            "Schedule cardiology consultation within 48 hours",
            "Take medications as prescribed",
            "Monitor vital signs closely",
            "Follow low-sodium diet",
        ])
    else:
        actions.extend([
            "Continue regular cardiac monitoring",
            "Maintain prescribed medication schedule",
            "Follow heart-healthy diet",
            "Regular moderate exercise as approved",
        ])

    if arrhythmia_risk in ["AFib", "Tachycardia"]:
        actions.append("Avoid caffeine and alcohol")
    elif arrhythmia_risk == "Bradycardia":
        actions.append("Review beta-blocker dosage with doctor")

    return actions[:6]


def new_alert_id() -> str:
    """Generate an alert ID that cannot collide within one request."""
    return f"ALR{uuid.uuid4().hex[:10].upper()}"


# ==================== Global State ====================

patients_db = {}
alerts_db = {}
patient_vitals = {}
patient_counter = 0
family_contacts: Dict[str, dict] = {}
family_notifications: Dict[str, List[dict]] = {}
patient_flag_streaks: Dict[str, int] = {}
patient_flag_hour_keys: Dict[str, str] = {}
patient_flag_hour_status: Dict[str, bool] = {}
simulator_tasks: Dict[str, asyncio.Task] = {}
websocket_clients: Dict[str, Set[WebSocket]] = {}


def seed_demo_data():
    """Seed initial sample patients and alerts if empty"""
    global patient_counter
    if patients_db:
        return

    demo_patients = [
        {
            "patient_id": "PAT000001",
            "name": "Sarah Connor",
            "age": 48,
            "gender": "F",
            "email": "sarah.connor@example.com",
            "phone": "+1-555-0101",
            "bmi": 24.2,
            "smoker": False,
            "diabetes": False,
            "hypertension": False,
            "family_history_cvd": False,
            "family_history_hypertension": False,
            "total_cholesterol": 185,
            "hdl_cholesterol": 58,
            "ldl_cholesterol": 110,
            "risk_level": "LOW",
            "created_at": datetime.now().isoformat(),
        },
        {
            "patient_id": "PAT000002",
            "name": "John Davis",
            "age": 62,
            "gender": "M",
            "email": "john.davis@example.com",
            "phone": "+1-555-0102",
            "bmi": 29.8,
            "smoker": True,
            "diabetes": True,
            "hypertension": True,
            "family_history_cvd": True,
            "family_history_hypertension": True,
            "total_cholesterol": 245,
            "hdl_cholesterol": 38,
            "ldl_cholesterol": 160,
            "risk_level": "HIGH",
            "created_at": datetime.now().isoformat(),
        },
        {
            "patient_id": "PAT000003",
            "name": "Maria Rodriguez",
            "age": 55,
            "gender": "F",
            "email": "maria.r@example.com",
            "phone": "+1-555-0103",
            "bmi": 26.5,
            "smoker": False,
            "diabetes": False,
            "hypertension": True,
            "family_history_cvd": False,
            "family_history_hypertension": True,
            "total_cholesterol": 215,
            "hdl_cholesterol": 46,
            "ldl_cholesterol": 135,
            "risk_level": "MEDIUM",
            "created_at": datetime.now().isoformat(),
        },
        {
            "patient_id": "PAT000004",
            "name": "Robert Chen",
            "age": 71,
            "gender": "M",
            "email": "robert.chen@example.com",
            "phone": "+1-555-0104",
            "bmi": 28.1,
            "smoker": False,
            "diabetes": True,
            "hypertension": True,
            "family_history_cvd": True,
            "family_history_hypertension": True,
            "total_cholesterol": 260,
            "hdl_cholesterol": 34,
            "ldl_cholesterol": 178,
            "risk_level": "CRITICAL",
            "created_at": datetime.now().isoformat(),
        },
    ]

    for p in demo_patients:
        p["flag_streak"] = 0
        patients_db[p["patient_id"]] = p
        patient_vitals[p["patient_id"]] = [
            {
                "heart_rate_bpm": (
                    72 if p["risk_level"] == "LOW" else
                    88 if p["risk_level"] == "MEDIUM" else
                    115 if p["risk_level"] == "HIGH" else 125
                ),
                "blood_pressure_systolic": (
                    118 if p["risk_level"] == "LOW" else
                    134 if p["risk_level"] == "MEDIUM" else
                    165 if p["risk_level"] == "HIGH" else 185
                ),
                "blood_pressure_diastolic": (
                    78 if p["risk_level"] == "LOW" else
                    86 if p["risk_level"] == "MEDIUM" else
                    102 if p["risk_level"] == "HIGH" else 122
                ),
                "oxygen_saturation": (
                    98.5 if p["risk_level"] == "LOW" else
                    96.0 if p["risk_level"] == "MEDIUM" else
                    93.0 if p["risk_level"] == "HIGH" else 91.0
                ),
                "ecg_rhythm": "Normal sinus rhythm" if p["risk_level"] in ["LOW", "MEDIUM"] else "Tachycardia",
                "timestamp": datetime.now().isoformat(),
                "source": "wearable",
                "received_at": datetime.now().isoformat(),
            }
        ]
    patient_counter = max(int(pid.removeprefix("PAT")) for pid in patients_db)

    alerts_db["ALT000001"] = {
        "alert_id": "ALT000001",
        "patient_id": "PAT000004",
        "severity": "CRITICAL",
        "alert_type": "hypertension",
        "message": "Hypertensive crisis detected: BP 185/122 mmHg with Tachycardia",
        "timestamp": datetime.now().isoformat(),
        "acknowledged": False,
    }
    alerts_db["ALT000002"] = {
        "alert_id": "ALT000002",
        "patient_id": "PAT000002",
        "severity": "HIGH",
        "alert_type": "cardiac_event",
        "message": "Elevated 24h cardiac risk indicators detected - simplified Framingham estimate 76%",
        "timestamp": datetime.now().isoformat(),
        "acknowledged": False,
    }
    logger.info("Seeded initial demo patients and alerts for CardioTwin.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info("CardioTwin API Starting...")
    seed_demo_data()
    yield
    logger.info("CardioTwin API Shutting Down...")


# ==================== FastAPI App ====================

app = FastAPI(
    title="CardioTwin API",
    description="Real-time cardiovascular monitoring and prediction",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:19006", "http://127.0.0.1:19006"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.[0-9]+\.[0-9]+|10\.[0-9]+\.[0-9]+\.[0-9]+|172\.(1[6-9]|2[0-9]|3[01])\.[0-9]+\.[0-9]+)(:[0-9]+)?",
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
            "framingham_risk": True,
            "arrhythmia_detector": True,
            "bp_predictor": True,
        }
    }


# ==================== Patient Management ====================

@app.post("/api/patients", response_model=PatientResponse, tags=["Patients"])
async def register_patient(patient: PatientCreate):
    """Register a new cardiac patient"""
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
        "height_cm": patient.height_cm,
        "weight_kg": patient.weight_kg,
        "smoker": patient.smoker,
        "diabetes": patient.diabetes,
        "hypertension": patient.hypertension,
        "family_history_cvd": patient.family_history_cvd,
        "family_history_hypertension": patient.family_history_hypertension,
        "total_cholesterol": patient.total_cholesterol,
        "hdl_cholesterol": patient.hdl_cholesterol,
        "ldl_cholesterol": patient.ldl_cholesterol,
        "medications": patient.medications,
        "medical_history": patient.medical_history,
        "risk_level": "LOW",
        "flag_streak": 0,
        "created_at": datetime.now().isoformat(),
    }

    baseline_risk = calculate_framingham_risk(prepare_cardiac_features(patient_data, []))
    if baseline_risk >= 0.7 or patient.hypertension or patient.diabetes:
        patient_data["risk_level"] = "HIGH"
    elif baseline_risk >= 0.4:
        patient_data["risk_level"] = "MODERATE"

    patients_db[patient_id] = patient_data
    patient_vitals[patient_id] = []
    patient_flag_streaks[patient_id] = 0
    family_notifications[patient_id] = []

    logger.info(f"Registered cardiac patient: {patient_id}")

    return patient_data


@app.get("/api/patients/{patient_id}", tags=["Patients"])
async def get_patient(patient_id: str):
    """Get patient details"""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patients_db[patient_id]


@app.put("/api/patients/{patient_id}", tags=["Patients"])
async def update_patient(patient_id: str, patient: PatientCreate):
    """Replace a patient's validated EHR fields."""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    current = patients_db[patient_id]
    updated = patient.model_dump()
    updated.update({"patient_id": patient_id, "created_at": current.get("created_at"), "risk_level": current.get("risk_level", "LOW"), "flag_streak": patient_flag_streaks.get(patient_id, 0)})
    patients_db[patient_id] = updated
    snapshot = prediction_snapshot(updated, patient_vitals.get(patient_id, []))
    patients_db[patient_id]["risk_level"] = snapshot["risk_classification"]
    return patients_db[patient_id]


@app.delete("/api/patients/{patient_id}", tags=["Patients"])
async def delete_patient(patient_id: str):
    """Delete the patient and associated in-memory data."""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    task = simulator_tasks.pop(patient_id, None)
    if task:
        task.cancel()
    del patients_db[patient_id]
    patient_vitals.pop(patient_id, None)
    patient_flag_streaks.pop(patient_id, None)
    patient_flag_hour_keys.pop(patient_id, None)
    patient_flag_hour_status.pop(patient_id, None)
    family_contacts.pop(patient_id, None)
    family_notifications.pop(patient_id, None)
    websocket_clients.pop(patient_id, None)
    for alert_id in [key for key, alert in alerts_db.items() if alert.get("patient_id") == patient_id]:
        alerts_db.pop(alert_id, None)
    return {"status": "deleted", "patient_id": patient_id}


@app.get("/api/patients", tags=["Patients"])
async def list_patients():
    """List all patients"""
    return list(patients_db.values())


# ==================== Vital Signs Endpoints ====================

@app.post("/api/patients/{patient_id}/vitals", tags=["Vital Signs"])
async def submit_vital_signs(patient_id: str, vitals: VitalSigns):
    """Submit vital signs from wearable devices"""

    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    logger.info(f"Received vitals from {patient_id}: HR={vitals.heart_rate_bpm}, BP={vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic}")
    return await _ingest_and_broadcast(patient_id, vitals)



@app.get("/api/patients/{patient_id}/vitals", tags=["Vital Signs"])
async def get_patient_vitals(patient_id: str, limit: int = Query(default=100, ge=1, le=1000)):
    """Get recent vital signs for a patient"""

    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    vitals = patient_vitals.get(patient_id, [])
    return vitals[-limit:]


@app.get("/api/patients/{patient_id}/vitals/latest", tags=["Vital Signs"])
async def get_latest_vitals(patient_id: str):
    """Get latest vital signs for a patient"""

    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    vitals = patient_vitals.get(patient_id, [])
    if not vitals:
        raise HTTPException(status_code=404, detail="No vital signs recorded")

    return vitals[-1]


@app.post("/api/patients/{patient_id}/whatif", tags=["Predictions"])
async def what_if_prediction(patient_id: str, overrides: WhatIfRequest):
    """Return a deterministic hypothetical prediction without modifying stored data."""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    changes = overrides.model_dump(exclude_unset=True, exclude_none=True)
    patient_changes = {key: value for key, value in changes.items() if key in PatientCreate.model_fields}
    vital_changes = {key: value for key, value in changes.items() if key in VitalSigns.model_fields}
    hypothetical_patient = {**patients_db[patient_id], **patient_changes}
    history = [dict(item) for item in patient_vitals.get(patient_id, [])]
    if vital_changes:
        latest = history[-1] if history else {"timestamp": datetime.now().isoformat(), "source": "what-if"}
        history[-1:] = [{**latest, **vital_changes}]
    result = prediction_snapshot(hypothetical_patient, history)
    return {"patient_id": patient_id, **result, "what_if_only": True, "history_unchanged": True}


@app.get("/api/patients/{patient_id}/baseline", tags=["Analytics"])
async def patient_baseline(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    history = patient_vitals.get(patient_id, [])
    keys = {
        "heart_rate_bpm": "average_heart_rate_bpm",
        "blood_pressure_systolic": "average_systolic_bp",
        "blood_pressure_diastolic": "average_diastolic_bp",
        "oxygen_saturation": "average_oxygen_saturation",
    }
    average = {}
    for key, output_key in keys.items():
        values = [item[key] for item in history if item.get(key) is not None]
        average[output_key] = round(float(np.mean(values)), 1) if values else None
    latest = history[-1] if history else None
    deviation = {}
    large = False
    if latest:
        for key, output_key in keys.items():
            mean = average[output_key]
            value = latest.get(key)
            pct = round(((value - mean) / abs(mean)) * 100, 1) if value is not None and mean not in (None, 0) else None
            deviation[key] = pct
            if pct is not None and abs(pct) >= 20:
                large = True
    return {"patient_id": patient_id, "reading_count": len(history), "average": average, "latest": latest, "deviation_percent": deviation, "large_deviation": large}


@app.get("/api/patients/{patient_id}/explain", tags=["Predictions"])
async def explain_risk(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = patients_db[patient_id]
    history = patient_vitals.get(patient_id, [])
    features = prepare_cardiac_features(patient, history)
    factors = framingham_factors(features)
    total = sum(item["points"] for item in factors)
    prediction = prediction_snapshot(patient, history)
    return {
        "patient_id": patient_id,
        "factors": factors,
        "total_points": total,
        "divisor": 45,
        "probability": round(min(total / 45, 0.99), 3),
        "final_class": prediction["risk_classification"],
        "active_scoring_class": prediction["risk_classification"],
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/patients/{patient_id}/summary", tags=["Patients"])
async def patient_summary(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = patients_db[patient_id]
    history = patient_vitals.get(patient_id, [])
    prediction = prediction_snapshot(patient, history)
    if not history:
        text = f"{patient['name']} has no recorded vital readings. Current EHR-based risk is {prediction['risk_classification']} in this synthetic demo."
    else:
        v = history[-1]
        hr = f"heart rate {v.get('heart_rate_bpm', 'not recorded')} bpm"
        bp = f"blood pressure {v.get('blood_pressure_systolic', '--')}/{v.get('blood_pressure_diastolic', '--')} mmHg"
        spo2 = f"SpO2 {v.get('oxygen_saturation', 'not recorded')}%"
        text = f"Latest reading for {patient['name']}: {hr}, {bp}, and {spo2}. The deterministic synthetic risk estimate is {prediction['risk_classification']} ({prediction['cardiac_event_probability'] * 100:.1f}%)."
    return {"patient_id": patient_id, "summary": text, "latest": history[-1] if history else None, "risk_classification": prediction["risk_classification"], "timestamp": datetime.now().isoformat()}


@app.get("/api/patients/{patient_id}/family-contact", tags=["Family"])
async def get_family_contact(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"patient_id": patient_id, "contact": family_contacts.get(patient_id), "notifications": family_notifications.get(patient_id, []), "flag_streak": patient_flag_streaks.get(patient_id, 0)}


@app.post("/api/patients/{patient_id}/family-contact", tags=["Family"])
async def save_family_contact(patient_id: str, contact: FamilyContact):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    family_contacts[patient_id] = contact.model_dump()
    family_notifications.setdefault(patient_id, [])
    return {"patient_id": patient_id, "contact": family_contacts[patient_id], "status": "saved"}


@app.get("/api/patients/{patient_id}/export", tags=["Patients"])
async def export_patient(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"patient": patients_db[patient_id], "vitals": patient_vitals.get(patient_id, []), "alerts": [a for a in alerts_db.values() if a.get("patient_id") == patient_id], "family_contact": family_contacts.get(patient_id), "family_notifications": family_notifications.get(patient_id, []), "flag_streak": patient_flag_streaks.get(patient_id, 0), "synthetic": True}


# ==================== Cardiac Predictions ====================

@app.post("/api/patients/{patient_id}/predict/cardiac", response_model=CardiacPredictionResponse, tags=["Predictions"])
async def predict_cardiac_event(patient_id: str):
    """Predict cardiac event risk for a patient"""

    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient = patients_db[patient_id]
    vitals_history = patient_vitals.get(patient_id, [])

    # Prepare features
    features = prepare_cardiac_features(patient, vitals_history)

    # Calculate Framingham risk
    framingham_score = calculate_framingham_risk(features)
    cardiac_prob = framingham_score

    # Detect arrhythmia
    arrhythmia_risk = "Normal sinus rhythm"
    arrhythmia_severity = "NORMAL"
    if vitals_history:
        latest = vitals_history[-1]
        hr = latest.get('heart_rate_bpm') or 72
        ecg = latest.get('ecg_rhythm')
        result = detect_arrhythmia(hr, ecg)
        arrhythmia_risk = result['rhythm_status']
        arrhythmia_severity = result['severity']

    # Predict BP trend
    bp_trend = "STABLE"
    bp_risk = "NORMAL"
    if vitals_history:
        bp_data = [{'systolic': v.get('blood_pressure_systolic', 120),
                    'diastolic': v.get('blood_pressure_diastolic', 80)}
                   for v in vitals_history if v.get('blood_pressure_systolic')]
        if bp_data:
            bp_result = predict_bp_trend(bp_data)
            bp_trend = bp_result['trend']
            bp_risk = bp_result['risk_level']

    # Determine overall risk classification
    risk_classification = "LOW"
    if cardiac_prob > 0.85 or bp_risk == "CRITICAL":
        risk_classification = "CRITICAL"
    elif cardiac_prob > 0.7 or arrhythmia_severity == "HIGH" or bp_risk == "HIGH":
        risk_classification = "HIGH"
    elif cardiac_prob > 0.4 or arrhythmia_severity != "NORMAL" or bp_risk == "ELEVATED":
        risk_classification = "MODERATE"

    # Generate recommendations
    recommended_actions = get_cardiac_recommendations(risk_classification, arrhythmia_risk, bp_risk)

    # Create alert if high risk
    if risk_classification in ["HIGH", "CRITICAL"]:
        latest = vitals_history[-1] if vitals_history else None
        reading_timestamp = latest.get("timestamp") if latest else "no-readings"
        already_alerted = any(
            alert.get("patient_id") == patient_id
            and alert.get("severity") == risk_classification
            and (
                alert.get("prediction_reading_timestamp") == reading_timestamp
                or (latest and (alert.get("vital_signs") or {}).get("timestamp") == reading_timestamp)
            )
            for alert in alerts_db.values()
        )
        if not already_alerted:
            alert = {
                "alert_id": new_alert_id(),
                "patient_id": patient_id,
                "severity": risk_classification,
                "alert_type": "cardiac_event" if cardiac_prob > 0.7 else "arrhythmia" if arrhythmia_risk != "Normal sinus rhythm" else "hypertension",
                "message": f"Cardiac risk: {risk_classification} (Event prob: {cardiac_prob*100:.1f}%, Rhythm: {arrhythmia_risk})",
                "timestamp": datetime.now().isoformat(),
                "acknowledged": False,
                "vital_signs": latest,
                "prediction_reading_timestamp": reading_timestamp,
            }
            alerts_db[alert["alert_id"]] = alert

    return CardiacPredictionResponse(
        patient_id=patient_id,
        cardiac_event_probability=round(cardiac_prob, 3),
        arrhythmia_risk=arrhythmia_risk,
        blood_pressure_trend=bp_trend,
        bp_risk_level=bp_risk,
        risk_classification=risk_classification,
        framingham_score=round(framingham_score, 3),
        recommended_actions=recommended_actions,
        timestamp=datetime.now().isoformat(),
    )



def prepare_cardiac_features(patient: dict, vitals_history: List[dict]) -> dict:
    """Prepare features for cardiac prediction"""

    # Calculate vital sign statistics
    bp_systolic_list = [v.get('blood_pressure_systolic', 120) for v in vitals_history if v.get('blood_pressure_systolic')]
    bp_systolic = np.mean(bp_systolic_list) if bp_systolic_list else 120

    bp_diastolic_list = [v.get('blood_pressure_diastolic', 80) for v in vitals_history if v.get('blood_pressure_diastolic')]
    bp_diastolic = np.mean(bp_diastolic_list) if bp_diastolic_list else 80

    heart_rates = [v.get('heart_rate_bpm', 72) for v in vitals_history if v.get('heart_rate_bpm')]
    heart_rate_mean = np.mean(heart_rates) if heart_rates else 72

    spo2_values = [v.get('oxygen_saturation', 98) for v in vitals_history if v.get('oxygen_saturation')]
    spo2_mean = np.mean(spo2_values) if spo2_values else 98

    feature_dict = {
        'age': patient.get('age', 50),
        'gender_male': 1 if patient.get('gender') == 'M' else 0,
        'bmi': patient.get('bmi', 26),
        'systolic_bp': bp_systolic,
        'diastolic_bp': bp_diastolic,
        'heart_rate_mean': heart_rate_mean,
        'spo2': spo2_mean,
        'smoker': 1 if patient.get('smoker') else 0,
        'diabetes': 1 if patient.get('diabetes') else 0,
        'hypertension': 1 if patient.get('hypertension') else 0,
        'cholesterol_total': patient.get('total_cholesterol') or 200,
        'cholesterol_hdl': patient.get('hdl_cholesterol') or 50,
        'cholesterol_ldl': patient.get('ldl_cholesterol') or 120,
    }

    return feature_dict


def check_cardiac_alerts(patient_id: str, vitals: VitalSigns) -> List[dict]:
    """Check vital signs for cardiac alerts"""
    alerts = []

    if vitals.heart_rate_bpm is not None:
        if vitals.heart_rate_bpm > 120:
            alerts.append(create_alert(patient_id, "arrhythmia", "HIGH",
                f"Tachycardia detected - HR: {vitals.heart_rate_bpm} bpm", vitals))
        elif vitals.heart_rate_bpm < 50:
            alerts.append(create_alert(patient_id, "arrhythmia", "HIGH",
                f"Bradycardia detected - HR: {vitals.heart_rate_bpm} bpm", vitals))
        elif vitals.heart_rate_bpm > 100:
            alerts.append(create_alert(patient_id, "arrhythmia", "MEDIUM",
                f"Elevated heart rate - HR: {vitals.heart_rate_bpm} bpm", vitals))

    if vitals.blood_pressure_systolic is not None or vitals.blood_pressure_diastolic is not None:
        systolic = vitals.blood_pressure_systolic
        diastolic = vitals.blood_pressure_diastolic
        display_bp = f"{systolic if systolic is not None else '--'}/{diastolic if diastolic is not None else '--'}"
        if (systolic is not None and systolic >= 180) or (diastolic is not None and diastolic >= 120):
            alerts.append(create_alert(patient_id, "hypertension", "CRITICAL",
                f"Hypertensive crisis - BP: {display_bp} mmHg", vitals))
        elif (systolic is not None and systolic >= 160) or (diastolic is not None and diastolic >= 100):
            alerts.append(create_alert(patient_id, "hypertension", "HIGH",
                f"Stage 2 hypertension - BP: {display_bp} mmHg", vitals))
        elif (systolic is not None and systolic >= 140) or (diastolic is not None and diastolic >= 90):
            alerts.append(create_alert(patient_id, "hypertension", "MEDIUM",
                f"Stage 1 hypertension - BP: {display_bp} mmHg", vitals))
        elif (systolic is not None and systolic < 90) or (diastolic is not None and diastolic < 60):
            alerts.append(create_alert(patient_id, "hypotension", "MEDIUM",
                f"Hypotension - BP: {display_bp} mmHg", vitals))

    if vitals.oxygen_saturation is not None and vitals.oxygen_saturation < 90:
        alerts.append(create_alert(patient_id, "hypoxia", "HIGH",
            f"Low oxygen saturation - SpO2: {vitals.oxygen_saturation}%", vitals))

    if vitals.ecg_rhythm and vitals.ecg_rhythm in ['AFib', 'PVC', 'ST Elevation', 'T Wave Inversion']:
        alerts.append(create_alert(patient_id, "ecg", "HIGH",
            f"Abnormal ECG rhythm: {vitals.ecg_rhythm}", vitals))

    return alerts


def create_alert(patient_id: str, alert_type: str, severity: str, message: str, vitals: VitalSigns) -> dict:
    """Create an alert object"""
    return {
        "alert_id": new_alert_id(),
        "patient_id": patient_id,
        "severity": severity,
        "alert_type": alert_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "acknowledged": False,
        "vital_signs": {
            "heart_rate_bpm": vitals.heart_rate_bpm,
            "blood_pressure_systolic": vitals.blood_pressure_systolic,
            "blood_pressure_diastolic": vitals.blood_pressure_diastolic,
            "oxygen_saturation": vitals.oxygen_saturation,
            "ecg_rhythm": vitals.ecg_rhythm,
            "timestamp": vitals.timestamp,
        }
    }


# ==================== Alerts ====================

@app.get("/api/patients/{patient_id}/alerts", tags=["Alerts"])
async def get_patient_alerts(patient_id: str, limit: int = Query(default=20, ge=1, le=1000)):
    """Get recent alerts for a patient"""

    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_alerts = [
        alert for alert in alerts_db.values()
        if alert["patient_id"] == patient_id
    ]

    return sorted(patient_alerts, key=lambda x: x["timestamp"], reverse=True)[:max(1, limit)]


@app.post("/api/alerts/{alert_id}/acknowledge", tags=["Alerts"])
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""

    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")

    alerts_db[alert_id]["acknowledged"] = True
    alerts_db[alert_id]["acknowledged_at"] = datetime.now().isoformat()

    return alerts_db[alert_id]


@app.get("/api/alerts", tags=["Alerts"])
async def get_all_alerts(severity: Optional[str] = None, limit: int = Query(default=50, ge=1, le=1000)):
    """Get all alerts (for doctor dashboard)"""

    alerts = list(alerts_db.values())

    if severity:
        alerts = [a for a in alerts if a["severity"] == severity.upper()]

    return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)[:max(1, limit)]


async def _simulation_loop(patient_id: str):
    tick = 0
    simulation_base = datetime.now()
    try:
        while patient_id in patients_db:
            history = patient_vitals.get(patient_id, [])
            latest = history[-1] if history else {}
            spike = random.random() < 0.12
            hr = max(55, min(100, int(latest.get("heart_rate_bpm") or 72) + random.randint(-5, 5)))
            systolic = max(100, min(145, int(latest.get("blood_pressure_systolic") or 120) + random.randint(-6, 6)))
            diastolic = max(60, min(95, int(latest.get("blood_pressure_diastolic") or 80) + random.randint(-4, 4)))
            spo2 = round(max(94, min(100, float(latest.get("oxygen_saturation") or 98) + random.uniform(-1.0, 0.5))), 1)
            if spike:
                hr, systolic, diastolic = random.choice([(128, 182, 118), (132, 168, 104), (48, 122, 78)])
                spo2 = 88.0 if hr > 120 else 96.0
            vital = VitalSigns(
                heart_rate_bpm=hr,
                blood_pressure_systolic=systolic,
                blood_pressure_diastolic=diastolic,
                oxygen_saturation=spo2,
                ecg_rhythm="Tachycardia" if hr > 120 else "Normal sinus rhythm",
                ecg_quality="GOOD",
                source="simulator",
                timestamp=datetime.now().isoformat(),
            )
            summary_time = simulation_base + timedelta(hours=tick)
            await _ingest_and_broadcast(patient_id, vital, summary_timestamp=summary_time.isoformat())
            tick += 1
            await asyncio.sleep(3)
    except asyncio.CancelledError:
        raise
    finally:
        simulator_tasks.pop(patient_id, None)


@app.post("/api/simulate/{patient_id}/start", tags=["Simulation"])
async def start_simulation(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    task = simulator_tasks.get(patient_id)
    if task is None or task.done():
        simulator_tasks[patient_id] = asyncio.create_task(_simulation_loop(patient_id))
    return {"patient_id": patient_id, "status": "running", "interval_seconds": 3}


@app.post("/api/simulate/{patient_id}/stop", tags=["Simulation"])
async def stop_simulation(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    task = simulator_tasks.pop(patient_id, None)
    if task:
        task.cancel()
    return {"patient_id": patient_id, "status": "stopped"}


@app.post("/api/reset", tags=["Demo"])
async def reset_demo_data():
    global patient_counter
    for task in list(simulator_tasks.values()):
        task.cancel()
    simulator_tasks.clear()
    patients_db.clear()
    alerts_db.clear()
    patient_vitals.clear()
    family_contacts.clear()
    family_notifications.clear()
    patient_flag_streaks.clear()
    patient_flag_hour_keys.clear()
    patient_flag_hour_status.clear()
    websocket_clients.clear()
    patient_counter = 0
    seed_demo_data()
    for patient_id in patients_db:
        patient_flag_streaks[patient_id] = 0
        family_notifications[patient_id] = []
    return {"status": "reset", "patient_count": len(patients_db), "synthetic": True}


# ==================== WebSocket ====================

@app.websocket("/ws/patient/{patient_id}")
async def websocket_endpoint(websocket: WebSocket, patient_id: str):
    """WebSocket endpoint for real-time cardiac data streaming"""

    if patient_id not in patients_db:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    websocket_clients.setdefault(patient_id, set()).add(websocket)
    logger.info(f"WebSocket connected: {patient_id}")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "subscribe":
                await websocket.send_json({
                    "type": "subscribed",
                    "patient_id": patient_id,
                    "timestamp": datetime.now().isoformat(),
                })

            elif message.get("type") == "vitals":
                vitals = VitalSigns(**message.get("data", {}))
                await _ingest_and_broadcast(patient_id, vitals)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websocket_clients.get(patient_id, set()).discard(websocket)
        logger.info(f"WebSocket disconnected: {patient_id}")


# ==================== Statistics ====================

@app.get("/api/statistics", tags=["Analytics"])
async def get_statistics():
    """Get system statistics"""

    high_risk_patients = 0
    heart_rates = []
    for pid, patient in patients_db.items():
        vitals_history = patient_vitals.get(pid, [])
        heart_rates.extend(
            v["heart_rate_bpm"] for v in vitals_history
            if v.get("heart_rate_bpm") is not None
        )
        if vitals_history:
            features = prepare_cardiac_features(patient, vitals_history)
            risk = calculate_framingham_risk(features)
            if risk >= 0.4 or patient.get('hypertension') or patient.get('diabetes'):
                high_risk_patients += 1

    return {
        "total_patients": len(patients_db),
        "high_risk_patients": high_risk_patients,
        "total_alerts": len(alerts_db),
        "critical_alerts": sum(1 for a in alerts_db.values() if a["severity"] == "CRITICAL"),
        "high_alerts": sum(1 for a in alerts_db.values() if a["severity"] == "HIGH"),
        "high_risk_alerts": sum(1 for a in alerts_db.values() if a["severity"] in ["HIGH", "CRITICAL"]),
        "unacknowledged_alerts": sum(1 for a in alerts_db.values() if not a["acknowledged"]),
        "average_heart_rate": round(float(np.mean(heart_rates)), 1) if heart_rates else None,
        "timestamp": datetime.now().isoformat(),
    }


# ==================== Root ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CardioTwin API - Cardiac Digital Twin",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
