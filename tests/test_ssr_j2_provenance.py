"""G35 provenance bridge: mutation controls on NASA SSR custody and physics status."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from export_ssr_j2_provenance import LEDGER, UPSTREAM, G35, SIM, OUT, build, render


class J2Provenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = [json.loads(p.read_text()) for p in (LEDGER, UPSTREAM, G35, SIM)]

    def variant(self, index=None, mutate=None):
        docs = copy.deepcopy(self.docs)
        if index is not None:
            mutate(docs[index])
        return build(*docs)

    def test_six_cells_three_same_edition_pairs(self):
        v = self.variant()
        self.assertEqual(len(v['cells']), 6)
        self.assertEqual(len(v['contrasts']), 3)
        self.assertEqual(len({(x['publication_date_not_epoch'], x['source_pdf_sha256']) for x in v['cells']}), 3)
        self.assertNotIn('1963-003B', str(v['cells']))
        self.assertFalse(v['active_physical_constraint'])
        self.assertEqual(v['physical_domain_effect'], 'THETA_UNCHANGED')
        self.assertIsNone(v['lean_j2_proof'])
        self.assertIsNone(v['simulator_calibrated_values'])
        self.assertTrue(all(x['instrument_epoch_utc'] is None for x in v['cells']))
        self.assertTrue(all(x['conditional_a_minus_c_deg_day'][0] > 0 for x in v['contrasts']))

    def test_source_digest_substitution_is_rejected(self):
        with self.assertRaises(ValueError):
            self.variant(2, lambda d: d['results'][0].update(source_pdf_sha256='0'*64))

    def test_swap_publication_and_object_is_rejected(self):
        with self.assertRaises(ValueError):
            self.variant(2, lambda d: d['results'][0].update(designator='1963-003C'))

    def test_wrong_physical_units_are_rejected(self):
        with self.assertRaises(ValueError):
            self.variant(0, lambda d: d['objects'][0]['printed_values_scaled'][0].update(perigee_km=9240))

    def test_j2_nominal_forgery_is_rejected(self):
        with self.assertRaises(ValueError):
            self.variant(2, lambda d: d['results'][2].update(nominal_deg_day=0.0))

    def test_interval_forgery_is_rejected(self):
        with self.assertRaises(ValueError):
            self.variant(2, lambda d: d['paired_model_contrasts'][1].update(a_minus_c_deg_day=[0., 0.]))

    def test_sensor_epoch_forgery_is_rejected(self):
        with self.assertRaises(ValueError):
            self.variant(1, lambda d: d['cells'][0].update(instrument_epoch='1963-11-08T00:00:00Z'))

    def test_instrument_uncertainty_forgery_is_rejected(self):
        with self.assertRaises(ValueError):
            self.variant(2, lambda d: d['limitations'].update(original_covariance=[[1.]]))

    def test_assume_instrumental_holdout_is_rejected(self):
        with self.assertRaises(ValueError):
            self.variant(2, lambda d: d['limitations'].update(validation='HISTORICALLY_VALIDATED'))

    def test_g34_documentary_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            self.variant(1, lambda d: d.update(active_physical_constraint=True))

    def test_stale_or_oversized_export_rejected(self):
        self.assertEqual(render(), OUT.read_text())
        self.assertLessEqual(OUT.stat().st_size, 20000)


if __name__ == '__main__':
    unittest.main()
