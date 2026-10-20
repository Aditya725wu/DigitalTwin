"""
Cardiac Data Generation for CardioTwin
Generates realistic cardiovascular patient data
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()


class CardiacPatientGenerator:
    """Generate synthetic cardiac patient data"""

    def __init__(self, num_patients: int = 100):
        self.num_patients = num_patients

    def generate_ehr(self) -> dict:
        """Generate cardiac-specific Electronic Health Record"""
        patient_id = fake.uuid4()
        age = random.randint(35, 85)
        gender = random.choice(['M', 'F'])

        # Cardiovascular risk factors
        bmi = random.gauss(26, 4)  # Average BMI for cardiac patients
        systolic_bp = random.gauss(135, 20) if random.random() > 0.4 else random.gauss(120, 10)
        diastolic_bp = random.gauss(85, 12) if random.random() > 0.4 else random.gauss(80, 8)

        # Cholesterol levels
        total_cholesterol = random.gauss(210, 40)
        hdl = random.gauss(45, 15)
        ldl = random.gauss(130, 35)

        return {
            "patient_id": patient_id,
            "age": max(18, age),
            "gender": gender,
            "bmi": round(max(18, bmi), 1),
            "height_cm": random.randint(150, 200),
            "weight_kg": random.randint(50, 120),
            "family_history_cvd": random.choice([True, False]),
            "family_history_hypertension": random.choice([True, False]),
            "smoker": random.choice([True, False]),
            "diabetes": random.choice([True, False]),
            "hypertension": random.choice([True, False]),
            "previous_cardiac_event": random.choice([True, False]),
            "blood_pressure": {
                "systolic": round(systolic_bp),
                "diastolic": round(diastolic_bp),
            },
            "cholesterol": {
                "total": round(total_cholesterol),
                "hdl": round(hdl),
                "ldl": round(ldl),
                "triglycerides": random.randint(80, 400),
            },
            "medications": self._generate_cardiac_medications(),
            "allergies": self._generate_allergies(),
            "comorbidities": self._generate_comorbidities(),
            "lab_results": {
                "creatinine": round(random.gauss(1.0, 0.3), 2),
                "gfr": random.randint(60, 120),
                "fasting_blood_sugar": random.randint(80, 180),
                "hba1c": round(random.gauss(6.5, 1.5), 1),
            },
            "lifestyle": {
                "physical_activity": random.choice(["Sedentary", "Light", "Moderate", "Active"]),
                "alcohol_consumption": random.choice(["None", "Occasional", "Moderate", "Heavy"]),
                "stress_level": random.randint(1, 10),
            },
            "last_cardiac_checkup": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
            "enrollment_date": datetime.now().isoformat(),
        }

    def _generate_cardiac_medications(self) -> list:
        """Generate cardiac medication list"""
        medications = []

        common_meds = [
            {"name": "Aspirin", "dosage": "81mg", "frequency": "daily", "type": "Antiplatelet"},
            {"name": "Atorvastatin", "dosage": "20mg", "frequency": "daily", "type": "Statin"},
            {"name": "Lisinopril", "dosage": "10mg", "frequency": "daily", "type": "ACE Inhibitor"},
            {"name": "Metoprolol", "dosage": "25mg", "frequency": "twice daily", "type": "Beta Blocker"},
            {"name": "Amlodipine", "dosage": "5mg", "frequency": "daily", "type": "Calcium Channel Blocker"},
        ]

        # Add medications based on conditions
        if random.random() > 0.5:
            medications.append(random.choice(common_meds))
        if random.random() > 0.6:
            medications.append(random.choice(common_meds))

        return medications if medications else [{"name": "None", "dosage": "", "frequency": "", "type": "None"}]

    def _generate_allergies(self) -> list:
        """Generate allergy information for cardiac patients"""
        common_allergies = ["Aspirin", "Penicillin", "Statins", "None"]
        if random.random() > 0.8:
            return [random.choice(common_allergies)]
        return ["None"]

    def _generate_comorbidities(self) -> list:
        """Generate cardiac comorbidities"""
        comorbidities = []
        common_comorbidities = [
            "Hypertension", "Hyperlipidemia", "Diabetes",
            "Obesity", "Chronic Kidney Disease", "COPD",
            "Sleep Apnea", "Atrial Fibrillation"
        ]

        num_comorbidities = random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.3, 0.1])[0]

        for _ in range(num_comorbidities):
            comorbidity = random.choice(common_comorbidities)
            if comorbidity not in comorbidities:
                comorbidities.append(comorbidity)

        return comorbidities if comorbidities else ["None"]

    def generate_all_patients(self) -> list:
        """Generate all synthetic cardiac patients"""
        patients = []
        for _ in range(self.num_patients):
            patients.append(self.generate_ehr())
        return patients


class CardiacVitalsGenerator:
    """Generate realistic cardiac vital signs time-series data"""

    def generate_blood_pressure_data(self, patient_id: str, baseline_systolic: float = 120) -> list:
        """Generate blood pressure readings over time"""
        data = []
        current_systolic = baseline_systolic

        for day in range(30):  # 30 days of data
            # Daily pattern: higher in morning, dip at night
            morning_systolic = current_systolic + random.gauss(5, 3)
            evening_systolic = current_systolic + random.gauss(-5, 3)

            # Add some variation
            morning_diastolic = morning_systolic * 0.6 + random.gauss(0, 2)
            evening_diastolic = evening_systolic * 0.6 + random.gauss(0, 2)

            data.append({
                "timestamp": (datetime.now() - timedelta(days=30-day, hours=8)).isoformat(),
                "blood_pressure_systolic": round(morning_systolic),
                "blood_pressure_diastolic": round(morning_diastolic),
                "patient_id": patient_id,
                "reading_type": "morning",
            })

            data.append({
                "timestamp": (datetime.now() - timedelta(days=30-day, hours=20)).isoformat(),
                "blood_pressure_systolic": round(evening_systolic),
                "blood_pressure_diastolic": round(evening_diastolic),
                "patient_id": patient_id,
                "reading_type": "evening",
            })

            # Gradual trend
            if random.random() > 0.7:
                current_systolic += random.gauss(0, 2)

        return data

    def generate_heart_rate_data(self, patient_id: str) -> list:
        """Generate heart rate and HRV data"""
        data = []
        base_hr = random.randint(60, 80)

        for hour in range(24 * 30):  # 24 hours * 30 days
            # Normal daily variation
            hour_factor = 15 * np.sin(hour * np.pi / 12) + random.gauss(0, 3)
            hr = base_hr + hour_factor

            # Simulate activity spikes
            if hour % 24 in [7, 12, 18]:  # Meal times
                hr += random.gauss(10, 5)

            # Add occasional arrhythmias
            hr = self._add_occasional_arrythmia(hr, hour)

            data.append({
                "timestamp": (datetime.now() - timedelta(hours=24*30-hour)).isoformat(),
                "heart_rate_bpm": int(max(40, min(180, hr))),
                "heart_rate_variability": round(random.gauss(50, 15)),
                "patient_id": patient_id,
                "source": "wearable",
            })

        return data

    def _add_occasional_arrythmia(self, hr: float, hour: int) -> float:
        """Simulate occasional arrhythmias"""
        if hour % 100 == 0:  # Every ~100 hours
            arrhythmia_type = random.choice(["tachycardia", "bradycardia", "afib"])

            if arrhythmia_type == "tachycardia":
                return hr + random.uniform(30, 60)
            elif arrhythmia_type == "bradycardia":
                return hr - random.uniform(20, 40)
            elif arrhythmia_type == "afib":
                return hr + random.uniform(-20, 40)  # Irregular

        return hr

    def generate_ecg_data(self, patient_id: str) -> list:
        """Generate simulated ECG data (simplified)"""
        data = []

        for day in range(30):
            ecg_quality = random.choice(["GOOD", "FAIR", "POOR"])
            rhythm = "Normal"

            # Occasional abnormal rhythms
            if random.random() < 0.05:  # 5% chance of abnormality
                rhythm = random.choice(["AFib", "PVC", "ST Elevation", "T Wave Inversion"])

            data.append({
                "timestamp": (datetime.now() - timedelta(days=30-day)).isoformat(),
                "ecg_quality": ecg_quality,
                "rhythm": rhythm,
                "heart_rate": random.randint(60, 100),
                "patient_id": patient_id,
                "source": "ecg_monitor",
            })

        return data

    def generate_oxygen_saturation_data(self, patient_id: str) -> list:
        """Generate SpO2 data"""
        data = []

        for day in range(30):
            spo2 = random.gauss(97, 1.5)

            data.append({
                "timestamp": (datetime.now() - timedelta(days=30-day)).isoformat(),
                "oxygen_saturation": round(spo2, 1),
                "patient_id": patient_id,
                "source": "pulse_oximeter",
            })

        return data


def generate_all_cardiac_data(num_patients: int = 50):
    """Generate complete cardiac dataset"""

    data_dir = Path("data/cardiac")
    data_dir.mkdir(exist_ok=True, parents=True)

    print(f"Generating {num_patients} cardiac patients...")

    # Generate patient EHR data
    patient_generator = CardiacPatientGenerator(num_patients)
    patients = patient_generator.generate_all_patients()

    with open(data_dir / "cardiac_patients_ehr.json", "w") as f:
        json.dump(patients, f, indent=2)
    print(f"✓ Generated {num_patients} cardiac patient EHR records")

    # Generate vitals data
    vitals_generator = CardiacVitalsGenerator()

    all_bp_data = []
    all_hr_data = []
    all_ecg_data = []
    all_spo2_data = []

    for patient in patients:
        patient_id = patient["patient_id"]
        baseline_systolic = patient["blood_pressure"]["systolic"]

        # Blood pressure data
        bp_data = vitals_generator.generate_blood_pressure_data(patient_id, baseline_systolic)
        all_bp_data.extend(bp_data)

        # Heart rate data
        hr_data = vitals_generator.generate_heart_rate_data(patient_id)
        all_hr_data.extend(hr_data)

        # ECG data
        ecg_data = vitals_generator.generate_ecg_data(patient_id)
        all_ecg_data.extend(ecg_data)

        # SpO2 data
        spo2_data = vitals_generator.generate_oxygen_saturation_data(patient_id)
        all_spo2_data.extend(spo2_data)

    # Save all data
    pd.DataFrame(all_bp_data).to_csv(data_dir / "blood_pressure_readings.csv", index=False)
    print(f"✓ Generated {len(all_bp_data)} blood pressure readings")

    pd.DataFrame(all_hr_data).to_csv(data_dir / "heart_rate_readings.csv", index=False)
    print(f"✓ Generated {len(all_hr_data)} heart rate readings")

    pd.DataFrame(all_ecg_data).to_csv(data_dir / "ecg_readings.csv", index=False)
    print(f"✓ Generated {len(all_ecg_data)} ECG readings")

    pd.DataFrame(all_spo2_data).to_csv(data_dir / "oxygen_saturation.csv", index=False)
    print(f"✓ Generated {len(all_spo2_data)} oxygen saturation readings")

    print("\n✅ Cardiac data generation complete!")
    print(f"Data saved to: {data_dir.absolute()}")

    return patients, all_bp_data, all_hr_data, all_ecg_data, all_spo2_data


if __name__ == "__main__":
    generate_all_cardiac_data(num_patients=50)