from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

SIGNALS = ["heart_rate", "hrv", "systolic_bp", "diastolic_bp", "spo2", "activity"]
DEFAULTS = {"heart_rate": 72.0, "hrv": 48.0, "systolic_bp": 118.0, "diastolic_bp": 76.0, "spo2": 98.0, "activity": 420.0}
SCALES = {"heart_rate": 7.0, "hrv": 8.0, "systolic_bp": 8.0, "diastolic_bp": 6.0, "spo2": 0.7, "activity": 180.0}


def generate_patient(patient_index: int, hours: int = 168, seed: int = 0) -> pd.DataFrame:
    """Create one reproducible patient's time series with correlated scenario changes."""
    rng = np.random.default_rng(seed + patient_index * 7919)
    offset = rng.normal(0, [5, 6, 7, 5, .4, 100])
    rows = []
    start = datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=patient_index * 3)
    onset = int(rng.integers(48, max(49, hours - 20))) if hours > 70 else hours + 1
    duration = int(rng.integers(6, 20))
    kind = patient_index % 3
    delta = np.array([15, -15, 18, 10, -3, -180], dtype=float)
    if kind == 1:
        delta = -delta * np.array([.65, 1, .6, .6, 1, 1])
    if kind == 2:
        delta = np.array([0, 0, 0, 0, 0, 260], dtype=float)
    for i in range(hours):
        active = (i % 24) in range(7, 20)
        mean = np.array(list(DEFAULTS.values())) + offset
        mean[0] += 6 if active else 0
        mean[5] *= 1.5 if active else .2
        changed = onset <= i < onset + duration
        if changed:
            mean += delta
        values = mean + rng.normal(0, [3, 4, 4, 3, .35, 75])
        values[0] = np.clip(values[0], 42, 160)
        values[1] = np.clip(values[1], 8, 120)
        values[2] = np.clip(values[2], 80, 210)
        values[3] = np.clip(values[3], 45, 130)
        values[4] = np.clip(values[4], 88, 100)
        values[5] = max(0, values[5])
        row = dict(zip(SIGNALS, values))
        # Random device gaps, independent of the label.
        for signal in SIGNALS:
            if rng.random() < .025:
                row[signal] = np.nan
        rows.append({"patient_id": f"synthetic-{patient_index}", "timestamp": start + timedelta(hours=i), **row,
                     "label": int(changed)})
    return pd.DataFrame(rows)


def make_training_data(patients: int = 40, hours: int = 168, seed: int = 1729) -> pd.DataFrame:
    return pd.concat([generate_patient(i, hours, seed) for i in range(patients)], ignore_index=True)


def demo_reading(patient_id: str, timestamp: datetime, scenario: str, step: int, rng: np.random.Generator) -> dict:
    values = dict(DEFAULTS)
    active = timestamp.hour in range(7, 20)
    values["heart_rate"] += 5 if active else 0
    values["activity"] *= 1.5 if active else .2
    if scenario == "sustained_deviation":
        values.update(heart_rate=88, hrv=31, systolic_bp=137, diastolic_bp=87, spo2=94, activity=180)
    elif scenario == "recovery":
        recovery = max(0, 1 - step / 8)
        values.update(heart_rate=72 + 16 * recovery, hrv=48 - 18 * recovery,
                      systolic_bp=118 + 18 * recovery, diastolic_bp=76 + 10 * recovery,
                      spo2=98 - 4 * recovery, activity=420 - 200 * recovery)
    values = {k: max(0, v + rng.normal(0, SCALES[k] * .2)) for k, v in values.items()}
    if scenario == "incomplete":
        for signal in ("hrv", "spo2", "activity"):
            values[signal] = None
    return values
