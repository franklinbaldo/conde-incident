"""Adversarial checks for G38: a J2 proxy does not authenticate an orbit."""
import copy
import json
import unittest

from tools import ssr_dec31_nodal_g38 as g38

LEDGER = json.loads(g38.SOURCE.read_text(encoding='utf-8'))


class TestG38(unittest.TestCase):
    def test_seven_source_locked_rows(self):
        out = g38.evaluate(LEDGER)
        self.assertEqual(len(out['records']), 7)
        self.assertEqual(len({r['source_occurrence'] for r in out['records']}), 7)
        self.assertEqual(out['source_raw_instrument_observations'], 0)
        self.assertEqual(out['independent_527_529_holdout'], 'NOT_RUN')
        self.assertFalse(out['activated_historical_restriction'])

    def test_december_nodal_J2_correction_wrong_sign_for_529(self):
        contrast = g38.evaluate(LEDGER)['december_31_contrast']
        self.assertAlmostEqual(contrast['529_J2_minus_kepler_seconds'], 7.385, delta=0.02)
        self.assertAlmostEqual(contrast['529_printed_minus_J2_seconds'], -128.092, delta=0.02)
        self.assertTrue(contrast['529_printing_box_excludes_zero'])
        self.assertFalse(contrast['first_order_J2_alone_reconciles_529'])
        self.assertTrue(contrast['this_does_not_prove_NASA_error'])

    def test_same_report_527_comparator_is_not_held_out(self):
        out = g38.evaluate(LEDGER)
        self.assertAlmostEqual(out['december_31_contrast']['527_printed_minus_J2_seconds'], -2.716, delta=0.02)
        self.assertIsNone(out['uncertainty']['source_instrument_epoch'])
        self.assertIsNone(out['uncertainty']['source_covariance'])

    def test_all_printing_boxes_contain_nominal_residual(self):
        for row in g38.evaluate(LEDGER)['records']:
            low, high = row['print_box_only_residual_sec_NOT_sigma']
            self.assertLessEqual(low, row['printed_minus_J2_proxy_sec'])
            self.assertLessEqual(row['printed_minus_J2_proxy_sec'], high)
            self.assertIsNone(row['instrument_epoch_utc'])
            self.assertIsNone(row['instrumental_uncertainty'])
            self.assertFalse(row['historical_orbit_fit'])

    def test_mutations_of_unselected_cells_rejected(self):
        for si, ri, key, value in [
            (0, 1, 'period_min', '92.2'),
            (1, 0, 'inclination_deg', '25.00'),
            (2, 1, 'apogee_km', 535),
        ]:
            with self.subTest(si=si, ri=ri, key=key):
                changed = copy.deepcopy(LEDGER)
                changed['sources'][si]['rows'][ri][key] = value
                with self.assertRaises((ValueError, AssertionError)):
                    g38.evaluate(changed)

    def test_mutations_of_custody_rejected(self):
        for key, value in [('sha256', '0'*64), ('published', '1963-12-30'),
                           ('pdf_url', 'https://example.invalid/fake.pdf')]:
            with self.subTest(key=key):
                changed = copy.deepcopy(LEDGER)
                changed['sources'][-1][key] = value
                with self.assertRaises((ValueError, AssertionError)):
                    g38.evaluate(changed)

    def test_round_trip_and_drift_guard(self):
        content = g38.render(LEDGER)
        self.assertEqual(json.loads(content), g38.evaluate(LEDGER))
        self.assertEqual(content, g38.OUTPUT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
