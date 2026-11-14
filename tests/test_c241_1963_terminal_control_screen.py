"""Adversarial tests: catalogue screening must never invent calibrated reentry times."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c241_1963_terminal_control_screen import (  # noqa: E402
    CASES, collect_pinned, parsed_row, screen, unique_epochs,
)


def item(sid: int, day: int = 1, n: float = 16.0):
    return parsed_row({
        "norad_id": sid, "epoch": datetime(1963, 10, day, tzinfo=timezone.utc),
        "mean_motion": n, "eccentricity": 0.001,
        "inclination": 70.0, "raan": 28.0, "intl_designator": "63000  A",
    }, day)


def example():
    return {sid: [item(sid, 1), item(sid, 2, 16.1)] for sid in CASES}


class ScreenTests(unittest.TestCase):
    def test_no_calibrated_holdout_even_with_two_epochs_everywhere(self):
        data = screen(example(), pin_counts=False)
        self.assertEqual(data["archive_search_priority_norad"], [292, 308, 565, 668])
        self.assertEqual(data["inference"]["historical_mcmc"], "NOT_RUN")
        self.assertFalse(data["inference"]["active_constraint_528"])
        self.assertIsNone(data["inference"]["reentry_time_sigma_hours"])
        self.assertIsNone(data["inference"]["impact_probability"])
        self.assertTrue(all(not x["terminal_holdout_ready"] for x in data["cases"]))
        self.assertEqual(sum(x["instrumental_lineages_independently_authenticated"]
                             for x in data["cases"]), 0)

    def test_one_epoch_688_stays_non_estimable(self):
        groups = example()
        groups[688] = groups[688][:1]
        result = screen(groups, pin_counts=False)
        row = next(x for x in result["cases"] if x["norad"] == 688)
        self.assertEqual(row["within_object_local_secant"], "ONE_EPOCH_NO_SLOPE")
        self.assertEqual(row["terminal_evidence_grade"], "AF_IN_23784_INTERVAL_2210_2400Z")
        self.assertTrue(row["terminal_date_utc_convention_verified"])
        self.assertFalse(row["terminal_holdout_ready"])

    def test_duplicate_same_epoch_does_not_increase_count(self):
        groups = example()
        duplicate = deepcopy(groups[292][0])
        duplicate["source_row"] = 987
        groups[292].append(duplicate)
        result = screen(groups, pin_counts=False)
        row = next(x for x in result["cases"] if x["norad"] == 292)
        self.assertEqual(row["catalogue_raw_rows"], 3)
        self.assertEqual(row["catalogue_unique_epochs"], 2)
        self.assertEqual(row["conditional_pre_day_epoch_count"], 2)

    def test_conflicting_duplicate_rejected(self):
        groups = example()
        duplicate = deepcopy(groups[292][0])
        duplicate["mean_motion"] += 0.1
        groups[292].append(duplicate)
        with self.assertRaisesRegex(ValueError, "conflicting"):
            screen(groups, pin_counts=False)

    def test_different_designators_cannot_be_pooled(self):
        rows = [item(292), item(292, 2)]
        rows[1]["intl_designator"] = "63000  B"
        with self.assertRaisesRegex(ValueError, "designator changed"):
            unique_epochs(rows, 292)

    def test_no_future_rows_allowed_to_train(self):
        groups = example()
        groups[292].append(item(292, 29, 17.2))
        data = screen(groups, pin_counts=False)
        entry = next(x for x in data["cases"] if x["norad"] == 292)
        # October 29 is still *before* the Nov 26 archival lead.
        self.assertEqual(entry["conditional_pre_day_epoch_count"], 3)
        # But October 30 is AFTER the October 30 hypothetical UTC boundary.
        groups[308].append(item(308, 30, 17.2))
        entry = next(x for x in screen(groups, pin_counts=False)["cases"]
                     if x["norad"] == 308)
        self.assertEqual(entry["conditional_pre_day_epoch_count"], 2)
        self.assertEqual(entry["excluded_at_or_after_assumed_utc_boundary"], 1)
        self.assertEqual(entry["latest_pre_day_source_row"], 2)

    def test_never_use_target_as_archive_candidate(self):
        data = screen(example(), pin_counts=False)
        self.assertNotIn(528, data["archive_search_priority_norad"])
        self.assertNotIn(688, data["archive_search_priority_norad"])
        self.assertNotIn(637, data["archive_search_priority_norad"])

    def test_missing_object_or_cross_object_is_fail_closed(self):
        groups = example()
        del groups[668]
        with self.assertRaisesRegex(ValueError, "object set"):
            screen(groups, pin_counts=False)
        groups = example()
        groups[668][0]["norad_id"] = 528
        with self.assertRaisesRegex(ValueError, "cross-object"):
            screen(groups, pin_counts=False)

    def test_count_lock_requires_actual_pinned_dataset(self):
        with self.assertRaisesRegex(ValueError, "count drift"):
            screen(example(), pin_counts=True)

    def test_bad_datetime_and_numeric_inputs(self):
        valid = {"norad_id": 308, "epoch": datetime(1963, 10, 1, tzinfo=timezone.utc),
                 "mean_motion": 16.0, "eccentricity": 0.01, "inclination": 40.0,
                 "raan": 5.0, "intl_designator": "63000  A"}
        for field, value in (("epoch", datetime(1963, 10, 1)),
                             ("epoch", datetime(1962, 10, 1, tzinfo=timezone.utc)),
                             ("mean_motion", 0.0), ("mean_motion", float("nan")),
                             ("mean_motion", True), ("eccentricity", 1.0),
                             ("raan", 360), ("intl_designator", " ")):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                parsed_row({**valid, field: value}, 1)

    def test_mutated_parquet_rejected_before_pyarrow(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "untrusted.parquet"
            p.write_bytes(b"unverified byte sequence")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                collect_pinned(p)

    def test_reentry_not_inferred_from_kepler_perigee(self):
        data = screen(example(), pin_counts=False)
        for case in data["cases"]:
            self.assertIn("NOT_OBSERVED", next(k for k in case if k.startswith("last_kepler_perigee")))
            self.assertFalse(case["terminal_holdout_ready"])
            self.assertFalse(case["terminal_time_error_calibrated"])


if __name__ == "__main__":
    unittest.main()
