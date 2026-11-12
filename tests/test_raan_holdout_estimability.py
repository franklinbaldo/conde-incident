"""Adversarial exact conditional observability of frozen, nonblind RAAN holdouts."""
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_holdout_estimability import build, estimable, holdout_counts
from raan_temporal_gauge import model_row


class FrozenHoldoutEstimabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT/"research/statistics/raan_527_528_529_1963.json").read_bytes()
        cls.split = (ROOT/"research/statistics/raan_chronological_holdout_1963.json").read_bytes()
        cls.report = build(cls.raw, cls.split)

    def test_independent_reference_rows_not_assumed(self):
        self.assertEqual(self.report["historical_mcmc"], "NOT_RUN")
        self.assertEqual(self.report["holdout_logscore"], "NOT_RUN")
        self.assertIsNone(self.report["source"]["instrument_calibration"])

    def test_exact_527_validation_extrapolation_is_not_estimable(self):
        val_to_eval = self.report["comparisons"][2]
        self.assertEqual((val_to_eval["training_rows"], val_to_eval["training_rank"]), (23, 5))
        self.assertEqual(val_to_eval["by_object"]["527"], {
            "total": 4, "estimable": 0, "not_estimable": 4
        })
        self.assertEqual(val_to_eval["total_estimated"], 31)
        self.assertEqual(val_to_eval["total_holdout"], 35)

    def test_fit_can_express_holdout_linear_design_but_not_physics(self):
        for c in (self.report["comparisons"][0], self.report["comparisons"][1],
                  self.report["comparisons"][3]):
            self.assertEqual(c["total_estimated"], c["total_holdout"])
            self.assertTrue(c["row_space_only_no_physical_prediction"])

    def test_witness_separates_future_527(self):
        c = self.report["validation_527_counterexample"]
        self.assertEqual(c["validation_rank"], 5)
        self.assertEqual(c["with_two_absolute_528_anchors_rank"], 7)
        self.assertEqual(c["with_one_527_extra_epoch_rank"], 6)
        self.assertEqual(c["with_extra_and_both_528_anchors_rank"], 8)
        self.assertTrue(c["evaluation_527_prediction_changes_nonzero"])
        self.assertTrue(c["independent_angular_calibration_still_required"])

    def test_one_time_versus_two_time_observations(self):
        first = model_row("527", Fraction(3))
        later = model_row("527", Fraction(4))
        self.assertTrue(estimable([first], first))
        self.assertFalse(estimable([first], later))
        self.assertTrue(estimable([first, later], model_row("527", Fraction(5))))

    def test_reject_holdout_as_own_training(self):
        m = json.loads(self.split)
        with self.assertRaisesRegex(ValueError, "holdout"):
            holdout_counts(m, ("validation",), "validation")
        with self.assertRaisesRegex(ValueError, "unknown"):
            holdout_counts(m, ("injected",), "evaluation")

    def test_tampered_dataset_rejected(self):
        m = json.loads(self.split)
        m["memberships"]["527"]["validation"] = []
        with self.assertRaises(ValueError):
            build(self.raw, json.dumps(m).encode())

    def test_fake_independent_provenance_rejected(self):
        d = json.loads(self.raw)
        d["provenance"]["lineage"] = "two calibrated independent sensors"
        with self.assertRaises(ValueError):
            build(json.dumps(d).encode(), self.split)

    def test_report_replay(self):
        data = (json.dumps(self.report, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()
        self.assertEqual(data, (ROOT/"research/statistics/raan_holdout_estimability_C241.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
