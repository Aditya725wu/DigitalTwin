"""
Demo Alerts Script - Simulates real-time alerts for the DiabetesTwin system
This demonstrates the alert system functionality
"""

import asyncio
import random
from datetime import datetime
from typing import List, Dict
import json


# Alert templates for different scenarios
ALERT_TEMPLATES = {
    "glucose_spike": [
        "Predicted glucose spike in the next 2 hours - probability: {prob}%",
        "High glucose trend detected - consider medication adjustment",
        "Rapid glucose increase detected - take corrective action",
    ],
    "glucose_low": [
        "Low glucose warning - hypoglycemia risk detected",
        "Glucose below target range - consume fast-acting carbs",
        "Rapid glucose drop detected - immediate attention needed",
    ],
    "medication": [
        "Missed medication dose detected",
        "Medication adherence below 80% this week",
        "Refill reminder - medication supply running low",
    ],
    "cardiovascular": [
        "Elevated cardiovascular risk detected",
        "Abnormal heart rate pattern - monitor closely",
        "Blood pressure trending upward",
    ],
    "activity": [
        "Activity level below target for today",
        "Prolonged sedentary period detected",
        "Recommended: 30 minutes of moderate exercise",
    ],
    "sleep": [
        "Sleep quality below average last night",
        "Irregular sleep pattern detected",
        "Recovery sleep recommended after low glucose night",
    ],
}


def generate_alert(patient_id: str, alert_type: str = None) -> Dict:
    """Generate a single alert"""
    if alert_type is None:
        alert_type = random.choice(list(ALERT_TEMPLATES.keys()))

    templates = ALERT_TEMPLATES[alert_type]
    message = random.choice(templates)

    # Add probability for glucose alerts
    if "glucose" in alert_type:
        prob = random.randint(60, 95)
        message = message.replace("{prob}", str(prob))

    severity_weights = {
        "glucose_spike": ["MEDIUM", "HIGH", "HIGH"],
        "glucose_low": ["HIGH", "CRITICAL", "HIGH"],
        "medication": ["LOW", "MEDIUM", "MEDIUM"],
        "cardiovascular": ["MEDIUM", "HIGH", "MEDIUM"],
        "activity": ["LOW", "LOW", "MEDIUM"],
        "sleep": ["LOW", "MEDIUM", "LOW"],
    }

    severity = random.choice(severity_weights.get(alert_type, ["LOW", "MEDIUM"]))

    return {
        "alert_id": f"ALR{random.randint(100000, 999999)}",
        "patient_id": patient_id,
        "severity": severity,
        "alert_type": alert_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "acknowledged": False,
    }


def generate_patient_alerts(patient_id: str, count: int = 5) -> List[Dict]:
    """Generate multiple alerts for a patient"""
    alerts = []
    alert_types = list(ALERT_TEMPLATES.keys())

    for _ in range(count):
        alert_type = random.choice(alert_types)
        alert = generate_alert(patient_id, alert_type)
        alerts.append(alert)

    return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)


def display_alert(alert: Dict):
    """Display alert in console with formatting"""
    severity_colors = {
        "LOW": "\033[92m",      # Green
        "MEDIUM": "\033[93m",   # Yellow
        "HIGH": "\033[91m",     # Red
        "CRITICAL": "\033[95m", # Magenta
    }
    RESET = "\033[0m"

    color = severity_colors.get(alert["severity"], "\033[0m")

    print(f"\n{'='*60}")
    print(f"{color}[!] {alert['severity']} ALERT{RESET}")
    print(f"{'='*60}")
    print(f"Patient ID: {alert['patient_id']}")
    print(f"Alert ID: {alert['alert_id']}")
    print(f"Type: {alert['alert_type'].replace('_', ' ').title()}")
    print(f"Time: {alert['timestamp']}")
    print(f"\nMessage:")
    print(f"  {alert['message']}")
    print(f"\nAcknowledged: {'Yes' if alert['acknowledged'] else 'No'}")
    print(f"{'='*60}\n")


async def simulate_realtime_alerts():
    """Simulate real-time alerts arriving"""
    print("\n" + "="*60)
    print("DiabetesTwin Alert Simulation")
    print("="*60)
    print("Generating sample alerts...\n")

    # Generate sample patients
    patients = [f"PAT{str(i).zfill(6)}" for i in range(1, 6)]

    # Generate alerts for each patient
    all_alerts = []
    for patient_id in patients:
        patient_alerts = generate_patient_alerts(patient_id, random.randint(2, 5))
        all_alerts.extend(patient_alerts)

    # Sort by timestamp (newest first)
    all_alerts.sort(key=lambda x: x["timestamp"], reverse=True)

    # Display high severity alerts
    print("\n*** HIGH & CRITICAL ALERTS ***")
    print("-"*40)
    high_severity = [a for a in all_alerts if a["severity"] in ["HIGH", "CRITICAL"]]
    for alert in high_severity[:5]:
        display_alert(alert)

    # Summary
    print("\n" + "="*60)
    print("ALERT SUMMARY")
    print("="*60)

    severity_counts = {}
    for alert in all_alerts:
        severity = alert["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    for severity, count in sorted(severity_counts.items()):
        print(f"  {severity}: {count}")

    print(f"\nTotal Alerts: {len(all_alerts)}")
    print(f"Patients Monitored: {len(patients)}")
    print(f"Active (unacknowledged): {sum(1 for a in all_alerts if not a['acknowledged'])}")
    print("="*60)

    # Save to file
    with open("demo_alerts.json", "w") as f:
        json.dump(all_alerts, f, indent=2)
    print("\n[SUCCESS] Alerts saved to demo_alerts.json")

    return all_alerts


def show_recommendations(alert: Dict):
    """Show recommended actions based on alert"""
    recommendations = {
        "glucose_spike": [
            "Check blood glucose with finger stick",
            "Take corrective insulin if prescribed",
            "Drink water to help flush excess glucose",
            "Light exercise can help lower glucose",
            "Contact healthcare provider if above 300 mg/dL",
        ],
        "glucose_low": [
            "Consume 15-20g fast-acting carbohydrates",
            "Wait 15 minutes and recheck glucose",
            "Have a snack if next meal is more than 30 min away",
            "Avoid driving if glucose is below 70 mg/dL",
            "Consider glucagon emergency kit if severe",
        ],
        "medication": [
            "Take missed dose as soon as remembered",
            "Skip dose if it's close to next scheduled dose",
            "Never double dose without consulting doctor",
            "Set phone reminders for future doses",
        ],
        "cardiovascular": [
            "Rest and monitor heart rate",
            "Check blood pressure if available",
            "Avoid strenuous activity until resolved",
            "Consult cardiologist if persistent",
        ],
    }

    alert_type = alert.get("alert_type", "")
    recs = recommendations.get(alert_type, ["Monitor closely"])

    print("\n*** RECOMMENDED ACTIONS ***")
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    # Run the alert simulation
    alerts = asyncio.run(simulate_realtime_alerts())

    # Show detailed recommendations for first alert
    if alerts:
        print("\n" + "="*60)
        print("DETAILED RECOMMENDATIONS")
        print("="*60)
        show_recommendations(alerts[0])