#!/usr/bin/env python3
"""Offline unit and integrity tests for C241 NORAD 637 23-interval MSIS MCMC ledger."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'tools'))

import c241_mcmc_637_msis as mod
import c241_msis_decay_holdout as m

LEDGER = REPO_ROOT / 'research' / 'statistics' / 'c241_mcmc_637_msis_20261124.json'
REPORT = REPO_ROOT / 'research' / 'statistics' / 'C241_MCMC_637_MSIS_20261124.md'
TOOL = REPO_ROOT / 'tools' / 'c241_mcmc_637_msis.py'
SECANT_REF = REPO_ROOT / 'research' / 'statistics' / 'c241_plane_637_decaying_a_last_secant.json'


class TestC241Mcmc637Msis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text(encoding='utf-8'))

    def test_all_files_under_20kb_prek_limit(self):
        for p in (LEDGER, REPORT, TOOL, Path(__file__)):
            self.assertLessEqual(p.stat().st_size, 20000, f'{p} exceeds 20,000 bytes')

    def test_provenance_and_negative_epistemic_contract(self):
        prov = self.data['provenance']
        self.assertEqual(prov['tle_parquet_sha256'], m.PARQUET_SHA256)
        self.assertEqual(len(prov['gfz_space_weather_sha256']), 64)
        self.assertEqual(prov['n_unique_tles'], 25)
        self.assertEqual(prov['n_decay_intervals_used'], 23)
        self.assertEqual(len(prov['excluded_intervals']), 1)
        self.assertGreater(prov['excluded_intervals'][0]['da_obs_km'], 0.0)
        self.assertLess(prov['total_da_km_23_intervals'], -105.0)
        self.assertEqual(prov['nasa_ssr_decay_day_utc'], '1963-11-07')

        ec = self.data['epistemic_contract']
        self.assertIsNone(ec['historical_event_time_utc'])
        self.assertIsNone(ec['terminal_time_sigma_hours'])
        self.assertEqual(ec['calibrated_terminal_holdouts'], 0)
        self.assertEqual(ec['phase_constraint'], 'NOT_EVALUATED')
        self.assertFalse(ec['active_constraint_637'])
        self.assertIsNone(ec['impact_geography'])

    def test_both_msis_models_bic_and_reentry_window(self):
        models = self.data['models']
        self.assertIn('NRLMSIS_2_1', models)
        self.assertIn('NRLMSISE_00', models)
        for key, b_lo, b_hi in (('NRLMSIS_2_1', 0.015, 0.022), ('NRLMSISE_00', 0.012, 0.019)):
            blk = models[key]
            mm = blk['mcmc_models']
            m1 = mm['M1_isotropic_fast_tumbling']
            m2 = mm['M2_altitude_trend']
            m3 = mm['M3_nonspherical_raan_modulation']
            # M1 wins BIC over M2 and M3
            self.assertLess(m1['bic'], m2['bic'], f'{key} M1 should beat M2')
            self.assertLess(m1['bic'], m3['bic'], f'{key} M1 should beat M3')
            self.assertGreater(m1['B0_median_m2_kg'], b_lo)
            self.assertLess(m1['B0_median_m2_kg'], b_hi)
            # Reentry predictive median falls on 1963-11-07 UTC
            pred = blk['posterior_predictive_reentry_M1']
            self.assertTrue(pred['parameter_only']['median_utc'].startswith('1963-11-07'))
            self.assertTrue(pred['full_predictive_with_sigma_f']['median_utc'].startswith('1963-11-07'))
            self.assertGreaterEqual(pred['full_predictive_with_sigma_f']['frac_in_nov07_utc'], 0.85)
            # Full predictive strictly wider than parameter-only
            self.assertGreater(
                pred['full_predictive_with_sigma_f']['ci90_width_hours'],
                pred['parameter_only']['ci90_width_hours'],
            )

    def test_conde_plane_crossings_match_secant_reference_within_15s(self):
        ref = json.loads(SECANT_REF.read_text(encoding='utf-8'))
        ref_nov7 = [
            datetime.fromisoformat(c['crossing_utc'].replace('Z', '+00:00'))
            for c in ref['crossings'] if c['crossing_utc'].startswith('1963-11-07')
        ]
        self.assertEqual(len(ref_nov7), 2)
        for key in ('NRLMSIS_2_1', 'NRLMSISE_00'):
            crossings = self.data['models'][key]['conde_plane_crossings_1963_11_07']
            self.assertEqual(len(crossings), 2)
            for c, r_dt in zip(crossings, ref_nov7):
                c_dt = datetime.fromisoformat(c['crossing_utc'].replace('Z', '+00:00'))
                self.assertLess(abs((c_dt - r_dt).total_seconds()), 15.0)
                self.assertAlmostEqual(c['window_width_min']['50'], 3.69, delta=0.05)
                self.assertGreaterEqual(c['cdf_in_full_predictive'], 0.0)
                self.assertLessEqual(c['cdf_in_full_predictive'], 1.0)

    def test_plane_distance_helper_antisymmetry_and_bounds(self):
        dt = datetime(1963, 11, 7, 5, 23, 34, tzinfo=timezone.utc)
        d = mod.signed_plane_distance_km(dt, 267.2654, 81.8766)
        self.assertLess(abs(d), 2.0)
        # Flipping RAAN by 180 deg gives ~2*cos(i)*sin(lat)*R (~368 km); +90 deg gives >6000 km
        d_opp = mod.signed_plane_distance_km(dt, (267.2654 + 180.0) % 360.0, 81.8766)
        self.assertGreater(abs(d_opp), 300.0)
        d_quad = mod.signed_plane_distance_km(dt, (267.2654 + 90.0) % 360.0, 81.8766)
        self.assertGreater(abs(d_quad), 6000.0)


if __name__ == '__main__':
    unittest.main()
