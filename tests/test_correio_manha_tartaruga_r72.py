"""Negative controls for the original Correio da Manhã page-8 record."""
import copy
import json
import unittest

from tools.audit_correio_manha_tartaruga_r72 import MANIFEST, validate


class TestC241R72(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_pinned_custody_and_limited_claim(self):
        self.assertTrue(validate(self.record))

    def test_mutations_of_source(self):
        for key, replacement in (
            ("sha256", "0" * 64),
            ("bytes", 1),
            ("date", "1963-11-08"),
            ("original_pdf_page", 9),
            ("reading_status", "LIDO_COM_HORA"),
            ("reading_status_scope", "ENTIRE_EDITION"),
        ):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.record)
                doc["source"][key] = replacement
                with self.assertRaises(ValueError):
                    validate(doc)

    def test_mutations_of_event_claims(self):
        for key, replacement in (
            ("event_local_clock", "20:40"),
            ("event_utc_clock", "23:40Z"),
            ("eyewitness_name", "unnamed eyewitness"),
            ("direct_independent_event_observation", True),
            ("article_source_independence", "INDEPENDENT"),
            ("official_original_denials_recovered", True),
        ):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.record)
                doc["reporting"][key] = replacement
                with self.assertRaises(ValueError):
                    validate(doc)

    def test_conflation_and_unsupported_scientific_conclusion(self):
        for field, value in (
            ("orbital_constraint_activated", True),
            ("article_proves_nonoccurrence", True),
            ("pdf_other_pages_exhaustively_read", True),
            ("event_time_confirmed", True),
        ):
            with self.subTest(field=field):
                doc = copy.deepcopy(self.record)
                doc["limitations"][field] = value
                with self.assertRaises(ValueError):
                    validate(doc)

    def test_denial_is_attributed_not_instrumental(self):
        doc = copy.deepcopy(self.record)
        doc["reporting"]["attributed_denials"] = ["DIRECT_PHYSICAL_INSPECTION"]
        with self.assertRaises(ValueError):
            validate(doc)

    def test_other_incidents_are_not_conde(self):
        doc = copy.deepcopy(self.record)
        doc["reporting"]["other_localities_not_conde"] = []
        with self.assertRaises(ValueError):
            validate(doc)


if __name__ == "__main__":
    unittest.main()
