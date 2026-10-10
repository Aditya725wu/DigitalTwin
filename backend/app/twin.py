import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupShuffleSplit

from .simulation import SIGNALS, SCALES, make_training_data

FEATURES = [f"{name}_z" for name in SIGNALS] + [f"{name}_missing" for name in SIGNALS] + ["persistence_hours"]


def baseline_from_rows(rows: list[dict]) -> tuple[dict, dict]:
    frame = pd.DataFrame(rows)
    means, spreads = {}, {}
    for signal in SIGNALS:
        series = pd.to_numeric(frame.get(signal), errors="coerce").dropna()
        means[signal] = float(series.median()) if len(series) else None
        mad = float((series - series.median()).abs().median() * 1.4826) if len(series) else None
        spreads[signal] = max(mad or 0, SCALES[signal] * .25) if len(series) else None
    return means, spreads


def feature_row(reading: dict, baseline: dict, spreads: dict, persistence_hours: int) -> dict:
    features = {"persistence_hours": persistence_hours}
    for signal in SIGNALS:
        value = reading.get(signal)
        center, spread = baseline.get(signal), spreads.get(signal)
        missing = value is None or center is None or pd.isna(value) or pd.isna(center)
        features[f"{signal}_missing"] = int(missing)
        features[f"{signal}_z"] = ((float(value) - center) / spread if not missing and spread else np.nan)
    return features


def transparent_rule(features: dict) -> tuple[bool, list[str]]:
    changed = [s for s in SIGNALS if not features[f"{s}_missing"] and abs(features[f"{s}_z"]) >= 2.5]
    # A simple explainable comparator: at least two measured signals depart substantially.
    return len(changed) >= 2, changed


class TwinModel:
    def __init__(self):
        data = make_training_data()
        engineered = []
        for _, patient in data.groupby("patient_id", sort=False):
            records = patient.to_dict("records")
            centers, spreads = baseline_from_rows(records[:48])
            streak = 0
            for row in records:
                streak = streak + 1 if row["label"] else 0
                engineered.append(feature_row(row, centers, spreads, streak))
        x = pd.DataFrame(engineered)[FEATURES]
        y = data.label.astype(int)
        groups = data.patient_id
        train_idx, test_idx = next(GroupShuffleSplit(n_splits=1, test_size=.25, random_state=42).split(x, y, groups))
        self.pipeline = make_pipeline(SimpleImputer(strategy="median"),
                                      HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=15, random_state=42))
        self.pipeline.fit(x.iloc[train_idx], y.iloc[train_idx])
        pred = self.pipeline.predict(x.iloc[test_idx])
        self.metrics = {"classification_report": classification_report(y.iloc[test_idx], pred, output_dict=True, zero_division=0),
                        "confusion_matrix": confusion_matrix(y.iloc[test_idx], pred).tolist(),
                        "held_out_patients": int(groups.iloc[test_idx].nunique()), "training_source": "synthetic_demo_only"}

    def assess(self, reading: dict, baseline: dict, spreads: dict, persistence: int, model_enabled: bool = True) -> dict:
        feat = feature_row(reading, baseline, spreads, persistence)
        x = pd.DataFrame([feat])[FEATURES]
        rule_state, rule_signals = transparent_rule(feat)
        if model_enabled:
            proba = self.pipeline.predict_proba(x)[0]
            score = float(proba[1])
            state = "deviation" if score >= .55 else "baseline"
            source = "synthetic_demo_classifier"
        else:
            state, score = ("deviation", .5) if rule_state else ("baseline", .5)
            source = "transparent_rule_fallback"
        contributing = []
        for signal in SIGNALS:
            if feat[f"{signal}_missing"]:
                continue
            z = feat[f"{signal}_z"]
            if abs(z) >= 1.25:
                contributing.append({"signal": signal, "value": reading[signal], "baseline": baseline[signal],
                                     "change_z": round(float(z), 2), "direction": "above" if z > 0 else "below"})
        missing = [s for s in SIGNALS if feat[f"{s}_missing"]]
        if contributing:
            reasons = [f"{x['signal'].replace('_', ' ')} is {abs(x['change_z']):.1f} robust baseline spreads {x['direction']} usual" for x in contributing]
            explanation = "Recent measurements differ from this patient's learned baseline: " + "; ".join(reasons) + "."
        else:
            explanation = "Measured values are close to the learned baseline." if not missing else "Available values are close to baseline; some signals are missing, so this assessment is incomplete."
        if missing:
            explanation += " Missing readings: " + ", ".join(missing) + "."
        return {"state": state, "confidence": round(score, 3), "confidence_note": "Model score for synthetic deviation labels; not medical risk.",
                "model_source": source, "transparent_rule_state": "deviation" if rule_state else "baseline",
                "contributing_measurements": contributing, "missing_signals": missing, "explanation": explanation,
                "persistence_hours": persistence, "assessed_at": datetime.now(timezone.utc).isoformat()}


model = TwinModel()


def json_dumps(obj) -> str:
    return json.dumps(obj, allow_nan=False)
