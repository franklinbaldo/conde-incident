"""R60 guards: no pseudoreplication or promotion of secondary dates."""
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c241_1963_archive_fixed_h_stress import (
    CANDIDATES, METHODS, OFFSETS_DAYS, evaluate, report)
from c241_king_hele_fixed_h_falsifier import required_h_for_one_origin


def rows(count=12):
    day = datetime(1963, 10, 30, tzinfo=timezone.utc)
    return [{"epoch": day - timedelta(days=25-2*i),
             "mean_motion": 15.7 + .02*i, "source_row": i}
            for i in range(count)]


class R60Tests(unittest.TestCase):
    def test_frozen_design_no_target(self):
        self.assertEqual(CANDIDATES, (292, 308, 565, 668))
        self.assertEqual(OFFSETS_DAYS, (14, 10, 6, 3))
        self.assertEqual(METHODS, ("last_two", "median_three"))
        self.assertNotIn(528, CANDIDATES)

    def test_both_methods_all_cutoffs_preterminal(self):
        for method in METHODS:
            with self.subTest(method=method):
                x = evaluate(rows(), "1963-10-30", method)
                self.assertEqual(len(x["attempts"]), 4)
                self.assertEqual(x["duplicate_cutoffs_coalesced"], 0)
                self.assertTrue(all(a["origin_utc"] < a["cutoff_utc"]
                                    for a in x["attempts"]))

    def test_repeated_origin_not_independent(self):
        x = evaluate(rows(9), "1963-10-30", "last_two")
        self.assertGreater(x["duplicate_cutoffs_coalesced"], 0)
        self.assertEqual(x["distinct_catalogue_origins"]
                         + x["duplicate_cutoffs_coalesced"], 4)

    def test_one_origin_cannot_falsify(self):
        x = evaluate(rows(3), "1963-10-30", "last_two")
        self.assertEqual(x["distinct_catalogue_origins"], 1)
        self.assertEqual(x["common_clock_24h"]["status"],
                         "NOT_ESTIMABLE_FEWER_DISTINCT_ORIGINS")

    def test_median_incomplete_is_not_pass(self):
        x = evaluate(rows(5), "1963-10-30", "median_three")
        self.assertTrue(x["common_clock_24h"]["status"].startswith("NOT_ESTIMABLE"))

    def test_non_decaying_slope_not_estimable(self):
        data = rows()
        for row in data:
            row["mean_motion"] = 16.
        x = evaluate(data, "1963-10-30", "last_two")
        self.assertTrue(x["common_clock_24h"]["status"].startswith("NOT_ESTIMABLE"))

    def test_no_postcutoff_leakage(self):
        data = rows()
        data.append({"epoch": datetime(1963, 11, 1, tzinfo=timezone.utc),
                     "mean_motion": 900, "source_row": 400})
        x = evaluate(data, "1963-10-30", "last_two")
        self.assertTrue(all(a["origin_utc"] < "1963-10-30"
                            for a in x["attempts"]))

    def test_unknown_method_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(rows(), "1963-10-30", "best_posthoc")

    def test_conflicting_duplicate_cannot_be_coalesced(self):
        original = required_h_for_one_origin
        n = 0
        def mutated(*args):
            nonlocal n
            x = original(*args)
            n += 1
            if n == 2:
                x["decay_magnitude_km_day_LOCAL_PROXY"] += 1
            return x
        with patch("c241_1963_archive_fixed_h_stress.required_h_for_one_origin",
                   side_effect=mutated):
            with self.assertRaisesRegex(ValueError, "conflicting"):
                evaluate(rows(3), "1963-10-30", "last_two")

    def test_secondary_label_must_not_be_promoted(self):
        import c241_1963_archive_fixed_h_stress as mod
        with patch.dict(mod.CASES, {292: ("1963-11-26", "x",
                                         "PRIMARY_TERMINAL", "CANDIDATE")}):
            with patch.object(mod, "screen", return_value={
                "source": {}, "cases": [{"terminal_holdout_ready": False}]}):
                with self.assertRaisesRegex(ValueError, "promoted"):
                    report({292: []}, pinned=False)


if __name__ == "__main__":
    unittest.main()
