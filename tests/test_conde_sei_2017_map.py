"""Adversarial tests: a 2017 map is never evidence of a 1963 boundary."""
import copy
import os
import json
from pathlib import Path
import unittest

from tools.verify_conde_sei_2017_map import validate, verify_bytes

DOC = json.loads((Path(__file__).resolve().parents[1] / 'research/archive/' /
                  'conde_sei_2017_map_custody_20261113.json').read_text())


class SEI2017CustodyTests(unittest.TestCase):
    def test_base_manifest(self):
        self.assertEqual(validate(DOC), [])

    def test_no_backdating_2017_map_to_1963(self):
        for key in ('1963_legal_boundary_demonstrated',
                    'orbital_constraint_activated',
                    '2017_map_is_an_independent_1963_survey',
                    'precise_1963_coordinates_established'):
            bad = copy.deepcopy(DOC)
            bad['epistemology'][key] = True
            self.assertTrue(validate(bad), key)

    def test_no_later_layer_as_contemporary_survey(self):
        bad = copy.deepcopy(DOC)
        bad['source_layers'][0]['year'] = 1963
        self.assertTrue(validate(bad))
        bad = copy.deepcopy(DOC)
        bad['source_layers'][0]['year'] = 1973
        bad['epistemology']['2007_2010_2017_source_layers_are_1963_observations'] = True
        self.assertTrue(validate(bad))

    def test_2013_context_is_not_proof_no_local_amendments(self):
        bad = copy.deepcopy(DOC)
        bad['government_context_2013']['proves_no_intervening_specific_acts'] = True
        self.assertTrue(validate(bad))

    def test_point_order_and_identity(self):
        bad = copy.deepcopy(DOC)
        bad['boundary_points_2017'][0]['id'] = 'P00'
        self.assertTrue(validate(bad))
        bad = copy.deepcopy(DOC)
        bad['boundary_points_2017'] = bad['boundary_points_2017'][:15]
        self.assertTrue(validate(bad))

    def test_no_invented_wayback(self):
        bad = copy.deepcopy(DOC)
        bad['retrieval']['wayback_url'] = 'https://web.archive.org/web/20261113/example'
        self.assertTrue(validate(bad))

    def test_raw_pdf_bytes_and_corruption(self):
        good = b'%PDF-1.6\nabc\n%%EOF\n'
        fixture = {'retrieval': {'bytes': len(good), 'sha256': __import__('hashlib').sha256(good).hexdigest()}}
        self.assertEqual(verify_bytes(good, fixture), [])
        self.assertTrue(any('SHA-256' in x for x in verify_bytes(good.replace(b'abc',b'abd'),fixture)))
        self.assertTrue(any('end marker' in x for x in verify_bytes(good[:-7],fixture)))

    def test_real_pdf_if_available(self):
        source = Path(os.environ['CONDE_SEI_PDF']) if os.environ.get('CONDE_SEI_PDF') else None
        if source and source.is_file():
            self.assertEqual(verify_bytes(source.read_bytes(), DOC), [])
        else:
            self.skipTest('optional downloaded PDF not in CI checkout')


if __name__ == '__main__':
    unittest.main()
