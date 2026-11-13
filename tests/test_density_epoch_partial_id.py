"""Adversarial tests for the C241-P30 conditional observability bound."""
import importlib.util
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "density_epoch_partial_id", ROOT / "tools/density_epoch_partial_id.py")
p30 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p30)


class PartialIdentificationTests(unittest.TestCase):
    def test_exact_common_factor_identifies_gamma(self):
        x = p30.gamma_interval(30, F("-0.6"), kappa0=F(0),
                               kappa1=F(0), error=F(0))
        self.assertEqual((x["gamma_min"], x["gamma_max"]),
                         ("1/50", "1/50"))

    def test_spatial_drift_widens_gamma_and_H(self):
        x = p30.gamma_interval(30, F("-0.6"), kappa0=F("0.1"),
                               kappa1=F("0.1"), error=F("0.05"))
        self.assertEqual((x["gamma_min"], x["gamma_max"]),
                         ("7/600", "17/600"))
        self.assertEqual(x["H_km"], "[600/17,600/7]")

    def test_infinite_scale_height_not_excluded(self):
        x = p30.gamma_interval(30, F("-0.6"), kappa0=F("0.3"),
                               kappa1=F("0.3"), error=F(0))
        self.assertEqual(x["gamma_min"], "0/1")
        self.assertEqual(x["status"], "NO_FINITE_UPPER_BOUND_H")

    def test_unbounded_q_always_unidentified(self):
        x = p30.gamma_interval(30, F("-0.6"))
        self.assertEqual(x["status"], "UNIDENTIFIED")

    def test_zero_altitude_interaction_is_not_identifiable(self):
        x = p30.gamma_interval(0, F("-0.6"), kappa0=F(0),
                               kappa1=F(0), error=F(0))
        self.assertEqual(x["status"], "REJECTED")
        x = p30.gamma_interval(0, F("0.0"), kappa0=F(0),
                               kappa1=F(0), error=F(0))
        self.assertEqual(x["status"], "UNIDENTIFIED")

    def test_physical_sign_rejects_positive_contrast(self):
        x = p30.gamma_interval(30, F("0.6"), kappa0=F(0),
                               kappa1=F(0), error=F(0))
        self.assertEqual(x["status"], "REJECTED")

    def test_negative_delta_yields_same_interval(self):
        x = p30.gamma_interval(-30, F("0.6"), kappa0=F("0.1"),
                               kappa1=F("0.1"), error=F("0.05"))
        self.assertEqual((x["gamma_min"], x["gamma_max"]),
                         ("7/600", "17/600"))

    def test_no_partial_or_negative_budgets(self):
        with self.assertRaises(ValueError):
            p30.gamma_interval(30, F(0), kappa0=F(0))
        with self.assertRaises(ValueError):
            p30.gamma_interval(30, F(0), kappa0=F(-1),
                               kappa1=F(0), error=F(0))
        with self.assertRaises(ValueError):
            p30.gamma_interval(30, F(0), kappa0=.1,
                               kappa1=F(0), error=F(0))

    def test_manifest_inactive_and_no_posterior(self):
        p = p30.report()
        self.assertFalse(p["active_constraint"])
        self.assertEqual(p["historical_mcmc"], "NOT_RUN")
        self.assertEqual(p["historical_domain_reduction"], "NOT_EVALUABLE")
        self.assertEqual(p["holdout"], "NOT_AVAILABLE")
        self.assertEqual(p["NORAD_528_ballistic_identification"],
                         "UNIDENTIFIED_NO_528_OBSERVATION")

    def test_manifest_deterministic(self):
        self.assertEqual(p30.report(), p30.report())


if __name__ == "__main__":
    unittest.main()
