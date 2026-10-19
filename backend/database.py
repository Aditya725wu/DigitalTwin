"""
Database models for DiabetesTwin
SQLAlchemy models for PostgreSQL
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    bmi = Column(Float, nullable=False)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    family_history_diabetes = Column(Boolean, default=False)
    family_history_hypertension = Column(Boolean, default=False)
    smoker = Column(Boolean, default=False)
    medications = Column(JSON, default=list)
    allergies = Column(JSON, default=list)
    comorbidities = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lab_results = relationship("LabResult", back_populates="patient", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="patient", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")


class LabResult(Base):
    """Lab results model"""
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"), nullable=False)
    hba1c = Column(Float)
    fasting_glucose = Column(Float)
    total_cholesterol = Column(Float)
    ldl = Column(Float)
    hdl = Column(Float)
    triglycerides = Column(Float)
    creatinine = Column(Float)
    gfr = Column(Integer)
    test_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="lab_results")


class SensorReading(Base):
    """Sensor readings from wearables"""
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"), nullable=False, index=True)
    reading_type = Column(String(50), nullable=False)  # glucose, heart_rate, activity, sleep
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    source = Column(String(50), default="wearable")  # wearable, manual
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="sensor_readings")


class Prediction(Base):
    """ML predictions"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"), nullable=False, index=True)
    prediction_type = Column(String(50), nullable=False)  # glucose_spike, cv_risk, medication_adherence
    probability = Column(Float, nullable=False)
    risk_level = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    recommended_actions = Column(JSON, default=list)
    predicted_value = Column(Float)
    prediction_window_minutes = Column(Integer, default=120)  # 2 hours
    model_version = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="predictions")


class Alert(Base):
    """Alert model"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"), nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    alert_type = Column(String(50), nullable=False)  # glucose_spike, medication_missed, etc.
    message = Column(Text, nullable=False)
    related_prediction_id = Column(Integer, ForeignKey("predictions.id"))
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    patient = relationship("Patient", back_populates="alerts")


class HealthMetric(Base):
    """Aggregated health metrics"""
    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"), nullable=False, index=True)
    metric_date = Column(DateTime, nullable=False, index=True)

    # Daily aggregations
    avg_glucose = Column(Float)
    max_glucose = Column(Float)
    min_glucose = Column(Float)
    glucose_variability = Column(Float)

    avg_heart_rate = Column(Float)
    resting_hr = Column(Float)
    hr_variability = Column(Float)

    total_steps = Column(Integer)
    active_minutes = Column(Integer)
    calories_burned = Column(Float)

    sleep_duration_hours = Column(Float)
    sleep_quality_score = Column(Float)

    risk_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)