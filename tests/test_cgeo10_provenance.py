"""CGEO-10 provenance bridge: documentary connectivity, no physical activation."""
from __future__ import annotations
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_cgeo10_provenance as bridge


class CGEO10ProvenanceTests(unittest.TestCase):
    def test_full_source_to_simulator_chain_without_orphan(self):
        data = bridge.build()
        nodes = {node["id"] for node in data["nodes"]}
        self.assertEqual(len(nodes), len(data["nodes"]))
        self.assertTrue(all(edge["from"] in nodes and edge["to"] in nodes
                            for edge in data["edges"]))
        start = bridge.SOURCE_ID
        reach = {start}
        while True:
            next_reach = reach | {e["to"] for e in data["edges"] if e["from"] in reach}
            if next_reach == reach:
                break
            reach = next_reach
        self.assertIn("sim_param_legal_boundary_Conde_BA_1963", reach)
        self.assertEqual(data["connectivity_delta"]["new_documentary_bridge"], 1)
        self.assertEqual(data["connectivity_delta"]["active_orbital_constraints"], 0)

    def test_frozen_matrix_not_renumbered(self):
        d = bridge.build()
        self.assertTrue(d["matrix_identity"]["supplemental_not_in_frozen_C001_C238"])
        self.assertEqual(d["matrix_identity"]["frozen_matrix_occurrence_count_delta"], 0)
        self.assertEqual(d["matrix_identity"]["frozen_matrix_git_blob_sha1"],
                         "a7978c3a75a153b16ab70118a92c434bba674cb7")

    def test_two_project_records_share_one_ibge_work_not_two_sensors(self):
        d = bridge.build()
        self.assertEqual(d["source_independence"]["family"], bridge.FAMILY)
        self.assertIsNone(d["source_independence"]["independent_observation_count"])
        self.assertFalse(d["source_independence"]["stanford_mirror_independent"])
        self.assertFalse(d["source_independence"]["multiple_project_extractions_independent"])
        self.assertEqual(sum(n["kind"] == "primary_digital_cartographic_archive"
                             for n in d["nodes"]), 1)
        self.assertEqual(d["nodes"][0]["sha256"], bridge.ZIP_SHA)

    def test_unactivated_lean_and_simulation_no_fake_1963_boundary(self):
        d = bridge.build()
        c = d["constraint_candidate"]
        self.assertEqual(c["status"], "CONNECTED_PENDING_CALIBRATION")
        self.assertEqual(c["lean_status"], "NOT_PROMOTED")
        self.assertEqual(c["simulation_status"], "CANDIDATE_NOT_ACTIVATED")
        self.assertFalse(c["activation"])
        for key in ("boundary_value", "event_position", "horizontal_error_m",
                    "geodetic_epoch", "verified_reentry_point", "verified_reentry_time"):
            self.assertIsNone(c[key])
        self.assertEqual(len(c["required_bridges"]), 4)

    def test_src_is_projected_xy_not_unjustified_lat_lon(self):
        raw = json.loads((ROOT / bridge.NATIVE_PATH).read_text())
        self.assertEqual(raw["native_crs"]["linear_unit"], "metre")
        self.assertIsNone(raw["native_crs"]["epsg_projected"])
        self.assertNotIn("coordinates_lon_lat", bridge.serialize(bridge.build()))

    def test_manifest_sha_or_identity_tampering_rejected(self):
        for path, mutation in (
            (bridge.RETRO_PATH, lambda d: d["source"]["binary"].__setitem__(
                "source_zip_sha256", "0" * 64)),
            (bridge.RETRO_PATH, lambda d: d["source"]["binary"].__setitem__(
                "dbf_record_index_0based", 55)),
            (bridge.RETRO_PATH, lambda d: d["method_and_limits"].__setitem__(
                "orbital_constraint_activated", True)),
            (bridge.RETRO_PATH, lambda d: d["source"].__setitem__("publication_year", 1960)),
            (bridge.NATIVE_PATH, lambda d: d["native_crs"].__setitem__(
                "epsg_projected", "EPSG:4326")),
            (bridge.NATIVE_PATH, lambda d: d["historical_1963"].__setitem__(
                "can_constrain_reentry", True)),
            (bridge.NATIVE_PATH, lambda d: d["dependency_graph"].__setitem__("edges", [])),
            (bridge.LEGAL_PATH, lambda d: d["dependency_graph"].__setitem__(
                "boundary_1963", {"invented": True})),
        ):
            with self.subTest(path=path, mutation=mutation):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    for name in (bridge.RETRO_PATH, bridge.NATIVE_PATH, bridge.LEGAL_PATH):
                        dst = root / name
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(ROOT / name, dst)
                    f = root / path
                    j = json.loads(f.read_text())
                    mutation(j)
                    f.write_text(json.dumps(j))
                    with self.assertRaisesRegex(ValueError, "CGEO-10 provenance mismatch"):
                        bridge.build(root)

    def test_generated_site_feed_is_reproducible_and_size_bounded(self):
        expected = bridge.serialize(bridge.build())
        self.assertEqual((ROOT / "public/data/conde-cgeo10-provenance.json").read_text(),
                         expected)
        self.assertLessEqual(len(expected.encode()), 20_000)


if __name__ == "__main__":
    unittest.main()
