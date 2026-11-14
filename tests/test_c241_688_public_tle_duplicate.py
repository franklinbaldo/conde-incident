"""Contraprovas para reapresentação externa do TLE de 688."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c241_688_public_tle_duplicate import (  # noqa: E402
    LINE1, LINE2, audit, checksum, parse_tle,
)


def rec(epoch: datetime, motion: float) -> dict:
    return {'epoch': epoch, 'mean_motion_rev_day': motion, 'source_row': 1}


def recalc_checksum(line: str) -> str:
    return line[:68] + str(checksum(line))


class PublicTleDuplicateTests(unittest.TestCase):
    def setUp(self):
        self.original = parse_tle(LINE1, LINE2)
        self.rows = {687: [rec(datetime(1963, 11, 11, tzinfo=timezone.utc), 16.12),
                           rec(datetime(1963, 11, 12, tzinfo=timezone.utc), 16.15)],
                     688: [rec(self.original['epoch_utc'], self.original['mean_motion_rev_day'])]}

    def test_transcription_has_valid_checksums_and_1963_epoch(self):
        self.assertEqual(len(LINE1), 69)
        self.assertEqual(len(LINE2), 69)
        self.assertEqual(self.original['epoch_utc'].date().isoformat(), '1963-11-11')
        self.assertEqual(self.original['epoch_utc'].hour, 16)
        self.assertEqual(self.original['epoch_utc'].minute, 35)
        self.assertEqual(self.original['mean_motion_rev_day'], 16.29621717)

    def test_public_tle_reproduces_one_catalogue_epoch_not_a_new_measurement(self):
        report = audit(self.original, self.rows)
        self.assertTrue(report['duplicate_state_candidate'])
        self.assertFalse(report['independent_new_epoch_found'])
        self.assertFalse(report['independent_instrument_or_lineage_demonstrated'])
        self.assertFalse(report['identifiability']['688_secant_identifiable_from_pinned_plus_public'])
        self.assertIsNone(report['identifiability']['terminal_sigma_hours'])
        self.assertIsNone(report['identifiability']['impact_geography_528'])
        self.assertEqual(report['identifiability']['historical_mcmc'], 'NOT_RUN')

    def test_wrong_checksum_cannot_be_counted(self):
        for line1, line2 in ((LINE1[:-1] + ('0' if LINE1[-1] != '0' else '1'), LINE2),
                             (LINE1, LINE2[:-1] + ('0' if LINE2[-1] != '0' else '1'))):
            with self.subTest(line1=line1, line2=line2), self.assertRaisesRegex(ValueError, 'checksum'):
                parse_tle(line1, line2)

    def test_wrong_object_rejected_even_if_checksum_recomputed(self):
        bad = recalc_checksum(LINE2[:2] + '00528' + LINE2[7:])
        with self.assertRaisesRegex(ValueError, 'NORAD'):
            parse_tle(LINE1, bad)

    def test_wrong_designator_rejected_even_with_valid_checksum(self):
        bad = recalc_checksum(LINE1[:9] + '63003  B' + LINE1[17:])
        with self.assertRaisesRegex(ValueError, 'designator'):
            parse_tle(bad, LINE2)

    def test_second_epoch_would_trigger_review_not_silent_confirmation(self):
        second = dict(self.original, epoch_utc=self.original['epoch_utc'] + timedelta(hours=2))
        report = audit(second, self.rows)
        self.assertFalse(report['duplicate_state_candidate'])
        self.assertTrue(report['independent_new_epoch_found'])
        self.assertFalse(report['independent_instrument_or_lineage_demonstrated'])

    def test_different_motion_same_epoch_is_not_validated_as_duplicate(self):
        changed = dict(self.original, mean_motion_rev_day=16.4)
        report = audit(changed, self.rows)
        self.assertFalse(report['duplicate_state_candidate'])
        self.assertFalse(report['independent_new_epoch_found'])
        self.assertFalse(report['independent_instrument_or_lineage_demonstrated'])

    def test_missing_or_extra_catalogue_epochs_rejected(self):
        for groups in ({687: self.rows[687]},
                       {687: self.rows[687], 688: []},
                       {687: self.rows[687], 688: 2 * self.rows[688]}):
            with self.subTest(groups=groups), self.assertRaises(ValueError):
                audit(self.original, groups)


if __name__ == '__main__':
    unittest.main()
