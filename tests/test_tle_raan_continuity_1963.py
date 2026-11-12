"""C241-L4 adversarial SYNTHETIC controls; historical data only in CI pinned Parquet."""
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from cross_object_epoch_support import FIELDS
from tle_raan_continuity_1963 import audit_series, elapsed_us, short_arc_deg

BASE = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=timezone.utc)


def item(i, days, raan):
    state = ["0"] * len(FIELDS)
    state[FIELDS.index("raan")] = str(raan)
    return {"epoch": BASE + timedelta(days=days),
            "source_rows": [i], "state": tuple(state)}


def check(seq):
    return audit_series(seq, BASE, 198.5261)


class CircularCustodyTests(unittest.TestCase):
    def test_wraps_and_shortest_path(self):
        self.assertAlmostEqual(short_arc_deg(359.99, 0.01), 0.02)
        self.assertAlmostEqual(short_arc_deg(0.01, 359.99), -0.02)

    def test_half_circle_is_ambiguous(self):
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            short_arc_deg(10, 190)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            check([item(1, -1, 10), item(2, 0, 190)])

    def test_sort_determinism_and_secant_is_not_model(self):
        rows = [item(1, -5, 359.99), item(2, -3, 0.01), item(3, 0, 198.5261)]
        a, b = check(rows), check(list(reversed(rows)))
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertAlmostEqual(a["intervals"][0]["shortest_signed_RAAN_delta_deg"], 0.02)
        self.assertEqual(a["intervals"][0]["meaning"],
                         "DESCRIPTIVE_CIRCULAR_DIFFERENCE_NOT_ORBIT_PROPAGATION")

    def test_missing_observations_not_interpolated(self):
        r = check([item(1, -5, 220), item(2, 0, 198.5261)])
        self.assertEqual((r["samples"], r["adjacent_intervals"]), (2, 1))
        self.assertEqual((r["intervals_at_most_24h"], r["intervals_over_72h"]), (0, 1))
        self.assertEqual(r["max_gap_days"], 5)

    def test_no_same_epoch_and_wrong_raan_fail(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            check([item(1, -3, 220), item(2, -1, 200)])
        with self.assertRaisesRegex(ValueError, "disagrees"):
            check([item(1, -3, 220), item(2, 0, 199)])

    def test_duplicate_epoch_and_source_index_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate/conflicting"):
            check([item(1, 0, 198.5261), item(2, 0, 198.5261)])
        with self.assertRaisesRegex(ValueError, "source_row"):
            check([item(1, -1, 220), item(1, 0, 198.5261)])

    def test_invalid_time_and_raan_fail(self):
        with self.assertRaisesRegex(ValueError, "UTC"):
            a = item(1, -1, 220)
            a["epoch"] = a["epoch"].replace(tzinfo=None)
            check([a, item(2, 0, 198.5261)])
        for raan in (-1, 360, float("nan"), float("inf")):
            with self.subTest(raan=raan), self.assertRaisesRegex(ValueError, "RAAN"):
                check([item(1, -1, raan), item(2, 0, 198.5261)])

    def test_microsecond_quantization_guard(self):
        yes = [item(1, -1, 220), item(2, 0, 198.5261)]
        yes[1]["epoch"] += timedelta(microseconds=432)
        self.assertEqual(check(yes)["literal_528"]["delta_epoch_microseconds"], -432)
        no = [item(1, -1, 220), item(2, 0, 198.5261)]
        no[1]["epoch"] += timedelta(microseconds=433)
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            check(no)

    def test_nasa_day_only_has_one_day_span_and_no_reentry_position(self):
        r = check([item(1, -1, 220), item(2, 0, 198.5261)])
        gaps = r["days_last_record_to_NASA_date_only"]
        self.assertEqual(gaps["before_1963_11_09_00UTC"] -
                         gaps["at_1963_11_08_00UTC"], 1)
        self.assertEqual(r["constraint_link"]["physics_predicate_Lean_4_35_0"],
                         "NOT_PROMOTED")
        self.assertEqual(r["constraint_link"]["sensor_error_covariance"], None)

    def test_inactive_legacy_nearest_angle_is_not_paired_observation(self):
        r = check([item(1, -1, 284.3), item(2, 0, 198.5261)])
        legacy = r["legacy_284_1520_FORENSIC_NOT_OBSERVATION"]
        self.assertEqual(legacy["status"], "UNPROVEN_INACTIVE")
        self.assertEqual(legacy["nearest_secondary_by_angle_ONLY"]["source_rows"], [1])
        self.assertAlmostEqual(legacy["difference_from_literal_deg"], 85.6259)

    def test_last_record_not_in_november(self):
        with self.assertRaisesRegex(ValueError, "not before"):
            audit_series([item(1, 0, 198.5261),
                          {"epoch": datetime(1963, 11, 8, tzinfo=timezone.utc),
                           "source_rows": [2], "state": item(2, 0, 190)["state"]}],
                         BASE, 198.5261)

    def test_zero_or_wrong_count_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least two"):
            check([item(1, 0, 198.5261)])
        with self.assertRaisesRegex(ValueError, "count"):
            audit_series([item(1, -1, 220), item(2, 0, 198.5261)],
                         BASE, 198.5261, expected_epochs=45)

    def test_integral_microsecond_gap(self):
        self.assertEqual(elapsed_us(BASE, BASE + timedelta(microseconds=864)), 864)


if __name__ == "__main__":
    unittest.main()
