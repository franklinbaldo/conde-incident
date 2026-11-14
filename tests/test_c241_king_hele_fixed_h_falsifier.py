"""Adversarial synthetic tests for the fixed-H date-window counterfactual."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c241_king_hele_fixed_h_falsifier import (  # noqa: E402
    civil_day_utc_counterfactual, required_h_for_one_origin, intersection, report,
    common_h_under_day_shift,
)

UTC = timezone.utc
DAY = "1963-11-07"
CUTOFF = "1963-11-05T00:00:00+00:00"


def observation(day: int, motion: float, row: int | None = None) -> dict:
    return {"epoch": datetime(1963, 10, 1, tzinfo=UTC) + timedelta(days=day),
            "mean_motion": motion, "source_row": day if row is None else row}


def status_interval(low: float, high: float) -> dict:
    return {"status": "COUNTERFACTUAL_INTERVAL_ONLY",
            "required_H_km_UTC_DAY_COUNTERFACTUAL": [low, high]}


def moving_interval(low: float, high: float, velocity: float) -> dict:
    return {**status_interval(low, high),
            "decay_magnitude_km_day_LOCAL_PROXY": velocity}


class FixedHTests(unittest.TestCase):
    def setUp(self):
        self.rows = [observation(3*i, 15.0 + 0.03*i) for i in range(11)]

    def test_no_time_is_inferred_from_day_label(self):
        start, end = civil_day_utc_counterfactual(DAY)
        self.assertEqual((end - start).total_seconds(), 86400)
        self.assertEqual(start.tzinfo, UTC)
        for wrong in ("1963-11-07T12:00:00", "1963-11-7", "1963-13-07"):
            with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                civil_day_utc_counterfactual(wrong)

    def test_cutoff_exclusive_and_future_cannot_affect_H(self):
        before = required_h_for_one_origin(self.rows, CUTOFF, DAY, "last_two")
        altered = self.rows + [observation(70, 100.0)]
        self.assertEqual(before, required_h_for_one_origin(altered, CUTOFF, DAY, "last_two"))
        self.assertEqual(before["status"], "COUNTERFACTUAL_INTERVAL_ONLY")
        self.assertLess(before["required_H_km_UTC_DAY_COUNTERFACTUAL"][0],
                        before["required_H_km_UTC_DAY_COUNTERFACTUAL"][1])

    def test_non_decaying_secant_rejected(self):
        rows = [observation(0, 16), observation(1, 15.9)]
        actual = required_h_for_one_origin(rows, CUTOFF, DAY, "last_two")
        self.assertEqual(actual["status"], "NOT_ESTIMABLE_NON_DECAYING_SECANT")
        self.assertIsNone(actual["required_H_km_UTC_DAY_COUNTERFACTUAL"])

    def test_median_needs_four_earlier_epochs(self):
        rows = self.rows[:3]
        record = required_h_for_one_origin(rows, CUTOFF, DAY, "median_three")
        self.assertEqual(record["status"], "NOT_ESTIMABLE_FEWER_PRIOR_EPOCHS")

    def test_epoch_after_terminal_day_is_not_used(self):
        rows = [observation(38, 16), observation(39, 16.01)]
        record = required_h_for_one_origin(
            rows, "1963-11-15T00:00:00+00:00", DAY, "last_two")
        self.assertEqual(record["status"], "NOT_ESTIMABLE_ORIGIN_NOT_BEFORE_DAY_END")

    def test_reject_unsupported_slope_variant(self):
        with self.assertRaises(ValueError):
            required_h_for_one_origin(self.rows, CUTOFF, DAY, "least_squares_after_label")

    def test_intersection_cross_cutoff_falsification(self):
        records = [status_interval(11, 24), status_interval(25, 48)]
        test = intersection(records, (40, 50))
        self.assertEqual(test["status"], "EMPTY_INTERSECTION_CONDITIONAL_FIXED_H")
        self.assertIsNone(test["intersection_all_cutoffs_km"])

    def test_half_open_intervals_touching_boundary_are_disjoint(self):
        records = [status_interval(0, 40), status_interval(40, 50)]
        self.assertEqual(intersection(records, (30, 50))["status"],
                         "EMPTY_INTERSECTION_CONDITIONAL_FIXED_H")

    def test_common_H_but_outside_stress_range_is_not_a_rejection(self):
        records = [status_interval(2, 18), status_interval(10, 20)]
        test = intersection(records, (40, 50))
        self.assertEqual(test["status"], "NO_H_IN_STRESS_RANGE_CONDITIONAL_FIXED_H")
        self.assertEqual(test["intersection_all_cutoffs_km"], [10, 18])
        self.assertIsNone(test["intersection_with_H_stress_km"])

    def test_common_H_within_stress_range(self):
        test = intersection([status_interval(34, 49), status_interval(41, 55)],
                            (40, 50))
        self.assertEqual(test["intersection_all_cutoffs_km"], [41, 49])
        self.assertEqual(test["intersection_with_H_stress_km"], [41, 49])

    def test_one_missing_origin_cannot_be_dropped(self):
        missing = {"status": "NOT_ESTIMABLE_FEWER_PRIOR_EPOCHS",
                   "required_H_km_UTC_DAY_COUNTERFACTUAL": None}
        test = intersection([status_interval(42, 44), missing], (40, 50))
        self.assertEqual(test["status"], "NOT_ESTIMABLE_ALL_CUTOFFS")
        self.assertIsNone(test["intersection_all_cutoffs_km"])
        self.assertEqual(test["cutoffs_estimable"], 1)

    def test_invalid_stress_range_rejected(self):
        for bounds in ((50, 40), (0, 50), (40, 40)):
            with self.subTest(bounds=bounds), self.assertRaises(ValueError):
                intersection([status_interval(40, 60)], bounds)

    def test_duplicate_source_epoch_rejected(self):
        with self.assertRaises(ValueError):
            required_h_for_one_origin(self.rows[:2] + [self.rows[1]],
                                      CUTOFF, DAY, "last_two")

    def test_report_stays_uncalibrated_and_no_cross_object_H(self):
        result = report({637: self.rows, 528: self.rows})
        self.assertEqual(set(result["objects"]), {"528", "637"})
        self.assertEqual(len(result["objects"]["637"]["source_cutoffs_frozen"]), 4)
        self.assertEqual(len(result["objects"]["528"]["source_cutoffs_frozen"]), 1)
        self.assertFalse(result["inference"]["active_constraint"])
        self.assertFalse(result["inference"]["H_empirically_calibrated"])
        self.assertFalse(result["inference"]["physical_model_falsified"])
        self.assertIsNone(result["inference"]["terminal_time_sigma_hours"])
        self.assertIsNone(result["inference"]["impact_geography"])
        self.assertEqual(result["inference"]["historical_mcmc"], "NOT_RUN")
        self.assertTrue(result["assumptions"]["different_objects_not_forced_to_share_H"])

    def test_missing_object_rejected(self):
        with self.assertRaises(ValueError):
            report({528: self.rows})


    def test_clock_shift_has_no_effect_when_velocities_equal(self):
        records = [moving_interval(1, 2, 24), moving_interval(2, 3, 24)]
        result = common_h_under_day_shift(records, -24, 24)
        self.assertEqual(result["status"],
                         "NO_COMMON_H_FOR_ANY_SHIFT_IN_STRESS_WINDOW")
        self.assertIsNotNone(result["incompatible_pair_witness"])
        self.assertEqual(result["incompatible_pair_witness"]
                         ["max_upper_minus_lower_km_over_shift_range"], 0)

    def test_shift_can_rescue_only_as_assumption(self):
        # x=shift hours: [1+x, 2+x) vs [2+2x, 3+2x).
        # A common positive H exists for -1 < x < 0 in [-1,0].
        records = [moving_interval(1, 2, 24), moving_interval(2, 3, 48)]
        result = common_h_under_day_shift(records, -1, 0)
        self.assertEqual(result["status"], "FEASIBLE_ONLY_IN_ASSUMED_SHIFT_MODEL")
        self.assertEqual(result["feasible_shift_hours"], [-1, 0.0])
        self.assertEqual(result["feasible_shift_endpoints_inclusive"], [True, False])
        self.assertFalse(result["calibrated_timezone"])
        self.assertEqual(common_h_under_day_shift(records, 0, 24)["status"],
                         "NO_COMMON_H_FOR_ANY_SHIFT_IN_STRESS_WINDOW")

    def test_boundary_touch_never_becomes_positive_overlap(self):
        records = [moving_interval(3, 4, 24), moving_interval(4, 5, 24)]
        for x in (-3, 0, 3):
            with self.subTest(shift=x):
                self.assertEqual(common_h_under_day_shift(records, x, x)["status"],
                                 "NO_COMMON_H_FOR_ANY_SHIFT_IN_STRESS_WINDOW")

    def test_positive_height_constraint_included(self):
        # Both intervals would overlap after -2h, but both are nonpositive.
        records = [moving_interval(1, 2, 24), moving_interval(1, 2, 24)]
        self.assertEqual(common_h_under_day_shift(records, -4, -2)["status"],
                         "NO_COMMON_H_FOR_ANY_SHIFT_IN_STRESS_WINDOW")
        self.assertEqual(common_h_under_day_shift(records, -1, 0)["status"],
                         "FEASIBLE_ONLY_IN_ASSUMED_SHIFT_MODEL")

    def test_missing_origin_prevents_clock_shift_rescue(self):
        records = [moving_interval(1, 2, 24),
                   {"status": "NOT_ESTIMABLE_FEWER_PRIOR_EPOCHS"}]
        result = common_h_under_day_shift(records, -14, 14)
        self.assertEqual(result["status"], "NOT_ESTIMABLE_ALL_CUTOFFS")
        self.assertIsNone(result["feasible_shift_hours"])

    def test_bad_shift_bounds_and_degeneracies_rejected(self):
        import math
        records = [moving_interval(1, 2, 24)]
        for low, high in ((4, -4), (math.nan, 1), (-1, math.inf)):
            with self.subTest(bounds=(low, high)), self.assertRaises(ValueError):
                common_h_under_day_shift(records, low, high)
        for bad in (moving_interval(-1, 1, 24),
                    moving_interval(1, 1, 24),
                    moving_interval(1, 2, 0),
                    moving_interval(1, 2, math.nan)):
            with self.subTest(record=bad), self.assertRaises(ValueError):
                common_h_under_day_shift([bad], -14, 14)

    def test_real_report_structure_never_claims_terminal_posterior(self):
        result = report({637: self.rows, 528: self.rows})
        for obj in result["objects"].values():
            for variant in obj["variants"].values():
                stress = variant["day_boundary_shift_stress"]
                self.assertEqual(set(stress), {"plus_minus_14h", "plus_minus_24h"})
                self.assertFalse(stress["plus_minus_14h"]["calibrated_timezone"])
        self.assertEqual(result["inference"]["historical_mcmc"], "NOT_RUN")
        self.assertIsNone(result["inference"]["impact_geography"])



if __name__ == "__main__":
    unittest.main()
