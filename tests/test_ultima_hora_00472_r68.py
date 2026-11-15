"""Adversarial scope, clock, and custody checks for the first internal-page batch."""
import copy
import json
import unittest
from tools.audit_ultima_hora_00472_r68 import PATH, validate

class TestUltimaHoraR68(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(PATH.read_text(encoding="utf-8"))

    def test_source(self):
        self.assertTrue(validate(self.d))

    def test_forged_timestamp_and_independence_rejected(self):
        for field, value in (("event_time_literal", "20:40"), ("independent_witness_verified", True), ("conde_ba_article_verified", True)):
            with self.subTest(field=field):
                d = copy.deepcopy(self.d)
                d["pages"][2][field] = value
                with self.assertRaises(ValueError):
                    validate(d)

    def test_unearned_whole_edition_negative_rejected(self):
        for field in ("whole_edition_no_article_claim", "whole_edition_no_time_claim", "physical_orbital_constraint_added"):
            d = copy.deepcopy(self.d)
            d["result"][field] = True
            with self.assertRaises(ValueError):
                validate(d)

    def test_changed_digest_or_page_coverage_rejected(self):
        for mutate in (lambda d: d["source"].update(pdf_sha256="0"*64),
                       lambda d: d["pages"].pop(),
                       lambda d: d["pages"][1].update(review_scope="FULL_TEXT_READ"),
                       lambda d: d["result"].update(pages_remaining_for_panorama_of_all_four_editions=0)):
            d = copy.deepcopy(self.d)
            mutate(d)
            with self.assertRaises(ValueError):
                validate(d)

if __name__ == "__main__":
    unittest.main()
