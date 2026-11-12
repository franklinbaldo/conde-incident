"""Synthetic adversarial tests: not historical tracking observations."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from gaviao_ch13_recency_audit import audit, recent_forecasts, validated_rows, verify_published

BASE = datetime(1963, 1, 1, tzinfo=timezone.utc)

def corpus(days=(0, 1, 3, 6, 11, 17), values=None):
    if values is None:
        values = [15.0 + 0.01*d for d in days]
    return [(sat, BASE+timedelta(days=d), 14.0 if sat != 529 else v)
            for sat in (527, 528, 529) for d, v in zip(days, values)]

class IndependentRecentAudit(unittest.TestCase):
    def test_linear_irregular_epoch_secant_and_ols(self):
        out = audit(corpus())
        self.assertEqual((out["candidate_targets"], out["scored"], len(out["not_run"])), (5, 3, 2))
        self.assertLess(out["rmse_rev_day"]["secant_2"], 1e-11)
        self.assertLess(out["rmse_rev_day"]["ols_3"], 1e-11)
        self.assertTrue(out["cohort_eligibility_depends_on_donor_availability"])

    def test_future_target_cannot_enter_its_own_fit(self):
        rows = corpus()
        a = audit(rows)
        changed = [(s,t,v+2 if s==529 and t==BASE+timedelta(days=17) else v)
                   for s,t,v in rows]
        b = audit(changed)
        self.assertEqual(a["steps"][-1]["predictions"], b["steps"][-1]["predictions"])
        self.assertNotEqual(a["steps"][-1]["errors"], b["steps"][-1]["errors"])

    def test_real_utc_intervals_not_row_index(self):
        past = [(BASE+timedelta(days=d), 1+2*d) for d in (0,2,5)]
        predictions = recent_forecasts(past, BASE+timedelta(days=11))
        for value in predictions.values():
            self.assertAlmostEqual(value, 23, places=10)

    def test_alternating_noise_can_make_secant_worse_than_persistence(self):
        out = audit(corpus(values=[15,16,15,16,15,16]))
        self.assertGreater(out["rmse_rev_day"]["secant_2"], out["rmse_rev_day"]["persistence"])

    def test_conflicting_duplicate_is_not_hidden(self):
        rows = corpus()
        rows.append((529, rows[-1][1], rows[-1][2]+0.1))
        with self.assertRaisesRegex(ValueError, "conflicting"):
            validated_rows(rows)

    def test_identical_duplicate_does_not_multiply_scoring(self):
        rows = corpus()
        self.assertEqual(audit(rows+rows)["scored"], audit(rows)["scored"])

    def test_naive_and_nonfinite_are_rejected(self):
        rows = corpus()
        rows[-1] = (529, BASE.replace(tzinfo=None), 15.)
        with self.assertRaisesRegex(ValueError, "invalid"):
            audit(rows)
        rows = corpus()
        rows[-1] = (529, rows[-1][1], float("nan"))
        with self.assertRaisesRegex(ValueError, "invalid"):
            audit(rows)

    def test_missing_donor_does_not_forge_complete_cohort(self):
        rows = [x for x in corpus() if x[0] != 527]
        with self.assertRaisesRegex(ValueError, "missing"):
            audit(rows)
        rows = [x for x in corpus() if x[0] != 527 or x[1] == BASE]
        self.assertEqual(audit(rows)["scored"], 0)

    def test_unordered_and_short_history_rejected(self):
        past = [(BASE+timedelta(days=i), 15.+i) for i in (0,1,3)]
        with self.assertRaisesRegex(ValueError, "insufficient"):
            recent_forecasts(past, BASE+timedelta(days=3))
        with self.assertRaisesRegex(ValueError, "insufficient"):
            recent_forecasts(past[:2], BASE+timedelta(days=4))

    def test_fabricated_published_counts_rejected(self):
        with self.assertRaisesRegex(ValueError, "cohort"):
            verify_published({"candidate_targets": 1, "scored": 0, "not_run": [1]})

    def test_horizon_groups_disjoint_and_leave_one_target_out(self):
        out = audit(corpus())
        self.assertEqual(sum(v["count"] for v in out["by_horizon"].values()), out["scored"])
        self.assertEqual(out["leave_one_target_out"]["evaluated"], out["scored"])

    def test_no_historical_physical_conclusion(self):
        out = audit(corpus())
        self.assertEqual(out["conde"], "INDETERMINATE")
        self.assertFalse(out["admissible_physical_domain_reduced"])
        self.assertEqual(out["terminal_simulator_holdout"], "NOT_RUN")
        self.assertEqual(out["provenance_independence"], "SINGLE_SECONDARY_MIRROR")

if __name__ == "__main__":
    unittest.main()
