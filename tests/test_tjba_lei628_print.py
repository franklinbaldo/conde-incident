"""Adversarial tests for the original DOE publication and temporal limits."""
import copy
import json
import unittest
from tools.verify_tjba_lei628_print import MANIFEST, VOLUME, verify_record


class TestPrimaryPrint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.parent = json.loads(VOLUME.read_text(encoding="utf-8"))

    def test_page_level_evidence(self):
        self.assertEqual(verify_record(self.d, self.parent), [])

    def test_sanction_is_not_publication_date(self):
        changed = copy.deepcopy(self.d)
        changed["law_publication_date"] = "1953-12-30"
        self.assertTrue(verify_record(changed, self.parent))

    def test_page_offset_matters(self):
        changed = copy.deepcopy(self.d)
        changed["pdf_pages_with_law"] = [1, 2]
        self.assertTrue(verify_record(changed, self.parent))

    def test_wrong_parent_digest(self):
        changed = copy.deepcopy(self.d)
        changed["source_pdf_sha256"] = "0" * 64
        self.assertTrue(verify_record(changed, self.parent))

    def test_no_inferred_annex(self):
        changed = copy.deepcopy(self.d)
        changed["annex_vi_page_identified"] = True
        self.assertTrue(verify_record(changed, self.parent))

    def test_no_1963_boundary_inferred(self):
        changed = copy.deepcopy(self.d)
        changed["legal_boundary_1963_demonstrated"] = True
        self.assertTrue(verify_record(changed, self.parent))

    def test_no_orbital_activation(self):
        changed = copy.deepcopy(self.d)
        changed["orbital_constraint_activated"] = True
        self.assertTrue(verify_record(changed, self.parent))


if __name__ == "__main__":
    unittest.main()
