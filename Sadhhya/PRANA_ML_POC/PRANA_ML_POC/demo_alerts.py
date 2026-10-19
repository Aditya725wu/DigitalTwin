
"""PRANA controlled what-if demo.
Tests simulated baseline deviations; not heart-attack prediction.
"""
from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path("models/deviation_model.joblib")

FEATURES = [
    "heart_rate_delta_filled",
    "hrv_delta_filled",
    "systolic_bp_delta_filled",
    "diastolic_bp_delta_filled",
    "spo2_delta_filled",
    "activity_delta_filled",
    "heart_rate_missing",
    "hrv_missing",
    "systolic_bp_missing",
    "diastolic_bp_missing",
    "spo2_missing",
    "activity_missing",
    "multi_signal_change",
    "recent_change_count",
]

def main():
    if not MODEL_PATH.exists():
        print("Model not found. Run python train_model.py first.")
        return

    bundle = joblib.load(MODEL_PATH)
    model = bundle["pipeline"]

    # Five consecutive hourly what-if readings.
    # Values represent simulated changes from a personal baseline.
    rows = []
    for hour in range(1, 6):
        rows.append({
            "heart_rate_delta_filled": 16,
            "hrv_delta_filled": -14,
            "systolic_bp_delta_filled": 17,
            "diastolic_bp_delta_filled": 9,
            "spo2_delta_filled": -2.0,
            "activity_delta_filled": -14,
            "heart_rate_missing": 0,
            "hrv_missing": 0,
            "systolic_bp_missing": 0,
            "diastolic_bp_missing": 0,
            "spo2_missing": 0,
            "activity_missing": 0,
            "multi_signal_change": 1,
            "recent_change_count": min(hour, 3),
        })

    scenario = pd.DataFrame(rows, columns=FEATURES)
    predictions = model.predict(scenario)
    probabilities = model.predict_proba(scenario)
    classes = list(model.classes_)
    deviation_index = classes.index(1) if 1 in classes else None

    streak = 0
    print("PRANA — CONTROLLED SYNTHETIC WHAT-IF TEST")
    print("Five simulated hourly readings; not medical measurements.")
    print("-" * 55)

    for hour, (_, row) in enumerate(scenario.iterrows(), start=1):
        predicted_deviation = int(predictions[hour - 1]) == 1
        streak = streak + 1 if predicted_deviation else 0
        alert_eligible = streak >= 3

        deviation_score = (
            float(probabilities[hour - 1, deviation_index])
            if deviation_index is not None else None
        )

        print(f"\nHour {hour}")
        print("Model state:", (
            "persistent_deviation" if predicted_deviation
            else "no_model_flag"
        ))

        if deviation_score is not None:
            print(
                "Model deviation-class probability:",
                f"{deviation_score:.3f}"
            )

        print("Consecutive positive hours:", streak)
        print("Family alert eligible:", alert_eligible)

        if predicted_deviation:
            print(
                "Explanation: The model classified this simulated pattern "
                "as a deviation from the personal baseline across multiple signals."
            )
        else:
            print(
                "Explanation: The model did not flag this simulated pattern. "
                "This does not establish that a person is medically safe."
            )

    print("\nThis test checks software behavior only.")
    print("It does not validate clinical performance or predict heart attacks.")
    print("Real notifications require backend authorization and consent.")

if __name__ == "__main__":
    main()
