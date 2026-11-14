import copy
import json
import unittest

from tools.audit_azh_issue_r57 import PATH, validate


class TestBibliographicCustody(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(PATH.read_text(encoding="utf-8"))

    def test_untouched_manifest(self):
        self.assertTrue(validate(self.data))

    def test_conflicting_claim_preserved(self):
        self.assertEqual(self.data["original_publication"]["claimed_month"], "1963-05")
        self.assertEqual(self.data["chronology_review"]["status"], "CITATION_CHRONOLOGY_UNRESOLVED")

    def test_no_facsimile(self):
        self.assertFalse(self.data["original_publication"]["facsimile_retrieved"])

    def test_catalogue_holdings_not_sensor(self):
        self.assertEqual(self.data["scientific_limits"]["norad_527_528_529_instrumental_observations"], [])
        self.assertEqual(self.data["scientific_limits"]["activated_orbital_constraints"], 0)

    def test_mutation_attacks(self):
        edits = [
            ("original_publication", "actual_issue_month", "1963-09"),
            ("original_publication", "facsimile_retrieved", True),
            ("original_publication", "original_pdf_sha256", "fabricated"),
            ("original_publication", "claimed_issue", 3),
            ("chronology_review", "status", "VERIFIED"),
            ("scientific_limits", "new_sensor_identified", True),
            ("scientific_limits", "activated_orbital_constraints", 1),
            ("scientific_limits", "contact_with_institutions", True),
            ("upstream", "intermediary_us_report_date", "1963-11-19"),
        ]
        for scope, key, val in edits:
            with self.subTest(scope=scope, key=key):
                tampered = copy.deepcopy(self.data)
                tampered[scope][key] = val
                with self.assertRaises(ValueError):
                    validate(tampered)

    def test_index_only_cannot_be_promoted(self):
        tampered = copy.deepcopy(self.data)
        tampered["holdings"][1]["status"] = "PDF_RETRIEVED"
        with self.assertRaises(ValueError):
            validate(tampered)

    def test_holdings_cannot_be_invented(self):
        tampered = copy.deepcopy(self.data)
        tampered["holdings"][0]["issues_listed"] = [1, 2, 3, 4, 5]
        with self.assertRaises(ValueError):
            validate(tampered)

    def test_no_fabricated_html_hash(self):
        tampered = copy.deepcopy(self.data)
        tampered["holdings"][0]["html_sha256_observed"] = "0" * 64
        with self.assertRaises(ValueError):
            validate(tampered)


if __name__ == "__main__":
    unittest.main()
