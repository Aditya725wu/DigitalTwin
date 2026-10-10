import unittest

from app.simulation import DEFAULTS, SIGNALS, make_training_data
from app.twin import TwinModel, baseline_from_rows, feature_row, model


class TwinBehaviorTests(unittest.TestCase):
    def test_training_data_has_patient_groups_and_both_labels(self):
        data = make_training_data(patients=8, hours=100)
        self.assertGreaterEqual(data.patient_id.nunique(), 8)
        self.assertEqual(set(data.label.unique()), {0, 1})

    def test_missing_readings_are_marked_missing_not_normal(self):
        centers = dict(DEFAULTS)
        spreads = {signal: 5.0 for signal in SIGNALS}
        reading = {**DEFAULTS, "spo2": None}
        features = feature_row(reading, centers, spreads, 0)
        self.assertEqual(features["spo2_missing"], 1)

    def test_explanation_names_changed_signals_and_missing_data(self):
        centers = dict(DEFAULTS)
        spreads = {signal: 5.0 for signal in SIGNALS}
        reading = {**DEFAULTS, "heart_rate": 100, "spo2": None}
        result = model.assess(reading, centers, spreads, 3)
        self.assertIn("heart rate", result["explanation"])
        self.assertIn("spo2", result["missing_signals"])
        self.assertNotIn("medical risk", result["explanation"].lower())

    def test_evaluation_uses_held_out_patients(self):
        fresh = TwinModel()
        self.assertGreater(fresh.metrics["held_out_patients"], 0)
        self.assertEqual(fresh.metrics["training_source"], "synthetic_demo_only")
        self.assertEqual(len(fresh.metrics["confusion_matrix"]), 2)


if __name__ == "__main__":
    unittest.main()
