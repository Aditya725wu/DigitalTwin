import os
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ML Models
MODELS_DIR = os.path.join(os.path.dirname(__file__), "../models")
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

# CardioTwin Configuration
API_TITLE = "CardioTwin - Cardiovascular Digital Twin API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Synthetic cardiovascular monitoring and risk prediction API"

# Prediction thresholds (cardiac)
CARDIAC_EVENT_HIGH_THRESHOLD = 0.7
CARDIAC_EVENT_MEDIUM_THRESHOLD = 0.4
BP_CRITICAL_SYSTOLIC = 180
BP_HYPERTENSIVE_SYSTOLIC = 140

# Alert settings
ALERT_PREDICTION_WINDOW = 120  # minutes (2 hours)
HIGH_RISK_SCORE = 0.7
MEDIUM_RISK_SCORE = 0.4

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8081").split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
