"""Reject unearned NARA film-can identification from generic search hits."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('cgeo50_nara_locator_search', ROOT / 'tools/cgeo50_nara_locator_search.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class NaraCatalogTests(unittest.TestCase):
    def setUp(self):
        self.data = module.load(module.DATA)
        self.parent = module.load(module.PARENT)

    def reject(self, mutator):
        bad = copy.deepcopy(self.data)
        mutator(bad)
        with self.assertRaises(ValueError):
            module.validate(bad, self.parent)

    def test_valid(self): self.assertEqual(module.validate(self.data, self.parent), 3)
    def test_wrong_sheet(self): self.reject(lambda d: d.update(candidate_overlay='m1765-317-00250.jpg'))
    def test_wrong_field(self): self.reject(lambda d: d.update(number_printed_field='SPOT NUMBER'))
    def test_fake_spot(self): self.reject(lambda d: d.update(candidate_spot_number='125374'))
    def test_fake_film_can(self): self.reject(lambda d: d.update(candidate_original_negative_can='ON012345'))
    def test_bad_url(self): self.reject(lambda d: d['catalog_searches'][0].update(url='https://example.org/'))
    def test_wrong_term(self): self.reject(lambda d: d['catalog_searches'][0].update(term='000000'))
    def test_scope_overclaim(self): self.reject(lambda d: d.update(catalog_query_scope='All negative inventory examined'))
    def test_false_positive(self): self.reject(lambda d: d['catalog_searches'][0].update(matched_1942_negative_confirmed=True))
    def test_fake_contact(self): self.reject(lambda d: d.update(archivist_contact_sent=True))
    def test_fake_crosswalk(self): self.reject(lambda d: d.update(can_locator_crosswalk_confirmed=True))
    def test_offline_locator_claim(self): self.reject(lambda d: d.update(can_locator_available_on_open_web=True))
    def test_negative_proof(self): self.reject(lambda d: d['limitations'].update(public_search_proves_absence_of_negative=True))
    def test_fake_capture_date(self): self.reject(lambda d: d['limitations'].update(exposure_date_at_conde_verified='1942-09-20'))
    def test_fake_center(self): self.reject(lambda d: d['limitations'].update(conde_urban_center_1963=[-37.6,-11.8]))
    def test_fake_event(self): self.reject(lambda d: d['limitations'].update(event_location=[-37.6,-11.8]))
    def test_orbital_promotion(self): self.reject(lambda d: d['limitations'].update(orbital_constraints_activated=True))

if __name__ == '__main__': unittest.main()
