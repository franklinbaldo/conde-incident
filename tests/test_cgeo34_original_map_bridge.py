"""Adversarial contracts for CGEO-34 map surrogate and inactive geographic links."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_cgeo34_original_map_bridge import SOURCE, PARENT, GRAPH, OUT, build, render


class OriginalMapBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / SOURCE).read_text())
        cls.parent = json.loads((ROOT / PARENT).read_text())
        cls.graph = json.loads((ROOT / GRAPH).read_text())
        cls.header = bytes.fromhex((ROOT / cls.source["asset"]["header_fixture"]).read_text())

    def mutate(self, index, fn):
        docs = [copy.deepcopy(self.source), copy.deepcopy(self.parent), copy.deepcopy(self.graph)]
        fn(docs[index])
        with self.assertRaises(ValueError):
            build(*docs, {}, self.header)

    def test_real_parent_and_frozen_output(self):
        self.assertEqual(OUT.read_bytes(), render())
        d = json.loads(render())
        self.assertEqual(len(d["dependency_graph"]), 9)
        self.assertEqual(d["source"]["jp2_bytes"], 110453331)
        self.assertEqual(d["documentary_context"]["independent_physical_witnesses_added"], 0)
        self.assertEqual([p["name"] for p in d["simulator_latent_parameters"]],
                         ["historical_map_pixel_to_geodetic_transform",
                          "conde_municipal_boundary_1963",
                          "reported_city_center_1963_geometry",
                          "reported_event_position_1963"])
        self.assertFalse(d["activation"])
        self.assertEqual(d["physical_domain_effect"], "THETA_UNCHANGED")
        for param in d["simulator_latent_parameters"]:
            self.assertIsNone(param["value"])
            self.assertIsNone(param["uncertainty"])
            self.assertFalse(param["activation"])

    def test_false_original_independence(self):
        self.mutate(0, lambda d: d.update(same_physical_map_as_parent=False))

    def test_fake_position_and_precision(self):
        self.mutate(0, lambda d: d["scientific_limits"].update(
            observed_reentry_location=[-37, -11], horizontal_error_m=1))

    def test_false_map_date(self):
        self.mutate(0, lambda d: d["map_historical_readings"].update(catalog_year=1963))

    def test_2017_processing_not_survey(self):
        self.mutate(0, lambda d: d["asset"]["embedded_xml"].update(
            change_history_meaning="SURVEY_CAPTURE_DATE"))

    def test_false_raster_inspection(self):
        self.mutate(0, lambda d: d["asset"].update(full_image_visual_inspection_performed=True))

    def test_full_jp2_hash_not_editable(self):
        self.mutate(0, lambda d: d["asset"].update(sha256="a" * 64))

    def test_parent_map_1963_boundary_is_missing(self):
        self.mutate(1, lambda d: d["epistemic_and_model_links"].update(
            historical_polygon_1963={"type": "Polygon"}))
        # The source validator covers custody; the cumulative parent is separately locked.
        # A fabricated polygon on an otherwise unchanged parent must fail too.

    def test_source_family_cannot_be_replaced(self):
        self.mutate(2, lambda d: d["candidate_links"][1].update(source_candidates=["OTHER"]))

    def test_parent_citation_not_promoted(self):
        self.mutate(2, lambda d: d["edges"][4].update(kind="OBSERVED_FALL_LOCATION"))

    def test_parent_municipal_filter_cannot_activate(self):
        self.mutate(2, lambda d: d["candidate_links"][1].update(simulator_filter=[-37, -11]))

    def test_optimized_python_still_validates(self):
        result = subprocess.run([sys.executable, "-O", str(ROOT / "tools/export_cgeo34_original_map_bridge.py"),
                                 "--check-site"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
