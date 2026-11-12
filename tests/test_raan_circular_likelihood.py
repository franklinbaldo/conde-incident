"""Adversarial tests for a conditional mathematical model, NOT historical fit."""
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_circular_likelihood import (
    Datum, LOG_TAU, log_i0, marginal_log_density, predictive_log_density,
)


def d(n, r, k, lineage="same", pred=0.0):
    return Datum(norad=527, epoch_utc=f"synthetic-{n}",
                 lineage=lineage, observed_raan_deg=r,
                 predicted_raan_deg=pred, kappa=k,
                 prediction_ref="synthetic-H", calibration_ref="synthetic-kappa")


def log_i0_independent_quadrature(x, n=8192):
    # Periodic trapezoidal integral for exp(x*cos(theta) - x), independently
    # of the series/asymptotic implementation. No external dependency.
    vals = [math.exp(x * (math.cos(2.0 * math.pi * j / n) - 1.0))
            for j in range(n)]
    return x + math.log(math.fsum(vals) / n)


class CircularLikelihoodTest(unittest.TestCase):
    def test_bessel_vs_independent_integral_and_boundary(self):
        for x in (0, 1e-6, 0.1, 1, 10, 49.999, 50, 50.001, 100, 500, 1000):
            with self.subTest(x=x):
                self.assertAlmostEqual(log_i0(x),
                                       log_i0_independent_quadrature(x),
                                       delta=2e-11)
        for x in (-0.1, float("nan"), float("inf"), True, "5"):
            with self.assertRaises(ValueError):
                log_i0(x)

    def test_single_observation_no_phase_information(self):
        for r in (-900, -180, 0, 179.9, 721):
            for k in (0, 0.1, 1, 10, 100):
                self.assertAlmostEqual(marginal_log_density([d(1, r, k)]),
                                       -LOG_TAU, delta=1e-11)

    def test_shared_offset_makes_relative_angles_informative(self):
        aligned = [d(1, 0, 4), d(2, 0, 4)]
        opposite = [d(1, 0, 4), d(2, 180, 4)]
        self.assertGreater(marginal_log_density(aligned),
                           marginal_log_density(opposite))
        separated = [d(1, 0, 4, "a"), d(2, 180, 4, "b")]
        self.assertAlmostEqual(marginal_log_density(separated),
                               -2 * LOG_TAU, delta=1e-11)
        self.assertNotAlmostEqual(marginal_log_density(opposite),
                                  marginal_log_density(separated), delta=0.1)

    def test_gauge_invariance_per_lineage_and_wrap(self):
        source = [d(1, 359.9, 1), d(2, 0.1, 10),
                  d(3, 120, 50, "other")]
        ref = marginal_log_density(source)
        for rotation in (-720, -359, -31.25, 0, 45, 360, 720):
            rotated = [Datum(x.norad, x.epoch_utc, x.lineage,
                             x.observed_raan_deg + rotation, x.predicted_raan_deg,
                             x.kappa, x.prediction_ref, x.calibration_ref) for x in source]
            self.assertAlmostEqual(marginal_log_density(rotated), ref, delta=1e-11)
            moved_prediction = [Datum(x.norad, x.epoch_utc, x.lineage,
                                      x.observed_raan_deg, x.predicted_raan_deg + rotation,
                                      x.kappa, x.prediction_ref, x.calibration_ref) for x in source]
            self.assertAlmostEqual(marginal_log_density(moved_prediction), ref,
                                   delta=1e-11)

    def test_two_data_vs_direct_latent_bias_integration(self):
        # Independent numerical integration of latent b on circle, using
        # original von Mises product rather than the resultant-vector formula.
        xs = [d(1, 15, 1.5), d(2, 75, 3.25)]
        n = 4096
        integrand = []
        for j in range(n):
            b = 2.0 * math.pi * j / n
            total = sum(x.kappa * math.cos(
                math.radians(x.observed_raan_deg - x.predicted_raan_deg) - b)
                        for x in xs)
            integrand.append(math.exp(total))
        direct = (math.log(math.fsum(integrand) / n)
                  - sum(log_i0(x.kappa) for x in xs) - len(xs) * LOG_TAU)
        self.assertAlmostEqual(marginal_log_density(xs), direct, delta=2e-11)

    def test_holdout_predictive_is_ratio_and_no_double_count(self):
        fit = [d(1, 0, 3), d(2, 1, 3)]
        later = [d(3, 0, 5)]
        score = predictive_log_density(fit, later)
        self.assertAlmostEqual(score,
            marginal_log_density(fit + later)-marginal_log_density(fit))
        bad = [d(1, 0, 3)]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            predictive_log_density(fit, bad)
        for train, future in (([], later), (fit, [])):
            with self.assertRaises(ValueError):
                predictive_log_density(train, future)

    def test_explicit_custody_and_calibration_fail_closed(self):
        examples = [
            Datum(527, "t1", "", 0, 0, 1, "H", "K"),
            Datum(527, "", "same", 0, 0, 1, "H", "K"),
            Datum(0, "t1", "same", 0, 0, 1, "H", "K"),
            Datum(527, "t1", "same", 0, 0, -1, "H", "K"),
            Datum(527, "t1", "same", 0, 0, float("nan"), "H", "K"),
            Datum(527, "t1", "same", 0, 0, "unspecified", "H", "K"),
            Datum(527, "t1", "same", float("inf"), 0, 1, "H", "K"),
            Datum(527, "t1", "same", 0, 0, 1, "", "K"),
            Datum(527, "t1", "same", 0, 0, 1, "H", ""),
        ]
        for bad in examples:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                marginal_log_density([bad])
        with self.assertRaises(ValueError):
            marginal_log_density([])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            marginal_log_density([d(1, 0, 1), d(1, 0, 1, "mirror")])

    def test_real_corpus_is_not_scored_without_calibrated_inputs(self):
        # Existing historical data includes ONLY epoch, angle and NORAD.
        # Reject any interpretation that supplies an implicit kappa or H(theta).
        import json
        data = json.loads((ROOT / "research/statistics/raan_527_528_529_1963.json").read_text())
        self.assertEqual(len(data["records"]), 123)
        unique = {(r["norad"], r["epoch_utc"]) for r in data["records"]}
        self.assertEqual(len(unique), 119)
        self.assertEqual(data["provenance"]["status"],
                         "SECONDARY_CATALOGUE_DERIVED_NOT_ORIGINAL_TRACK")
        sample = data["records"][0]
        missing_prediction_and_kappa = Datum(
            sample["norad"], sample["epoch_utc"], "single-secondary-source",
            sample["raan_deg"], float("nan"), float("nan"), "unavailable", "unavailable"
        )
        with self.assertRaises(ValueError):
            marginal_log_density([missing_prediction_and_kappa])


if __name__ == "__main__":
    unittest.main()
