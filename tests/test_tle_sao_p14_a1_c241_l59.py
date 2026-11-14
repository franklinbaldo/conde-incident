"""Mutation controls for P-14 printed coverage, time scale, and source integrity."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools/tle_sao_p14_a1_c241_l59.py"
SPEC = importlib.util.spec_from_file_location("sao_p14_c241_l59", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class P14ScopeControls(unittest.TestCase):
    def setUp(self):
        self.m = mod.load()

    def test_baseline(self):
        result = mod.validate(self.m)
        self.assertEqual(result["status"], "CONTEXT_ONLY")
        self.assertEqual(result["selected_observation_rows"], 5140)
        self.assertEqual(result["target_observations"], 0)

    def test_published_formula_starts_at_reference(self):
        self.assertAlmostEqual(mod.a1_minus_wwv_seconds(self.m, 38030.0), 2.292725, places=9)
        self.assertAlmostEqual(mod.a1_minus_wwv_seconds(self.m, 38211.0), 2.495165898, places=9)
        self.assertAlmostEqual(mod.a1_minus_wwv_seconds(self.m, 38333.0), 2.631617774, places=9)

    def test_out_of_scope_rejected(self):
        for value in (38029.999, 38334.0, 38335.0, float("nan"), float("inf"), None, True, "38333"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                mod.a1_minus_wwv_seconds(self.m, value)

    def test_instrument_epoch_cannot_be_fabricated(self):
        for field in ("raw_observations", "instrumental_epoch_utc", "station", "covariance", "reentry_location"):
            c = copy.deepcopy(self.m)
            c["target_527_528_529"][field] = "1963-11-08T12:00:00Z"
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.validate(c)

    def test_no_auto_transfer_of_sigma_or_constraint(self):
        cases = [
            ("measurement_method_context_only", "assigned_angular_standard_error_arcsec", 1.0),
            ("measurement_method_context_only", "typical_time_uncertainty_milliseconds", 0.0),
            ("target_527_528_529", "physical_constraints_activated", 1),
            ("target_527_528_529", "independent_instrumental_measurements_added", 1)
        ]
        for group, key, value in cases:
            c = copy.deepcopy(self.m)
            c[group][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                mod.validate(c)

    def test_source_identity_and_scope_are_immutable(self):
        cases = [
            ("source", "pdf_sha256", "0" * 64),
            ("source", "pdf_bytes", 42),
            ("observations_scope", "primary_calendar_window", ["1963-01-01", "1963-11-08"]),
            ("observations_scope", "norad_527_528_529_in_list", True),
            ("observations_scope", "listed_targets", ["NORAD 528"]),
            ("observations_scope", "scope_interpretation", "528_NOT_OBSERVED")
        ]
        for group, key, value in cases:
            c = copy.deepcopy(self.m)
            c[group][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                mod.validate(c)

    def test_wwv_emitted_is_not_utc(self):
        for key, value in (
            ("time_scale", "UTC"),
            ("time_emission_reference", "UTC"),
            ("angular_reference", "TEME"),
            ("station_geodetic_reference", "WGS84"),
            ("refraction", "CORRECTED")
        ):
            c = copy.deepcopy(self.m)
            c["measurement_method_context_only"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                mod.validate(c)

    def test_wrong_clock_coefficients_rejected(self):
        for key, value in (
            ("mjd_lower_inclusive", 38031.0),
            ("mjd_upper_exclusive", 38335.0),
            ("intercept_seconds", 2.0),
            ("slope_seconds_per_day", 0.0),
            ("reference_mjd", 38031.0)
        ):
            c = copy.deepcopy(self.m)
            c["measurement_method_context_only"]["a1_minus_wwv_seconds"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                mod.validate(c)

    def test_corrupt_pdf_rejected_before_parsing(self):
        with self.assertRaisesRegex(ValueError, "source bytes drifted"):
            mod.inspect_pdf(b"%PDF-not-real")


if __name__ == "__main__":
    unittest.main()
