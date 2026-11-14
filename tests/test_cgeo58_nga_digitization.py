"""CGEO-58: adversarial fail-closed tests, equally effective with python -O."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cgeo58", ROOT / "tools/cgeo58_nga_digitization.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TestNGA(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(m.CONTRACT.read_text(encoding="utf-8"))

    def reject(self, change):
        x = copy.deepcopy(self.data)
        change(x)
        with self.assertRaises(ValueError):
            m.validate(x)

    def test_contract(self):
        self.assertEqual(m.validate(self.data), 3)

    def test_cannot_claim_new_photo(self):
        self.reject(lambda x: x.update(classification="aerial photograph acquired"))

    def test_no_fake_original(self):
        self.reject(lambda x: x["limitations"].update(original_film_frames_acquired=1))

    def test_no_fake_nga_coverage(self):
        self.reject(lambda x: x["limitations"].update(nga_has_specific_conde_negative=True))

    def test_no_fake_access(self):
        self.reject(lambda x: x["limitations"].update(nga_public_digitization_available=True))

    def test_no_foia_sent(self):
        self.reject(lambda x: x["contact"].update(foia_request_sent=True))

    def test_no_nga_request_sent(self):
        self.reject(lambda x: x["contact"].update(nga_request_sent=True))

    def test_no_nara_contact_sent(self):
        self.reject(lambda x: x["contact"].update(nara_contact_sent=True))

    def test_no_spot_assumption(self):
        self.reject(lambda x: x["known_index"].update(spot_numbers_verified=["125374"]))

    def test_no_exposure_claim(self):
        self.reject(lambda x: x["known_index"].update(individual_exposure_ids_verified=["16"]))

    def test_no_film_can(self):
        self.reject(lambda x: x["known_index"].update(film_can_identifiers_verified=["ON9999"]))

    def test_no_fall(self):
        self.reject(lambda x: x["limitations"].update(verified_fall_location=[-11, -37]))

    def test_no_center(self):
        self.reject(lambda x: x["limitations"].update(verified_conde_1963_geometry=[-11, -37]))

    def test_no_orbital_constraint(self):
        self.reject(lambda x: x["limitations"].update(orbital_constraint_activated=True))

    def test_no_mutated_source(self):
        self.reject(lambda x: x["sources"][0].update(sha256="0" * 64))

    def test_no_missing_source(self):
        self.reject(lambda x: x["sources"].pop())

    def test_no_duplication(self):
        self.reject(lambda x: x["sources"][2].update(id="NGA-HIST"))

    def test_no_foia_overclaim(self):
        self.reject(lambda x: x["claims"][1].update(implication="NGA must create an image"))

    def test_nara_semantic_guard_rejects_empty_source(self):
        with self.assertRaises(ValueError):
            m.check_nara_semantics(b"<html>Access denied</html>")

    def test_nara_semantic_guard_accepts_archival_cues(self):
        m.check_nara_semantics(b"<html>Overlay Indexes. Spot Number. Can Locator.</html>")

    def test_no_wrong_parent(self):
        self.reject(lambda x: x.update(parent="CGEO-54"))

if __name__ == "__main__":
    unittest.main()

