#!/usr/bin/env python3
"""Offline unit and integrity tests for C241 physical Cd, priors, and storm-gamma audit."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'tools'))

import c241_msis_decay_holdout as m
import c241_physical_cd_priors as mod

LEDGER = REPO_ROOT / 'research' / 'statistics' / 'c241_physical_cd_priors_20261124.json'
REPORT = REPO_ROOT / 'research' / 'statistics' / 'C241_PHYSICAL_CD_PRIORS_20261124.md'
TOOL = REPO_ROOT / 'tools' / 'c241_physical_cd_priors.py'


class TestC241PhysicalCdHelpers(unittest.TestCase):
    def test_sentman_sphere_hypersonic_limit_and_sesam_bounds(self):
        # As speed ratio s -> large and vr_v -> 0, free-molecular sphere Cd -> 2.0
        cd = mod.sentman_sphere(np.array([50.0]), np.array([0.0]))[0]
        self.assertAlmostEqual(float(cd), 2.0, delta=0.01)
        a_lo = mod.sesam_alpha_e(np.array([0.0]), np.array([1000.0]))[0]
        a_hi = mod.sesam_alpha_e(np.array([1e18]), np.array([1000.0]))[0]
        self.assertAlmostEqual(float(a_lo), 0.70, places=4)
        self.assertAlmostEqual(float(a_hi), 0.98, places=3)

    def test_knudsen_bridge_limits(self):
        # Very low density -> Kn >> 1 -> free molecular
        cd_fm = mod.knudsen_bridge(np.array([2.25]), 0.92, np.array([1e12]), 2.0)[0]
        self.assertAlmostEqual(float(cd_fm), 2.25, delta=0.01)
        # Very high density -> Kn << 1 -> continuum
        cd_c = mod.knudsen_bridge(np.array([2.25]), 0.92, np.array([1e22]), 2.0)[0]
        self.assertAlmostEqual(float(cd_c), 0.92, delta=0.01)


class TestC241PhysicalCdLedger(unittest.TestCase):
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
        ec = self.data['epistemic_contract']
        self.assertIsNone(ec['historical_event_time_utc'])
        self.assertFalse(ec['mass_528_identified'])
        self.assertFalse(ec['storm_gamma_promoted'])
        self.assertIsNone(ec['impact_geography'])

    def test_637_and_528_physical_cd_findings(self):
        cmp = self.data['cd_regime_comparison']
        # 637 physical Cd reduces sigma_f and shifts reentry positively by ~1-2h
        self.assertLess(cmp['637_phys_cyl_L35']['sigma_f_frac'], cmp['637_fixed_Cd22']['sigma_f_frac'])
        self.assertGreater(cmp['637_phys_cyl_L35']['delta_hours_vs_fixed'], 0.5)
        self.assertLess(cmp['637_phys_cyl_L35']['cd_at_120km'], 2.15)
        # 528 smooth flat plate worsens BIC and shifts reentry by >15h
        self.assertGreater(cmp['528_phys_plate_tumble']['bic'], cmp['528_fixed_Cd22']['bic'] + 2.0)
        self.assertGreater(cmp['528_phys_plate_tumble']['delta_hours_vs_fixed'], 15.0)

        # Engineering prior excludes axial attitude for Agena D 1169 (< 670 kg dry floor)
        priors = self.data['engineering_priors']
        floor_kg = priors['norad_637_agena_d_dry_floor_kg']
        for row in priors['norad_637_attitude_mass_map']:
            self.assertLess(row['mass_axial_flow_aligned_kg'], floor_kg)
            self.assertGreater(row['mass_uniform_tumbling_kg'], 900.0)

    def test_storm_gamma_negative_control_no_bic_win(self):
        sg = self.data['storm_gamma_negative_control']
        for obj_key, row in sg['individual_fits'].items():
            self.assertGreater(row['delta_bic'], 0.0, f'{obj_key} unexpectedly won BIC with gamma')
        oos = sg['post_oct27_out_of_sample']
        self.assertLess(oos['637']['rel_rmse_joint_gamma'], oos['637']['rel_rmse_gamma0'])


if __name__ == '__main__':
    unittest.main()
