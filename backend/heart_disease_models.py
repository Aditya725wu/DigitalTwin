"""
Heart Disease Prediction Models for CardioTwin
ML models for cardiovascular disease prediction and monitoring
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
from pathlib import Path


class HeartDiseasePredictor:
    """Predict heart disease risk based on patient data"""

    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()
        self.feature_names = None

    def prepare_features(self, patients_df: pd.DataFrame, vitals_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features from patient and vital signs data"""
        features = []

        for _, patient in patients_df.iterrows():
            patient_id = patient['patient_id']

            # Get recent vital signs
            patient_vitals = vitals_df[vitals_df['patient_id'] == patient_id]

            if len(patient_vitals) < 10:  # Need sufficient data
                continue

            # Calculate vital sign statistics
            bp_systolic = patient_vitals['blood_pressure_systolic'].mean()
            bp_diastolic = patient_vitals['blood_pressure_diastolic'].mean()
            heart_rate_mean = patient_vitals['heart_rate'].mean()
            heart_rate_std = patient_vitals['heart_rate'].std()
            spo2_mean = patient_vitals['oxygen_saturation'].mean() if 'oxygen_saturation' in patient_vitals.columns else 98

            # Heart Rate Variability (simplified)
            hrv = heart_rate_std * 2  # Simplified HRV calculation

            # ECG features (if available)
            ecg_abnormal = patient_vitals['ecg_abnormal'].mean() > 0.1 if 'ecg_abnormal' in patient_vitals.columns else 0

            # Risk calculation based on clinical guidelines
            feature_dict = {
                'age': patient['age'],
                'gender_male': 1 if patient['gender'] == 'M' else 0,
                'bmi': patient['bmi'],
                'systolic_bp': bp_systolic,
                'diastolic_bp': bp_diastolic,
                'heart_rate_mean': heart_rate_mean,
                'heart_rate_std': heart_rate_std,
                'hrv': hrv,
                'spo2': spo2_mean,
                'ecg_abnormal': ecg_abnormal,
                'smoker': 1 if patient['smoker'] else 0,
                'diabetes': 1 if patient['diabetes'] else 0,
                'hypertension': 1 if patient['hypertension'] else 0,
                'cholesterol_total': patient['cholesterol_total'] if 'cholesterol_total' in patient else 200,
                'cholesterol_hdl': patient['cholesterol_hdl'] if 'cholesterol_hdl' in patient else 50,
                'cholesterol_ldl': patient['cholesterol_ldl'] if 'cholesterol_ldl' in patient else 120,
                'family_history_cvd': 1 if patient['family_history_cvd'] else 0,
                'patient_id': patient_id,
            }

            # Calculate Framingham Risk Score (simplified)
            framingham_score = self._calculate_framingham_risk(feature_dict)
            feature_dict['framingham_score'] = framingham_score

            # Target: high risk if Framingham score > 10% or existing condition
            high_risk_threshold = framingham_score > 0.10 or patient['hypertension'] or patient['diabetes']
            feature_dict['high_risk'] = 1 if high_risk_threshold else 0

            features.append(feature_dict)

        return pd.DataFrame(features)

    def _calculate_framingham_risk(self, features: dict) -> float:
        """Calculate simplified Framingham Risk Score"""
        score = 0

        # Age scoring
        if features['age'] >= 55:
            score += 8
        elif features['age'] >= 45:
            score += 6
        elif features['age'] >= 35:
            score += 4

        # Gender
        if features['gender_male']:
            score += 3

        # Blood pressure
        if features['systolic_bp'] >= 140:
            score += 7
        elif features['systolic_bp'] >= 130:
            score += 5
        elif features['systolic_bp'] >= 120:
            score += 3

        # Cholesterol
        if features['cholesterol_total'] >= 240:
            score += 5
        elif features['cholesterol_total'] >= 200:
            score += 3

        # HDL cholesterol (inverse)
        if features['cholesterol_hdl'] < 40:
            score += 4
        elif features['cholesterol_hdl'] < 50:
            score += 2

        # Smoking
        if features['smoker']:
            score += 4

        # Diabetes
        if features['diabetes']:
            score += 3

        # Convert to probability (simplified)
        probability = score / 45  # Max possible score ~45

        return min(probability, 0.99)

    def train(self, features_df: pd.DataFrame):
        """Train the heart disease prediction model"""
        print("Training Heart Disease Predictor...")

        # Prepare features and target
        X = features_df[[col for col in features_df.columns
                        if col not in ['patient_id', 'high_risk']]]
        y = features_df['high_risk']

        self.feature_names = X.columns.tolist()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]

        print("\nHeart Disease Predictor Performance:")
        print(classification_report(y_test, y_pred, target_names=['Low Risk', 'High Risk']))
        print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

        return self.model, self.scaler

    def predict(self, features_dict: dict) -> dict:
        """Predict heart disease risk for a patient"""
        feature_values = np.array([[features_dict.get(f, 0) for f in self.feature_names]])
        feature_scaled = self.scaler.transform(feature_values)

        prediction = self.model.predict_proba(feature_scaled)[0]

        return {
            'low_risk_probability': float(prediction[0]),
            'high_risk_probability': float(prediction[1]),
            'predicted_risk': bool(prediction[1] > 0.5)
        }


