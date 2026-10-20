"""
FastAPI Backend - CardioTwin
Main application and API endpoints for cardiac digital twin
"""

from fastapi import FastAPI, HTTPException, Query, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, List
import logging
from datetime import datetime
import json
import numpy as np
import uuid

from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Pydantic Models ====================

class PatientCreate(BaseModel):
    """Patient registration model for cardiac monitoring"""
    name: str
    age: int = Field(ge=18, le=120)
    gender: str
    email: str
    phone: str
    bmi: float = Field(gt=0, le=100)
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
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


class PatientResponse(BaseModel):
    """Patient response model"""
    patient_id: str
    name: str
    age: int
    gender: str
    email: str
    risk_level: Optional[str] = "LOW"
    created_at: str


class VitalSigns(BaseModel):
    """Vital signs model for cardiac monitoring"""
    heart_rate_bpm: Optional[int] = Field(default=None, ge=20, le=250)
    blood_pressure_systolic: Optional[int] = Field(default=None, ge=40, le=300)
    blood_pressure_diastolic: Optional[int] = Field(default=None, ge=20, le=200)
    oxygen_saturation: Optional[float] = Field(default=None, ge=50, le=100)
    ecg_rhythm: Optional[str] = None
    ecg_quality: Optional[str] = None
    timestamp: Optional[str] = None
    source: str = "wearable"


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
        "created_at": datetime.now().isoformat(),
    }

    baseline_risk = calculate_framingham_risk(prepare_cardiac_features(patient_data, []))
    if baseline_risk >= 0.7 or patient.hypertension or patient.diabetes:
        patient_data["risk_level"] = "HIGH"
    elif baseline_risk >= 0.4:
        patient_data["risk_level"] = "MODERATE"

    patients_db[patient_id] = patient_data
    patient_vitals[patient_id] = []

    logger.info(f"Registered cardiac patient: {patient_id}")

    return patient_data


@app.get("/api/patients/{patient_id}", tags=["Patients"])
async def get_patient(patient_id: str):
    """Get patient details"""
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patients_db[patient_id]


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

    vitals_dict = vitals.model_dump()
    vitals_dict["timestamp"] = vitals_dict.get("timestamp") or datetime.now().isoformat()
    vitals_dict["received_at"] = datetime.now().isoformat()

    if patient_id not in patient_vitals:
        patient_vitals[patient_id] = []

    patient_vitals[patient_id].append(vitals_dict)

    # Keep only last 1000 readings
    if len(patient_vitals[patient_id]) > 1000:
        patient_vitals[patient_id] = patient_vitals[patient_id][-1000:]

    logger.info(f"Received vitals from {patient_id}: HR={vitals.heart_rate_bpm}, BP={vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic}")

    # Check for immediate alerts
    alerts = check_cardiac_alerts(patient_id, vitals)
    for alert in alerts:
        alerts_db[alert["alert_id"]] = alert
        logger.warning(f"Alert created: {alert['alert_id']} - {alert['message']}")

    return {
        "status": "received",
        "patient_id": patient_id,
        "alerts_generated": len(alerts),
        "timestamp": datetime.now().isoformat(),
    }



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
        alert = {
            "alert_id": new_alert_id(),
            "patient_id": patient_id,
            "severity": risk_classification,
            "alert_type": "cardiac_event" if cardiac_prob > 0.7 else "arrhythmia" if arrhythmia_risk != "Normal sinus rhythm" else "hypertension",
            "message": f"Cardiac risk: {risk_classification} (Event prob: {cardiac_prob*100:.1f}%, Rhythm: {arrhythmia_risk})",
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False,
            "vital_signs": vitals_history[-1] if vitals_history else None,
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


# ==================== WebSocket ====================

@app.websocket("/ws/patient/{patient_id}")
async def websocket_endpoint(websocket: WebSocket, patient_id: str):
    """WebSocket endpoint for real-time cardiac data streaming"""

    if patient_id not in patients_db:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
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

                # Store vitals
                vitals_dict = vitals.model_dump()
                vitals_dict["timestamp"] = vitals_dict.get("timestamp") or datetime.now().isoformat()
                vitals_dict["received_at"] = datetime.now().isoformat()
                patient_vitals.setdefault(patient_id, []).append(vitals_dict)
                if len(patient_vitals[patient_id]) > 1000:
                    patient_vitals[patient_id] = patient_vitals[patient_id][-1000:]

                # Check alerts
                alerts = check_cardiac_alerts(patient_id, vitals)
                for alert in alerts:
                    alerts_db[alert["alert_id"]] = alert
                    await websocket.send_json({
                        "type": "alert",
                        "data": alert
                    })

                # Send prediction update
                patient = patients_db[patient_id]
                features = prepare_cardiac_features(patient, patient_vitals[patient_id])
                cardiac_prob = calculate_framingham_risk(features)

                await websocket.send_json({
                    "type": "prediction_update",
                    "cardiac_event_probability": round(cardiac_prob, 3),
                    "risk_classification": "HIGH" if cardiac_prob > 0.7 else "MODERATE" if cardiac_prob > 0.4 else "LOW",
                    "timestamp": datetime.now().isoformat(),
                })

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
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
