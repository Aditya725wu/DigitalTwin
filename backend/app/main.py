import json
import os
from datetime import datetime, timedelta, timezone

import numpy as np
from fastapi import FastAPI, HTTPException

from .alerts import emit_alert, set_contact
from .database import connect, initialize
from .schemas import FamilyContactInput, ReadingInput, SimulateRequest, WhatIfRequest
from .simulation import DEFAULTS, SIGNALS, demo_reading
from .twin import baseline_from_rows, model

app = FastAPI(title="Cardiovascular Digital Twin POC", version="0.1.0",
              description="Simulated deviation monitoring demo; not a diagnostic or medical-event prediction system.")
PERSISTENCE_HOURS = max(1, int(os.getenv("TWIN_ALERT_PERSISTENCE_HOURS", "3")))
PATIENT = "demo"


def rows_for(patient_id: str, limit: int | None = None) -> list[dict]:
    with connect() as db:
        sql = "SELECT * FROM readings WHERE patient_id=? ORDER BY timestamp DESC"
        args = [patient_id]
        if limit:
            sql += " LIMIT ?"
            args.append(limit)
        rows = [dict(r) for r in db.execute(sql, args).fetchall()]
    rows.reverse()
    return rows


def ensure_patient(patient_id: str) -> None:
    with connect() as db:
        count = db.execute("SELECT COUNT(*) FROM readings WHERE patient_id=?", (patient_id,)).fetchone()[0]
    if count:
        return
    # Seed a week of patient-specific readings. Baseline learns only the first 48 hours.
    rng = np.random.default_rng(2026)
    start = datetime.now(timezone.utc) - timedelta(hours=168)
    with connect() as db:
        for i in range(168):
            timestamp = start + timedelta(hours=i)
            values = demo_reading(patient_id, timestamp, "normal", i, rng)
            db.execute("INSERT INTO readings(patient_id,timestamp,heart_rate,hrv,systolic_bp,diastolic_bp,spo2,activity) VALUES(?,?,?,?,?,?,?,?)",
                       (patient_id, timestamp.isoformat(), *(values[s] for s in SIGNALS)))
    calibrate(patient_id)


def calibrate(patient_id: str) -> dict:
    all_rows = rows_for(patient_id)
    if len(all_rows) < 24:
        raise HTTPException(400, "At least 24 hourly readings are required to learn a baseline.")
    # An initial 48-hour calibration window. Existing baseline stays fixed thereafter.
    with connect() as db:
        existing = db.execute("SELECT * FROM baselines WHERE patient_id=?", (patient_id,)).fetchone()
        if existing:
            return {"patient_id": patient_id, "sample_count": existing["sample_count"],
                    "values": json.loads(existing["values_json"]), "spreads": json.loads(existing["spreads_json"]),
                    "calibrated_at": existing["calibrated_at"]}
        source = all_rows[:min(48, len(all_rows))]
        values, spreads = baseline_from_rows(source)
        calibrated_at = datetime.now(timezone.utc).isoformat()
        db.execute("INSERT INTO baselines VALUES(?,?,?,?,?)", (patient_id, calibrated_at, len(source),
                   json.dumps(values), json.dumps(spreads)))
    return {"patient_id": patient_id, "sample_count": len(source), "values": values, "spreads": spreads,
            "calibrated_at": calibrated_at}


def get_baseline(patient_id: str) -> dict:
    ensure_patient(patient_id)
    return calibrate(patient_id)


def assess(patient_id: str, rows: list[dict] | None = None, reading_override: dict | None = None,
           trigger_alert: bool = False) -> dict:
    baseline = get_baseline(patient_id)
    history = rows if rows is not None else rows_for(patient_id)
    if not history and reading_override is None:
        raise HTTPException(404, "No patient readings found")
    latest = reading_override or history[-1]
    persistence = 0
    for row in reversed(history):
        result = model.assess(row, baseline["values"], baseline["spreads"], persistence + 1)
        if result["state"] != "deviation":
            break
        persistence += 1
    result = model.assess(latest, baseline["values"], baseline["spreads"], persistence)
    result["alert_threshold_hours"] = PERSISTENCE_HOURS
    result["alert_eligible"] = result["state"] == "deviation" and persistence >= PERSISTENCE_HOURS
    if result["alert_eligible"] and trigger_alert:
        with connect() as db:
            recent = db.execute("SELECT timestamp FROM alerts WHERE patient_id=? ORDER BY timestamp DESC LIMIT 1", (patient_id,)).fetchone()
        latest_time = datetime.fromisoformat(latest["timestamp"])
        already_alerted = bool(recent and (latest_time - datetime.fromisoformat(recent["timestamp"])).total_seconds() < 6 * 3600)
        if not already_alerted:
            result["alert"] = emit_alert(patient_id, result["explanation"] + f" Pattern persisted for {persistence} consecutive hourly summaries.", latest["timestamp"])
        else:
            result["alert"] = None
    return result


