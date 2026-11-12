"""SYNTHETIC, not NORAD data: full-pipeline single-epoch deletion controls."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from texugo_holdout_529 import Observation
from texugo_influence_529 import direction, evaluate_influence, run


def artificial():
    first = datetime(1963, 7, 1, tzinfo=timezone.utc)
    rows = []
    for sat, c in ((527, 0.10), (528, 0.55), (529, 0.10)):
        for day in range(0, 171, 6):
            x = day / 60.0
            rows.append(Observation(sat, first + timedelta(days=day),
                                    15.0 + sat / 10000.0 + .01*x + c*x*x))
    return rows


class SingleEpochFalsifiers(unittest.TestCase):
    def test_every_omission_is_prior_to_cutoff_and_counted(self):
        r = evaluate_influence(artificial(), "1963-10-21")
        self.assertEqual(r["status"], "EVALUATED_POST_HOC")
        cutoff = datetime(1963, 10, 21, 23, 59, 59, tzinfo=timezone.utc)
        self.assertTrue(r["trials"])
        for sat in (527, 528, 529):
            self.assertEqual(r["by_deleted_sat"][str(sat)]["prior_epochs"],
                             sum(t["removed_sat"] == sat for t in r["trials"]))
        for trial in r["trials"]:
            self.assertLessEqual(datetime.fromisoformat(trial["removed_epoch_utc"]), cutoff)
            self.assertIn(trial["status"], ("NOT_RUN", "EVALUATED_RETROSPECTIVE"))

    def test_single_catalog_epoch_removed_without_future_leakage(self):
        rows = artificial()
        original = evaluate_influence(rows, "1963-10-21")
        cutoff = datetime(1963, 10, 21, 23, 59, 59, tzinfo=timezone.utc)
        damaged = [Observation(o.sat, o.epoch, o.mean_motion + 2.0)
                   if o.sat == 529 and o.epoch > cutoff else o for o in rows]
        altered = evaluate_influence(damaged, "1963-10-21")
        # No held-out observation may enter the inner selector or its selection.
        self.assertEqual(original["reference"]["selected_model_without_outer_holdout"],
                         altered["reference"]["selected_model_without_outer_holdout"])
        self.assertEqual(
            [(t["removed_sat"], t["removed_epoch_utc"],
              t.get("selected_model_without_outer_holdout")) for t in original["trials"]],
            [(t["removed_sat"], t["removed_epoch_utc"],
              t.get("selected_model_without_outer_holdout")) for t in altered["trials"]])
        # The measured OUTER error must change when the outer truth is altered.
        self.assertNotEqual(original["reference"]["donor528_minus_quadratic_rev_day"],
                            altered["reference"]["donor528_minus_quadratic_rev_day"])

    def test_donor527_deletion_cannot_change_528_only_or_quadratic_fits(self):
        r = evaluate_influence(artificial(), "1963-10-21")
        expected = r["reference"]["donor528_minus_quadratic_rev_day"]
        for trial in r["trials"]:
            if trial["removed_sat"] == 527 and trial["status"] == "EVALUATED_RETROSPECTIVE":
                self.assertAlmostEqual(trial["donor528_minus_quadratic_rev_day"], expected, places=9)

    def test_result_not_promoted_to_probability_or_geolocation(self):
        r = run(artificial())
        self.assertTrue(r["no_probability"])
        self.assertTrue(r["no_geolocation"])
        self.assertEqual(len(r["results"]), 4)
        self.assertIn("POST_HOC", r["status"])
        self.assertNotIn("Conde", str(r))

    def test_insufficient_data_stays_not_run(self):
        self.assertEqual(evaluate_influence(artificial()[:4], "1963-10-21")["status"], "NOT_RUN")
        self.assertEqual(direction(-0.01), "BETTER")
        self.assertEqual(direction(0.01), "WORSE")
        self.assertEqual(direction(0), "TIE")


if __name__ == "__main__":
    unittest.main()
