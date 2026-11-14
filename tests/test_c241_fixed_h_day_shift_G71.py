"""G71 synthetic adversarial controls; real source replay belongs to CI."""
from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c241_fixed_h_day_shift_G71 import day_shift_certificate, report  # noqa: E402


def interval(low: float, high: float) -> dict:
    return {"status": "COUNTERFACTUAL_INTERVAL_ONLY",
            "required_H_km_UTC_DAY_COUNTERFACTUAL": [low, high]}


class IndependentShiftTests(unittest.TestCase):
    def test_disjoint_even_with_24h_independent_shifts(self):
        cases = [interval(36.73, 38.54), interval(29.83, 31.71),
                 interval(41.74, 45.37), interval(21.68, 23.96)]
        r = day_shift_certificate(cases)
        self.assertEqual(r["status"], "CERTIFIED_INCOMPATIBLE_WITH_INDEPENDENT_DATE_SHIFTS")
        self.assertGreater(r["separation_after_expansion_km"], 0)
        self.assertGreater(r["infimum_offset_days_before_common_H_possible"], 3.0)
        self.assertFalse(r["active_constraint"])

    def test_second_variant_still_incompatible(self):
        cases = [interval(33.74, 35.41), interval(28.51, 30.31),
                 interval(25.39, 27.59), interval(21.68, 23.96)]
        r = day_shift_certificate(cases)
        self.assertEqual(r["status"], "CERTIFIED_INCOMPATIBLE_WITH_INDEPENDENT_DATE_SHIFTS")
        self.assertGreater(r["infimum_offset_days_before_common_H_possible"], 2.0)

    def test_affine_threshold_on_simple_pair(self):
        cases = [interval(10, 11), interval(0, 1)]
        self.assertEqual(day_shift_certificate(cases, 1)["status"],
                         "CERTIFIED_INCOMPATIBLE_WITH_INDEPENDENT_DATE_SHIFTS")
        self.assertAlmostEqual(day_shift_certificate(cases, 1)
                               ["infimum_offset_days_before_common_H_possible"], 4.5)
        self.assertEqual(day_shift_certificate(cases, 5)["status"],
                         "INCONCLUSIVE_UNDER_DATE_SHIFTS")

    def test_touching_half_open_intervals_still_disjoint(self):
        cases = [interval(10, 11), interval(0, 1)]
        r = day_shift_certificate(cases, 4.5)
        self.assertEqual(r["status"], "CERTIFIED_INCOMPATIBLE_WITH_INDEPENDENT_DATE_SHIFTS")
        self.assertTrue(r["half_open_upper_endpoint"])

    def test_overlapping_intervals_not_falsified(self):
        r = day_shift_certificate([interval(3, 7), interval(4, 8)])
        self.assertEqual(r["status"], "INCONCLUSIVE_UNDER_DATE_SHIFTS")
        self.assertFalse(r["active_constraint"])

    def test_one_origin_cannot_be_a_holdout(self):
        self.assertEqual(day_shift_certificate([interval(40, 41)])["status"],
                         "NOT_ESTIMABLE_SINGLE_CUTOFF")

    def test_missing_cutoff_blocks_claim(self):
        missing = {"status": "NOT_ESTIMABLE", "required_H_km_UTC_DAY_COUNTERFACTUAL": None}
        self.assertEqual(day_shift_certificate([interval(3, 5), missing])["status"],
                         "NOT_ESTIMABLE_ALL_CUTOFFS")

    def test_bad_bounds_fail_closed(self):
        for v in (float("nan"), float("inf"), -1, True):
            with self.subTest(v=v), self.assertRaises(ValueError):
                day_shift_certificate([interval(1, 3), interval(5, 7)], v)
        for bad in (interval(-1, 1), interval(1, 1), interval(2, 1),
                    interval(math.nan, 3), interval(1, math.inf)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                day_shift_certificate([interval(2, 3), bad])

    def test_reordering_cannot_invent_compatibility(self):
        cases = [interval(36.73, 38.54), interval(21.68, 23.96),
                 interval(41.74, 45.37)]
        a = day_shift_certificate(cases)
        b = day_shift_certificate(cases[::-1])
        self.assertEqual(a["status"], b["status"])
        self.assertAlmostEqual(a["infimum_offset_days_before_common_H_possible"],
                               b["infimum_offset_days_before_common_H_possible"])

    def test_different_objects_never_share_a_common_H(self):
        self.assertEqual(day_shift_certificate([interval(40, 41)])["status"],
                         "NOT_ESTIMABLE_SINGLE_CUTOFF")


if __name__ == "__main__":
    unittest.main()
