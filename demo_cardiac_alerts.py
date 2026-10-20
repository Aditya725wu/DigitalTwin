"""
Cardiac Alert Demo Script for CardioTwin
Demonstrates the cardiac alert system for heart disease prediction
"""

import asyncio
import random
from datetime import datetime
from typing import List, Dict
import json


# Cardiac-specific alert templates
CARDIAC_ALERT_TEMPLATES = {
    "arrhythmia": [
        "Irregular heartbeat pattern detected - possible AFib",
        "Rapid heart rate (Tachycardia) detected - HR above 120 bpm",
        "Slow heart rate (Bradycardia) detected - HR below 50 bpm",
        "Ventricular Premature Contractions (PVCs) detected",
    ],
    "hypertension": [
        "Blood pressure spike detected - Systolic above 160 mmHg",
        "Hypertensive crisis warning - Seek immediate care",
        "Sustained elevated blood pressure trend detected",
        "Morning blood pressure surge pattern identified",
    ],
    "hypotension": [
        "Low blood pressure detected - Risk of fainting",
        "Postural hypotension warning - Rise slowly",
        "Orthostatic hypotension detected",
    ],
    "cardiac_event": [
        "High risk of cardiac event detected in next 24 hours",
        "Elevated cardiac stress indicators - Monitor closely",
        "Multiple cardiac risk factors active - Consult cardiologist",
    ],
    "medication": [
        "Cardiac medication reminder - Beta blocker due",
        "Missed dose detected - Aspirin schedule",
        "Statin refill needed - Cholesterol management",
    ],
    "lifestyle": [
        "Elevated stress levels detected today",
        "Physical activity below target for cardiac health",
        "Sleep quality below optimal for heart recovery",
        "High sodium intake detected - Blood pressure impact",
    ],
    "ecg": [
        "ECG shows abnormal ST segment - Medical attention recommended",
        "T-wave inversion detected in ECG",
        "ECG quality degraded - Reposition sensor",
    ],
}


def generate_cardiac_alert(patient_id: str, alert_type: str = None) -> Dict:
    """Generate a cardiac-specific alert"""
    if alert_type is None:
        alert_type = random.choice(list(CARDIAC_ALERT_TEMPLATES.keys()))

    templates = CARDIAC_ALERT_TEMPLATES[alert_type]
    message = random.choice(templates)

    # Add specific values for cardiac alerts
    if alert_type == "arrhythmia":
        hr = random.randint(40, 160)
        message = f"{message} (Current HR: {hr} bpm)"
    elif alert_type == "hypertension":
        bp = random.randint(140, 200)
        message = f"{message} (Current BP: {bp}/{random.randint(80,120)} mmHg)"

    # Determine severity based on alert type
    severity_map = {
        "cardiac_event": ["HIGH", "CRITICAL", "CRITICAL"],
        "arrhythmia": ["MEDIUM", "HIGH", "MEDIUM"],
        "hypertension": ["MEDIUM", "HIGH", "LOW"],
        "hypotension": ["MEDIUM", "HIGH", "LOW"],
        "medication": ["LOW", "MEDIUM", "LOW"],
        "lifestyle": ["LOW", "LOW", "MEDIUM"],
        "ecg": ["HIGH", "MEDIUM", "HIGH"],
    }

    severity = random.choice(severity_map.get(alert_type, ["LOW", "MEDIUM"]))

    return {
        "alert_id": f"ALR{random.randint(100000, 999999)}",
        "patient_id": patient_id,
        "severity": severity,
        "alert_type": alert_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "acknowledged": False,
        "vital_signs": {
            "heart_rate": random.randint(50, 140),
            "blood_pressure_systolic": random.randint(110, 200),
            "blood_pressure_diastolic": random.randint(60, 120),
            "oxygen_saturation": random.randint(92, 100),
        }
    }


def generate_patient_cardiac_alerts(patient_id: str, count: int = 5) -> List[Dict]:
    """Generate multiple cardiac alerts for a patient"""
    alerts = []
    alert_types = list(CARDIAC_ALERT_TEMPLATES.keys())

    for _ in range(count):
        alert_type = random.choice(alert_types)
        alert = generate_cardiac_alert(patient_id, alert_type)
        alerts.append(alert)

    return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)


