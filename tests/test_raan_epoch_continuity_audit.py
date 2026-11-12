"""C241-T7 controls: explicitly SYNTHETIC histories; no inferred 1963 track."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_epoch_continuity_audit import (
    MIRROR_PAIR_SHA256, audit_raan_timeline, delta_us,
    literal_mirror, signed_short_arc_deg,
)

BASE = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=timezone.utc)


def synthetic(source_row, days, raan):
    return {
        "source_row": source_row, "epoch_utc": BASE + timedelta(days=days),
        "fields": {"raan": raan},
    }


def check(rows, **kw):
    return audit_raan_timeline(rows, "SYNTHETIC_NOT_A_SOURCE",
                               BASE, 198.5261, **kw)


class RaanEpochContinuityControls(unittest.TestCase):
    def test_circular_wrap_is_not_359_degree_jump(self):
        self.assertAlmostEqual(signed_short_arc_deg(359.99, 0.01), 0.02)
        self.assertAlmostEqual(signed_short_arc_deg(0.01, 359.99), -0.02)
        self.assertAlmostEqual(signed_short_arc_deg(198.5261, 198.5261), 0)

    def test_exactly_180_degree_turn_is_directionally_ambiguous(self):
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            signed_short_arc_deg(10, 190)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            check([synthetic(2, -2, 10), synthetic(3, -1, 190)])

    def test_sorted_and_unsorted_input_agree(self):
        a = [synthetic(8, -3, 359.99), synthetic(4, -1, 0.01),
             synthetic(10, 0, 1.00)]
        self.assertEqual(json.dumps(check(a), sort_keys=True),
                         json.dumps(check(list(reversed(a))), sort_keys=True))
        report = check(a)
        self.assertEqual(report["adjacent_intervals"], 2)
        self.assertAlmostEqual(report["per_adjacent_epoch_interval"][0][
            "shortest_raan_delta_deg"], 0.02)
        self.assertEqual(report["per_adjacent_epoch_interval"][0][
            "method"], "PAIRWISE_CIRCULAR_DIFFERENCE_NOT_FITTED_MOTION")

    def test_gap_is_not_filled_with_derived_measurements(self):
        report = check([synthetic(1, -5, 220), synthetic(2, 0, 198.5261)])
        self.assertEqual(report["samples"], 2)
        self.assertEqual(report["adjacent_intervals"], 1)
        self.assertEqual(report["gaps"]["intervals_le_24h"], 0)
        self.assertEqual(report["gaps"]["intervals_gt_72h"], 1)
        self.assertEqual(report["gaps"]["max_gap_days"], 5)
        self.assertEqual(report["simulation_and_holdout"],
                         "NOT_RUN_NO_CALIBRATED_TRACK")

    def test_duplicate_epoch_and_index_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate/conflicting"):
            check([synthetic(1, 0, 198), synthetic(2, 0, 198)])
        with self.assertRaisesRegex(ValueError, "source_row"):
            check([synthetic(1, -1, 220), synthetic(1, 0, 198)])

    def test_invalid_frame_range_time_and_count_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "RAAN"):
            check([synthetic(1, -1, 360), synthetic(2, 0, 198)])
        with self.assertRaisesRegex(ValueError, "RAAN"):
            check([synthetic(1, -1, -0.1), synthetic(2, 0, 198)])
        with self.assertRaisesRegex(ValueError, "UTC"):
            bad = synthetic(1, -1, 220)
            bad["epoch_utc"] = bad["epoch_utc"].replace(tzinfo=None)
            check([bad, synthetic(2, 0, 198)])
        with self.assertRaisesRegex(ValueError, "1963"):
            check([synthetic(1, -1, 220),
                   {"source_row": 2, "epoch_utc": BASE.replace(year=1964),
                    "fields": {"raan": 198}}])
        with self.assertRaisesRegex(ValueError, "count"):
            check([synthetic(1, -1, 220), synthetic(2, 0, 198)],
                  required_count=45)

    def test_legacy_time_offset_is_exact_microseconds_not_rounded(self):
        result = check([synthetic(1, -1, 220), synthetic(2, 0, 198.5261)])
        legacy = result["legacy_conflict"]
        self.assertEqual(legacy["legacy_constructed_epoch_utc"],
                         "1963-10-27T14:39:59.999904Z")
        self.assertEqual(legacy["epoch_difference_mirror_minus_legacy_microseconds"],
                         16_132_608)
        self.assertFalse(legacy["within_same_432us_epoch"])
        self.assertAlmostEqual(legacy["angular_discrepancy_deg"], 85.6259)
        self.assertEqual(legacy["resolution"], "UNRESOLVED_PRIMARY_ORIGIN")
        self.assertEqual(legacy["secondary_samples_at_literal_mirror_epoch"],
                         [{"source_row": 2, "raan_deg": 198.5261}])

    def test_nasa_date_is_an_interval_not_terminal_timestamp(self):
        r = check([synthetic(1, -1, 221), synthetic(2, 0, 198)])
        gap = r["gaps"]["last_to_NASA_08Nov_date_only_gap_days"]
        self.assertGreater(gap["at_08Nov_00UTC"], 0)
        self.assertAlmostEqual(gap["before_09Nov_00UTC"] -
                               gap["at_08Nov_00UTC"], 1)
        self.assertEqual(r["provenance"]["original_line1_line2_for_45_epochs"],
                         "NOT_RECOVERED")

    def test_pinned_literal_pair_and_tamper_rejection(self):
        p = ROOT / "research/tle_custody/mirror_528_1963-10-27.tle"
        raw = p.read_bytes()
        import hashlib
        self.assertEqual(hashlib.sha256(raw).hexdigest(), MIRROR_PAIR_SHA256)
        date, raan = literal_mirror(p)
        self.assertEqual(date, BASE)
        self.assertAlmostEqual(raan, 198.5261)
        with tempfile.TemporaryDirectory() as tmp:
            altered = Path(tmp) / "not_original.tle"
            altered.write_bytes(raw.replace(b"198.5261", b"284.1520"))
            with self.assertRaisesRegex(ValueError, "SHA256"):
                literal_mirror(altered)

    def test_source_data_cannot_reach_november_silently(self):
        with self.assertRaisesRegex(ValueError, "not before"):
            check([synthetic(1, -1, 210),
                   {"source_row": 2,
                    "epoch_utc": datetime(1963, 11, 8, tzinfo=timezone.utc),
                    "fields": {"raan": 190}}])

    def test_only_one_row_has_no_secant_rate(self):
        with self.assertRaisesRegex(ValueError, "at least two"):
            check([synthetic(1, 0, 198)])

    def test_microsecond_delta_is_integral(self):
        self.assertEqual(delta_us(BASE, BASE + timedelta(microseconds=864)), 864)


if __name__ == "__main__":
    unittest.main()
