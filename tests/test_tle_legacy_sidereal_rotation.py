"""C241-P6: synthetic calendar, circular and source-integrity controls.

These tests do NOT assert UT1-UTC or a TEME frame for either 1963 line.
"""
import math
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from tle_legacy_sidereal_rotation import (
    EARTH_TURN_DEG_PER_UTC_PROXY_SECOND,
    evaluate, gmst_utc_proxy_deg, jd_utc_proxy,
    signed_circular_difference_deg,
)


class LegacySiderealControls(unittest.TestCase):
    def test_j2000_noon_calendar_anchor(self):
        date = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
        self.assertAlmostEqual(jd_utc_proxy(date), 2451545.0, places=7)
        self.assertAlmostEqual(gmst_utc_proxy_deg(date), 280.46061837, places=7)

    def test_midnight_across_gregorian_month(self):
        a = datetime(1963, 10, 31, 12, tzinfo=timezone.utc)
        b = a + timedelta(days=1)
        self.assertAlmostEqual(jd_utc_proxy(b) - jd_utc_proxy(a), 1., places=7)

    def test_timezone_or_naive_date_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "explicit UTC"):
            jd_utc_proxy(datetime(1963, 10, 27))
        other = timezone(timedelta(hours=-4))
        with self.assertRaisesRegex(ValueError, "explicit UTC"):
            jd_utc_proxy(datetime(1963, 10, 27, tzinfo=other))

    def test_circular_angles_and_nonfinite(self):
        self.assertAlmostEqual(signed_circular_difference_deg(0, 359), 1.)
        self.assertAlmostEqual(signed_circular_difference_deg(359, 0), -1.)
        self.assertAlmostEqual(signed_circular_difference_deg(284.152, 198.5261), 85.6259)
        with self.assertRaisesRegex(ValueError, "non-finite"):
            signed_circular_difference_deg(float("nan"), 2)

    def test_actual_pinned_october_raans_and_epochs(self):
        x = evaluate()
        self.assertEqual(x["source_occurrences"][0], "C25#1")
        self.assertAlmostEqual(x["legacy_raan_deg"], 284.1520)
        self.assertAlmostEqual(x["secondary_raan_deg"], 198.5261)
        self.assertAlmostEqual(x["printed_epoch_separation_seconds"], 16.132608, places=6)
        self.assertAlmostEqual(x["unrotated_abs_difference_deg"], 85.6259)
        self.assertEqual(x["physical_domain_delta"], "NONE")

    def test_both_convention_signs_at_actual_epochs(self):
        x = evaluate()
        by_epoch = x["results_by_printed_epoch"]
        at_secondary = by_epoch["secondary_528_literal"]
        self.assertAlmostEqual(
            at_secondary["gmst_deg_using_UTC_as_UT1_proxy"], 255.307643, places=5)
        self.assertAlmostEqual(
            at_secondary["rotations"]["minus_gmst"]["predicted_angle_deg"],
            303.218457, places=5)
        self.assertAlmostEqual(
            x["best_minus_gmst_at_secondary_epoch_abs_residual_deg"],
            19.066457, places=5)
        self.assertAlmostEqual(
            abs(at_secondary["rotations"]["plus_gmst"]["signed_residual_to_legacy_deg"]),
            169.681743, places=5)
        self.assertGreater(
            abs(by_epoch["constructed_legacy_printed"]["rotations"]["minus_gmst"][
                "signed_residual_to_legacy_deg"]), 19.)

    def test_declared_60s_stress_does_not_make_angles_equal(self):
        x = evaluate(60.)
        self.assertEqual(x["declared_utc_proxy_stress_seconds_not_DUT1_bound"], 60.)
        for epoch in x["results_by_printed_epoch"].values():
            for sign in ("minus_gmst", "plus_gmst"):
                self.assertGreater(
                    epoch["rotations"][sign][
                        "minimum_abs_residual_within_stress_deg"], 18.)
        self.assertEqual(
            x["verdict_within_declared_stress"],
            "SIMPLE_GREENWICH_Z_ROTATION_NOT_SUFFICIENT_AT_PRINTED_EPOCHS")

    def test_time_shift_needed_is_far_more_than_60s_stress(self):
        x = evaluate()
        seconds = x["approx_extra_time_shift_to_zero_minus_gmst_seconds"]
        self.assertGreater(seconds, 4500.)
        self.assertLess(seconds, 4700.)
        self.assertGreater(EARTH_TURN_DEG_PER_UTC_PROXY_SECOND, 0.)

    def test_stress_parameter_is_not_covariance(self):
        for bad in (-1, float("nan"), float("inf")):
            with self.assertRaisesRegex(ValueError, "stress"):
                evaluate(bad)
        x = evaluate(0.)
        self.assertEqual(x["declared_utc_proxy_stress_seconds_not_DUT1_bound"], 0.)

    def test_source_checksum_fails_closed_on_missing_file(self):
        with patch("tle_legacy_sidereal_rotation.LITERAL", ROOT / "missing-1963.tle"):
            with self.assertRaises(FileNotFoundError):
                evaluate()

    def test_no_activation_of_physical_lean_constraint(self):
        x = evaluate()
        self.assertFalse(x["active_Lean_physical_constraint"])
        self.assertEqual(x["site_of_reentry"], "INDETERMINATE")
        self.assertIn("UT1-UTC", x["missing_to_test_REAL_frame_hypothesis"])


if __name__ == "__main__":
    unittest.main()
