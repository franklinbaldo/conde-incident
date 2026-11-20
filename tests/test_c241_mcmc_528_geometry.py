#!/usr/bin/env python3
"""Offline integrity tests for C241 10-month 528 MCMC ledger and Lean 4 geometry module."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / 'research' / 'statistics' / 'c241_mcmc_528_geometry_20261120.json'
REPORT = REPO_ROOT / 'research' / 'statistics' / 'C241_MCMC_528_GEOMETRY_20261120.md'
TOOL = REPO_ROOT / 'tools' / 'c241_mcmc_528_geometry.py'
LEAN_MOD = REPO_ROOT / 'formal' / 'Conde1963' / 'BallisticGeometryBound.lean'
LEAN_ROOT = REPO_ROOT / 'formal' / 'Conde1963.lean'


class TestC241Mcmc528Geometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text(encoding='utf-8'))

    def test_files_under_20kb_prek_limit(self):
        for p in (LEDGER, REPORT, TOOL, LEAN_MOD, Path(__file__)):
            self.assertLessEqual(p.stat().st_size, 20000, f'{p} exceeds 20,000 bytes')

    def test_lean_module_imported_and_axiom_free(self):
        lean_src = LEAN_MOD.read_text(encoding='utf-8')
        self.assertNotIn('sorry', lean_src)
        self.assertNotIn('axiom ', lean_src)
        for thm in (
            'solid_sphere_diameter_le_8mm',
            'macroscopic_solid_metal_sphere_excluded',
            'hollow_metal_shell_thickness_le_1337um',
            'thick_titanium_or_steel_shell_excluded',
            'tumbling_aluminum_sheet_witness',
            'tumbling_composite_fairing_witness',
        ):
            self.assertIn(f'theorem {thm}', lean_src)
        self.assertIn('import Conde1963.BallisticGeometryBound', LEAN_ROOT.read_text(encoding='utf-8'))

    def test_mcmc_ledger_consistency_and_model_selection(self):
        prov = self.data['provenance']
        self.assertEqual(prov['n_intervals_jan_oct_1963'], 43)
        self.assertLess(prov['total_da_km'], -140.0)

        models = self.data['mcmc_models']
        m1 = models['M1_isotropic_fast_tumbling']
        m2 = models['M2_altitude_trend']
        m3 = models['M3_nonspherical_raan_modulation']
        # M1 wins BIC over M2 and M3
        self.assertLess(m1['bic'], m2['bic'])
        self.assertLess(m1['bic'], m3['bic'])
        # B0 strictly inside the Lean-certified [0.180, 0.300] band
        self.assertGreaterEqual(m1['B0_ci90_m2_kg'][0], 0.180)
        self.assertLessEqual(m1['B0_ci90_m2_kg'][1], 0.300)

        # Storm vs quiet consistency within 10%
        sc = self.data['storm_vs_quiet_consistency']
        ratio = sc['storm_weighted_B_m2_kg'] / sc['quiet_weighted_B_m2_kg']
        self.assertGreater(ratio, 0.90)
        self.assertLess(ratio, 1.10)


if __name__ == '__main__':
    unittest.main()
