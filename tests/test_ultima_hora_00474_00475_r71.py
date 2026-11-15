"""Adversarial checks for R71 visual scope, provenance and editorial independence."""
import copy
import json
import unittest

from tools.audit_ultima_hora_00474_00475_r71 import PATH, validate


class TestUltimaHoraR71(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(PATH.read_text(encoding="utf-8"))

    def check_rejected(self, mutate):
        d = copy.deepcopy(self.original)
        mutate(d)
        with self.assertRaises(ValueError):
            validate(d)

    def test_original(self):
        self.assertTrue(validate(self.original))

    def test_source_integrity(self):
        for ed_idx in (0, 1):
            for field, value in (("pdf_sha256", "0" * 64), ("pdf_bytes", 1),
                                 ("pdf_pages", 9), ("date_printed", "1963-11-08")):
                with self.subTest(edition=ed_idx, field=field):
                    self.check_rejected(lambda d, i=ed_idx, f=field, v=value:
                                        d["editions"][i].__setitem__(f, v))

    def test_page_denominator(self):
        self.check_rejected(lambda d: d["editions"][0]["pages"].pop())
        self.check_rejected(lambda d: d["editions"][1]["pages"][1].update(pdf_page=3))

    def test_fabricated_time_and_witness(self):
        for field, value in (("event_time_literal", "23:30"),
                             ("independent_witness_verified", True),
                             ("conde_ba_article_verified", True),
                             ("full_page_body_read", True),
                             ("review_scope", "FULL_TEXT_READ")):
            with self.subTest(field=field):
                self.check_rejected(lambda d, f=field, v=value:
                                    d["editions"][1]["pages"][4].__setitem__(f, v))

    def test_false_edition_negative_and_orbital_link(self):
        for field, value in (("whole_edition_no_article_claim", True),
                             ("whole_edition_no_time_claim", True),
                             ("physical_orbital_constraint_added", True),
                             ("confirmed_independent_event_time", "19:30"),
                             ("full_columns_review_completed", True)):
            with self.subTest(field=field):
                self.check_rejected(lambda d, f=field, v=value:
                                    d["result"].__setitem__(f, v))

    def test_changed_topic_or_space_news(self):
        self.check_rejected(lambda d: d["editions"][1]["pages"][4].update(
            topic_overview="Conde viu a queda às 23:30"))
        self.check_rejected(lambda d: d["contextual_article"].update(orbital_observation=True))
        self.check_rejected(lambda d: d["contextual_article"].update(local_event_time=True))
        self.check_rejected(lambda d: d["contextual_article"].update(
            classification="prova original da queda do satélite 528 em Conde"))

    def test_free_text_and_unrecognized_fields_cannot_smuggle_new_evidence(self):
        self.check_rejected(lambda d: d["contextual_article"].update(
            classification=d["contextual_article"]["classification"] +
            "; porém a reportagem prova queda do 528 em Conde às 19h30"))
        self.check_rejected(lambda d: d.update(
            limitations=["Testemunha independente confirma a queda às 19h30."] * 5))
        self.check_rejected(lambda d: d["method"].update(
            visual_review="Todas as colunas lidas; hora da queda em Conde: 19h30"))
        self.check_rejected(lambda d: d["result"].update(
            scientific_conclusion="Fonte prova a reentrada do NORAD 528 às 19h30"))
        self.check_rejected(lambda d: d["editions"][0]["pages"][1].update(
            witness_claim="Testemunha confirma queda do 528 às 19h30"))
        self.check_rejected(lambda d: d.update(
            conde_event_time="1963-11-08 19:30"))


    def test_no_ocr_or_unearned_coverage(self):
        self.check_rejected(lambda d: d["method"].update(full_body_reading=True))
        self.check_rejected(lambda d: d["method"].update(ocr_performed=True))
        self.check_rejected(lambda d: d["result"].update(
            total_pages_with_cover_or_panorama_across_four_editions=50))


if __name__ == "__main__":
    unittest.main()
