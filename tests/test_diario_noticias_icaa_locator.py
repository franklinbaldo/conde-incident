"""Adversarial evidence-classification tests for ICAA/FBN catalog disambiguation."""
import copy
import json
import unittest
from tools.verify_diario_noticias_icaa_locator import MANIFEST, validate

class TestICAAHolding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_control(self):
        self.assertEqual(validate(self.record), [])

    def assert_rejected(self, path, value):
        d = copy.deepcopy(self.record)
        obj = d
        for key in path[:-1]:
            obj = obj[key]
        obj[path[-1]] = value
        self.assertNotEqual(validate(d), [])

    def test_no_fabricated_newspaper_image(self):
        self.assert_rejected(("catalog", "newspaper_image_retrieved"), True)
        self.assert_rejected(("catalog", "newspaper_image_sha256"), "0" * 64)

    def test_separate_year_runs(self):
        self.assert_rejected(("similarly_named_fbn_docreader", "declared_year_range"), [1876, 1963])
        self.assert_rejected(("similarly_named_fbn_docreader", "covers_target_1963"), True)
        self.assert_rejected(("similarly_named_fbn_docreader", "not_equivalent_to_icaa_digitized_item"), False)

    def test_item_is_not_conde_news(self):
        self.assert_rejected(("independence", "catalog_article_is_about_conde"), True)
        self.assert_rejected(("independence", "independent_conde_observation_added"), True)
        self.assert_rejected(("research_target", "text_corroboration_of_conde_event"), True)

    def test_no_unread_target_and_orbit(self):
        self.assert_rejected(("research_target", "target_article_read"), True)
        self.assert_rejected(("research_target", "newspaper_pdf_sha256"), "0" * 64)
        self.assert_rejected(("independence", "orbital_constraint_activated"), True)

    def test_date_and_page_must_not_slide(self):
        self.assert_rejected(("catalog", "date"), "1963-11-09")
        self.assert_rejected(("catalog", "printed_page"), 8)

if __name__ == "__main__":
    unittest.main()