@app.on_event("startup")
def startup():
    initialize()
    ensure_patient(PATIENT)
    print("Synthetic held-out evaluation:", json.dumps(model.metrics, indent=2))


@app.get("/api/health")
def health():
    return {"status": "ok", "disclaimer": "Simulated deviation monitoring only; not for medical decisions."}


@app.get("/api/model/metrics")
def metrics():
    return model.metrics


@app.get("/api/patients/{patient_id}/dashboard")
def dashboard(patient_id: str):
    ensure_patient(patient_id)
    history = rows_for(patient_id, 48)
    result = assess(patient_id, history)
    baseline = get_baseline(patient_id)
    with connect() as db:
        contact = db.execute("SELECT authorized FROM contacts WHERE patient_id=?", (patient_id,)).fetchone()
    return {"patient_id": patient_id, "latest": history[-1], "history": history,
            "baseline": baseline, "assessment": result,
            "family_contact_authorized": bool(contact["authorized"]) if contact else False,
            "disclaimer": "Deviation flags are for further attention only; they are not a diagnosis or medical-event prediction."}


@app.get("/api/patients/{patient_id}/baseline")
def baseline(patient_id: str):
    return get_baseline(patient_id)


@app.get("/api/patients/{patient_id}/assessment")
def current_assessment(patient_id: str):
    ensure_patient(patient_id)
    return assess(patient_id, rows_for(patient_id))


@app.post("/api/patients/{patient_id}/readings")
def add_reading(patient_id: str, reading: ReadingInput):
    ensure_patient(patient_id)
    data = reading.model_dump()
    timestamp = (data.pop("timestamp") or datetime.now(timezone.utc)).isoformat()
    with connect() as db:
        db.execute("INSERT INTO readings(patient_id,timestamp,heart_rate,hrv,systolic_bp,diastolic_bp,spo2,activity) VALUES(?,?,?,?,?,?,?,?)",
                   (patient_id, timestamp, *(data[s] for s in SIGNALS)))
    return {"reading": {"patient_id": patient_id, "timestamp": timestamp, **data},
            "assessment": assess(patient_id, rows_for(patient_id), trigger_alert=True)}


@app.post("/api/patients/{patient_id}/simulate")
def simulate(patient_id: str, request: SimulateRequest):
    ensure_patient(patient_id)
    rng = np.random.default_rng()
    history = rows_for(patient_id)
    start = datetime.fromisoformat(history[-1]["timestamp"]) + timedelta(hours=1)
    inserted = []
    with connect() as db:
        for i in range(request.hours):
            timestamp = start + timedelta(hours=i)
            values = demo_reading(patient_id, timestamp, request.scenario, i, rng)
            db.execute("INSERT INTO readings(patient_id,timestamp,heart_rate,hrv,systolic_bp,diastolic_bp,spo2,activity) VALUES(?,?,?,?,?,?,?,?)",
                       (patient_id, timestamp.isoformat(), *(values[s] for s in SIGNALS)))
            inserted.append({"patient_id": patient_id, "timestamp": timestamp.isoformat(), **values})
    full = rows_for(patient_id)
    result = assess(patient_id, full, trigger_alert=True)
    return {"inserted": inserted, "assessment": result}


@app.post("/api/patients/{patient_id}/what-if")
def what_if(patient_id: str, request: WhatIfRequest):
    ensure_patient(patient_id)
    history = rows_for(patient_id)
    hypothetical = {**history[-1], **request.changes}
    result = assess(patient_id, history, reading_override=hypothetical)
    result["alert_eligible"] = False
    result["alert"] = None
    result["hypothetical"] = True
    return result


@app.put("/api/patients/{patient_id}/family-contact")
def family_contact(patient_id: str, contact: FamilyContactInput):
    ensure_patient(patient_id)
    set_contact(patient_id, contact.authorized, contact.name, contact.fcm_token)
    return {"patient_id": patient_id, "authorized": contact.authorized, "name": contact.name,
            "delivery": "firebase_cloud_messaging_if_configured_otherwise_local_demo"}


@app.get("/api/patients/{patient_id}/alerts")
def alerts(patient_id: str):
    with connect() as db:
        rows = [dict(r) for r in db.execute("SELECT * FROM alerts WHERE patient_id=? ORDER BY timestamp DESC LIMIT 100", (patient_id,)).fetchall()]
    return {"alerts": rows}
