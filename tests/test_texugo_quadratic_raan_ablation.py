"""Adversarial fit-only quadratic RAAN controls, no catalog claims without CI."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import math
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from texugo_quadratic_raan_ablation import (  # noqa: E402
    fit_quadratic, quadratic_predict, metrics, solve_3x3,
)
from raan_frozen_trend_holdout import fit_only, wrap_deg  # noqa: E402


class QuadraticFalsifiers(unittest.TestCase):
    def setUp(self):
        self.t0 = datetime(1963, 1, 1, tzinfo=timezone.utc)
        self.fit_dates = [self.t0 + timedelta(days=i) for i in range(12)]

    def make_fit(self, fn):
        return [(t, fn(i) % 360) for i, t in enumerate(self.fit_dates)]

    def test_known_acceleration_predicted_without_future_training(self):
        fit = self.make_fit(lambda i: 15.0 + 0.7*i + 0.035*i*i)
        model = fit_quadratic(fit)
        future = self.t0 + timedelta(days=16)
        self.assertAlmostEqual(wrap_deg(quadratic_predict(model, future) -
                                        (15+0.7*16+0.035*16**2)), 0, places=7)

    def test_negative_control_quadratic_overfits_nonpolynomial_fit(self):
        fit = self.make_fit(lambda i: 70.0 + 1.2*i + (3.0 if i == 11 else 0.0))
        linear = fit_only(fit)
        quad = fit_quadratic(fit)
        targets = [(self.t0+timedelta(days=i), (70+1.2*i) % 360)
                   for i in (22, 25, 30)]
        q = metrics([wrap_deg(v - quadratic_predict(quad, t)) for t, v in targets])
        l = metrics([wrap_deg(v - (linear["intercept_deg_unwrapped"] +
                                  linear["slope_deg_per_day"] *
                                  (t-linear["origin"]).total_seconds()/86400))
                     for t, v in targets])
        self.assertGreater(q["mae_deg"], l["mae_deg"])

    def test_positive_control_acceleration_beats_linear(self):
        fit = self.make_fit(lambda i: 150-0.9*i+0.06*i*i)
        linear = fit_only(fit)
        quad = fit_quadratic(fit)
        future = self.t0+timedelta(days=24)
        truth = (150-0.9*24+0.06*24**2) % 360
        self.assertLess(abs(wrap_deg(truth-quadratic_predict(quad, future))),
                        abs(wrap_deg(truth-(linear["intercept_deg_unwrapped"] +
                                           linear["slope_deg_per_day"] * 24))))

    def test_future_values_do_not_affect_training(self):
        fit = self.make_fit(lambda i: 350 + 1.1*i + .01*i*i)
        model = fit_quadratic(fit)
        target = self.t0+timedelta(days=23)
        expected = quadratic_predict(model, target)
        # No future rows are passed into the fitting function.
        self.assertEqual(expected, quadratic_predict(fit_quadratic(fit), target))
        with self.assertRaisesRegex(ValueError, "leakage"):
            quadratic_predict(model, fit[-1][0])
        self.assertTrue(0 <= expected < 360)

    def test_reject_singular_and_nonfinite_inputs(self):
        with self.assertRaisesRegex(ValueError, "singular"):
            solve_3x3([[1, 1, 1]]*3, [1, 1, 1])
        with self.assertRaises(ValueError):
            fit_quadratic(self.make_fit(lambda i: float("nan")))
        with self.assertRaises(ValueError):
            metrics([])

    def test_single_observation_date_is_not_prediction(self):
        model = fit_quadratic(self.make_fit(lambda i: 24-0.3*i))
        with self.assertRaisesRegex(ValueError, "leakage"):
            quadratic_predict(model, model["last_fit_epoch"])
        self.assertTrue(math.isfinite(model["scale_days"]))


if __name__ == "__main__":
    unittest.main()
