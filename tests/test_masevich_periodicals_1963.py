import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "soviet_bibliography_c241_l34", ROOT / "tools/verify_masevich_periodicals_1963.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class BibliographyTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(module.MANIFEST.read_text(encoding="utf-8"))

    def test_manifest(self):
        self.assertTrue(module.validate(self.data))

    def test_no_measurement_promotion(self):
        for field, val in [
            ("target_specific_primary_measurements", 1),
            ("independent_physical_observation", True),
            ("orbital_constraint_activated", True),
            ("station_ephemeris_or_tle_record_found", True),
            ("observed_objects_identified_in_pages", [528]),
        ]:
            with self.subTest(field=field), self.assertRaises(AssertionError):
                copy_ = copy.deepcopy(self.data)
                copy_["interpretive_limits"][field] = val
                module.validate(copy_)

    def test_no_november_1963_projection(self):
        d = copy.deepcopy(self.data)
        d["source"]["russian_preface_date"] = "1963-11"
        with self.assertRaises(AssertionError):
            module.validate(d)

    def test_pagination_not_invented(self):
        d = copy.deepcopy(self.data)
        d["source"]["images"][0]["printed_page"] = 5
        with self.assertRaises(AssertionError):
            module.validate(d)

    def test_issue_not_retrieved(self):
        d = copy.deepcopy(self.data)
        d["bibliography"][1]["catalog_or_original_volume_retrieved"] = True
        with self.assertRaises(AssertionError):
            module.validate(d)

    def test_third_party_not_master_copy(self):
        d = copy.deepcopy(self.data)
        d["source"]["source_authentication"] = "ORIGINAL_ARCHIVE_AUTHENTICATED"
        with self.assertRaises(AssertionError):
            module.validate(d)

    def test_html_tampering_detected(self):
        with self.assertRaises(AssertionError):
            module.validate(self.data, html=b"x" * self.data["source"]["landing_html_bytes"])

    def test_webp_header_and_digest(self):
        asset = self.data["source"]["images"][0]
        fake = b"RIFF" + b"xxxx" + b"WEBP" + b"x" * (asset["bytes"]-12)
        with self.assertRaises(AssertionError):
            module.validate(self.data, page006=fake)

if __name__ == "__main__":
    unittest.main()
