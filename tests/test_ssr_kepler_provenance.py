"""Mutations of NASA SSR dimensional provenance must fail closed."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from export_ssr_kepler_provenance import LEDGER, AUDIT, LOCK, OUT, build, render


class KeplerProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text())
        cls.audit = json.loads(AUDIT.read_text())
        cls.lock = json.loads(LOCK.read_text())

    def variant(self, ledger=None, audit=None, lock=None):
        return build(ledger or self.ledger, audit or self.audit, lock or self.lock)

    def test_six_canonical_cells_keep_status_and_links(self):
        out = self.variant()
        self.assertEqual(len(out['cells']), 6)
        self.assertEqual({x['object'] for x in out['cells']}, {'1963-003A','1963-003C'})
        self.assertEqual(len({x['source_pdf_sha256'] for x in out['cells']}), 3)
        self.assertEqual(len({x['source_occurrence'] for x in out['cells']}), 3)
        self.assertNotIn('1963-003B', str(out['cells']))
        self.assertFalse(out['active_physical_constraint'])
        self.assertEqual(out['physical_domain_effect'], 'THETA_UNCHANGED')
        self.assertIsNone(out['lean_kepler_proof'])
        self.assertIsNone(out['simulator_parameter_values'])
        self.assertTrue(all(r['instrument_epoch'] is None and r['covariance'] is None for r in out['cells']))

    def test_reject_wrong_half_kilometer_unit(self):
        bad = copy.deepcopy(self.ledger)
        bad['objects'][0]['printed_values_scaled'][0]['apogee_km'] *= 2
        with self.assertRaises(ValueError): self.variant(ledger=bad)

    def test_reject_mutated_period_centimin(self):
        bad = copy.deepcopy(self.ledger)
        bad['objects'][1]['printed_values_scaled'][2]['period_min'] = 9260
        with self.assertRaises(ValueError): self.variant(ledger=bad)

    def test_reject_forged_pdf_digest(self):
        bad = copy.deepcopy(self.audit)
        bad['cross_field_diagnostics'][3]['source_pdf_sha256'] = '0'*64
        with self.assertRaises(ValueError): self.variant(audit=bad)

    def test_reject_independent_sensor_epoch(self):
        bad = copy.deepcopy(self.audit)
        bad['cross_field_diagnostics'][0]['observational_epoch'] = '1963-11-08T00:00:00Z'
        with self.assertRaises(ValueError): self.variant(audit=bad)

    def test_reject_copied_source_as_fourth_date(self):
        bad = copy.deepcopy(self.ledger)
        bad['source_ids'].append('C198#1')
        with self.assertRaises(ValueError): self.variant(ledger=bad)

    def test_reject_source_lock_drift(self):
        bad = copy.deepcopy(self.lock)
        bad['canonical_value_min'] = '94.8'
        with self.assertRaises(ValueError): self.variant(lock=bad)

    def test_reject_fabricated_precision(self):
        bad = copy.deepcopy(self.audit)
        bad['cross_field_diagnostics'][2]['two_body_period_min'] += .5
        with self.assertRaises(ValueError): self.variant(audit=bad)

    def test_reject_false_print_rounding_interval(self):
        bad = copy.deepcopy(self.audit)
        bad['cross_field_diagnostics'][0]['print_rounding_residual_seconds'] = [0, 0]
        with self.assertRaises(ValueError): self.variant(audit=bad)

    def test_reject_false_wrong_units_negative_control(self):
        bad = copy.deepcopy(self.audit)
        bad['cross_field_diagnostics'][5]['incorrect_unscaled_height_residual_seconds'] = 0
        with self.assertRaises(ValueError): self.variant(audit=bad)

    def test_json_render_reproducible(self):
        self.assertEqual(OUT.read_text(), render())
        self.assertLessEqual(OUT.stat().st_size, 20000)


if __name__ == '__main__':
    unittest.main()
