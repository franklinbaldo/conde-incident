import copy
import json
import unittest

from tools.audit_usno_translation_r58 import PATH, validate


class TestUSNOTranslationCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(PATH.read_text(encoding="utf-8"))

    def test_current_catalogue(self):
        self.assertTrue(validate(self.record))

    def test_original_and_translation_are_distinct_shelfmarks(self):
        cat = self.record["catalog"]
        self.assertNotEqual(cat["catalogue_number_russian_original"], cat["catalogue_number_translation"])

    def test_candidate_is_not_verified_article(self):
        limitations = self.record["inference_limits"]
        self.assertTrue(limitations["candidate_volume_is_inference"])
        self.assertFalse(limitations["translation_article_seen"])

    def test_negative_controls(self):
        mutants = [
            ("inference_limits", "issue_by_issue_mapping_verified", True),
            ("inference_limits", "original_russian_volume_40_issue_5_seen", True),
            ("inference_limits", "translation_article_seen", True),
            ("inference_limits", "independent_sensor_identified", True),
            ("inference_limits", "activated_orbital_constraints", 1),
            ("inference_limits", "original_article_pdf_sha256", "invented"),
            ("inference_limits", "observation_rows_527_528_529", [{"norad": 528}]),
            ("catalog", "catalogue_number_translation", "QB 1 .A455"),
            ("catalog", "record_bib_id", "unverified"),
            ("upstream", "conflict", "CITATION_CORRECTED"),
        ]
        for group, key, value in mutants:
            with self.subTest(group=group, key=key):
                candidate = copy.deepcopy(self.record)
                candidate[group][key] = value
                with self.assertRaises(ValueError):
                    validate(candidate)

    def test_false_html_hash(self):
        candidate = copy.deepcopy(self.record)
        candidate["catalog"]["catalogue_replay"]["sha256"] = "a" * 64
        with self.assertRaises(ValueError):
            validate(candidate)


if __name__ == "__main__":
    unittest.main()
