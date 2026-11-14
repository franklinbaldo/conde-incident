"""Synthetic controls for cross-object epoch audit, NOT historical observations."""
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from cross_object_epoch_support import parse_utc, nearest, normalize, summarize, read_pinned_csv

BASE = datetime(1963, 10, 27, 14, tzinfo=timezone.utc)


def row(sat, hours, index, **fields):
    data = {"norad_id": str(sat), "source_row": str(index),
            "epoch": (BASE + timedelta(hours=hours)).isoformat(
                timespec="microseconds").replace("+00:00", "Z"),
            "inclination": "81.0", "raan": "200.0", "eccentricity": "0.01",
            "arg_perigee": "50", "mean_anomaly": "40", "mean_motion": "15.7",
            "mean_motion_dot": "0", "bstar": "0",
            "intl_designator": "63003 B", "altitude_km": "200"}
    data.update(fields)
    return data


class TemporalAvailabilityControls(unittest.TestCase):
    def test_reject_non_utc_and_wrong_year(self):
        for value in ("1963-10-27T14:00:00", "1963-10-27T10:00:00-04:00",
                      "1964-10-27T14:00:00Z", "invalid"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_utc(value)

    def test_nearest_tie_is_earlier_without_interpolation(self):
        groups, _ = normalize([row(527, 1, 2), row(529, 0, 4),
                               row(527, -1, 1), row(528, 0, 3)])
        chosen = nearest(BASE, groups[527])
        self.assertEqual(chosen["source_rows"], [1])
        self.assertEqual(chosen["signed_delta_us"], -3_600_000_000)
        self.assertFalse(chosen["exact_utc_epoch"])

    def test_query_windows_do_not_assert_simultaneous_measurement(self):
        result = summarize([row(527, -6, 1), row(528, 0, 2), row(529, 24, 3)])
        count = result["count_of_528_epochs_with_nearby_527_529"]
        self.assertEqual(count["6h"], {"527": 1, "529": 0, "both": 0})
        self.assertEqual(count["24h"], {"527": 1, "529": 1, "both": 1})
        self.assertEqual(result["count_of_exact_shared_epochs"]["both"], 0)
        self.assertEqual(result["physical_joint_fit_and_holdouts"], "NOT_RUN")

    def test_half_quantum_is_not_exact_timestamp(self):
        close = row(527, 0, 1, epoch=(BASE + timedelta(microseconds=432)).isoformat(
            timespec="microseconds").replace("+00:00", "Z"))
        result = summarize([close, row(528, 0, 2), row(529, 0, 3)])
        self.assertEqual(result["count_of_exact_shared_epochs"]["527"], 0)
        self.assertEqual(result["count_within_432us"]["527"], 1)
        far = row(527, 0, 1, epoch=(BASE + timedelta(microseconds=433)).isoformat(
            timespec="microseconds").replace("+00:00", "Z"))
        self.assertEqual(summarize([far, row(528, 0, 2), row(529, 0, 3)])[
            "count_within_432us"]["527"], 0)

    def test_duplicate_epoch_retains_original_source_rows(self):
        result = summarize([row(527, 0, 1), row(527, 0, 2),
                            row(528, 0, 3), row(529, 0, 4)])
        self.assertEqual(result["object_extents"]["527"]["rows"], 2)
        self.assertEqual(result["object_extents"]["527"]["unique_epochs"], 1)
        self.assertEqual(result["nearest_by_528_epoch"][0]["nearest_527"]["source_rows"], [1, 2])

    def test_conflicting_same_epoch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "conflicting states"):
            summarize([row(527, 0, 1), row(527, 0, 2, raan="284"),
                       row(528, 0, 3), row(529, 0, 4)])

    def test_duplicate_source_index_and_nan_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "source_row"):
            summarize([row(527, 0, 1), row(528, 0, 1), row(529, 0, 3)])
        with self.assertRaisesRegex(ValueError, "non-finite"):
            summarize([row(527, 0, 1, bstar="nan"), row(528, 0, 2), row(529, 0, 3)])

    def test_input_order_cannot_change_result(self):
        import json
        records = [row(529, 0, 11), row(528, 1, 12), row(527, 1, 13),
                   row(528, 0, 14), row(527, -2, 15)]
        self.assertEqual(json.dumps(summarize(records), sort_keys=True),
                         json.dumps(summarize(list(reversed(records))), sort_keys=True))


    def test_decay_day_not_ordered_as_post_event(self):
        day = datetime(1963, 11, 8, tzinfo=timezone.utc)
        records = [row(527, 0, 1, epoch=(day - timedelta(microseconds=1)).isoformat().replace("+00:00", "Z")),
                   row(527, 0, 2, epoch=day.isoformat().replace("+00:00", "Z")),
                   row(527, 0, 3, epoch=(day + timedelta(hours=23)).isoformat().replace("+00:00", "Z")),
                   row(527, 0, 4, epoch=(day + timedelta(days=1)).isoformat().replace("+00:00", "Z")),
                   row(528, 0, 5, epoch=day.isoformat().replace("+00:00", "Z")),
                   row(529, 0, 6, epoch=(day + timedelta(days=1)).isoformat().replace("+00:00", "Z"))]
        d = summarize(records)["post_decay_day_control_coverage"]
        self.assertEqual((d["by_norad"]["527"]["distinct_epochs_before_day"],
                          d["by_norad"]["527"]["distinct_epochs_on_ambiguous_day"],
                          d["by_norad"]["527"]["distinct_epochs_after_day"]), (1, 2, 1))
        self.assertEqual(d["by_norad"]["527"]["first_after_day"]["source_rows"], [4])
        self.assertTrue(d["both_controls_have_later_catalog_epochs"])
        self.assertEqual(d["historical_holdout"], "NOT_RUN")
        self.assertEqual(d["528_trajectory_restriction"], "NONE")

    def test_post_day_duplicate_source_rows_not_independent(self):
        day = datetime(1963, 11, 9, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        d = summarize([row(527, 0, 1, epoch=day), row(527, 0, 2, epoch=day),
                       row(528, 0, 3), row(529, 0, 4, epoch=day)])[
                           "post_decay_day_control_coverage"]
        self.assertEqual(d["by_norad"]["527"]["post_day_source_rows"], [[1, 2]])
        self.assertEqual(d["by_norad"]["527"]["distinct_epochs_after_day"], 1)
        self.assertIsNone(d["by_norad"]["527"]["catalog_gap_last_pre_first_post_seconds"])

    def test_absent_later_record_stays_absent(self):
        d = summarize([row(527, 0, 1), row(528, 0, 2), row(529, 0, 3)])[
            "post_decay_day_control_coverage"]
        self.assertFalse(d["both_controls_have_later_catalog_epochs"])
        self.assertIsNone(d["by_norad"]["529"]["first_after_day"])
        self.assertEqual(d["physical_joint_fit"], "NOT_RUN")

    def test_pinned_reader_rejects_synthetic_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "invented.csv"
            file.write_text("norad_id,source_row,epoch\n528,1,1963-10-27T14:00:00Z\n",
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                read_pinned_csv(file)


if __name__ == "__main__":
    unittest.main()
