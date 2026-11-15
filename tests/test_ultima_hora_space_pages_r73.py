"""Adversarial tests for R73 narrow page-level negative and Explorer 18 identity."""
import copy
import json
import unittest
from tools.audit_ultima_hora_space_pages_r73 import PATH, validate

class TestR73(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(PATH.read_text(encoding="utf-8"))
    def reject(self, change):
        document=copy.deepcopy(self.doc)
        change(document)
        with self.assertRaises(ValueError):
            validate(document)
    def test_original(self):
        self.assertTrue(validate(self.doc))
    def test_wrong_synthetic_target(self):
        self.reject(lambda x:x["pages"][0].update(space_headline_literal='NASA: "Explorer 1" Abrirá Caminho Aos Cosmonautas'))
        self.reject(lambda x:x["pages"][0].update(pdf_sha256="0"*64))
    def test_no_invented_time_or_eyewitness(self):
        self.reject(lambda x:x["pages"][1].update(independent_event_time_literal="19h30"))
        self.reject(lambda x:x["pages"][0].update(independent_witness="testemunha"))
    def test_no_negative_beyond_two_pages(self):
        self.reject(lambda x:x["result"].update(full_editions_read=True))
        self.reject(lambda x:x["result"].update(all_four_editions_negative=True))
        self.reject(lambda x:x["method"].update(pdftotext_negative_inference=True))
    def test_no_new_orbital_constraint(self):
        self.reject(lambda x:x["result"].update(physical_orbital_constraint_added=True))
        self.reject(lambda x:x["pages"][1].update(orbital_observation_of_528_or_637=True))
    def test_no_freeform_fabrication(self):
        self.reject(lambda x:x["pages"][0].update(other_content="Conde/BA queda 19h30"))
        self.reject(lambda x:x.update(novel_confidence=1))
if __name__=="__main__":
    unittest.main()
