"""CGEO-19: regression and adversarial tests for three editorial 1959 photo claims."""
from __future__ import annotations

import copy
import json
import unittest

from tools.cgeo19_1959_photos import CONTRACT, EXPECTED, SOURCE_HTML_SHA, validate


class CGEO19Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_real_custody_and_editorial_count(self) -> None:
        validate(self.data)
        self.assertEqual(len(self.data["images"]), 4)
        self.assertEqual(self.data["source"]["html_sha256_at_retrieval"], SOURCE_HTML_SHA)
        self.assertEqual(sum(p["published_capture_year_claim"] == 1959 for p in self.data["images"]), 3)
        self.assertEqual(sum(p["published_capture_year_claim"] == 2012 for p in self.data["images"]), 1)
        self.assertEqual(self.data["editorial_claims"]["independent_publications_in_this_contract"], 1)

    def test_actual_hashes_are_fixed(self) -> None:
        for p in self.data["images"]:
            self.assertEqual(p["sha256"], EXPECTED[p["id"]][0])
            self.assertEqual(p["byte_size"], EXPECTED[p["id"]][1])

    def test_adversarial_date_geolocation_and_independence(self) -> None:
        for section, key, bad in (
            ("editorial_claims", "capture_year_1959_proven", True),
            ("editorial_claims", "photo_authenticity_and_location_1963_proven", True),
            ("editorial_claims", "independent_publications_in_this_contract", 4),
            ("editorial_claims", "claimed_1959_images", 4),
            ("editorial_claims", "original_image_byte_equality", True),
            ("editorial_claims", "transformation_or_pixel_identity_verified", True),
            ("geospatial_export", "historical_center_polygon", [[-37.62, -11.79]]),
            ("geospatial_export", "camera_positions_1959", [[-37.62, -11.79]]),
            ("geospatial_export", "matched_1958_ibge_square", "Praça Severiano Lima"),
            ("geospatial_export", "event_impact_location", [-37.62, -11.79]),
            ("geospatial_export", "can_constrain_orbital_reentry", True),
            ("source", "license_for_redistribution_verified", True),
        ):
            with self.subTest(key=key):
                altered = copy.deepcopy(self.data)
                altered[section][key] = bad
                with self.assertRaises(ValueError):
                    validate(altered)

    def test_adversarial_image_claims(self) -> None:
        for index, field, bad in (
            (0, "sha256", "0" * 64),
            (0, "source_capture_date_authenticated", True),
            (0, "source_photographer_authenticated", True),
            (0, "exif_capture_datetime", "1959-01-01T00:00:00"),
            (0, "camera_coordinates", [-37.62, -11.79]),
            (1, "published_capture_year_claim", 1959),
            (2, "geo_registration_points", [[0, 0]]),
            (3, "location_verified_to_building_or_street", True),
        ):
            with self.subTest(index=index, field=field):
                altered = copy.deepcopy(self.data)
                altered["images"][index][field] = bad
                with self.assertRaises(ValueError):
                    validate(altered)

    def test_graph_cannot_be_silently_disconnected(self) -> None:
        altered = copy.deepcopy(self.data)
        altered["dependencies"] = [e for e in altered["dependencies"] if e["to"] != "CGEO-18"]
        with self.assertRaises(ValueError):
            validate(altered)

    def test_captions_pinned_to_correct_order(self) -> None:
        altered = copy.deepcopy(self.data)
        altered["images"][0]["caption"] = altered["images"][2]["caption"]
        with self.assertRaises(ValueError):
            validate(altered)


if __name__ == "__main__":
    unittest.main()
