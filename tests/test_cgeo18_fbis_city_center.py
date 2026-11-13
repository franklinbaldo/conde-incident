"""CGEO-18: adversarial checks stop an English radio report becoming a GIS fix."""
import copy
import json
import unittest
from pathlib import Path

from tools.cgeo18_fbis_city_center import CONTRACT, EXPECTED_SHA256, validate, verify_source


class CGEO18CityCenterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_real_source_and_verbatim_english_phrase(self):
        validate(self.data)
        self.assertEqual(self.data["document"]["sha256"], EXPECTED_SHA256)
        self.assertFalse(self.data["document"]["original_portuguese_words_verified"])

    def test_source_binary_checksum_when_present(self):
        source = Path("/workspace/caranguejo-round16-evidence/FBIS-Tupi-1963-11-08.pdf")
        # Binary replay is optional and separate from offline contract tests.
        if source.is_file():
            verify_source(source)

    def test_fbis_phrase_is_not_a_municipality_centroid(self):
        self.assertFalse(self.data["spatial_interpretation"]["municipal_polygon_centroid_is_city_center"])
        self.assertIsNone(self.data["spatial_interpretation"]["historical_center_point"])

    def test_adversarial_promotions_fail(self):
        mutations = [
            ("transcript", "location_phrase_english", "FELL IN THE MIDDLE OF CONDE"),
            ("document", "sha256", "0" * 64),
            ("document", "original_portuguese_words_verified", True),
            ("transcript", "verified_event_time", "23:30"),
            ("transcript", "broadcast_clock_timezone", "UTC"),
            ("spatial_interpretation", "praça_severiano_lima_1958_identity_confirmed", True),
            ("spatial_interpretation", "municipal_polygon_centroid_is_city_center", True),
            ("spatial_interpretation", "historical_center_point", [-37.6, -11.8]),
            ("spatial_interpretation", "matched_square", "Praça Severiano Lima"),
            ("spatial_interpretation", "can_constrain_orbital_reentry", True),
        ]
        for section, key, new_value in mutations:
            with self.subTest(key=key):
                changed = copy.deepcopy(self.data)
                changed[section][key] = new_value
                with self.assertRaises(ValueError):
                    validate(changed)

    def test_source_not_independent_of_c01(self):
        changed = copy.deepcopy(self.data)
        changed["dependency_graph"] = [e for e in changed["dependency_graph"] if e["to"] != "C01"]
        with self.assertRaises(ValueError):
            validate(changed)


if __name__ == "__main__":
    unittest.main()
