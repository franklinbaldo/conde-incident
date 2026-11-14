"""Adversarial checks of the 688 reported-terminal-interval calibration gate."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c241_688_terminal_holdout_readiness import (  # noqa: E402
    DECAY_END, DECAY_START, LEDGER, analyze, digest, normalize_row,
    verify_ledger, extract_pinned,
)


class ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((Path(__file__).resolve().parents[1] / LEDGER).read_text())

    def setUp(self):
        def rec(i, hour, n):
            return {'source_row': i, 'epoch': datetime(1963, 11, 11, hour, tzinfo=timezone.utc),
                    'mean_motion_rev_day': n}
        self.groups = {687: [rec(100, 7, 16.22), rec(120, 11, 16.27)],
                       688: [rec(110, 16, 16.29)]}

    def test_report_2400_rolls_to_next_day(self):
        self.assertEqual(DECAY_END, datetime(1963, 11, 13, tzinfo=timezone.utc))
        self.assertEqual((DECAY_END - DECAY_START).total_seconds(), 6600)

    def test_one_epoch_does_not_identify_688_secant(self):
        result = analyze(self.groups, self.ledger)
        self.assertFalse(result['objects']['688']['within_object_secant_estimable'])
        self.assertTrue(result['objects']['687']['within_object_secant_estimable'])
        self.assertEqual(result['inference']['688_secant_status'],
                         'NOT_ESTIMABLE_ONE_PRE_TERMINAL_EPOCH')
        self.assertIsNone(result['inference']['terminal_time_sigma_hours'])
        self.assertFalse(result['inference']['active_constraint_528'])
        self.assertEqual(result['inference']['historical_mcmc'], 'NOT_RUN')

    def test_687_does_not_supply_688_slope(self):
        result = analyze(self.groups, self.ledger)
        self.assertEqual(result['inference']['687_to_688_transfer'],
                         'NOT_JUSTIFIED_DISTINCT_PHYSICAL_OBJECT')
        self.assertFalse(result['objects']['687']['terminal_time_holdout_ready'])
        self.assertFalse(result['objects']['688']['terminal_time_holdout_ready'])

    def test_missing_control_not_accepted(self):
        with self.assertRaises(ValueError):
            analyze({688: self.groups[688]}, self.ledger)

    def test_duplicate_or_reordered_epoch_rejected(self):
        groups = deepcopy(self.groups)
        groups[687][1] = groups[687][0]
        with self.assertRaises(ValueError):
            analyze(groups, self.ledger)
        groups[687] = list(reversed(self.groups[687]))
        with self.assertRaises(ValueError):
            analyze(groups, self.ledger)

    def test_post_terminal_observation_must_not_be_training(self):
        groups = deepcopy(self.groups)
        groups[688][0]['epoch'] = DECAY_END
        with self.assertRaises(ValueError):
            analyze(groups, self.ledger)

    def test_688_must_have_exactly_one_historical_epoch(self):
        groups = deepcopy(self.groups)
        groups[688].append({**groups[688][0], 'epoch': groups[688][0]['epoch'] + timedelta(hours=1)})
        with self.assertRaises(ValueError):
            analyze(groups, self.ledger)

    def test_pdf_custody_and_object_identity_required(self):
        for change in (('sha256', 'bad'), ('message', 'different'), ('object_ids', [528])):
            ledger = deepcopy(self.ledger)
            ledger['sources'][1][change[0]] = change[1]
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_ledger(ledger)
        ledger = deepcopy(self.ledger)
        ledger['sources'][1]['decay_window']['object_id'] = 528
        with self.assertRaises(ValueError):
            analyze(self.groups, ledger)

    def test_bad_designator_or_utc_or_mean_motion(self):
        basic = {'norad_id': 688, 'epoch': self.groups[688][0]['epoch'],
                 'mean_motion': 16.29, 'intl_designator': '63044  B'}
        self.assertEqual(normalize_row(14, basic)['source_row'], 14)
        for replacement in ({'intl_designator': '63003  B'},
                            {'epoch': datetime(1963, 11, 11, 16)},
                            {'mean_motion': -1}):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                normalize_row(14, {**basic, **replacement})

    def test_parquet_checksum_must_be_checked_before_import(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'fake.parquet'
            p.write_bytes(b'not historical parquet')
            self.assertNotEqual(digest(p), 'c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09')
            with self.assertRaisesRegex(ValueError, 'SHA mismatch'):
                extract_pinned(p)

    def test_no_claimed_probability_or_geo(self):
        result = analyze(self.groups, self.ledger)
        self.assertIsNone(result['inference']['impact_geography_528'])
        self.assertIsNone(result['inference']['mass_528_posterior'])
        self.assertFalse(result['inference']['independent_terminal_time_error_calibration'])


if __name__ == '__main__':
    unittest.main()
