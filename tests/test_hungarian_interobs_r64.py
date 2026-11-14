"""Adversarial tests for the original 46 MB PDF's separately recorded bibliography."""
import copy
import json
import unittest
from tools.audit_hungarian_interobs_r64 import MANIFEST, validate

class TestHungarianInterobsR64(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(MANIFEST.read_text(encoding="utf8"))

    def test_reference_passes(self):
        self.assertTrue(validate(self.source))

    def test_immutable_original_digest_size_and_page(self):
        for k, v in [("pdf_sha256", "a"*64),("pdf_size_bytes",46217177),
                     ("source_page_bibliography_one_based", 94),("visual_verification", "UNKNOWN")]:
            with self.subTest(k=k):
                d=copy.deepcopy(self.source);d["source"][k]=v
                with self.assertRaises(ValueError): validate(d)

    def test_no_fabricated_satellite_measurement(self):
        for k,v in [("original_1963_article_recovered",True),
                    ("original_soviet_bulletin_32_recovered",True),
                    ("independent_sensor_measurements_confirmed",True),
                    ("observations_identified_norad_527_528_529",[{"norad":528}]),
                    ("new_orbital_constraints",1)]:
            with self.subTest(k=k):
                d=copy.deepcopy(self.source);d["boundaries"][k]=v
                with self.assertRaises(ValueError):validate(d)

    def test_cannot_misread_1962_campaign_as_1963(self):
        d=copy.deepcopy(self.source);d["references"][1]["subject_observation_year"]=1963
        with self.assertRaises(ValueError):validate(d)

    def test_cannot_confuse_two_1963_serials(self):
        for k,v in [("different_series_first_1963_issue",2),
                    ("kyiv_holding_issue",32),
                    ("series_identity_status","ORIGINAL_SOVIET_BULLETIN")]:
            with self.subTest(k=k):
                d=copy.deepcopy(self.source);d["context"][k]=v
                with self.assertRaises(ValueError):validate(d)

    def test_original_bibliography_numbers_immutable(self):
        for item, v in [(28,32),(27,28)]:
            d=copy.deepcopy(self.source);d["references"][item-27]["item"]=v
            with self.assertRaises(ValueError):validate(d)

if __name__=="__main__":
    unittest.main()
