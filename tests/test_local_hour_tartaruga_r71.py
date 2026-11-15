"""Adversarial controls for NARA time fields and newspaper independence."""
import copy
import json
import unittest

from tools.audit_local_hour_tartaruga_r71 import MANIFEST, validate

class TestLocalHourR71(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_custody_and_claims(self):
        self.assertTrue(validate(self.base))

    def test_mutations_of_primary_page(self):
        for field, value in [("source_sha256", "0" * 64), ("source_bytes", 1),
                             ("status", "LIDO_COM_HORA"), ("event_clock", "20:40"),
                             ("independent_witness", True)]:
            with self.subTest(field=field):
                d = copy.deepcopy(self.base)
                d["nara"]["objects"][0][field] = value
                with self.assertRaises(ValueError):
                    validate(d)

    def test_telegram_time_cannot_be_event_time(self):
        d = copy.deepcopy(self.base)
        d["nara"]["objects"][1]["telegram_clock_role"] = "EVENT_TIME"
        with self.assertRaises(ValueError):
            validate(d)

    def test_newspaper_original_not_invented(self):
        for field, value in [("status", "LIDO_COM_HORA"), ("reported_event_clock", "20:40"),
                             ("article_independence", "INDEPENDENT")]:
            with self.subTest(field=field):
                d = copy.deepcopy(self.base)
                d["newspapers"][2][field] = value
                with self.assertRaises(ValueError):
                    validate(d)

    def test_diarios_affiliation_cannot_be_erased(self):
        d = copy.deepcopy(self.base)
        d["newspapers"][1]["editorial_network"] = "INDEPENDENT"
        with self.assertRaises(ValueError):
            validate(d)

    def test_orbital_conclusion_needs_observation(self):
        d = copy.deepcopy(self.base)
        d["limits"]["orbital_constraint"] = True
        with self.assertRaises(ValueError):
            validate(d)

if __name__ == "__main__":
    unittest.main()
