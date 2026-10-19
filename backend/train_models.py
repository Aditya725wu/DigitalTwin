"""
ML Model Training for DiabetesTwin
Trains predictive models for glucose spike prediction and risk assessment
"""

import json
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib


class GlucoseSpikePredictor:
    """Train model to predict glucose spikes in next 2 hours"""

    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_names = None

    def prepare_features(self, cgm_df: pd.DataFrame, hr_df: pd.DataFrame, activity_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features from sensor data"""
        features = []

        for patient_id in cgm_df['patient_id'].unique():
            patient_cgm = cgm_df[cgm_df['patient_id'] == patient_id].sort_values('timestamp')
            patient_hr = hr_df[hr_df['patient_id'] == patient_id].sort_values('timestamp')
            patient_activity = activity_df[activity_df['patient_id'] == patient_id].sort_values('timestamp')

            if len(patient_cgm) < 120:  # Need at least 2 hours of data
                continue

            # Create sliding windows
            for i in range(120, len(patient_cgm)):
                # Last 2 hours of glucose data
                glucose_window = patient_cgm.iloc[i-120:i]['glucose_mg_dl'].values

                # Calculate glucose features
                glucose_trend = glucose_window[-1] - glucose_window[0]
                glucose_std = np.std(glucose_window)
                glucose_mean = np.mean(glucose_window)
                glucose_max = np.max(glucose_window)
                glucose_min = np.min(glucose_window)
                glucose_velocity = np.mean(np.diff(glucose_window))

                # Heart rate features (if available)
                if len(patient_hr) > i:
                    hr_window = patient_hr.iloc[max(0, i-60):i]['heart_rate_bpm'].values
                    hr_mean = np.mean(hr_window) if len(hr_window) > 0 else 70
                else:
                    hr_mean = 70

                # Activity features
                if len(patient_activity) > i:
                    activity_window = patient_activity.iloc[max(0, i-60):i]['steps'].values
                    activity_total = np.sum(activity_window) if len(activity_window) > 0 else 0
                else:
                    activity_total = 0

                # Create feature vector
                feature_dict = {
                    'glucose_trend': glucose_trend,
                    'glucose_std': glucose_std,
                    'glucose_mean': glucose_mean,
                    'glucose_max': glucose_max,
                    'glucose_min': glucose_min,
                    'glucose_velocity': glucose_velocity,
                    'hr_mean': hr_mean,
                    'activity_total': activity_total,
                    'patient_id': patient_id,
                    'timestamp': patient_cgm.iloc[i]['timestamp'],
                }

                # Create target (1 if spike in next 60 minutes, 0 otherwise)
                if i + 60 < len(patient_cgm):
                    next_glucose = patient_cgm.iloc[i:i+60]['glucose_mg_dl'].max()
                    target = 1 if next_glucose > 180 else 0
                    feature_dict['spike_target'] = target
                    features.append(feature_dict)

        return pd.DataFrame(features)

    def train(self, features_df: pd.DataFrame):
        """Train the model"""
        print("Training Glucose Spike Predictor...")

        # Prepare data
        X = features_df[[col for col in features_df.columns if col not in ['patient_id', 'timestamp', 'spike_target']]]
        y = features_df['spike_target']

        self.feature_names = X.columns.tolist()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]

        print("\nGlucose Spike Predictor Performance:")
        print(classification_report(y_test, y_pred, target_names=['No Spike', 'Spike']))
        print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

        return self.model, self.scaler

    def predict(self, features_dict: dict) -> dict:
        """Predict glucose spike probability"""
        feature_values = np.array([[features_dict.get(f, 0) for f in self.feature_names]])
        feature_scaled = self.scaler.transform(feature_values)

        prediction = self.model.predict_proba(feature_scaled)[0]

        return {
            'no_spike_probability': float(prediction[0]),
            'spike_probability': float(prediction[1]),
            'predicted_spike': bool(prediction[1] > 0.5)
        }


class CardiovascularRiskModel:
    """Predict cardiovascular risk based on diabetes complications"""

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()

    def prepare_features(self, patients_df: pd.DataFrame, hr_df: pd.DataFrame, sleep_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare cardiovascular risk features"""
        features = []

        for _, patient in patients_df.iterrows():
            patient_id = patient['patient_id']

            # Get recent sensor data
            patient_hr = hr_df[hr_df['patient_id'] == patient_id]
            patient_sleep = sleep_df[sleep_df['patient_id'] == patient_id]

            hr_mean = patient_hr['heart_rate_bpm'].mean() if len(patient_hr) > 0 else 70
            hr_std = patient_hr['heart_rate_bpm'].std() if len(patient_hr) > 0 else 10

            sleep_quality = patient_sleep['sleep_quality_score'].mean() if len(patient_sleep) > 0 else 7

            # Calculate risk
            feature_dict = {
                'age': patient['age'],
                'bmi': patient['bmi'],
                'hba1c': patient['lab_results']['hba1c'],
                'ldl': patient['lab_results']['ldl'],
                'hdl': patient['lab_results']['hdl'],
                'systolic_bp': random.randint(120, 160),  # Simulated for now
                'hr_mean': hr_mean,
                'hr_std': hr_std,
                'sleep_quality': sleep_quality,
                'smoker': patient['smoker'],
                'patient_id': patient_id,
            }

            # Risk target (simplified)
            risk_score = (patient['age'] > 60) * 0.2 + (patient['bmi'] > 30) * 0.2 + \
                        (patient['lab_results']['hba1c'] > 8) * 0.3 + (sleep_quality < 5) * 0.2

            feature_dict['high_risk'] = int(risk_score > 0.5)
            features.append(feature_dict)

        return pd.DataFrame(features)

    def train(self, features_df: pd.DataFrame):
        """Train cardiovascular risk model"""
        print("Training Cardiovascular Risk Model...")

        X = features_df[[col for col in features_df.columns if col not in ['patient_id', 'high_risk']]]
        y = features_df['high_risk']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model.fit(X_train_scaled, y_train)

        y_pred = self.model.predict(X_test_scaled)

        print("\nCardiovascular Risk Model Performance:")
        print(classification_report(y_test, y_pred, target_names=['Low Risk', 'High Risk']))


def train_all_models():
    """Train all ML models and save them"""

    data_dir = Path("data")
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    # Load synthetic data
    print("Loading synthetic data...")

    with open(data_dir / "patients_ehr.json", "r") as f:
        patients_data = json.load(f)

    patients_df = pd.DataFrame(patients_data)
    cgm_df = pd.read_csv(data_dir / "cgm_readings.csv")
    hr_df = pd.read_csv(data_dir / "heart_rate_readings.csv")
    activity_df = pd.read_csv(data_dir / "activity_data.csv")
    sleep_df = pd.read_csv(data_dir / "sleep_data.csv")

    # Train Glucose Spike Predictor
    glucose_predictor = GlucoseSpikePredictor()
    features_df = glucose_predictor.prepare_features(cgm_df, hr_df, activity_df)
    glucose_predictor.train(features_df)

    joblib.dump(glucose_predictor.model, models_dir / "glucose_spike_model.pkl")
    joblib.dump(glucose_predictor.scaler, models_dir / "glucose_spike_scaler.pkl")
    print("✓ Saved glucose spike model")

    # Train Cardiovascular Risk Model
    cv_model = CardiovascularRiskModel()
    cv_features_df = cv_model.prepare_features(patients_df, hr_df, sleep_df)
    cv_model.train(cv_features_df)

    joblib.dump(cv_model.model, models_dir / "cv_risk_model.pkl")
    joblib.dump(cv_model.scaler, models_dir / "cv_risk_scaler.pkl")
    print("✓ Saved cardiovascular risk model")

    print("\n✅ All models trained and saved!")


if __name__ == "__main__":
    import random
    train_all_models()
