"""Adversarial invariants for old journal indices and their observation-year ambiguity."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lontra_l35", ROOT / "tools/verify_nikolaev_soviet_photo_1962_1964.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BibliographicLocators(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(mod.MANIFEST.read_text(encoding="utf-8"))

    def test_manifest(self):
        self.assertTrue(mod.validate(self.data))

    def test_reject_orbit_claims(self):
        for key, bad in (
            ("target_specific_measurements_retrieved", 1),
            ("orbital_constraint_activated", True),
            ("source_is_original_1963_instrumental_record", True),
            ("asserts_1963_publication_absent", True),
            ("archive_contacted", True),
        ):
            with self.subTest(key=key), self.assertRaises(AssertionError):
                altered = copy.deepcopy(self.data)
                altered[key] = bad
                mod.validate(altered)

    def test_publication_not_observation_date(self):
        changed = copy.deepcopy(self.data)
        changed["references"][1]["observation_epoch"] = "1963-11-08"
        with self.assertRaises(AssertionError):
            mod.validate(changed)

    def test_no_automatic_target_id(self):
        changed = copy.deepcopy(self.data)
        changed["references"][2]["satellite_identifier"] = "1963-003B"
        with self.assertRaises(AssertionError):
            mod.validate(changed)

    def test_no_facsimile_promotion(self):
        changed = copy.deepcopy(self.data)
        changed["source"]["original_journal_facsimiles_retrieved"] = True
        with self.assertRaises(AssertionError):
            mod.validate(changed)

    def test_no_cross_catalogue_content_promotion(self):
        changed = copy.deepcopy(self.data)
        changed["cross_catalogue"]["journal_contents_read_from_this_catalogue"] = True
        with self.assertRaises(AssertionError):
            mod.validate(changed)

    def test_historical_issues_not_deduplicated(self):
        changed = copy.deepcopy(self.data)
        changed["references"][2]["journal_issue"] = 38
        with self.assertRaises(AssertionError):
            mod.validate(changed)

    def test_replay_rejects_html_tampering(self):
        with self.assertRaises(AssertionError):
            mod.validate(self.data, b"x" * self.data["source"]["bytes"])

    def test_source_encoding_is_not_utf8(self):
        changed = copy.deepcopy(self.data)
        changed["source"]["encoding"] = "utf-8"
        with self.assertRaises(AssertionError):
            mod.validate(changed)


if __name__ == "__main__":
    unittest.main()
