"""FBN UH PE 00471 source-classification adversarial tests."""
import copy
import json
import unittest
from tools.verify_ultima_hora_pe_00471_locator import MANIFEST, validate, selected_edition

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

    def test_previous_catalog_url_was_different_edition(self):
        x = copy.deepcopy(self.data)
        x["catalog_url"] = "https://memoria.bn.gov.br/DocReader/765147/5756"
        self.assertIn("catalog_url", validate(x))
        self.assertEqual(self.data["earlier_catalog_selected_edition"], "00507")

    def test_exact_physical_page_ids(self):
        self.assertEqual(self.data["docreader_first_physical_id"], 5339)
        self.assertEqual(self.data["docreader_last_physical_id"], 5346)
        self.assertEqual(self.data["docreader_requested_page8_candidate_id"], 5346)
        self.assertTrue(self.data["docreader_physical_ids_are_not_printed_pages"])

    def test_page8_candidate_is_not_page8_inspection(self):
        x = copy.deepcopy(self.data)
        x["docreader_page8_raster_retrieved"] = True
        self.assertIn("docreader_page8_raster_retrieved", validate(x))
        x = copy.deepcopy(self.data)
        x["docreader_requested_page8_candidate_url"] = x["earlier_catalog_url"]
        self.assertIn("docreader_requested_page8_candidate_url", validate(x))

    def test_selected_folder_not_sidebar_edition(self):
        menu = '<span class="rtIn">Edição 00471</span>'
        selected = '<span id="PastaTxt" title="Ano 1963\\Edição 00507">'
        self.assertEqual(selected_edition(selected + menu), "00507")
        good = '<span id="PastaTxt" title="Ano 1963\\Edição 00471">'
        self.assertEqual(selected_edition(good + menu), "00471")
        self.assertIsNone(selected_edition(menu))

if __name__ == "__main__":
    unittest.main()
