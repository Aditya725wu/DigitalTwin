import os
from datetime import datetime, timezone

from .database import connect


def set_contact(patient_id: str, authorized: bool, name: str, token: str | None) -> None:
    with connect() as db:
        db.execute("INSERT INTO contacts(patient_id,authorized,name,fcm_token) VALUES(?,?,?,?) "
                   "ON CONFLICT(patient_id) DO UPDATE SET authorized=excluded.authorized,name=excluded.name,fcm_token=excluded.fcm_token",
                   (patient_id, int(authorized), name, token))


def emit_alert(patient_id: str, message: str, event_timestamp: str | None = None) -> dict | None:
    with connect() as db:
        contact = db.execute("SELECT * FROM contacts WHERE patient_id=?", (patient_id,)).fetchone()
        if not contact or not contact["authorized"]:
            return None
        via = "local_demo"
        token = contact["fcm_token"]
        service_account = os.getenv("FCM_SERVICE_ACCOUNT")
        if token and service_account and os.path.exists(service_account):
            try:
                import firebase_admin
                from firebase_admin import credentials, messaging
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(credentials.Certificate(service_account))
                messaging.send(messaging.Message(token=token, notification=messaging.Notification(
                    title="Cardiovascular Twin pattern alert", body=message[:240])))
                via = "fcm"
            except Exception:
                via = "local_demo"
        ts = event_timestamp or datetime.now(timezone.utc).isoformat()
        cur = db.execute("INSERT INTO alerts(patient_id,timestamp,message,delivered_via) VALUES(?,?,?,?)",
                         (patient_id, ts, message, via))
        return {"id": cur.lastrowid, "patient_id": patient_id, "timestamp": ts, "message": message, "delivered_via": via}
