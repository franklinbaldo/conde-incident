"""Adversarial custody, source clock and scope tests for R69."""
import copy
import json
import unittest
from tools.audit_ultima_hora_00473_r69 import PATH, validate

class TestUltimaHoraR69(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PATH.read_text(encoding="utf-8"))

    def test_original(self):
        self.assertTrue(validate(self.data))

    def test_fabricated_clock_or_witness(self):
        for field, value in (("event_time_literal", "23:30"), ("independent_witness_verified", True),
                             ("conde_ba_article_verified", True), ("full_page_body_read", True)):
            d = copy.deepcopy(self.data)
            d["pages"][4][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(d)

    def test_whole_edition_and_orbit_promotions(self):
        for field, value in (("whole_edition_no_article_claim", True),
                             ("whole_edition_no_time_claim", True),
                             ("physical_orbital_constraint_added", True),
                             ("confirmed_independent_event_time", "23:30")):
            d = copy.deepcopy(self.data)
            d["result"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(d)

    def test_mutated_custody_and_page_coverage(self):
        for mutate in (lambda d: d["source"].update(pdf_sha256="0"*64),
                       lambda d: d["source"].update(pdf_bytes=1),
                       lambda d: d["pages"].pop(),
                       lambda d: d["pages"][2].update(review_scope="FULL_TEXT_READ"),
                       lambda d: d["contextual_article"].update(orbital_observation=True),
                       lambda d: d["result"].update(pages_remaining_for_panorama_of_all_four_editions=0)):
            d = copy.deepcopy(self.data)
            mutate(d)
            with self.assertRaises(ValueError):
                validate(d)

if __name__ == "__main__":
    unittest.main()
