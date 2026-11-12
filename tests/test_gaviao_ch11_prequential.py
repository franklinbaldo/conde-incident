"""Adversarial synthetic checks for independent C243-T10 chronological scoring.

All examples here are invented to test the algorithm; not 1963 observations.
The real pinned Parquet is separately replayed in GitHub Actions.
"""
import math
import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"tools"))
from gaviao_ch10_independent import Datum
from gaviao_ch11_prequential import (
    MODELS, EXPECTED, audit, assert_published_metrics, classify_horizon,
    coordinate, fit, verify_records,
)


def point(day):
    return datetime(1963, 1, 1, tzinfo=timezone.utc) + timedelta(days=day)


def sample():
    """Synthetic three-object catalog with unequally spaced observations."""
    data = []
    target_days = [1, 2, 5, 11, 13, 25, 40]
    for sat, days, curvature in (
        (527, [0, 1, 2, 6, 8, 15, 20, 35], .07),
        (528, [0, 1, 3, 6, 9, 15, 23, 36], -.04),
        (529, target_days, .02),
    ):
        for day in days:
            x = day/60.0
            data.append(Datum(sat, point(day), 15.0 + .02*x + curvature*x*x))
    return data


class Ch11AuditTests(unittest.TestCase):
    def test_inventory_and_unscored_preserved(self):
        result = audit(sample())
        self.assertEqual(result["possible_targets"], 6)
        self.assertEqual(result["scored"]+result["not_run"], 6)
        self.assertGreater(result["not_run"], 0)
        self.assertEqual(len(result["steps"]), 6)

    def test_all_six_models_paired(self):
        result = audit(sample())
        self.assertEqual(set(result["pooled_rmse_rev_day"]), set(MODELS))
        self.assertEqual(sum(x["scored"] for x in result["horizon_strata"].values()),
                         result["scored"])

    def test_non_future_target_training(self):
        result = audit(sample())
        for step in result["steps"]:
            self.assertLess(step["origin"], step["target"])
            self.assertGreater(step["horizon_days"], 0)
            self.assertEqual(step["train_counts"]["529"],
                             next(i for i, v in enumerate(result["steps"], 1)
                                  if v is step))

    def test_future_perturbation_does_not_change_prior_scores(self):
        orig = audit(sample())
        changed = [Datum(d.sat, d.epoch, d.n + 1.25)
                   if d.sat==529 and d.epoch==point(40) else d for d in sample()]
        later = audit(changed)
        self.assertEqual(orig["steps"][:-1], later["steps"][:-1])
        self.assertNotEqual(orig["steps"][-1], later["steps"][-1])

    def test_future_donor_does_not_leak_into_early_fit(self):
        orig = audit(sample())
        changed = [Datum(d.sat, d.epoch, d.n + 2)
                   if d.sat==527 and d.epoch==point(35) else d for d in sample()]
        later = audit(changed)
        self.assertEqual(orig["steps"][:-1], later["steps"][:-1])

    def test_horizon_boundaries_not_calendar_dates(self):
        self.assertEqual(classify_horizon(1), "up_to_1d")
        self.assertEqual(classify_horizon(1.01), "1_to_7d")
        self.assertEqual(classify_horizon(7), "1_to_7d")
        self.assertEqual(classify_horizon(30), "7_to_30d")
        self.assertEqual(classify_horizon(31), "over_30d")

    def test_zero_negative_nan_horizon_rejected(self):
        for value in [0, -0.5, float("nan"), float("inf")]:
            with self.assertRaises(ValueError):
                classify_horizon(value)

    def test_duplicate_epochs_fail_closed(self):
        records = sample()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(records + [records[0]])

    def test_nonfinite_and_negative_motion_rejected(self):
        records = sample()
        for motion in [float("nan"), float("inf"), -1]:
            bad = [Datum(records[0].sat, records[0].epoch, motion)] + records[1:]
            with self.assertRaisesRegex(ValueError, "invalid"):
                audit(bad)

    def test_non_utc_naive_time_rejected(self):
        records = sample()
        bad = [Datum(records[0].sat, datetime(1963,1,1), records[0].n)] + records[1:]
        with self.assertRaisesRegex(ValueError, "timezone"):
            audit(bad)

    def test_missing_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing object"):
            audit([d for d in sample() if d.sat != 528])

    def test_svd_matches_exact_synthetic_quadratic(self):
        records = [d for d in sample() if d.sat == 529]
        c = fit(records, point(40), 2)
        self.assertAlmostEqual(c[2], .02, places=7)
        self.assertAlmostEqual(coordinate(point(41), point(40)), 1/60)

    def test_synthetic_does_not_impersonate_historical_results(self):
        with self.assertRaises(AssertionError):
            assert_published_metrics(audit(sample()))
        self.assertEqual(len(EXPECTED), 6)

    def test_no_causal_or_geographic_inference(self):
        result = audit(sample())
        self.assertEqual(result["conclusao_conde"], "INDETERMINADO")
        self.assertFalse(result["physical_orbital_constraint"])
        self.assertFalse(result["independent_instruments"])
        self.assertFalse(result["blind_prospective"])

if __name__ == "__main__":
    unittest.main()
