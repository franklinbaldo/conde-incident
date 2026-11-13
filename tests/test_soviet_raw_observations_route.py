"""Adversarial guards for the IKI retrospective and RNB observation-series route."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("c241_l37", ROOT / "tools/verify_soviet_raw_observations_route.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SovietRawSeries(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(mod.MANIFEST.read_text(encoding="utf-8"))

    def test_valid(self):
        self.assertTrue(mod.validate(self.doc))

    def test_no_invented_orbit(self):
        for key, value in (
            ("independent_target_observations", 1),
            ("new_numeric_observables", 1),
            ("orbital_constraints_activated", 1),
            ("original_1963_instrument_read", True),
            ("archive_contacted", True),
        ):
            with self.subTest(key=key), self.assertRaises(AssertionError):
                bad = copy.deepcopy(self.doc)
                bad[key] = value
                mod.validate(bad)

    def test_no_catalogue_to_facsimile(self):
        for i in range(2):
            with self.subTest(i=i), self.assertRaises(AssertionError):
                bad = copy.deepcopy(self.doc)
                bad["bibliographic_followups"][i]["original_pages_retrieved"] = True
                mod.validate(bad)

    def test_catalogue_has_no_original_bytes_hash(self):
        bad = copy.deepcopy(self.doc)
        bad["bibliographic_followups"][0]["source_bytes_sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            mod.validate(bad)

    def test_no_target_identification_in_june_entry(self):
        bad = copy.deepcopy(self.doc)
        bad["bibliographic_followups"][0]["target_527_528_529_explicitly_named"] = True
        with self.assertRaises(AssertionError):
            mod.validate(bad)

    def test_no_serial_merge_by_similar_title(self):
        bad = copy.deepcopy(self.doc)
        bad["source_distinction"]["same_serial_title_proven"] = True
        with self.assertRaises(AssertionError):
            mod.validate(bad)

    def test_source_not_1963_instrument(self):
        bad = copy.deepcopy(self.doc)
        bad["retrospective_author_source"]["source_role"] = "INSTRUMENTAL_OBSERVATION"
        with self.assertRaises(AssertionError):
            mod.validate(bad)

    def test_publication_and_observation_dates_not_conflated(self):
        bad = copy.deepcopy(self.doc)
        bad["bibliographic_followups"][0]["period_described_in_catalogue"] = "1964"
        with self.assertRaises(AssertionError):
            mod.validate(bad)

    def test_reject_corrupt_pdf_bytes(self):
        with self.assertRaises(AssertionError):
            mod.validate(self.doc, b"bad")
        with self.assertRaises(AssertionError):
            mod.validate(self.doc, b"%PDF-" + b"a" * (7317076 - 5))

    def test_hash_diff_even_with_magic_and_eof(self):
        from hashlib import sha256
        pdf = b"%PDF-" + b" " * (7317076 - 10) + b"%%EOF"
        self.assertNotEqual(sha256(pdf).hexdigest(), self.doc["retrospective_author_source"]["sha256"])
        with self.assertRaises(AssertionError):
            mod.validate(self.doc, pdf)


if __name__ == "__main__":
    unittest.main()
