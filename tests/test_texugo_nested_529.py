"""SYNTHETIC adversarial controls for nested chronological 529 selection."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from texugo_holdout_529 import Observation
from texugo_nested_529 import MODELS, evaluate_nested, run


def synthetic(c527=0.10, c528=0.55, c529=0.10):
    start = datetime(1963, 7, 1, tzinfo=timezone.utc)
    rows = []
    for sat, c in ((527, c527), (528, c528), (529, c529)):
        for day in range(0, 171, 6):
            x = day / 60
            rows.append(Observation(sat, start + timedelta(days=day),
                                    15.0 + sat / 10000 + 0.01 * x + c * x * x))
    return rows


class NestedBlindTests(unittest.TestCase):
    def test_inner_selection_and_outer_holdout_are_disjoint(self):
        r = evaluate_nested(synthetic(), "1963-10-21")
        self.assertEqual(r["status"], "EVALUATED_RETROSPECTIVE")
        self.assertIn(r["selected_model_without_outer_holdout"], MODELS)
        self.assertGreater(r["inner_validation_529_count"], 1)
        self.assertLess(r["inner_boundary_utc"], "1963-10-21T23:59:59")
        self.assertGreater(r["target_529_outer_holdout"], 0)

    def test_any_future_satellite_changes_scores_not_selection(self):
        rows = synthetic()
        before = evaluate_nested(rows, "1963-10-21")
        cutoff = datetime(1963, 10, 21, 23, 59, 59, tzinfo=timezone.utc)
        tampered = [Observation(o.sat, o.epoch, o.mean_motion + (9 if o.sat == 529 else 3))
                    if o.epoch > cutoff else o for o in rows]
        after = evaluate_nested(tampered, "1963-10-21")
        self.assertEqual(before["selected_model_without_outer_holdout"],
                         after["selected_model_without_outer_holdout"])
        self.assertEqual(before["inner_validation_rmse_rev_day"],
                         after["inner_validation_rmse_rev_day"])
        self.assertEqual(before["outer_train_counts"], after["outer_train_counts"])
        self.assertNotEqual(before["selected_outer_rmse_rev_day"],
                            after["selected_outer_rmse_rev_day"])

    def test_inner_donors_do_not_see_midperiod_or_future(self):
        rows = synthetic()
        before = evaluate_nested(rows, "1963-10-21")
        inner = datetime.fromisoformat(before["inner_boundary_utc"])
        tampered = [Observation(o.sat, o.epoch, o.mean_motion + 5)
                    if o.sat in (527, 528) and o.epoch > inner else o for o in rows]
        after = evaluate_nested(tampered, "1963-10-21")
        self.assertEqual(before["inner_validation_rmse_rev_day"],
                         after["inner_validation_rmse_rev_day"])
        self.assertEqual(before["selected_model_without_outer_holdout"],
                         after["selected_model_without_outer_holdout"])

    def test_missing_history_or_future_is_not_run(self):
        rows = synthetic()
        self.assertEqual(evaluate_nested(rows[:5], "1963-10-21")["status"], "NOT_RUN")
        cutoff = datetime(1963, 10, 21, 23, 59, 59, tzinfo=timezone.utc)
        past_only = [o for o in rows if o.epoch <= cutoff]
        self.assertEqual(evaluate_nested(past_only, "1963-10-21")["status"], "NOT_RUN")

    def test_hindsight_oracle_cannot_be_selected_as_rule(self):
        result = evaluate_nested(synthetic(), "1963-10-21")
        oracle = result["hindsight_oracle_only_not_admissible_model_selection"]
        self.assertLessEqual(oracle["outer_rmse_rev_day"], result["selected_outer_rmse_rev_day"] + 1e-12)
        self.assertGreaterEqual(oracle["selector_regret_rev_day"], 0)
        self.assertNotIn("oracle", result["selection_rule"])
        self.assertNotIn("probability", result)

    def test_full_report_does_not_claim_independence_or_geolocation(self):
        report = run(synthetic())
        self.assertTrue(report["no_probability"])
        self.assertTrue(report["no_geolocation"])
        self.assertIn("ONE secondary", report["source_independence"])
        self.assertEqual(len(report["results"]), 4)
        self.assertTrue(all(r["status"] in ("EVALUATED_RETROSPECTIVE", "NOT_RUN")
                            for r in report["results"]))


if __name__ == "__main__":
    unittest.main()
