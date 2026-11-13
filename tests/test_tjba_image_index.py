"""Guard the difference between viewer-image entries and PDF page objects."""

from __future__ import annotations

import copy
import json
import unittest

from tools.verify_tjba_image_index import ARCHIVE, DOC_FILES, MANIFEST, validate


class ImageIndexAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.sources = {
            key: json.loads((ARCHIVE / path).read_text(encoding="utf-8"))
            for key, path in DOC_FILES.items()
        }

    def test_original_provenance(self):
        self.assertEqual([], validate(self.record, self.sources))

    def test_empty_image_index_does_not_erase_pdf_pages(self):
        self.assertEqual([823, 856],
                         [d["pdf_pages_preserved_separately"] for d in self.record["documents"]])
        self.assertEqual([0, 0], [d["viewer_total_value"] for d in self.record["documents"]])

    def test_wrong_catalog_node_detected(self):
        damaged = copy.deepcopy(self.record)
        damaged["documents"][0]["catalog_node_id"] = "0" * 32
        self.assertTrue(validate(damaged, self.sources))

    def test_wrong_pdf_page_count_detected(self):
        damaged = copy.deepcopy(self.record)
        damaged["documents"][1]["pdf_pages_preserved_separately"] = 0
        self.assertTrue(validate(damaged, self.sources))

    def test_no_legal_claim_promoted(self):
        damaged = copy.deepcopy(self.record)
        damaged["law_628_1953_page_found"] = True
        self.assertIn("law_628_1953_page_found:not-evidenced",
                      validate(damaged, self.sources))

    def test_false_image_count_detected(self):
        damaged = copy.deepcopy(self.record)
        damaged["documents"][1]["images_json_response"] = ["fictional"]
        self.assertTrue(validate(damaged, self.sources))


if __name__ == "__main__":
    unittest.main()
