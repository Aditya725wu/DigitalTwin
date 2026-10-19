import os
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/digitaltwin")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ML Models
MODELS_DIR = os.path.join(os.path.dirname(__file__), "../models")
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

# API Configuration
API_TITLE = "DiabetesTwin - Digital Twin API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Real-time diabetes monitoring and prediction API"

# Prediction thresholds
GLUCOSE_SPIKE_THRESHOLD = 180  # mg/dL
GLUCOSE_CRITICAL_THRESHOLD = 250  # mg/dL
GLUCOSE_LOW_THRESHOLD = 70  # mg/dL

# Alert settings
ALERT_PREDICTION_WINDOW = 120  # minutes (2 hours)
HIGH_RISK_SCORE = 0.7
MEDIUM_RISK_SCORE = 0.4

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8081").split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
