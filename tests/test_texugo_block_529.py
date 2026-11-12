"""SYNTHETIC, not NORAD TLE: chronological multi-object block controls."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from texugo_holdout_529 import Observation
from texugo_block_529 import ANCHOR, prior_blocks, evaluate_blocks, run


def artificial():
    first = datetime(1963, 7, 1, tzinfo=timezone.utc)
    return [Observation(sat, first + timedelta(days=d),
                        15 + sat / 10000 + .01 * d / 60 + curvature * (d / 60) ** 2)
            for sat, curvature in ((527, .10), (528, .55), (529, .10))
            for d in range(0, 171, 6)]


class CalendarBlockFalsifiers(unittest.TestCase):
    def test_complete_partition_pre_cutoff_only(self):
        rows = artificial()
        cutoff = datetime(1963, 10, 21, 23, 59, 59, tzinfo=timezone.utc)
        for width in (14, 28):
            groups = prior_blocks(rows, cutoff, width)
            self.assertEqual(set(o for _, group in groups for o in group),
                             {o for o in rows if o.epoch <= cutoff})
            self.assertTrue(all(start == ANCHOR + timedelta(days=((start - ANCHOR).days // width) * width)
                                and all(start <= o.epoch < start + timedelta(days=width) for o in group)
                                for start, group in groups))

    def test_joint_deletion_tracks_all_satellites_and_not_runs(self):
        result = evaluate_blocks(artificial(), "1963-10-21", 14)
        self.assertEqual(result["status"], "EVALUATED_POST_HOC")
        self.assertGreater(result["multi_epoch_blocks"], 0)
        self.assertEqual(result["blocks_total"], result["blocks_evaluable"] + result["blocks_not_run"])
        self.assertTrue(any(all(t["removed_prior_by_sat"][str(s)] > 0 for s in (527, 528, 529))
                            for t in result["trials"]))
        for trial in result["trials"]:
            self.assertEqual(trial["removed_prior_total"], len(trial["removed_keys"]))
            self.assertEqual(trial["removed_prior_total"], sum(trial["removed_prior_by_sat"].values()))
            self.assertIn(trial["status"], ("NOT_RUN", "EVALUATED_RETROSPECTIVE"))

    def test_future_target_changes_errors_not_selector_or_deleted_training_keys(self):
        rows = artificial()
        cutoff = datetime(1963, 10, 21, 23, 59, 59, tzinfo=timezone.utc)
        before = evaluate_blocks(rows, "1963-10-21", 28)
        altered = [Observation(o.sat, o.epoch, o.mean_motion + 2)
                   if o.sat == 529 and o.epoch > cutoff else o for o in rows]
        after = evaluate_blocks(altered, "1963-10-21", 28)
        self.assertEqual(before["reference"]["selected_model_without_outer_holdout"],
                         after["reference"]["selected_model_without_outer_holdout"])
        for a, b in zip(before["trials"], after["trials"]):
            self.assertEqual(a["removed_keys"], b["removed_keys"])
            self.assertEqual(a.get("selected_model_without_outer_holdout"),
                             b.get("selected_model_without_outer_holdout"))
        self.assertNotEqual(before["reference"]["donor528_minus_quadratic_rev_day"],
                            after["reference"]["donor528_minus_quadratic_rev_day"])

    def test_synthetic_negative_joint_and_insufficient_data(self):
        self.assertGreater(evaluate_blocks(artificial(), "1963-10-21", 14)
                           ["reference"]["joint_minus_quadratic_rev_day"], 0)
        self.assertEqual(evaluate_blocks(artificial()[:4], "1963-10-21", 14)["status"], "NOT_RUN")
        with self.assertRaises(ValueError):
            prior_blocks(artificial(), datetime(1963, 10, 21, tzinfo=timezone.utc), 3)

    def test_no_probability_or_orbit_claims(self):
        report = run(artificial())
        self.assertTrue(report["no_probability"])
        self.assertTrue(report["no_geolocation"])
        self.assertEqual(len(report["results"]), 8)
        self.assertIn("POST_HOC", report["status"])


if __name__ == "__main__":
    unittest.main()
