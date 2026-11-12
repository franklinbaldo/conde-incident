"""Adversarial synthetic calendar examples; NOT historical NORAD observations."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from gaviao_chapter06_recheck import summarize, nearest_by_exhaustive_scan, normalize

T = datetime(1963, 10, 27, 12, tzinfo=timezone.utc)


def t(us=0):
    return T + timedelta(microseconds=us)


class IndependentCalendarTests(unittest.TestCase):
    def test_exact_zero_triad_is_counted_once(self):
        r = summarize([(527, t(), 10), (528, t(), 20), (529, t(), 30)])
        self.assertEqual(r["zero_delta"], {"527": 1, "529": 1, "both": 1})
        self.assertEqual(r["windows"]["6h"]["both"], 1)

    def test_tie_break_prefers_earlier_epoch_not_an_interpolation(self):
        sat = normalize([(527, t(-1000), 1), (527, t(1000), 2),
                         (528, t(), 3), (529, t(), 4)])[527]
        self.assertEqual(nearest_by_exhaustive_scan(t(), sat), t(-1000))

    def test_half_quantum_is_inclusive_and_433_microseconds_is_not(self):
        yes = summarize([(527, t(432), 1), (528, t(), 2), (529, t(-432), 3)])
        no = summarize([(527, t(433), 1), (528, t(), 2), (529, t(-432), 3)])
        self.assertEqual(yes["within_432us"]["both"], 1)
        self.assertEqual(no["within_432us"]["both"], 0)

    def test_calendar_window_boundaries_are_inclusive(self):
        r = summarize([(527, t(-6*3600*1000000), 1),
                       (528, t(), 2), (529, t(6*3600*1000000), 3)])
        self.assertEqual(r["windows"]["6h"]["both"], 1)
        self.assertEqual(r["zero_delta"]["both"], 0)

    def test_duplicates_do_not_create_new_independent_epochs(self):
        r = summarize([(527, t(), 1), (527, t(), 2),
                       (528, t(), 3), (529, t(), 4), (529, t(), 5)])
        self.assertEqual(r["objects"]["527"], {"rows": 2, "unique_epochs": 1})
        self.assertEqual(r["objects"]["529"], {"rows": 2, "unique_epochs": 1})
        self.assertEqual(r["distinct_nearest_support_epochs_within_72h"], {"527": 1, "529": 1})

    def test_reject_naive_timestamp_or_nonzero_offset(self):
        for bad in (T.replace(tzinfo=None),
                    T.replace(tzinfo=timezone(timedelta(hours=-4)))):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                summarize([(527, bad, 1), (528, t(), 2), (529, t(), 3)])

    def test_reject_duplicate_physical_row_indices(self):
        with self.assertRaisesRegex(ValueError, "reused"):
            summarize([(527, t(), 1), (528, t(), 1), (529, t(), 3)])

    def test_reject_missing_satellite(self):
        with self.assertRaisesRegex(ValueError, "529"):
            summarize([(527, t(), 1), (528, t(), 2)])

    def test_no_physical_or_terminal_conclusion_even_when_dates_overlap(self):
        r = summarize([(527, t(), 1), (528, t(), 2), (529, t(), 3)])
        self.assertEqual(r["impact_or_reentry_location"], "UNDETERMINED")
        self.assertEqual(r["lean_physical_restriction"], "NOT_JUSTIFIED")
        self.assertEqual(r["numerical_joint_fit"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
