"""
Utilities for DiabetesTwin
Helper functions and common utilities
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import hashlib
import secrets
import re


def generate_patient_id(prefix: str = "PAT") -> str:
    """Generate a unique patient ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(4).upper()
    return f"{prefix}{timestamp}{random_suffix}"


def generate_alert_id(prefix: str = "ALR") -> str:
    """Generate a unique alert ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(3).upper()
    return f"{prefix}{timestamp}{random_suffix}"


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's 10-15 digits
    return re.match(r'^\d{10,15}$', cleaned) is not None


def calculate_glucose_risk(glucose_value: float, trend: float = 0) -> str:
    """Calculate risk level based on glucose value and trend"""
    if glucose_value < 70:
        return "CRITICAL"  # Hypoglycemia
    elif glucose_value < 80:
        return "HIGH"  # Low
    elif glucose_value <= 120:
        return "LOW"  # Normal
    elif glucose_value <= 180:
        return "MEDIUM"  # Elevated
    elif glucose_value <= 250:
        return "HIGH"  # High
    else:
        return "CRITICAL"  # Very high


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 1)


def get_bmi_category(bmi: float) -> str:
    """Get BMI category"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def calculate_time_in_range(glucose_readings: List[float], min_range: float = 70, max_range: float = 180) -> float:
    """Calculate time in range (TIR) percentage"""
    if not glucose_readings:
        return 0.0

    in_range = sum(1 for g in glucose_readings if min_range <= g <= max_range)
    return round((in_range / len(glucose_readings)) * 100, 1)


def get_glucose_trend_description(velocity: float) -> str:
    """Get text description of glucose trend"""
    if velocity < -3:
        return "Falling rapidly"
    elif velocity < -1:
        return "Falling"
    elif velocity < 1:
        return "Stable"
    elif velocity < 3:
        return "Rising"
    else:
        return "Rising rapidly"


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for secure storage"""
    return hashlib.sha256(data.encode()).hexdigest()


def parse_sensor_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and normalize sensor data"""
    parsed = {
        "glucose_mg_dl": None,
        "heart_rate_bpm": None,
        "steps": None,
        "timestamp": None,
    }

    if "glucose" in data:
        parsed["glucose_mg_dl"] = float(data["glucose"])
    if "hr" in data or "heart_rate" in data:
        parsed["heart_rate_bpm"] = int(data.get("hr", data.get("heart_rate")))
    if "steps" in data:
        parsed["steps"] = int(data["steps"])
    if "timestamp" in data:
        parsed["timestamp"] = data["timestamp"]
    elif "time" in data:
        parsed["timestamp"] = data["time"]

    return parsed


def format_glucose_value(value: float, unit: str = "mg/dL") -> str:
    """Format glucose value for display"""
    return f"{value:.0f} {unit}"


def get_recommended_actions(risk_level: str, prediction_type: str) -> List[str]:
    """Get recommended actions based on risk level"""
    actions_map = {
        "glucose_spike": {
            "LOW": ["Continue monitoring"],
            "MEDIUM": ["Stay hydrated", "Light exercise"],
            "HIGH": ["Take corrective action", "Check medication timing", "Contact healthcare provider"],
            "CRITICAL": ["Immediate intervention required", "Seek medical attention"],
        },
        "cv_risk": {
            "LOW": ["Maintain healthy lifestyle"],
            "MEDIUM": ["Regular exercise", "Diet modifications"],
            "HIGH": ["Cardiac consultation recommended", "Monitor blood pressure"],
            "CRITICAL": ["Immediate cardiac evaluation"],
        },
    }

    return actions_map.get(prediction_type, {}).get(risk_level, ["Monitor closely"])


def sanitize_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize patient data for privacy"""
    sensitive_fields = ["ssn", "aadhar", "password", "token"]

    sanitized = data.copy()
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = "***REDACTED***"

    return sanitized