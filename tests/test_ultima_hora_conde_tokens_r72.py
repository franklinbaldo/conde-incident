"""Adversarial source and interpretation checks for the R72 FBN text-layer index."""
import copy
import json
import unittest

from tools.audit_ultima_hora_conde_tokens_r72 import PATH, validate


class TestR72(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(PATH.read_text(encoding="utf-8"))

    def rejected(self, fn):
        doc = copy.deepcopy(self.original)
        fn(doc)
        with self.assertRaises(ValueError):
            validate(doc)

    def test_original_index(self):
        self.assertTrue(validate(self.original))

    def test_corpus_mutation(self):
        self.rejected(lambda d: d["editions"][0].update(pdf_sha256="0" * 64))
        self.rejected(lambda d: d["editions"][2].update(pdf_pages=9))
        self.rejected(lambda d: d["editions"].pop())

    def test_disallow_fabricated_event_and_witness(self):
        self.rejected(lambda d: d["editions"][1]["checked_pages"][0].update(event_time_literal="19h30"))
        self.rejected(lambda d: d["editions"][1]["checked_pages"][0].update(independent_witness_verified=True))
        self.rejected(lambda d: d["result"].update(confirmed_local_event_time="23:30"))

    def test_no_full_edition_negative_from_text_search(self):
        self.rejected(lambda d: d["result"].update(whole_edition_negative=True))
        self.rejected(lambda d: d["result"].update(full_column_reading_completed=True))
        self.rejected(lambda d: d["method"].update(whole_edition_negative_certified=True))
        self.rejected(lambda d: d["method"].update(new_ocr_performed=True))

    def test_no_arbitrary_reinterpretation(self):
        self.rejected(lambda d: d["editions"][1]["checked_pages"][0].update(
            interpretation="A página confirma a queda do 528 às 19h30 em Conde/BA"))
        self.rejected(lambda d: d["limitations"].append(
            "A ausência do token prova ausência do incidente."))
        self.rejected(lambda d: d["editions"][3]["hits_by_pdf_page"].update({"4": 1}))
        self.rejected(lambda d: d["result"].update(physical_orbital_constraint_added=True))
        self.rejected(lambda d: d.update(independent_satellite_observation=True))


if __name__ == "__main__":
    unittest.main()
