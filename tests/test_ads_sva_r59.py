import copy
import json
import unittest
from tools.audit_ads_sva_r59 import PATH, validate

class TestAdsSvaLocator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PATH.read_text(encoding="utf-8"))

    def test_manifest(self):
        self.assertTrue(validate(self.data))

    def test_negative_promotions(self):
        mutations = [
            ("individual_1963_article_link_found",True),
            ("volume_7_issue_3_opened",True),
            ("original_russian_article_opened",True),
            ("issue_month_crosswalk_verified",True),
            ("independent_soviet_tracking_sensor",True),
            ("new_orbital_constraints",1),
            ("observations_norad_527_528_529",[{"norad":528}]),
            ("pdf_sha256","f"*64),
        ]
        for key,value in mutations:
            with self.subTest(key=key):
                case = copy.deepcopy(self.data)
                case["inference_limits"][key] = value
                with self.assertRaises(ValueError):
                    validate(case)

    def test_hash_is_index_only(self):
        case = copy.deepcopy(self.data)
        case["catalogue"]["hash_scope"] = "hash proves source article"
        with self.assertRaises(ValueError):
            validate(case)

if __name__ == "__main__":
    unittest.main()
