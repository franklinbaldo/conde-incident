"""Adversarial tests for CGEO-15: modern GPS never proves a 1963 impact."""
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path
import unittest

from tools.cgeo15_matriz_camera import CATALOGUE, evaluate, validate, verify_bytes


class MatrizCameraTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = validate(json.loads(CATALOGUE.read_text(encoding="utf-8")))

    def test_modern_coordinates_are_points_of_view_only(self):
        out = evaluate(self.data)
        self.assertEqual(len(out["modern_viewpoint_coordinates_only"]), 2)
        self.assertIsNone(out["coordinate_reference_system"])
        self.assertIsNone(out["historical_center_geometry"])
        self.assertIsNone(out["1963_observed_event_location"])
        self.assertFalse(out["can_constrain_orbital_reentry"])

    def test_photographic_hashes_and_license(self):
        self.assertEqual(len({v["sha256"] for v in self.data["captured_images"]}), 2)
        self.assertEqual({v["license"] for v in self.data["captured_images"]}, {"CC BY-SA 4.0"})
        self.assertEqual({v["photographer"] for v in self.data["captured_images"]}, {"Túllio F"})

    def test_no_historical_photo_verified_in_1958_volume(self):
        archive = self.data["archived_candidate"]
        self.assertEqual(archive["publication_year"], 1958)
        self.assertEqual(archive["pages_visually_inspected"], 0)
        self.assertFalse(archive["conde_photographs_verified"])

    def test_fails_if_gps_promoted_to_event_or_center(self):
        for section, key, value in (
            ("place_context", "municipal_center_1963_point", [-37.621, -11.798]),
            ("place_context", "reported_object_location_1963", [-37.621, -11.798]),
            ("castor_contract", "event_buffer_m", 100),
            ("castor_contract", "orbital_constraint_activated", True),
        ):
            with self.subTest(section=section, key=key):
                altered = copy.deepcopy(self.data)
                altered[section][key] = value
                with self.assertRaises(ValueError):
                    validate(altered)

    def test_fails_if_gps_precision_invented(self):
        for key, value in (("epsg", 4326), ("gps_horizontal_error_m", 2), ("datum", "WGS84"), ("srs_usable_for_1963", True)):
            altered = copy.deepcopy(self.data)
            altered["captured_images"][0]["camera_point_from_commons"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(altered)

    def test_fails_if_photo_custody_broken(self):
        altered = copy.deepcopy(self.data)
        altered["captured_images"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            validate(altered)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                verify_bytes(self.data, Path(tmp))

    def test_fails_if_independence_rewritten(self):
        altered = copy.deepcopy(self.data)
        altered["dependency_graph"]["modern_photographic_sessions_confirmed"] = 2
        with self.assertRaises(ValueError):
            validate(altered)
        altered = copy.deepcopy(self.data)
        altered["dependency_graph"]["links"].pop()
        with self.assertRaises(ValueError):
            validate(altered)

    def test_fails_if_uninspected_volume_promoted(self):
        altered = copy.deepcopy(self.data)
        altered["archived_candidate"]["conde_photographs_verified"] = True
        with self.assertRaises(ValueError):
            validate(altered)


if __name__ == "__main__":
    unittest.main()
