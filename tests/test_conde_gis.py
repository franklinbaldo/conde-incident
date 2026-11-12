"""Native SIRGAS 2000 IBGE municipal footprint: regression and refusal tests."""
from __future__ import annotations

from pathlib import Path
import copy
import json
import math
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from conde_gis import (  # noqa: E402
    SOURCES, evaluate, extract_conde, read_snapshot, ring_position,
)

DATA = ROOT / "research/geo"


class CondeGISContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = read_snapshot(DATA / "conde_ibge_2022_sirgas2000.json")
        cls.b = read_snapshot(DATA / "conde_ibge_2025_sirgas2000.json")

    def test_original_ibge_attributes_and_distinct_2022_2025_snapshots(self):
        for year, o in [(2022, self.a), (2025, self.b)]:
            self.assertEqual(o["jurisdiction"]["municipality_code_ibge"], "2908606")
            self.assertEqual(o["source"]["edition"], year)
            self.assertEqual(o["coordinates"]["reference_system"], "SIRGAS 2000")
            self.assertEqual(o["coordinates"]["epsg"], 4674)
            self.assertEqual(o["coordinates"]["axis_order"], ["longitude", "latitude"])
            self.assertFalse(o["coordinates"]["transform_to_wgs84_performed"])
            self.assertIsNone(o["metadata"]["boundary_positional_accuracy_m"])
            self.assertEqual(o["metadata"]["valid_in_november_1963"], "NOT_ESTABLISHED")
            self.assertEqual(o["metadata"]["reported_area_km2"], 931.106)
            self.assertEqual(o["metadata"]["vertices_including_closure"], SOURCES[year]["vertices"])
            self.assertLess(o["metadata"]["bbox_lonlat"][2], -37.5)
            self.assertGreater(o["metadata"]["bbox_lonlat"][3], -11.7)
        self.assertEqual(self.a["metadata"]["vertices_including_closure"], 3303)
        self.assertEqual(self.b["metadata"]["vertices_including_closure"], 3260)
        self.assertNotEqual(self.a["source"]["archive_sha256"], self.b["source"]["archive_sha256"])

    def test_modern_geometry_has_real_spatial_selectivity(self):
        inside = evaluate(-37.61, -11.81, "1963-11-08", "EPSG:4674", 100, self.a, self.b)
        outside = evaluate(-40, -15, "1963-11-08", "EPSG:4674", 100, self.a, self.b)
        self.assertEqual(inside["modern_comparison"], "CONSISTENT_MODERN_INSIDE")
        self.assertEqual(outside["modern_comparison"], "CONSISTENT_MODERN_OUTSIDE")
        self.assertGreater(inside["source_edition_results"]["2022"]["approx_distance_to_polygon_edge_m"], 6000)
        self.assertEqual(inside["historical_1963_membership"], "UNRESOLVED_NO_1963_BOUNDARY")
        self.assertEqual(outside["historical_1963_membership"], "UNRESOLVED_NO_1963_BOUNDARY")
        self.assertFalse(inside["can_constrain_historical_orbital_reentry"])
        self.assertFalse(outside["can_constrain_historical_orbital_reentry"])

    def test_boundary_on_exact_source_vertex_is_not_forced_in_or_out(self):
        for snapshot in [self.a, self.b]:
            x, y = snapshot["geometry"]["coordinates"][0][0]
            r = ring_position(x, y, snapshot["geometry"]["coordinates"][0], 10)
            self.assertEqual(r["modern_polygon_membership"], "NEAR_BOUNDARY")
            self.assertLess(r["approx_distance_to_polygon_edge_m"], 0.01)

    def test_synthetic_polygon_orientation_and_distance(self):
        ring = [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]
        self.assertEqual(ring_position(.5, .5, ring)["modern_polygon_membership"], "INSIDE")
        self.assertEqual(ring_position(2, 2, ring)["modern_polygon_membership"], "OUTSIDE")
        self.assertEqual(ring_position(0, .5, ring, 1)["modern_polygon_membership"], "NEAR_BOUNDARY")
        self.assertEqual(ring_position(.5, .5, list(reversed(ring)))["modern_polygon_membership"], "INSIDE")

    def test_reject_frame_ambiguity_and_invalid_coordinates(self):
        for frame in ("EPSG:4326", "WGS84", "ECI", ""):
            with self.assertRaisesRegex(ValueError, "CRS"):
                evaluate(-37.61, -11.81, "1963-11-08", frame, 0, self.a, self.b)
        for lon, lat, margin in [(math.nan, -12, 0), (-37, math.inf, 0),
                                 (-180.1, 1, 0), (0, 90.1, 0), (0, 0, -1)]:
            with self.assertRaises(ValueError):
                evaluate(lon, lat, "1963-11-08", "EPSG:4674", margin, self.a, self.b)
        with self.assertRaisesRegex(ValueError, "date"):
            evaluate(-37, -12, "1963-11-99", "EPSG:4674", 0, self.a, self.b)

    def test_tamper_of_geometry_and_source_is_rejected(self):
        for year, orig in [(2022, self.a), (2025, self.b)]:
            tampered = copy.deepcopy(orig)
            tampered["geometry"]["coordinates"][0][42][0] += 0.0005
            p = DATA / f"conde_ibge_{year}_sirgas2000.json"
            try:
                temp = ROOT / "tools" / f".tmp_gis_{year}.json"
                temp.write_text(json.dumps(tampered))
                with self.assertRaisesRegex(ValueError, "pinned source"):
                    read_snapshot(temp)
            finally:
                temp.unlink(missing_ok=True)
            self.assertEqual(read_snapshot(p), orig)
        with self.assertRaisesRegex(ValueError, "ZIP SHA256"):
            extract_conde(b"fake source", 2022)

    def test_2025_versus_2022_not_historical_boundary_evidence(self):
        r = evaluate(-37.61, -11.81, "1963-11-08", "EPSG:4674", 0, self.a, self.b)
        self.assertNotEqual(r["modern_comparison"], "DISCORDANT_MODERN_EDITIONS")
        self.assertFalse(r["can_constrain_historical_orbital_reentry"])
        self.assertIn("1963", r["missing"][0])


if __name__ == "__main__":
    unittest.main()
