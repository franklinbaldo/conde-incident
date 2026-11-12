"""Adversarial independent review tests; synthetic data are NOT historical evidence."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from gaviao_ch09_timeline import (DAY_US, calculate, delta_us, editorial_guards,
                                  get_bytes, git_blob_sha1, select_rows)
UTC = timezone.utc
START = datetime(1963, 2, 6, tzinfo=UTC)

def row(i, days, angle=190.0):
    return (i, START + timedelta(days=days), angle)

class ReviewTests(unittest.TestCase):
    def test_ordering(self):
        r = calculate([row(20, 5), row(2, 0), row(1, 1)])
        self.assertEqual((r["samples"], r["intervals"], r["over72h"], r["atmost24h"]), (3, 2, 1, 1))
        self.assertEqual((r["max_from"], r["max_to"]), (1, 20))
    def test_exact_thresholds(self):
        r = calculate([row(1, 0), row(2, 1), row(3, 4)])
        self.assertEqual((r["over72h"], r["atmost24h"], r["maxgap_us"]), (0, 1, 3 * DAY_US))
    def test_after_threshold(self):
        r = calculate([row(1, 0), (2, START + timedelta(days=3, microseconds=1), 190)])
        self.assertEqual(r["over72h"], 1)
    def test_duplicate_epoch(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            calculate([row(1, 0), row(2, 0)])
    def test_duplicate_source_row(self):
        with self.assertRaisesRegex(ValueError, "source row"):
            calculate([row(1, 0), row(1, 1)])
    def test_naive_utc(self):
        with self.assertRaisesRegex(ValueError, "UTC"):
            calculate([row(1, 0), (2, START.replace(tzinfo=None), 190)])
    def test_wrong_year(self):
        with self.assertRaisesRegex(ValueError, "UTC"):
            calculate([row(1, 0), (2, START.replace(year=1964), 190)])
    def test_nan(self):
        with self.assertRaisesRegex(ValueError, "RAAN"):
            calculate([row(1, 0), (2, START + timedelta(days=1), float("nan"))])
    def test_wrong_count(self):
        with self.assertRaisesRegex(ValueError, "count"):
            calculate([row(1, 0), row(2, 1)], required_count=45)
    def test_late_terminal_epoch(self):
        with self.assertRaisesRegex(ValueError, "October"):
            calculate([row(1, 0), (2, datetime(1963, 11, 8, tzinfo=UTC), 190)])
    def test_original_row_index(self):
        r = select_rows([{"norad_id":527,"epoch":START,"raan":30},
                         {"norad_id":528,"epoch":START,"raan":190},
                         {"norad_id":528,"epoch":START+timedelta(days=1),"raan":191}])
        self.assertEqual([x[0] for x in r], [1, 2])
    def test_no_naive_source(self):
        with self.assertRaisesRegex(ValueError, "timezone"):
            select_rows([{"norad_id":528,"epoch":START.replace(tzinfo=None),"raan":190}])
    def test_invalid_source_raan(self):
        for angle in (-1, 360, float("nan"), True):
            with self.subTest(angle=angle), self.assertRaisesRegex(ValueError, "RAAN"):
                select_rows([{"norad_id":528,"epoch":START,"raan":angle}])
    def test_calendar_reference_not_observation(self):
        last = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=UTC)
        first_day = datetime(1963, 11, 8, tzinfo=UTC)
        self.assertEqual(round(delta_us(last, first_day) / DAY_US, 8), 11.38870217)
        self.assertEqual(round(delta_us(last, first_day + timedelta(days=1)) / DAY_US, 8), 12.38870217)
    def test_git_blob(self):
        import hashlib
        self.assertEqual(git_blob_sha1(b"test"), hashlib.sha1(b"blob 4\0test").hexdigest())
    def test_editorial_omission(self):
        self.assertGreater(len(editorial_guards("Chapter 10: impact proved")), 9)
    def test_no_arbitrary_web(self):
        with self.assertRaisesRegex(ValueError, "non-pinned"):
            get_bytes("https://example.org/test")
    def test_no_dynamic_conclusion(self):
        r = calculate([row(1, 0), row(2, 1)])
        self.assertNotIn("impact_latitude", r)
        self.assertNotIn("precession_rate", r)

if __name__ == "__main__":
    unittest.main()
