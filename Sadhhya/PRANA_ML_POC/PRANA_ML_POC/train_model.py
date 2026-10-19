"""Train/evaluate a patient-separated Random Forest for synthetic deviation labels."""
from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

DATA_PATH = Path("data/synthetic_cardiovascular_hourly.csv")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

FEATURES = [
    "heart_rate_delta_filled", "hrv_delta_filled", "systolic_bp_delta_filled",
    "diastolic_bp_delta_filled", "spo2_delta_filled", "activity_delta_filled",
    "heart_rate_missing", "hrv_missing", "systolic_bp_missing",
    "diastolic_bp_missing", "spo2_missing", "activity_missing",
    "multi_signal_change", "recent_change_count",
]
TARGET = "deviation_label"

def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError("Dataset not found. Run: python generate_dataset.py")

    df = pd.read_csv(DATA_PATH)
    # -1 means no measurements at all; don't train by treating this as normal.
    df = df[df[TARGET].isin([0, 1])].copy()
    X, y, groups = df[FEATURES], df[TARGET].astype(int), df["patient_id"]

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups=groups))
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    train_patients = sorted(groups.iloc[train_idx].unique())
    test_patients = sorted(groups.iloc[test_idx].unique())

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=False)),
        ("model", RandomForestClassifier(
            n_estimators=250,
            class_weight="balanced",
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        )),
    ])
    pipeline.fit(X_train, y_train)
    pred = pipeline.predict(X_test)

    print("\n=== Patient-separated evaluation (synthetic data only) ===")
    print(f"Train patients: {len(train_patients)} | Test patients: {len(test_patients)}")
    print(f"Training rows: {len(X_train):,} | Test rows: {len(X_test):,}")
    print("\nClassification report:")
    print(classification_report(y_test, pred, labels=[0, 1],
                                target_names=["normal_variation", "persistent_deviation"],
                                zero_division=0))
    print("Confusion matrix (rows=true [0,1], columns=predicted [0,1]):")
    print(confusion_matrix(y_test, pred, labels=[0, 1]))

    # Save pipeline and feature schema for inference.
    joblib.dump({"pipeline": pipeline, "features": FEATURES}, MODEL_DIR / "deviation_model.joblib")
    metrics = {
        "note": "Synthetic demonstration metrics; not clinical performance.",
        "train_patient_count": len(train_patients),
        "test_patient_count": len(test_patients),
        "train_patients": train_patients,
        "test_patients": test_patients,
        "class_labels": {"0": "normal_variation", "1": "persistent_deviation"},
        "confusion_matrix_rows_true_cols_pred": confusion_matrix(y_test, pred, labels=[0, 1]).tolist(),
        "classification_report": classification_report(y_test, pred, labels=[0, 1],
            target_names=["normal_variation", "persistent_deviation"],
            output_dict=True, zero_division=0),
    }
    (MODEL_DIR / "evaluation_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"\nSaved model to {MODEL_DIR / 'deviation_model.joblib'}")
    print(f"Saved metrics to {MODEL_DIR / 'evaluation_metrics.json'}")
    print("Do not interpret model confidence as medical risk.")

if __name__ == "__main__":
    main()
