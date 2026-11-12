"""CGEO-10: native 1960 map is not a legal boundary for reentry in 1963."""
import copy
import json
from pathlib import Path
import unittest
from tempfile import TemporaryDirectory

from tools.conde_ibge_1960 import (
    CODE, NAME, RECORD_INDEX, RECORD_SHA, RING_SHA, SOURCE_URL, ZIP_SHA,
    evaluate, extract, load_contract,
)


class CondeIBGE1960Test(unittest.TestCase):
    def setUp(self):
        self.data = load_contract()

    def mutate(self, field, value):
        with TemporaryDirectory() as d:
            clone = copy.deepcopy(self.data)
            field(clone, value)
            p = Path(d) / "mutated.json"
            p.write_text(json.dumps(clone), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_contract(p)

    def test_archival_source_uses_direct_ibge_url_and_sha(self):
        s = self.data["source"]
        self.assertTrue(SOURCE_URL.startswith("https://geoftp.ibge.gov.br/"))
        self.assertEqual(s["archive_url"], SOURCE_URL)
        self.assertEqual(s["zip_sha256"], ZIP_SHA)
        self.assertEqual(s["shapefile_record_sha256"], RECORD_SHA)
        self.assertEqual(s["shapefile_record_index_zero_based"], RECORD_INDEX)
        self.assertEqual(s["dbf_identifier"], {"codigo": CODE, "nome": NAME})

    def test_retrospective_epoch_and_source_lineage(self):
        self.assertEqual(self.data["source"]["nominal_map_year"], 1960)
        self.assertIn("2013", self.data["source"]["lineage"])
        self.assertIn("2016", self.data["source"]["lineage"])

    def test_native_polygon_not_geographic_wgs84_geojson(self):
        p = self.data["native_geometry"]
        self.assertEqual(p["type"], "Polygon")
        self.assertEqual(p["vertex_count_with_closure"], 47)
        self.assertEqual(p["ring_xy_sha256"], RING_SHA)
        self.assertEqual(len(p["coordinates_xy_m"][0]), 47)
        self.assertEqual(p["coordinates_xy_m"][0][0], p["coordinates_xy_m"][0][-1])
        self.assertEqual(p["bbox_xy_m"], [1761251.25, -1390060.375, 1795968.5, -1336775.625])
        self.assertGreater(p["coordinates_xy_m"][0][0][0], 1_000_000)

    def test_projection_datum_and_unknown_epsg(self):
        crs = self.data["native_crs"]
        self.assertEqual(crs["projection"], "Polyconic")
        self.assertEqual(crs["datum"], "SIRGAS_2000")
        self.assertEqual(crs["ellipsoid"], "GRS_1980")
        self.assertEqual(crs["central_meridian_deg"], -54.0)
        self.assertEqual(crs["linear_unit"], "metre")
        self.assertIsNone(crs["epsg_projected"])

    def test_missing_1963_boundary_is_preserved(self):
        for day in ("1960-07-01", "1963-11-08", "2025-01-01"):
            result = evaluate(day, self.data)
            self.assertIsNone(result["legal_boundary_for_date"])
            self.assertIsNone(result["point_membership_for_date"])
            self.assertFalse(result["can_constrain_reentry"])

    def test_original_polygon_not_a_1963_event(self):
        h = self.data["historical_1963"]
        self.assertIsNone(h["legal_boundary_for_date"])
        self.assertIsNone(h["date_1963_membership"])
        self.assertIsNone(h["coordinate_transformation_to_event_frame"])
        self.assertIsNone(h["geodetic_epoch_and_horizontal_accuracy_m"])
        self.assertFalse(h["can_constrain_reentry"])

    def test_graph_retains_unresolved_temporal_bridge(self):
        edges = self.data["dependency_graph"]["edges"]
        self.assertEqual(len(edges), 3)
        self.assertIn("NOT_A_VALIDATED_TEMPORAL_BRIDGE", {e["kind"] for e in edges})
        self.assertIn("CGEO-09", self.data["dependency_graph"]["nodes"])

    def test_tamper_cannot_change_zip_sha(self):
        self.mutate(lambda d, v: d["source"].__setitem__("zip_sha256", v), "0" * 64)

    def test_tamper_cannot_change_polygon_without_replay(self):
        self.mutate(lambda d, v: d["native_geometry"]["coordinates_xy_m"][0][8].__setitem__(0, v), 1.0)

    def test_tamper_cannot_claim_1963_membership(self):
        self.mutate(lambda d, v: d["historical_1963"].__setitem__("can_constrain_reentry", v), True)

    def test_tamper_cannot_invent_epsg(self):
        self.mutate(lambda d, v: d["native_crs"].__setitem__("epsg_projected", v), "EPSG:4326")

    def test_tamper_cannot_remove_dependency(self):
        self.mutate(lambda d, v: d["dependency_graph"].__setitem__("edges", v), [])

    def test_missing_archive_is_explicit_replay_error(self):
        with self.assertRaises(FileNotFoundError):
            extract(Path("/nonexistent/ibge-1960.zip"))

    def test_arbitrary_archive_is_not_accepted(self):
        with TemporaryDirectory() as d:
            path = Path(d) / "fake.zip"
            path.write_bytes(b"not official shapefile")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                extract(path)


if __name__ == "__main__":
    unittest.main()
