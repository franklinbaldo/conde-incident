"""FBN UH PE 00471 source-classification adversarial tests."""
import copy
import json
import unittest
from tools.verify_ultima_hora_pe_00471_locator import MANIFEST, validate

class TestSourceBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf8"))

    def test_manifest(self):
        self.assertEqual(validate(self.data), [])

    def test_wrong_newspaper(self):
        x = copy.deepcopy(self.data)
        x["publication"] = "Ultima Hora (RJ)"
        self.assertTrue(validate(x))

    def test_wrong_edition(self):
        x = copy.deepcopy(self.data)
        x["edition"] = "00477"
        self.assertTrue(validate(x))

    def test_invented_document_hash(self):
        x = copy.deepcopy(self.data)
        x["pdf_sha256"] = "0" * 64
        self.assertTrue(validate(x))

    def test_hole_claim_without_primary_page(self):
        x = copy.deepcopy(self.data)
        x["four_metre_hole_verified"] = True
        self.assertTrue(validate(x))

    def test_page_promoted_from_index(self):
        x = copy.deepcopy(self.data)
        x["page_8_inspected"] = True
        self.assertTrue(validate(x))

    def test_cdx_absence_exaggeration(self):
        x = copy.deepcopy(self.data)
        x["archive_cdx_scope"] = "The document is absent from the Internet"
        self.assertTrue(validate(x))

    def test_original_text_not_recovered(self):
        x = copy.deepcopy(self.data)
        x["original_text_verified"] = True
        self.assertTrue(validate(x))

if __name__ == "__main__":
    unittest.main()
