"""
Synthetic Data Generation for DiabetesTwin
Generates realistic patient data for Type 2 Diabetes simulation
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()


class SyntheticPatientGenerator:
    """Generate synthetic patient Electronic Health Records"""

    def __init__(self, num_patients: int = 100):
        self.num_patients = num_patients
        self.patients = []

    def generate_ehr(self) -> dict:
        """Generate a synthetic Electronic Health Record"""
        patient_id = fake.uuid4()
        age = random.randint(35, 75)
        gender = random.choice(['M', 'F'])

        # Diabetes risk factors
        bmi = random.gauss(27, 5)  # Average BMI for diabetes patients
        family_history = random.choice([True, False])

        # Lab results
        hba1c = random.gauss(7.5, 1.2) if random.random() > 0.3 else random.gauss(6.2, 0.8)
        fasting_glucose = random.gauss(130, 25)

        return {
            "patient_id": patient_id,
            "age": max(18, age),
            "gender": gender,
            "bmi": round(max(15, bmi), 1),
            "height_cm": random.randint(150, 200),
            "weight_kg": random.randint(50, 150),
            "family_history_diabetes": family_history,
            "family_history_hypertension": random.choice([True, False]),
            "smoker": random.choice([True, False]),
            "medications": self._generate_medications(),
            "allergies": self._generate_allergies(),
            "comorbidities": self._generate_comorbidities(),
            "lab_results": {
                "hba1c": round(hba1c, 1),
                "fasting_glucose": round(fasting_glucose, 1),
                "total_cholesterol": random.randint(120, 300),
                "ldl": random.randint(50, 200),
                "hdl": random.randint(20, 100),
                "triglycerides": random.randint(50, 400),
                "creatinine": round(random.gauss(1.0, 0.3), 2),
                "gfr": random.randint(60, 120),
            },
            "last_checkup": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
            "enrollment_date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
        }

    def _generate_medications(self) -> list:
        """Generate medication list"""
        medications = [
            {"name": "Metformin", "dosage": f"{random.choice([500, 1000, 1500])}mg", "frequency": "daily"},
        ]

        if random.random() > 0.4:
            medications.append({
                "name": random.choice(["Glipizide", "Sitagliptin", "Dulaglutide"]),
                "dosage": f"{random.randint(1, 100)}mg",
                "frequency": "daily"
            })

        return medications

    def _generate_allergies(self) -> list:
        """Generate allergy information"""
        common_allergies = ["Penicillin", "Sulfonamides", "None"]
        if random.random() > 0.8:
            return [random.choice(common_allergies)]
        return ["None"]

    def _generate_comorbidities(self) -> list:
        """Generate comorbidities"""
        comorbidities = []
        if random.random() > 0.6:
            comorbidities.append("Hypertension")
        if random.random() > 0.7:
            comorbidities.append("Hyperlipidemia")
        if random.random() > 0.8:
            comorbidities.append("Obesity")
        return comorbidities if comorbidities else ["None"]

    def generate_all_patients(self) -> list:
        """Generate all synthetic patients"""
        patients = []
        for _ in range(self.num_patients):
            patients.append(self.generate_ehr())
        return patients


class SyntheticSensorDataGenerator:
    """Generate realistic wearable sensor time-series data"""

    def __init__(self, num_samples_per_patient: int = 1440):  # 1 day of data (1 min intervals)
        self.num_samples_per_patient = num_samples_per_patient

    def generate_cgm_data(self, patient_id: str, baseline_glucose: float = 130) -> list:
        """
        Generate Continuous Glucose Monitoring data
        Simulates realistic glucose patterns over 24 hours
        """
        data = []
        current_glucose = baseline_glucose

        for hour in range(24):
            # Simulate glucose variation throughout day
            # Lower in morning, rise after meals, peak at night
            hour_factor = np.sin(hour * np.pi / 12) * 30 + 20

            # Add meal-related spikes
            if hour in [7, 12, 18]:  # Breakfast, lunch, dinner times
                hour_factor += random.gauss(40, 10)

            # Generate minute-level readings
            for minute in range(60):
                noise = random.gauss(0, 3)
                glucose = current_glucose + hour_factor + noise
                glucose = max(40, min(400, glucose))  # Keep in realistic range

                data.append({
                    "timestamp": (datetime.now() - timedelta(hours=24-hour, minutes=60-minute)).isoformat(),
                    "glucose_mg_dl": round(glucose, 1),
                    "patient_id": patient_id,
                    "source": "CGM"
                })

            current_glucose = baseline_glucose + hour_factor

        return data

    def generate_heart_rate_data(self, patient_id: str) -> list:
        """Generate heart rate variability data"""
        data = []
        base_hr = random.randint(60, 85)

        for hour in range(24):
            hour_factor = 10 * np.sin(hour * np.pi / 12)

            for minute in range(60):
                noise = random.gauss(0, 2)
                hr = base_hr + hour_factor + noise + (10 if random.random() > 0.95 else 0)  # Activity spikes
                hr = max(40, min(180, hr))

                data.append({
                    "timestamp": (datetime.now() - timedelta(hours=24-hour, minutes=60-minute)).isoformat(),
                    "heart_rate_bpm": round(hr),
                    "heart_rate_variability": round(random.gauss(50, 15)),
                    "patient_id": patient_id,
                    "source": "Wearable"
                })

        return data

    def generate_activity_data(self, patient_id: str) -> list:
        """Generate physical activity data"""
        data = []

        for hour in range(24):
            # Activity pattern: low at night, increase during day, peak in evening
            activity_level = max(0, 30 * np.sin(hour * np.pi / 12) + random.gauss(20, 10))

            for minute in range(0, 60, 5):  # 5-minute intervals
                data.append({
                    "timestamp": (datetime.now() - timedelta(hours=24-hour, minutes=60-minute)).isoformat(),
                    "steps": int(activity_level * random.uniform(0.8, 1.2)),
                    "calories_burned": round(activity_level * random.uniform(0.5, 1.5), 1),
                    "active_minutes": int(activity_level / 10),
                    "patient_id": patient_id,
                    "source": "Wearable"
                })

        return data

    def generate_sleep_data(self, patient_id: str) -> dict:
        """Generate sleep quality data"""
        return {
            "patient_id": patient_id,
            "sleep_duration_hours": round(random.gauss(7, 1.5), 1),
            "sleep_quality_score": round(random.gauss(7, 1.5)),  # 1-10
            "deep_sleep_percentage": random.randint(10, 30),
            "rem_sleep_percentage": random.randint(20, 35),
            "light_sleep_percentage": random.randint(30, 60),
            "sleep_efficiency": round(random.gauss(0.85, 0.1), 2),
            "timestamp": datetime.now().isoformat(),
            "source": "Wearable"
        }


def generate_all_synthetic_data(num_patients: int = 50):
    """Generate complete synthetic dataset"""

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    print(f"Generating {num_patients} synthetic patients...")

    # Generate EHR data
    ehr_generator = SyntheticPatientGenerator(num_patients)
    patients = ehr_generator.generate_all_patients()

    with open(data_dir / "patients_ehr.json", "w") as f:
        json.dump(patients, f, indent=2)
    print(f"✓ Generated {num_patients} patient EHR records")

    # Generate sensor data
    sensor_generator = SyntheticSensorDataGenerator()
    all_cgm_data = []
    all_hr_data = []
    all_activity_data = []
    all_sleep_data = []

    for patient in patients:
        patient_id = patient["patient_id"]
        baseline_glucose = patient["lab_results"]["fasting_glucose"]

        # CGM data
        cgm_data = sensor_generator.generate_cgm_data(patient_id, baseline_glucose)
        all_cgm_data.extend(cgm_data)

        # Heart rate data
        hr_data = sensor_generator.generate_heart_rate_data(patient_id)
        all_hr_data.extend(hr_data)

        # Activity data
        activity_data = sensor_generator.generate_activity_data(patient_id)
        all_activity_data.extend(activity_data)

        # Sleep data
        sleep_data = sensor_generator.generate_sleep_data(patient_id)
        all_sleep_data.append(sleep_data)

    # Save sensor data
    pd.DataFrame(all_cgm_data).to_csv(data_dir / "cgm_readings.csv", index=False)
    print(f"✓ Generated {len(all_cgm_data)} CGM readings")

    pd.DataFrame(all_hr_data).to_csv(data_dir / "heart_rate_readings.csv", index=False)
    print(f"✓ Generated {len(all_hr_data)} heart rate readings")

    pd.DataFrame(all_activity_data).to_csv(data_dir / "activity_data.csv", index=False)
    print(f"✓ Generated {len(all_activity_data)} activity records")

    pd.DataFrame(all_sleep_data).to_csv(data_dir / "sleep_data.csv", index=False)
    print(f"✓ Generated {len(all_sleep_data)} sleep records")

    print("\n✅ Synthetic data generation complete!")
    print(f"Data saved to: {data_dir.absolute()}")


if __name__ == "__main__":
    generate_all_synthetic_data(num_patients=50)
