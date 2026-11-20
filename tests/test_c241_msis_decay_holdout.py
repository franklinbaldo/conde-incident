#!/usr/bin/env python3
"""Offline unit and adversarial tests for C241 MSIS-2.1/NRLMSISE-00 decay holdout."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'tools'))

import c241_msis_decay_holdout as mod

LEDGER_PATH = REPO_ROOT / 'research' / 'statistics' / 'c241_msis_decay_holdout_20261120.json'
REPORT_PATH = REPO_ROOT / 'research' / 'statistics' / 'C241_MSIS_DECAY_HOLDOUT_20261120.md'
TOOL_PATH = REPO_ROOT / 'tools' / 'c241_msis_decay_holdout.py'


class TestC241MsisHelpers(unittest.TestCase):
    def test_mean_motion_to_a_matches_528_reference(self):
        a = mod.mean_motion_to_a(15.74901460)
        self.assertAlmostEqual(a, 6723.0486, places=3)
        with self.assertRaises(ValueError):
            mod.mean_motion_to_a(0.0)
        with self.assertRaises(ValueError):
            mod.mean_motion_to_a(float('nan'))

    def test_j2_rates_match_528_nodal_precession(self):
        a = mod.mean_motion_to_a(15.74901460)
        draan, _ = mod.j2_rates_deg_day(a, 0.0017147, 81.8615)
        self.assertAlmostEqual(draan, -1.1731, places=3)
        with self.assertRaises(ValueError):
            mod.j2_rates_deg_day(6000.0, 0.01, 81.8)

    def test_strict_training_cutoff_rejects_leakage_and_non_utc(self):
        t1 = datetime(1963, 10, 10, tzinfo=timezone.utc)
        t2 = datetime(1963, 10, 20, tzinfo=timezone.utc)
        cut = datetime(1963, 10, 15, tzinfo=timezone.utc)
        out = mod.strict_training_cutoff([{'epoch': t1}, {'epoch': t2}], cut)
        self.assertEqual([r['epoch'] for r in out], [t1])
        # Reject unsorted / duplicate epochs
        with self.assertRaises(ValueError):
            mod.strict_training_cutoff([{'epoch': t2}, {'epoch': t1}], cut)
        # Reject non-UTC cutoff
        tz_br = timezone(timedelta(hours=-3))
        with self.assertRaises(ValueError):
            mod.strict_training_cutoff([{'epoch': t1}], datetime(1963, 10, 15, tzinfo=tz_br))

    def test_assumed_utc_day_error_interval(self):
        pred = datetime(1963, 11, 7, 12, 0, tzinfo=timezone.utc)
        err = mod.assumed_utc_day_error(pred, '1963-11-07')
        self.assertEqual(err, [-0.5, 0.5])
        with self.assertRaises(ValueError):
            mod.assumed_utc_day_error(pred, '1963-11-07T12:00Z')


class TestC241MsisLedgerIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER_PATH.read_text(encoding='utf-8'))

    def test_all_deliverables_under_20kb_prek_ceiling(self):
        for p in (LEDGER_PATH, REPORT_PATH, TOOL_PATH, Path(__file__)):
            self.assertLessEqual(p.stat().st_size, 20000, f'{p} exceeds 20,000-byte ceiling')

    def test_provenance_and_negative_epistemic_contract(self):
        prov = self.data['provenance']
        self.assertEqual(prov['tle_parquet_sha256'], mod.PARQUET_SHA256)
        self.assertEqual(len(prov['gfz_space_weather_sha256']), 64)

        contract = self.data['epistemic_contract']
        self.assertIsNone(contract['historical_event_time_utc'])
        self.assertIsNone(contract['terminal_time_sigma_hours'])
        self.assertEqual(contract['calibrated_terminal_holdouts'], 0)
        self.assertEqual(contract['historical_mcmc'], 'NOT_RUN')
        self.assertFalse(contract['active_constraint_528'])
        self.assertIsNone(contract['impact_geography'])

    def test_zero_chronological_leakage_and_error_consistency_in_holdouts(self):
        holdouts = self.data['control_holdouts']
        self.assertEqual(len(holdouts), 32)  # 4 objects * 4 cutoffs * 2 MSIS versions
        for row in holdouts:
            cut = datetime.fromisoformat(row['cutoff_utc'].replace('Z', '+00:00'))
            last_train = datetime.fromisoformat(row['train_last_epoch_utc'].replace('Z', '+00:00'))
            self.assertLess(last_train, cut, f'Chronological leakage in {row}')
            pred = datetime.fromisoformat(row['predicted_decay_utc'].replace('Z', '+00:00'))
            recomputed = mod.assumed_utc_day_error(pred, row['label_day'])
            self.assertAlmostEqual(row['assumed_utc_day_error_interval'][0], recomputed[0], delta=0.0002)
            self.assertAlmostEqual(row['assumed_utc_day_error_interval'][1], recomputed[1], delta=0.0002)
            self.assertEqual(row['hits_assumed_utc_day'], recomputed[0] <= 0.0 <= recomputed[1])

    def test_calibrators_and_528_scenarios_present(self):
        cals = self.data['density_calibrators']
        self.assertIn('81', cals)
        self.assertIn('529', cals)
        self.assertGreater(cals['81']['pre_oct28_median_B_m2_kg'], 3.0)
        self.assertGreater(len(cals['81']['post_oct27_intervals']), 3)
        self.assertGreater(len(cals['529']['post_oct27_intervals']), 3)

        s528 = self.data['norad_528_exploratory']
        self.assertEqual(s528['nasa_catalog_day_label'], '1963-11-08')
        self.assertEqual(len(s528['scenarios']), 8)
        self.assertGreaterEqual(len(s528['msis21_median_oct_daily_altitude_profile']), 10)


if __name__ == '__main__':
    unittest.main()
