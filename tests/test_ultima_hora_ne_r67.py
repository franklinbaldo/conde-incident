"""Mutations must not promote newspaper covers into event times or full-page negatives."""
import copy
import json
import unittest

from tools.audit_ultima_hora_ne_r67 import MANIFEST, validate


class TestUltimaHoraR67(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_original(self):
        self.assertTrue(validate(self.source))

    def test_wrong_hash_or_edition_fails(self):
        for index, key, val in [(0, "pdf_sha256", "0" * 64), (1, "edition", "00471"), (2, "pdf_bytes", 1), (3, "date", "1963-11-13")]:
            with self.subTest(index=index, key=key):
                d = copy.deepcopy(self.source)
                d["issues"][index][key] = val
                with self.assertRaises(ValueError):
                    validate(d)

    def test_false_whole_edition_negative_fails(self):
        for key, val in [("other_pages_fully_read", True), ("edition_wide_negative_claim", True), ("front_page_status_scope", "WHOLE_ISSUE")]:
            with self.subTest(key=key):
                d = copy.deepcopy(self.source)
                d["issues"][0][key] = val
                with self.assertRaises(ValueError):
                    validate(d)

    def test_made_up_clock_or_witness_fails(self):
        for key, val in [("condereport_hour_quoted", "20:40"), ("condereport_site_quoted", "Conde"), ("reporter_independence", "INDEPENDENT")]:
            with self.subTest(key=key):
                d = copy.deepcopy(self.source)
                d["issues"][2][key] = val
                with self.assertRaises(ValueError):
                    validate(d)

    def test_a_tarde_is_digitized_but_not_online_read(self):
        for key, val in [("claim_not_digitized", True), ("scans_read", True), ("exact_issues_confirmed", True)]:
            with self.subTest(key=key):
                d = copy.deepcopy(self.source)
                d["atarde"][key] = val
                with self.assertRaises(ValueError):
                    validate(d)

    def test_no_fabricated_independent_hours(self):
        for key, val in [("hour_local_event_found", True), ("independent_witness_verified", True), ("physical_orbital_constraint_added", True), ("all_original_pages_visually_read", True)]:
            with self.subTest(key=key):
                d = copy.deepcopy(self.source)
                d["limitations"][key] = val
                with self.assertRaises(ValueError):
                    validate(d)


if __name__ == "__main__":
    unittest.main()