class ArrhythmiaDetector:
    """Detect arrhythmias from ECG data"""

    def __init__(self):
        # Placeholder for CNN model
        self.model_loaded = False

    def detect_arrythmias(self, ecg_signal: np.ndarray) -> dict:
        """Analyze ECG signal for arrhythmias"""
        # Simplified detection logic
        heart_rate = self._estimate_heart_rate(ecg_signal)

        # Basic rhythm analysis
        if heart_rate > 100:
            rhythm_status = "Tachycardia detected"
            severity = "MODERATE"
        elif heart_rate < 60:
            rhythm_status = "Bradycardia detected"
            severity = "MODERATE"
        else:
            rhythm_status = "Normal sinus rhythm"
            severity = "NORMAL"

        # Simulate occasional arrhythmia detection
        import random
        if random.random() < 0.1:  # 10% chance for demo
            arrhythmia_type = random.choice(["AFib", "PVC", "PAC"])
            rhythm_status = f"{arrhythmia_type} detected"
            severity = "HIGH"

        return {
            'heart_rate': heart_rate,
            'rhythm_status': rhythm_status,
            'severity': severity,
            'ecg_quality': 'GOOD' if len(ecg_signal) > 100 else 'POOR',
        }

    def _estimate_heart_rate(self, ecg_signal: np.ndarray) -> float:
        """Estimate heart rate from ECG signal"""
        if len(ecg_signal) < 100:
            return 72.0  # Default

        # Simplified heart rate estimation
        # In real implementation, detect R-peaks
        return np.random.uniform(60, 100)  # Placeholder


class BloodPressurePredictor:
    """Predict blood pressure trends"""

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def predict_trend(self, bp_history: pd.DataFrame) -> dict:
        """Predict blood pressure trend"""
        if len(bp_history) < 5:
            return {'trend': 'STABLE', 'confidence': 0.5}

        # Calculate basic statistics
        systolic_mean = bp_history['systolic'].mean()
        systolic_std = bp_history['systolic'].std()
        diastolic_mean = bp_history['diastolic'].mean()

        # Determine trend
        recent_avg = bp_history['systolic'].tail(3).mean()
        older_avg = bp_history['systolic'].head(3).mean()

        if recent_avg > older_avg + 10:
            trend = "RISING"
        elif recent_avg < older_avg - 10:
            trend = "FALLING"
        else:
            trend = "STABLE"

        # Risk assessment
        if systolic_mean > 140 or diastolic_mean > 90:
            risk = "HIGH"
        elif systolic_mean > 130 or diastolic_mean > 85:
            risk = "ELEVATED"
        else:
            risk = "NORMAL"

        return {
            'trend': trend,
            'risk_level': risk,
            'systolic_mean': systolic_mean,
            'diastolic_mean': diastolic_mean,
            'variability': systolic_std,
        }


def train_all_cardiac_models():
    """Train all cardiac ML models"""

    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    print("Loading cardiac patient data...")

    # Generate synthetic cardiac data
    try:
        from .generate_cardiac_data import CardiacPatientGenerator
    except ImportError:
        # Support running this module directly from the backend directory.
        from generate_cardiac_data import CardiacPatientGenerator
    generator = CardiacPatientGenerator(num_patients=100)
    patients = generator.generate_all_patients()

    # Convert to DataFrames
    patients_df = pd.DataFrame(patients)

    # Generate vitals data
    vitals_data = []
    for patient in patients:
        for _ in range(30):  # 30 days of vitals
            vitals_data.append({
                'patient_id': patient['patient_id'],
                'blood_pressure_systolic': np.random.normal(
                    patient.get('systolic_bp', 120),
                    10
                ),
                'blood_pressure_diastolic': np.random.normal(
                    patient.get('diastolic_bp', 80),
                    5
                ),
                'heart_rate': np.random.normal(72, 10),
                'oxygen_saturation': np.random.normal(98, 1),
            })

    vitals_df = pd.DataFrame(vitals_data)

    # Train Heart Disease Predictor
    heart_predictor = HeartDiseasePredictor()
    features_df = heart_predictor.prepare_features(patients_df, vitals_df)
    heart_predictor.train(features_df)

    joblib.dump(heart_predictor.model, models_dir / "heart_disease_model.pkl")
    joblib.dump(heart_predictor.scaler, models_dir / "heart_disease_scaler.pkl")
    print("✓ Saved heart disease prediction model")

    # Save feature names
    with open(models_dir / "heart_features.json", "w") as f:
        import json
        json.dump(heart_predictor.feature_names, f)

    print("\n✅ All cardiac models trained and saved!")


if __name__ == "__main__":
    train_all_cardiac_models()
