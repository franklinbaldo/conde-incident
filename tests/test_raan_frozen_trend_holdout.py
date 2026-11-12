"""Adversarial regression for Polvo C241-P1 fit-only predictive controls."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_frozen_trend_holdout import (SOURCE, FROZEN, compute, fit_only,
                                      score, wrap_deg)  # noqa: E402


class FrozenRaanHoldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_bytes()
        cls.split = FROZEN.read_bytes()
        cls.report = compute(cls.source, cls.split)

    def test_snapshot_reproduces_exact_committed_bytes(self):
        frozen = ROOT / "research/statistics/raan_frozen_trend_holdout_C241-P1.json"
        expected = json.dumps(self.report, ensure_ascii=False, sort_keys=True, indent=2)+"\n"
        self.assertEqual(frozen.read_text(), expected)
        self.assertLess(len(frozen.read_bytes()), 20_000)

    def test_true_train_and_future_windows_and_duplicate_accounting(self):
        sizes = {"527": (15, 1, 4, 21),
                 "528": (24, 13, 8, 45),
                 "529": (22, 9, 23, 57)}
        for sat, (fit, val, test, raw) in sizes.items():
            with self.subTest(sat=sat):
                actual = self.report["objects"][sat]
                self.assertEqual((actual["fit"]["n"], actual["validation"]["n"],
                                  actual["evaluation"]["n"], actual["raw_rows"]),
                                 (fit, val, test, raw))
                self.assertLess(actual["fit"]["last_epoch_utc"], "1963-08-01")
                self.assertGreaterEqual(actual["evaluation"]["first_epoch_utc"], "1963-10-01")

    def test_fitted_rates_and_holdout_mae_regression_real_catalogue(self):
        expected = {
            "527": (-1.0767041099, 0.0702109578, 0.1918824952),
            "528": (-1.0924085249, 1.4111995244, 2.9080048450),
            "529": (-1.0844591439, 1.0173063086, 3.7437225768),
        }
        for sat, (slope, valid, future) in expected.items():
            with self.subTest(sat=sat):
                r = self.report["objects"][sat]
                self.assertAlmostEqual(r["fit"]["linear_slope_deg_per_day"], slope, places=7)
                self.assertAlmostEqual(r["validation"]["models"]["fitonly_linear"]["mae_deg"], valid, places=7)
                self.assertAlmostEqual(r["evaluation"]["models"]["fitonly_linear"]["mae_deg"], future, places=7)
                self.assertTrue(r["evaluation"]["linear_better_in_mae"])

    def test_membranes_reject_modifying_split_even_if_counts_same(self):
        split = json.loads(self.split)
        # Move a future point into a different block, while preserving all 123 rows.
        val = split["memberships"]["528"]["validation"]
        future = split["memberships"]["528"]["evaluation"]
        val[-1], future[0] = future[0], val[-1]
        with self.assertRaises(ValueError):
            compute(self.source, json.dumps(split).encode())

    def test_refuses_conflicting_duplicate_catalogue_value(self):
        source = json.loads(self.source)
        changed = deepcopy(source["records"][0])
        changed["raan_deg"] += 0.5
        source["records"].append(changed)
        with self.assertRaises(ValueError):
            compute(json.dumps(source).encode(), self.split)

    def test_cannot_evaluate_on_or_before_last_fit_epoch(self):
        now = datetime(1963, 7, 31, tzinfo=timezone.utc)
        fit = [(now-timedelta(days=2), 15.0),
               (now-timedelta(days=1), 14.0), (now, 13.0)]
        model = fit_only(fit)
        with self.assertRaises(ValueError):
            score([(now, 13.0)], model)

    def test_circular_arithmetic_handles_wrap_and_rejects_nonfinite(self):
        self.assertAlmostEqual(wrap_deg(1.0 - 359.5), 1.5)
        self.assertAlmostEqual(wrap_deg(359.5 - 1.0), -1.5)
        for invalid in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                wrap_deg(invalid)

    def test_predeclared_fit_only_input_is_not_refit_on_holdout(self):
        now = datetime(1963, 1, 1, tzinfo=timezone.utc)
        train = [(now+timedelta(days=i), (359.0 + i) % 360) for i in range(5)]
        model = fit_only(train)
        self.assertAlmostEqual(model["slope_deg_per_day"], 1)
        future = [(now+timedelta(days=8), 7.0)]
        original = score(future, model)
        adversarial = score([(future[0][0], 180)], model)
        self.assertNotEqual(original["models"]["fitonly_linear"]["mae_deg"],
                            adversarial["models"]["fitonly_linear"]["mae_deg"])
        self.assertEqual(model["slope_deg_per_day"], 1)


if __name__ == "__main__":
    unittest.main()
