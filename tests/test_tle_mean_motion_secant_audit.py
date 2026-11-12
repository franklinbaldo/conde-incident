"""C241-T11: SYNTHETIC controls only, never 1963 source observations."""
import csv
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tle_mean_motion_secant_audit import (
    CSV_SHA, audit, interval, normalize, read_rows, summary,
)

BASE = datetime(1963, 1, 1, tzinfo=timezone.utc)


def make(idx, days=0, n="15", dot="0.01", sat=528):
    day = BASE + timedelta(days=days)
    return {
        "source_row": str(idx), "norad_id": str(sat),
        "epoch": day.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "intl_designator": "1963-003B",
        "inclination": "80", "raan": "198.5261",
        "eccentricity": "0.001", "arg_perigee": "100",
        "mean_anomaly": "200", "mean_motion": str(n),
        "mean_motion_dot": str(dot), "bstar": "0",
    }


class MeanMotionSecantControls(unittest.TestCase):
    def test_negative_secant_despite_two_positive_dot_fields(self):
        report = audit([make(1, 0, "15", "0.1"),
                        make(2, 1, "14.9", "0.2")], "SYNTHETIC")
        pair = report["by_norad"]["528"]["per_adjacent_epoch"][0]
        self.assertEqual(pair["delta_mean_motion_rev_day"], "-0.1")
        self.assertEqual(pair["secant_rev_day2"], "-0.1")
        self.assertEqual(pair["naive_midpoint_delta_rev_day"], "0.3")
        self.assertEqual(pair["naive_midpoint_residual_rev_day"], "-0.4")
        self.assertTrue(pair["positive_encoded_dots_but_decreasing_n"])
        self.assertEqual(report["by_norad"]["528"]["up_to_24h"]["pairs"], 1)
        self.assertEqual(report["validated_simulation_or_holdout"], "NOT_RUN")

    def test_consistent_example_does_not_certify_physical_model(self):
        x = audit([make(1, 0, "15", "0.1"),
                   make(2, 1, "15.2", "0.1")], "SYNTHETIC")
        p = x["by_norad"]["528"]["per_adjacent_epoch"][0]
        self.assertEqual(p["naive_midpoint_residual_rev_day"], "0.0")
        self.assertFalse(p["positive_encoded_dots_but_decreasing_n"])
        self.assertEqual(x["lean_4_35_physical_restriction"],
                         "NOT_PROMOTED_NO_PRIMARY_FRAME_ERRORS")

    def test_window_boundaries_do_not_fill_gaps(self):
        x = audit([make(1, 0), make(2, 1), make(3, 4),
                   make(4, 8)], "SYNTHETIC")
        v = x["by_norad"]["528"]
        self.assertEqual(v["up_to_24h"]["pairs"], 1)
        self.assertEqual(v["up_to_72h"]["pairs"], 2)
        self.assertEqual(v["all_intervals"]["pairs"], 3)

    def test_identical_same_epoch_is_collapsed_but_provenance_preserved(self):
        rows = [make(7), make(8), make(9, 1)]
        unique, dup, observed = normalize(rows)
        self.assertEqual(len(unique), 2)
        self.assertEqual(dup["528:1963-01-01T00:00:00.000000Z"], [7, 8])
        self.assertEqual(observed, {528: 3})
        x = audit(rows, "SYNTHETIC")
        self.assertEqual(x["raw_rows"], 3)
        self.assertEqual(x["by_norad"]["528"]["all_intervals"]["pairs"], 1)
        self.assertEqual(x["by_norad"]["528"]["per_adjacent_epoch"][0][
            "source_rows_earlier"], [7, 8])

    def test_conflicting_duplicate_epoch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "contradictory"):
            audit([make(1), make(2, n="15.2"), make(3, 1)], "SYNTHETIC")

    def test_repeated_source_row_rejected(self):
        with self.assertRaisesRegex(ValueError, "source_row"):
            audit([make(1), make(1, 1)], "SYNTHETIC")

    def test_non_utc_and_off_grid_rejected(self):
        bad = make(1)
        bad["epoch"] = "1963-01-01T00:00:00.000001Z"
        with self.assertRaisesRegex(ValueError, "grid"):
            audit([bad], "SYNTHETIC")
        bad["epoch"] = "1963-01-01T00:00:00+01:00"
        with self.assertRaisesRegex(ValueError, "UTC"):
            audit([bad], "SYNTHETIC")
        bad["epoch"] = "1964-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "1963"):
            audit([bad], "SYNTHETIC")

    def test_nonfinite_or_nonpositive_mean_motion_rejected(self):
        for value in ("NaN", "Infinity", "0", "-1"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "nonfinite|positive"):
                    audit([make(1, n=value)], "SYNTHETIC")

    def test_missing_fields_and_wrong_catalog_rejected(self):
        bad = make(1)
        bad.pop("mean_motion_dot")
        with self.assertRaisesRegex(ValueError, "custody"):
            audit([bad], "SYNTHETIC")
        with self.assertRaisesRegex(ValueError, "catalog"):
            audit([make(1, sat=530)], "SYNTHETIC")

    def test_pinned_count_and_distinct_epoch_gates(self):
        with self.assertRaisesRegex(ValueError, "row counts"):
            audit([make(1)], "SYNTHETIC", counts={528: 45})
        with self.assertRaisesRegex(ValueError, "distinct"):
            audit([make(1)], "SYNTHETIC", distinct={528: 45})

    def test_csv_hash_gate_and_header(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "synthetic.csv"
            with p.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=make(1).keys(),
                                        lineterminator="\n")
                writer.writeheader()
                writer.writerow(make(1))
            with self.assertRaisesRegex(ValueError, "SHA256"):
                read_rows(p)
            rows, digest = read_rows(p, enforce_sha=False)
            self.assertNotEqual(digest, CSV_SHA)
            self.assertEqual(len(rows), 1)
            p.write_text("foo,bar\none,two\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "columns"):
                read_rows(p, enforce_sha=False)

    def test_negative_results_and_independence_labels_are_explicit(self):
        x = audit([make(1), make(2, 1)], "SYNTHETIC")
        self.assertEqual(x["provenance"]["primary_1963_TLE_pairs"], "NOT_RECOVERED")
        self.assertEqual(x["provenance"]["instrumental_independence"], "NOT_ESTABLISHED")
        self.assertEqual(x["raan_198_5261_vs_284_1520"], "UNRESOLVED_PRIMARY_ORIGIN")
        self.assertEqual(x["conde"], "INDETERMINATE")
        self.assertEqual(summary([], 3)["pairs"], 0)
        self.assertIsNone(summary([], 3)["naive_mean_abs_residual_rev_day"])


if __name__ == "__main__":
    unittest.main()
