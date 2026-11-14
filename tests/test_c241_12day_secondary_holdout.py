"""Adversarial logic checks; historical replay is a separate SHA-pinned step."""
import hashlib
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c241_12day_secondary_holdout as h


def row(sat, day, n, raan=90.0):
    return {'norad': sat, 'epoch': datetime(1963, 10, 1, tzinfo=timezone.utc) + timedelta(days=day),
            'source_row': day, 'mean_motion': n, 'raan': raan,
            'inclination': 81.8, 'eccentricity': .001}


class Secondary12DayTests(unittest.TestCase):
    def test_future_cannot_change_prediction(self):
        previous, origin, target = row(529, 0, 15.3), row(529, 3, 15.31), row(529, 15, 15.35)
        a = h.make_pairs([previous, origin, target])
        changed = {**target, 'mean_motion': 15.95, 'raan': 230.0}
        b = h.make_pairs([previous, origin, changed])
        self.assertEqual(len(a), 1)
        self.assertAlmostEqual(b[0]['signed_errors']['mean_motion_two_point_rev_day'] -
                               a[0]['signed_errors']['mean_motion_two_point_rev_day'], 0.6)
        self.assertAlmostEqual(h.wrap(b[0]['signed_errors']['raan_j2_deg'] -
                                      a[0]['signed_errors']['raan_j2_deg']), 140.0)

    def test_no_backwards_or_short_horizon(self):
        a, b = row(527, 0, 15.2), row(527, 1, 15.2)
        self.assertEqual(h.make_pairs([a, b, row(527, 2, 15.3)]), [])
        with self.assertRaises(ValueError):
            h.forecast(b, a, 12)

    def test_closest_future_target_without_selection_on_values(self):
        rows = [row(529, 0, 15.3), row(529, 2, 15.31),
                row(529, 12, 15.5), row(529, 15, 15.6)]
        out = h.make_pairs(rows)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['target_epoch_utc'][:10], '1963-10-16')

    def test_duplicate_and_wrong_order_blocked(self):
        rows = [row(527, 0, 15.2), row(527, 0, 15.2), row(527, 12, 15.3)]
        with self.assertRaises(ValueError):
            h.make_pairs(rows)

    def test_wrong_csv_hash_blocks_without_parsing(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'untrusted.csv'
            path.write_text('invalid source')
            with self.assertRaisesRegex(ValueError, 'SHA mismatch'):
                h.read_secondary_csv(path)

    def test_wrap_and_frozen_rate(self):
        self.assertEqual(h.wrap(359), -1)
        self.assertEqual(h.wrap(-359), 1)
        self.assertLess(h.rate_j2(row(527, 0, 15.2)), 0)
        self.assertEqual(h.report([])['decay_time_error_hours'], None)


if __name__ == '__main__':
    unittest.main()
