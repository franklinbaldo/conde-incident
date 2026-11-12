"""Adversarial synthetic controls for Gavião independent C243-T8/T9 audit."""
import hashlib
import math
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from gaviao_ch10_independent import (
    CUTS, SOURCE_SHA256, Datum, assert_pinned_result, cutoff, read_parquet,
    regress, validate_and_score,
)


def dt(day):
    return datetime.fromisoformat(day + "T12:00:00+00:00")


def synthetic():
    old = ("1963-02-01", "1963-03-15", "1963-04-30", "1963-06-01",
           "1963-07-21", "1963-08-20")
    future = ("1963-09-01", "1963-10-01", "1963-10-15", "1963-11-01")
    start = dt("1963-01-01")
    items = []
    for sat, curvature in ((527, 0.18), (528, 0.40), (529, 0.22)):
        for day in old + (future if sat == 529 else ()):
            stamp = dt(day)
            x = (stamp - start).total_seconds() / (86400 * 60)
            items.append(Datum(sat, stamp, 15 + .1 * x + curvature * x * x))
    return items


class IndependentCh10Tests(unittest.TestCase):
    def test_disjoint_vs_nested_scores_independent_count(self):
        result = validate_and_score(synthetic())
        self.assertEqual(result["overlapping_score_uses"], 10)
        self.assertEqual(result["unique_future_epochs"], 4)
        self.assertEqual([seg["count"] for seg in result["segments"]], [1, 1, 1, 1])
        self.assertTrue(result["no_physical_localization"])

    def test_weighted_squared_loss_not_arithmetic_mean_of_rmse(self):
        # Pinned published table only: consistency test, NOT a Parquet replay.
        n = (4, 3, 1, 20)
        q = (0.010525039, 0.010711596, 0.018127297, 0.223236815)
        shared = (0.011014283, 0.009848541, 0.016582726, 0.215116674)
        pooled = lambda vals: math.sqrt(math.fsum(k * v * v for k, v in zip(n, vals)) / 28)
        self.assertAlmostEqual(pooled(q), 0.188775134, places=8)
        self.assertAlmostEqual(pooled(shared), 0.181909995, places=8)
        self.assertGreater(pooled(q), sum(q) / 4)
        q_sse = math.fsum(k*v*v for k,v in zip(n,q))
        j_sse = math.fsum(k*v*v for k,v in zip(n,shared))
        self.assertGreater(20*q[-1]**2/q_sse, 0.998)
        self.assertGreater(20*shared[-1]**2/j_sse, 0.998)
        self.assertGreater(20*(q[-1]**2-shared[-1]**2)/(q_sse-j_sse), 0.999)

    def test_first_segment_does_not_consume_later_529_future(self):
        orig = validate_and_score(synthetic())
        modified = [Datum(z.sat, z.epoch, z.n + 4)
                    if z.sat == 529 and z.epoch == dt("1963-11-01") else z
                    for z in synthetic()]
        newer = validate_and_score(modified)
        self.assertAlmostEqual(orig["segments"][0]["rmse_rev_day"]["quadratic"],
                               newer["segments"][0]["rmse_rev_day"]["quadratic"])
        self.assertNotAlmostEqual(orig["segments"][3]["rmse_rev_day"]["quadratic"],
                                  newer["segments"][3]["rmse_rev_day"]["quadratic"])

    def test_regression_svd_reconstructs_synthetic_curvature(self):
        base = dt("1963-08-31")
        target = [d for d in synthetic() if d.sat == 529 and d.epoch < base]
        coefs = regress(target, base, 2)
        self.assertAlmostEqual(coefs[2], .22, places=10)

    def test_duplicate_epoch_fails_closed(self):
        entries = synthetic()
        with self.assertRaisesRegex(ValueError, "repeated epoch"):
            validate_and_score(entries + [entries[-1]])

    def test_missing_donor_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            validate_and_score([d for d in synthetic() if d.sat != 527])

    def test_naive_datetime_fails_closed(self):
        entries = synthetic()
        entries[0] = Datum(527, datetime(1963,2,1), entries[0].n)
        with self.assertRaisesRegex(ValueError, "timezone"):
            validate_and_score(entries)

    def test_nonfinite_mean_motion_fails_closed(self):
        entries = synthetic()
        entries[0] = Datum(527, entries[0].epoch, float("nan"))
        with self.assertRaisesRegex(ValueError, "invalid input"):
            validate_and_score(entries)

    def test_insufficient_training_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "cutoff cannot"):
            validate_and_score([d for d in synthetic() if
                                d.sat != 527 or d.epoch >= dt("1963-07-21")])

    def test_mutated_parquet_is_rejected_before_parsing(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            read_parquet(b"PAR1this-is-not-the-sourcePAR1")

    def test_expected_historical_claims_not_satisfied_by_fixture(self):
        with self.assertRaises(AssertionError):
            assert_pinned_result(validate_and_score(synthetic()))

    def test_cutoff_is_not_observed_reentry_time(self):
        self.assertEqual(CUTS[-1], "1963-10-21")
        self.assertEqual(cutoff(CUTS[0]).tzinfo, timezone.utc)


if __name__ == "__main__":
    unittest.main()
