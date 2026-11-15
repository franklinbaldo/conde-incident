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
    def test_invented_clock_in_free_text(self):
        self.reject(lambda x:x["pages"][0].update(space_article_classification="Testemunha confirmou queda às 20h15"))
    def test_invented_brazil_fall_in_other_content(self):
        self.reject(lambda x:x["pages"][1].update(other_content="Objeto metálico caiu na Bahia às 19h45"))
    def test_false_nasa_extrapolation(self):
        self.reject(lambda x:x["external_crosscheck"].update(finding="NASA confirmou queda do NORAD 528 em 1963"))
    def test_unreviewed_method_field(self):
        self.reject(lambda x:x["method"].update(verified_independent_event_clock="20h15"))
    def test_invented_rationale(self):
        self.reject(lambda x:x.update(rationale="Documento comprova hora de 20h15"))
    def test_global_negative_in_limitations(self):
        self.reject(lambda x:x["limitations"].__setitem__(0,"Todos os jornais foram lidos; ausencia global confirmada"))
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
