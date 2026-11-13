"""Offline controls for limiting a third-party index lookup to its actual scope."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import unittest
from tools.verify_bahia_lei628_locator import validate

DATA = json.loads((Path(__file__).resolve().parents[1] /
                   'research/archive/bahia_lei628_1953_locator_20261113.json').read_text())

class BahiaLei628LocatorTests(unittest.TestCase):
    def test_original_record_is_scoped_to_search_index(self):
        self.assertEqual(validate(DATA), [])
    def assert_rejected(self, edits):
        d = deepcopy(DATA)
        edits(d)
        self.assertNotEqual(validate(d), [])
    def test_no_fabricated_original_pdf(self):
        self.assert_rejected(lambda d: d['locator'].update(pdf_sha256='0'*64))
        self.assert_rejected(lambda d: d['locator'].update(official_1953_1954_facsimile_retrieved=True))
    def test_no_period_projection_to_1963(self):
        self.assert_rejected(lambda d: d['interpretation'].update(caption_period_end_proves_1963_limits_expired=True))
        self.assert_rejected(lambda d: d['interpretation'].update(legal_status_on_target_date='CONFIRMED'))
    def test_no_laundering_search_snippet_as_primary(self):
        self.assert_rejected(lambda d: d['locator'].update(direct_original_text_inspected=True))
        self.assert_rejected(lambda d: d['locator'].update(type='ORIGINAL_FACSIMILE'))
    def test_wrong_toponym_or_law_rejected(self):
        self.assert_rejected(lambda d: d['legal_identity'].update(target_municipality='Conde, Paraíba'))
        self.assert_rejected(lambda d: d['legal_identity'].update(act_date='1954-01-01'))
    def test_no_numerical_geography_from_metadata(self):
        self.assert_rejected(lambda d: d['interpretation'].update(new_geographic_coordinates=True))
        self.assert_rejected(lambda d: d['interpretation'].update(new_orbital_constraint=True))
    def test_reject_unverified_portal_facsimile_claim(self):
        self.assert_rejected(lambda d: d['official_repository_locator'].update(law_specific_original_found_there=True))

if __name__ == '__main__':
    unittest.main()
