"""CGEO-14 source integrity and adversarial epistemic controls."""
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path
import unittest

from tools.cgeo14_vila_visual import CATALOGUE, evaluate, validate, verify_files


class VilaVisualTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = validate(json.loads(CATALOGUE.read_text(encoding="utf-8")))

    def test_blog_publication_not_capture_epoch(self):
        self.assertEqual(self.data["source_page"]["published_at"][:10], "2014-03-13")
        self.assertTrue(all(r["capture_date"] is None for r in self.data["images"]))

    def test_three_distinct_files_one_publication_lineage(self):
        self.assertEqual(len({r["sha256"] for r in self.data["images"]}), 3)
        self.assertEqual(self.data["dependency_graph"]["independent_historical_captures_confirmed"], 0)

    def test_geographic_and_temporal_veto(self):
        result = evaluate(self.data)
        self.assertIsNone(result["historical_center_geometry"])
        self.assertFalse(result["center_of_city_1963_verified"])
        self.assertFalse(result["can_constrain_orbital_reentry"])
        self.assertIsNone(result["point_of_reentry"])

    def test_do_not_confuse_vila_seat_and_sitio(self):
        p = self.data["place_context"]
        self.assertIsNone(p["center_equals_Vila_do_Conde_in_1963"])
        self.assertIsNone(p["center_equals_Sitio_do_Conde_in_1963"])

    def test_no_rehosting_without_license(self):
        src = self.data["source_page"]
        self.assertIsNone(src["rights_or_reuse_license"])
        self.assertFalse(src["rehost_permitted"])

    def test_replay_requires_original_jpeg_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                verify_files(self.data, Path(d))
            (Path(d) / "vila-velha-001.jpg").write_bytes(b"not a source photograph")
            with self.assertRaisesRegex(ValueError, "byte/hash mismatch"):
                verify_files(self.data, Path(d))

    def test_fail_closed_on_false_date_datum_coordinates(self):
        mutations = (
            (0, "capture_date", "1963-11-08"),
            (0, "latitude", -11.8),
            (1, "datum", "EPSG:4674"),
            (2, "camera_pose", [1, 2, 3]),
            (1, "documented_1963_scene", True),
            (2, "sha256", "0" * 64),
        )
        for i, field, value in mutations:
            with self.subTest(field=field):
                bad = copy.deepcopy(self.data)
                bad["images"][i][field] = value
                with self.assertRaises(ValueError):
                    validate(bad)

    def test_fail_closed_on_false_center_or_independence(self):
        for target, field, value in (
            ("place_context", "historical_center_point", [-37.6, -11.8]),
            ("place_context", "center_equals_Vila_do_Conde_in_1963", True),
            ("dependency_graph", "independent_historical_captures_confirmed", 3),
            ("dependency_graph", "can_constrain_1963_reentry", True),
            ("source_page", "rehost_permitted", True),
        ):
            with self.subTest(field=field):
                bad = copy.deepcopy(self.data)
                bad[target][field] = value
                with self.assertRaises(ValueError):
                    validate(bad)

    def test_source_links_cannot_disappear(self):
        bad = copy.deepcopy(self.data)
        bad["dependency_graph"]["links"].pop()
        with self.assertRaisesRegex(ValueError, "dependency graph"):
            validate(bad)


if __name__ == "__main__":
    unittest.main()
