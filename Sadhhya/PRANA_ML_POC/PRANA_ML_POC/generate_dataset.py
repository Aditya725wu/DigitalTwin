"""Generate an explicitly synthetic hourly cardiovascular monitoring dataset.

Labels represent simulated persistent deviations from personal baseline, NOT heart attacks.
"""
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("data")
OUT.mkdir(exist_ok=True)

RNG = np.random.default_rng(42)
N_PATIENTS = 120
HOURS_PER_PATIENT = 24 * 14  # 14 simulated days per patient

def generate_patient(patient_num: int) -> pd.DataFrame:
    pid = f"P{patient_num:03d}"
    start = pd.Timestamp("2026-01-01") + pd.Timedelta(days=patient_num % 28)
    # Personal baselines vary between simulated people; values are not clinical targets.
    
    base = {
    "heart_rate": float(np.clip(RNG.normal(72, 7), 55, 92)),
    "hrv": float(np.clip(RNG.normal(48, 10), 25, 75)),
    "systolic_bp": float(np.clip(RNG.normal(119, 8), 100, 138)),
    "diastolic_bp": float(np.clip(RNG.normal(77, 6), 62, 88)),
    "spo2": float(np.clip(RNG.normal(97.5, 0.7), 95, 99)),
    "activity": float(np.clip(RNG.normal(35, 12), 10, 65)),
}

    rows = []
    # Choose several scenario windows; scenarios are synthetic patterns only.
    scenario = np.zeros(HOURS_PER_PATIENT, dtype=int)  # 0 normal, 1 sustained shift
    cursor = 12
    while cursor < HOURS_PER_PATIENT - 12:
        if RNG.random() < 0.035:
            duration = int(RNG.integers(4, 13))
            scenario[cursor:min(cursor + duration, HOURS_PER_PATIENT)] = 1
            cursor += duration + int(RNG.integers(12, 48))
        else:
            cursor += int(RNG.integers(6, 20))

    # Baseline plus realistic-looking synthetic variation and daily activity rhythm.
    for h in range(HOURS_PER_PATIENT):
        ts = start + pd.Timedelta(hours=h)
        active = max(0.0, np.sin((h % 24 - 7) / 24 * 2 * np.pi))
        is_shift = scenario[h] == 1
        hr = base["heart_rate"] + 5 * active + RNG.normal(0, 4)
        hrv = base["hrv"] - 3 * active + RNG.normal(0, 5)
        sbp = base["systolic_bp"] + 3 * active + RNG.normal(0, 5)
        dbp = base["diastolic_bp"] + 1.5 * active + RNG.normal(0, 3)
        spo2 = base["spo2"] + RNG.normal(0, 0.6)
        activity = base["activity"] + 18 * active + RNG.normal(0, 10)

        if is_shift:
            # Multisignal shifts are intentionally synthetic and are not a clinical model.
            hr += RNG.choice([12, 16, 20])
            hrv -= RNG.choice([10, 14, 18])
            sbp += RNG.choice([12, 17, 22])
            dbp += RNG.choice([6, 9, 12])
            spo2 -= RNG.choice([1.5, 2.0, 2.5])
            activity -= RNG.choice([8, 14, 20])

        vals = {
            "heart_rate": float(np.clip(hr, 35, 180)),
            "hrv": float(np.clip(hrv, 5, 120)),
            "systolic_bp": float(np.clip(sbp, 70, 220)),
            "diastolic_bp": float(np.clip(dbp, 40, 140)),
            "spo2": float(np.clip(spo2, 80, 100)),
            "activity": float(np.clip(activity, 0, 150)),
        }

        # Missingness occurs independently of label; missing is never labeled "normal" by itself.
        for col in vals:
            if RNG.random() < 0.045:
                vals[col] = np.nan

        row = {
            "patient_id": pid,
            "timestamp": ts.isoformat(),
            **vals,
            **{f"baseline_{k}": v for k, v in base.items()},
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    # Feature engineering uses only observed measurements and baseline values.
    df = add_features(df)
    # Label deviation only after the simulated shift has persisted for 3 consecutive hours.
    # The first two hours of a shift are not yet labeled as persistent.
    sustained = (
        pd.Series(scenario)
        .rolling(3, min_periods=3)
        .sum()
        .eq(3)
        .astype(int)
        .to_numpy()
    )
    df["deviation_label"] = sustained
    # Missing-only rows are unscorable; retain them in CSV but exclude from supervised training.
    signal_cols = ["heart_rate", "hrv", "systolic_bp", "diastolic_bp", "spo2", "activity"]
    df.loc[df[signal_cols].isna().all(axis=1), "deviation_label"] = -1
    return df

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Differences from the patient's baseline, plus explicit missingness flags.
    for col in ["heart_rate", "hrv", "systolic_bp", "diastolic_bp", "spo2", "activity"]:
        bcol = f"baseline_{col}"
        delta = df[col] - df[bcol]
        df[f"{col}_delta"] = delta
        df[f"{col}_missing"] = df[col].isna().astype(int)
        # Safe fill for the model is paired with a missingness indicator.
        df[f"{col}_delta_filled"] = delta.fillna(0)
    # Persistence-like features from observable changes; not based on the target label.
    hr = df["heart_rate_delta"].abs() >= 10
    hrv = df["hrv_delta"] <= -8
    sbp = df["systolic_bp_delta"] >= 10
    spo2 = df["spo2_delta"] <= -1.5
    multi_signal = (hr.astype(int) + hrv.astype(int) + sbp.astype(int) + spo2.astype(int)) >= 2
    df["multi_signal_change"] = multi_signal.astype(int)
    # Rolling count over current and previous two hourly summaries, reset per patient.
    df["recent_change_count"] = (
        multi_signal.astype(int).groupby(df["patient_id"]).rolling(3, min_periods=1).sum()
        .reset_index(level=0, drop=True).sort_index().astype(float)
    )
    return df

def main():
    frames = [generate_patient(i + 1) for i in range(N_PATIENTS)]
    data = pd.concat(frames, ignore_index=True)
    OUT.mkdir(exist_ok=True)
    path = OUT / "synthetic_cardiovascular_hourly.csv"
    data.to_csv(path, index=False)
    print(f"Saved {len(data):,} rows from {N_PATIENTS} synthetic patients to {path}")
    print("Label counts (-1=insufficient all-signal data, 0=normal variation, 1=synthetic deviation):")
    print(data["deviation_label"].value_counts().sort_index().to_string())
    print("\nReminder: these are simulated labels, not clinical outcomes or heart-attack labels.")

if __name__ == "__main__":
    main()
