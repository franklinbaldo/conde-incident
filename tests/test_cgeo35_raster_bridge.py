"""Adversarial checks for CGEO-35 pixel evidence and inactive scientific variables."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_cgeo35_raster_bridge import SOURCE, PARENT, PRIOR, OUT, build, render


class RasterBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real = [json.loads((ROOT / p).read_text()) for p in (SOURCE, PARENT, PRIOR)]
        cls.hashes = json.loads(render())["source_sha256"]

    def mutate(self, index, change):
        values = copy.deepcopy(self.real)
        change(values[index])
        with self.assertRaises(ValueError):
            build(*values, self.hashes)

    def test_frozen_export_and_linkage(self):
        self.assertEqual(OUT.read_bytes(), render())
        doc = json.loads(render())
        self.assertEqual((doc["source_occurrence"], doc["parent_occurrence"],
                          doc["matrix_context"]), ("CGEO-35", "CGEO-34", "C24#1"))
        self.assertEqual(doc["image_coordinate_datum"]["settlement_symbol_xy_pixels"],
                         [4465, 5413])
        self.assertEqual(len(doc["dependency_graph"]), 6)
        self.assertEqual(len(doc["simulator_latent_parameters"]), 3)
        self.assertTrue(all(p["value"] is None and not p["activation"]
                            for p in doc["simulator_latent_parameters"]))
        self.assertFalse(doc["activation"])
        self.assertEqual(doc["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertEqual(doc["independent_physical_witnesses_added"], 0)

    def test_different_pixel_anchor_rejected(self):
        self.mutate(0, lambda d: d["image_space_only"].update(
            conde_symbol_original_px_visual_estimate=[600, 100]))

    def test_roi_hash_substitution_rejected(self):
        self.mutate(0, lambda d: d["inspection"].update(rgb_pixel_sha256="0"*64))

    def test_independence_claim_rejected(self):
        self.mutate(0, lambda d: d["historical_context"].update(
            new_independent_historical_witness=True))

    def test_geocoding_without_controls_rejected(self):
        self.mutate(0, lambda d: d["scientific_limits"].update(
            map_pixel_to_world_transform=[1, 0, 0, 0, 1, 0]))

    def test_observed_location_fabrication_rejected(self):
        self.mutate(0, lambda d: d["scientific_limits"].update(
            observed_reentry_location=[-37.6, -11.8]))

    def test_parent_jp2_identity_rejected(self):
        self.mutate(1, lambda d: d["asset"].update(sha256="0"*64))

    def test_parent_activation_rejected(self):
        self.mutate(2, lambda d: d.update(activation=True))

    def test_parent_documentary_identity_rejected(self):
        self.mutate(2, lambda d: d["documentary_context"].update(
            snapshot_occurrence="C197#1"))

    def test_prior_export_digest_checked(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for p in (SOURCE, PARENT, PRIOR):
                f = root / p
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes((ROOT / p).read_bytes())
            path = root / PRIOR
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                render(root)


if __name__ == "__main__":
    unittest.main()