async def simulate_cardiac_alerts():
    """Simulate real-time cardiac alerts"""
    print("\n" + "="*60)
    print("CardioTwin - Cardiac Alert System")
    print("="*60)
    print("Generating cardiac patient alerts...\n")

    # Generate cardiac patients
    patients = [f"PAT{str(i).zfill(6)}" for i in range(1, 6)]

    all_alerts = []
    for patient_id in patients:
        patient_alerts = generate_patient_cardiac_alerts(patient_id, random.randint(2, 5))
        all_alerts.extend(patient_alerts)

    all_alerts.sort(key=lambda x: x["timestamp"], reverse=True)

    # Display critical cardiac alerts
    print("\n*** CRITICAL CARDIAC ALERTS ***")
    print("-"*40)
    critical = [a for a in all_alerts if a["severity"] in ["HIGH", "CRITICAL"]]
    for alert in critical[:5]:
        print(f"\n[{alert['severity']}] {alert['alert_type'].upper()}")
        print(f"Patient: {alert['patient_id']}")
        print(f"Message: {alert['message']}")
        print(f"Vitals: HR={alert['vital_signs']['heart_rate']} bpm, "
              f"BP={alert['vital_signs']['blood_pressure_systolic']}/{alert['vital_signs']['blood_pressure_diastolic']}")
        print(f"SpO2: {alert['vital_signs']['oxygen_saturation']}%")

    # Summary by alert type
    print("\n" + "="*60)
    print("CARDIAC ALERT SUMMARY")
    print("="*60)

    type_counts = {}
    for alert in all_alerts:
        at = alert['alert_type']
        type_counts[at] = type_counts.get(at, 0) + 1

    for atype, count in sorted(type_counts.items()):
        print(f"  {atype}: {count}")

    severity_counts = {}
    for alert in all_alerts:
        sev = alert['severity']
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    print("\nBy Severity:")
    for sev, count in sorted(severity_counts.items()):
        print(f"  {sev}: {count}")

    print(f"\nTotal Alerts: {len(all_alerts)}")
    print(f"Patients Monitored: {len(patients)}")

    # Save to file
    with open("demo_cardiac_alerts.json", "w", encoding='utf-8') as f:
        json.dump(all_alerts, f, indent=2)
    print("\n[SUCCESS] Cardiac alerts saved to demo_cardiac_alerts.json")

    return all_alerts


def show_cardiac_recommendations(alert: Dict):
    """Show cardiac-specific recommendations"""
    recommendations = {
        "arrhythmia": [
            "Sit down and rest immediately",
            "Avoid caffeine and alcohol",
            "Check pulse for regularity",
            "Contact doctor if persistent >5 minutes",
            "Call emergency if chest pain or dizziness",
        ],
        "hypertension": [
            "Take prescribed blood pressure medication",
            "Reduce sodium intake immediately",
            "Practice deep breathing exercises",
            "Avoid strenuous activity",
            "Seek emergency care if >180/120 mmHg",
        ],
        "cardiac_event": [
            "Call emergency services immediately",
            "Take aspirin if not allergic",
            "Stay calm and rest",
            "Have someone stay with you",
            "Prepare for possible CPR",
        ],
        "medication": [
            "Take medication as prescribed",
            "Set reminder for next dose",
            "Do not skip doses",
            "Contact pharmacist for refills",
        ],
        "lifestyle": [
            "Practice stress management techniques",
            "Take a 10-minute walk",
            "Practice deep breathing",
            "Consider meditation or yoga",
        ],
        "ecg": [
            "Remain calm and still",
            "Check electrode connections",
            "Record episode duration",
            "Share ECG with cardiologist",
        ],
    }

    alert_type = alert.get("alert_type", "")
    recs = recommendations.get(alert_type, ["Monitor closely and consult doctor"])

    print("\n*** CARDIAC RECOMMENDATIONS ***")
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    alerts = asyncio.run(simulate_cardiac_alerts())

    if alerts:
        print("\n" + "="*60)
        print("DETAILED RECOMMENDATIONS")
        print("="*60)
        show_cardiac_recommendations(alerts[0])