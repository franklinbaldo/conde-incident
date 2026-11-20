#!/usr/bin/env python3
"""Offline integrity tests for C241 aerothermal reentry survival & Lean 4 energy bounds."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'tools'))

import c241_reentry_thermal_survival as mod

LEDGER = REPO_ROOT / 'research' / 'statistics' / 'c241_reentry_thermal_survival_20261120.json'
REPORT = REPO_ROOT / 'research' / 'statistics' / 'C241_REENTRY_THERMAL_SURVIVAL_20261120.md'
TOOL = REPO_ROOT / 'tools' / 'c241_reentry_thermal_survival.py'
LEAN_MOD = REPO_ROOT / 'formal' / 'Conde1963' / 'ReentryTerminalEnergyBound.lean'
LEAN_ROOT = REPO_ROOT / 'formal' / 'Conde1963.lean'


class TestC241ReentryThermalSurvival(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text(encoding='utf-8'))

    def test_files_under_20kb_prek_limit(self):
        for p in (LEDGER, REPORT, TOOL, LEAN_MOD, Path(__file__)):
            self.assertLessEqual(p.stat().st_size, 20000, f'{p} exceeds 20,000 bytes')

    def test_lean_module_imported_and_clean(self):
        src = LEAN_MOD.read_text(encoding='utf-8')
        self.assertNotIn('sorry', src)
        self.assertNotIn('axiom ', src)
        for thm in (
            'norad528_2m_shell_kinetic_le_4860J',
            'norad528_surviving_shell_cannot_excavate_4m_crater',
            'norad528_2m_shell_deficit_over_630x',
            'norad528_1m_titanium_shell_kinetic_le_1296J',
            'high_B_radiative_survival_yet_no_4m_crater_witness',
        ):
            self.assertIn(f'theorem {thm}', src)
        self.assertIn('import Conde1963.ReentryTerminalEnergyBound', LEAN_ROOT.read_text(encoding='utf-8'))

    def test_subsonic_terminal_stats_helper(self):
        v_t, e_kj = mod.subsonic_terminal_stats(0.236, 2.2, 0.47, 29.2)
        self.assertLessEqual(v_t, 18.0)
        self.assertLess(e_kj, 5.0)

    def test_reentry_suite_physical_consistency(self):
        rows = self.data['results']
        self.assertEqual(len(rows), 24)  # 8 geometries * 3 entry angles
        floor_kj = self.data['crater_4m_overburden_floor_kJ']
        self.assertEqual(floor_kj, 3155)
        for r in rows:
            if r['id'] in ('528-A', '528-B'):
                self.assertFalse(r['survived'])
                self.assertIsNotNone(r['demise_alt_km'])
                self.assertGreater(r['demise_alt_km'], 80.0)
            if r['object'] == 528 and r['survived']:
                self.assertLessEqual(r['subsonic_v_terminal_ms'], 18.0)
                self.assertLess(r['terminal_kinetic_kJ'], 5.0)
                self.assertLess(r['terminal_kinetic_kJ'] * 600, floor_kj)
            if r['object'] == 637:
                self.assertTrue(r['survived'])
                self.assertLess(r['terminal_kinetic_kJ'], floor_kj)


if __name__ == '__main__':
    unittest.main()
