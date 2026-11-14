import copy
import json
import unittest
from tools.audit_polish_nafa_r60 import PATH, validate

class TestPolishNafa(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(PATH.read_text(encoding="utf-8"))

    def test_valid(self):
        self.assertTrue(validate(self.source))

    def test_source_mutations_rejected(self):
        for field,value in [("year",1963),("sha256","f"*64),("bytes",1),
                            ("pdf_eof_seen",False),("pdf_page_indices_zero_based_verified_visually",[62,71]),
                            ("custody_scope","original 1963 Soviet observation")]:
            with self.subTest(field=field):
                case=copy.deepcopy(self.source)
                case["source"][field]=value
                with self.assertRaises(ValueError): validate(case)

    def test_reference_promotions_rejected(self):
        for index,field,value in [(4,"bulletin_issue",33),(4,"year",1969),
                                  (4,"authors",["Other Author"]),(4,"status","FACSIMILE_RETRIEVED")]:
            with self.subTest(field=field):
                case=copy.deepcopy(self.source)
                case["source_references"][index][field]=value
                with self.assertRaises(ValueError):validate(case)

    def test_false_physical_constraints_rejected(self):
        for field,value in [("original_1963_bulletin_32_retrieved",True),
                            ("original_1963_azh_article_retrieved",True),
                            ("chronograph_21p_same_instrument_proven",True),
                            ("observations_norad_527_528_529",[{"norad":528}]),
                            ("independent_instrumental_observations",1),
                            ("new_orbital_constraints",1),
                            ("institutional_contact_sent",True)]:
            with self.subTest(field=field):
                case=copy.deepcopy(self.source)
                case["boundaries"][field]=value
                with self.assertRaises(ValueError):validate(case)

if __name__=="__main__":
    unittest.main()
