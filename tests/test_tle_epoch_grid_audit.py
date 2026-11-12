"""Contraprovas inteiras e sintéticas: grade de epoca != autenticacao NORAD."""
import hashlib
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tle_epoch_grid_audit import assess_epoch_grid, audit_file, EXPECTED_CSV_SHA256


def row(idx, sat, stamp):
    return {"source_row": str(idx), "norad_id": str(sat), "epoch": stamp}


class EpochGrid(unittest.TestCase):
    def test_real_transcribed_epoch_is_on_grid(self):
        r = assess_epoch_grid([
            row(3, 527, "1963-10-27T00:00:00.000000Z"),
            row(3017, 528, "1963-10-27T14:40:16.132512Z"),
            row(7, 529, "1963-10-27T00:00:00.000864Z"),
        ])
        self.assertEqual(r["status"], "ALL_ON_8_DECIMAL_DAY_GRID")
        self.assertEqual(r["max_residual_microseconds"], 0)
        self.assertFalse(r["all_epochs_original_norad_verified"])
        self.assertEqual(r["per_object"]["528"]["exact_grid_rows"], 1)

    def test_offsets_1_432_433_us_are_not_grid_ticks(self):
        stamp = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=timezone.utc)
        cases = [row(i, 528, (stamp + timedelta(microseconds=us)).isoformat(
            timespec="microseconds").replace("+00:00", "Z"))
                 for i, us in enumerate((1, 432, 433))]
        report = assess_epoch_grid(cases)
        self.assertEqual(report["status"], "OFF_GRID_EPOCHS_PRESENT")
        self.assertEqual([x["residual_to_nearest_tle_epoch_grid_microseconds"]
                          for x in report["off_grid_details"]], [1, 432, 431])
        self.assertEqual(report["per_object"]["528"]["off_grid_rows"], 3)

    def test_next_day_boundary_and_864_us_step(self):
        r = assess_epoch_grid([
            row(1, 527, "1963-12-31T23:59:59.999136Z"),
            row(2, 528, "1963-12-31T00:00:00.000864Z"),
            row(3, 529, "1963-12-31T00:00:00.000000Z"),
        ])
        self.assertEqual(r["status"], "ALL_ON_8_DECIMAL_DAY_GRID")

    def test_reject_duplicate_indices_and_non_utc(self):
        with self.assertRaisesRegex(ValueError, "source_row duplicado"):
            assess_epoch_grid([row(4, 527, "1963-01-01T00:00:00Z"),
                               row(4, 528, "1963-01-01T00:00:00Z")])
        for stamp in ("1963-01-01T00:00:00+02:00", "1964-01-01T00:00:00Z"):
            with self.assertRaises(ValueError):
                assess_epoch_grid([row(4, 527, stamp)])

    def test_fail_closed_on_input_hash_or_missing_object(self):
        header = b"source_row,norad_id,epoch\n1,528,1963-10-27T14:40:16.132512Z\n"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sample.csv"
            p.write_bytes(header)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                audit_file(p)  # production pinned SHA only
            with self.assertRaisesRegex(ValueError, "tres objetos"):
                audit_file(p, hashlib.sha256(header).hexdigest())

    def test_original_pin_is_explicit_not_synthetic(self):
        self.assertEqual(len(EXPECTED_CSV_SHA256), 64)
        self.assertEqual(EXPECTED_CSV_SHA256,
                         "3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231")


if __name__ == "__main__":
    unittest.main()
