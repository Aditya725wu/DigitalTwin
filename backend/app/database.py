import os
import sqlite3
from pathlib import Path


DB_PATH = Path(os.getenv("TWIN_DB_PATH", Path(__file__).resolve().parents[1] / "twin.sqlite3"))


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def initialize() -> None:
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY, patient_id TEXT NOT NULL, timestamp TEXT NOT NULL,
            heart_rate REAL, hrv REAL, systolic_bp REAL, diastolic_bp REAL, spo2 REAL, activity REAL
        );
        CREATE INDEX IF NOT EXISTS idx_readings_patient_time ON readings(patient_id, timestamp);
        CREATE TABLE IF NOT EXISTS baselines (
            patient_id TEXT PRIMARY KEY, calibrated_at TEXT NOT NULL,
            sample_count INTEGER NOT NULL, values_json TEXT NOT NULL, spreads_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS contacts (
            patient_id TEXT PRIMARY KEY, authorized INTEGER NOT NULL, name TEXT NOT NULL, fcm_token TEXT
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY, patient_id TEXT NOT NULL, timestamp TEXT NOT NULL,
            message TEXT NOT NULL, delivered_via TEXT NOT NULL DEFAULT 'local_demo'
        );
        """)
