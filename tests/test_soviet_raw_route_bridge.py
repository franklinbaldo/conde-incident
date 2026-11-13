"""Adversarial checks of C241-L37 -> graph -> typed Lean/latent parameters."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_soviet_raw_route_bridge import ROUTE, PARENT, OUT, build, render


class SovietRawRouteBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / ROUTE).read_text())
        cls.parent = json.loads((ROOT / PARENT).read_text())

    def altered(self, index, change):
        docs = [copy.deepcopy(self.source), copy.deepcopy(self.parent)]
        change(docs[index])
        return build(*docs, {})

    def test_source_locked_and_three_separate_pending_search_paths(self):
        data = build(self.source, self.parent, {})
        self.assertEqual(len(data["source_dependency_graph"]), 11)
        self.assertEqual(data["new_retrieval_paths"], 3)
        self.assertEqual(data["existing_soviet_candidate_joins"], 6)
        self.assertEqual(data["new_independent_instrument_observations"], 0)
        self.assertEqual(data["new_numeric_orbital_constraints"], 0)
        self.assertFalse(data["activation"])
        self.assertEqual(data["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertEqual([x["norad"] for x in data["simulator_latent_parameters"]], [527, 528, 529])
        self.assertTrue(all(x["value"] is None and not x["activation"] for x in data["simulator_latent_parameters"]))
        self.assertIsNone(data["catalogue_leads"][0]["facsimile_sha256"])
        self.assertFalse(data["two_serials"]["identity_equivalent"])

    def test_mutant_same_serial_unproven(self):
        with self.assertRaises(ValueError):
            self.altered(0, lambda d: d["source_distinction"].update(same_serial_title_proven=True))

    def test_mutant_fabricated_target_observation(self):
        with self.assertRaises(ValueError):
            self.altered(0, lambda d: d["source_distinction"].update(raw_series_target_measurements_read=True))

    def test_mutant_catalogue_promotes_528(self):
        with self.assertRaises(ValueError):
            self.altered(0, lambda d: d["bibliographic_followups"][0].update(target_527_528_529_explicitly_named=True))

    def test_mutant_fabricated_facsimile_hash(self):
        with self.assertRaises(ValueError):
            self.altered(0, lambda d: d["bibliographic_followups"][0].update(source_bytes_sha256="f" * 64))

    def test_mutant_retroactive_instrument_data(self):
        with self.assertRaises(ValueError):
            self.altered(0, lambda d: d.update(independent_target_observations=1))

    def test_mutant_2007_pdf_digest(self):
        with self.assertRaises(ValueError):
            self.altered(0, lambda d: d["retrospective_author_source"].update(sha256="0" * 64))

    def test_mutant_old_bridge_sensor_activation(self):
        with self.assertRaises(ValueError):
            self.altered(1, lambda d: d["simulator_latent_parameters"][0].update(active=True))

    def test_mutant_loss_of_provenance_dependency(self):
        with self.assertRaises(ValueError):
            self.altered(0, lambda d: d["dependencies"].remove("C241-L34"))

    def test_export_byte_exact_and_lean_declared(self):
        data = render()
        self.assertEqual(data, OUT.read_bytes())
        self.assertEqual(hashlib.sha256((ROOT / ROUTE).read_bytes()).hexdigest(),
                         json.loads(data)["parent_sha256"][str(ROUTE)])
        lean = (ROOT / "formal/Conde1963/SovietCatalogueCandidate.lean").read_text()
        self.assertIn("def sovietRawSeriesRoutes", lean)
        self.assertIn("C241-L37", lean)
        self.assertIn("RNB-1000287767", lean)
        self.assertLess(len(data), 20_000)


if __name__ == "__main__":
    unittest.main()
