"""SYNTHETIC controls for target rotation, never historical NORAD evidence."""
from __future__ import annotations
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from texugo_holdout_529 import Observation, evaluate
from texugo_rotate_target import evaluate_target, run


def artificial(curvatures=(.1, .1, .1)):
    first = datetime(1963, 7, 1, tzinfo=timezone.utc)
    return [
        Observation(sat, first + timedelta(days=day),
                    15 + sat / 10000 + .01 * day / 60 + curve * (day / 60) ** 2)
        for sat, curve in zip((527, 528, 529), curvatures)
        for day in range(0, 171, 6)
    ]


class TargetRotationFalsification(unittest.TestCase):
    def test_all_three_targets_and_four_original_cutoffs(self):
        report = run(artificial())
        self.assertEqual(len(report["results"]), 12)
        self.assertEqual({x["target_norad_id"] for x in report["results"]}, {527, 528, 529})
        self.assertTrue(report["no_probability"] and report["no_geolocation"])
        self.assertTrue(report["no_new_primary_evidence"])
        self.assertTrue(all(x["source_independence"].startswith("ONE SECONDARY")
                            for x in report["results"]))

    def test_shared_identical_curvatures_are_not_false_physical_proof(self):
        for target in (527, 528, 529):
            result = evaluate_target(artificial(), "1963-10-21", target)
            self.assertEqual(result["status"], "EVALUATED_POST_HOC")
            self.assertLess(result["outer_rmse_rev_day"]["equal_other_two_curvature"], 1e-8)
            self.assertTrue(result["interpretation"].startswith("POST_HOC"))

    def test_divergent_donor_curvature_can_be_worse_for_every_target(self):
        rows = artificial((.1, .55, .1))
        for target in (527, 528, 529):
            result = evaluate_target(rows, "1963-10-21", target)
            self.assertEqual(result["status"], "EVALUATED_POST_HOC")
            self.assertGreater(result["joint_minus_quadratic_rmse_rev_day"], 0.01)
            self.assertEqual(result["joint_direction"], "BASELINE_BETTER")

    def test_target_future_is_never_used_by_fit(self):
        rows = artificial((.1, .55, .1))
        cutoff = datetime(1963, 10, 21, 23, 59, 59, tzinfo=timezone.utc)
        changed = [Observation(o.sat, o.epoch, o.mean_motion + 3)
                   if o.sat == 529 and o.epoch > cutoff else o for o in rows]
        before = evaluate_target(rows, "1963-10-21", 529)
        after = evaluate_target(changed, "1963-10-21", 529)
        self.assertEqual(before["fit_coefficients"], after["fit_coefficients"])
        self.assertNotEqual(before["outer_rmse_rev_day"], after["outer_rmse_rev_day"])
        for target in (527, 528):
            self.assertEqual(evaluate_target(rows, "1963-10-21", target),
                             evaluate_target(changed, "1963-10-21", target))

    def test_original_529_scores_are_preserved(self):
        for day in ("1963-08-31", "1963-09-28", "1963-10-11", "1963-10-21"):
            rotated = evaluate_target(artificial(), day, 529)
            original = evaluate(artificial(), day)
            if rotated["status"] == "NOT_RUN":
                self.assertEqual(original["status"], "NOT_RUN")
            else:
                self.assertAlmostEqual(rotated["outer_rmse_rev_day"]["quadratic_target_only"],
                                       original["holdout_rmse_rev_day"]["quadratic_529_only"], places=8)
                self.assertAlmostEqual(rotated["outer_rmse_rev_day"]["equal_other_two_curvature"],
                                       original["holdout_rmse_rev_day"]["shared_curvature_527_528_to_529"], places=8)

    def test_missing_target_future_and_missing_donor_return_not_run(self):
        rows = artificial()
        self.assertEqual(evaluate_target(rows, "1963-12-31", 527)["status"], "NOT_RUN")
        without_527 = [o for o in rows if o.sat != 527]
        self.assertEqual(evaluate_target(without_527, "1963-10-21", 528)["status"], "NOT_RUN")
        with self.assertRaises(ValueError):
            evaluate_target(rows, "1963-10-21", 999)


if __name__ == "__main__":
    unittest.main()
