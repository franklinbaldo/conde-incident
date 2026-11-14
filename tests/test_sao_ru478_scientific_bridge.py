"""Adversarial tests for archival holdings -> latent, not observed, orbital parameters."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_sao_ru478_scientific_bridge import (
    MANIFEST, CROSSWALK, P17, PINNED, OUT, build, render,
)


class Ru478BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / MANIFEST).read_text())
        cls.crosswalk = json.loads((ROOT / CROSSWALK).read_text())
        cls.parent = json.loads((ROOT / P17).read_text())

    def mutate(self, change, target="source"):
        source = copy.deepcopy(self.source)
        crosswalk = copy.deepcopy(self.crosswalk)
        parent = copy.deepcopy(self.parent)
        change({"source": source, "crosswalk": crosswalk, "parent": parent}[target])
        with self.assertRaises(ValueError):
            build(source, crosswalk, parent)

    def test_exact_export_and_search_routes(self):
        self.assertEqual(render(), OUT.read_bytes())
        obj = json.loads(render())
        self.assertEqual(obj["source_occurrence"], "C241-L45")
        self.assertEqual(len(obj["archive_routes"]), 4)
        self.assertEqual(len(obj["simulator_latent_parameters"]), 12)
        self.assertEqual(len(obj["upstream_variable_dependencies"]), 6)
        self.assertEqual([v["norad_id"] for v in obj["object_search_candidates"]],
                         [527, 528, 529])
        self.assertEqual(len(obj["dependency_graph"]), 12)
        self.assertEqual(obj["not_covered_by_new_pdf_locators"], ["MOR-RU478-04"])
        self.assertFalse(obj["global_nonobservation_proved"])
        self.assertFalse(obj["activation"])
        self.assertEqual(obj["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertEqual(obj["independent_instrumental_observations_added"], 0)
        for v in obj["object_search_candidates"]:
            self.assertFalse(v["activation"])
            self.assertTrue(all(v[k] is None for k in (
                "target_observation_id", "epoch_utc", "station",
                "ra_dec_radians", "reference_frame", "angle_sigma_radians",
                "clock_correction_seconds")))
        self.assertTrue(all(not edge["independent_observation"]
                            for edge in obj["dependency_graph"]))

    def test_hash_scope_and_byte_replay(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for path in PINNED:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / path).read_bytes())
            self.assertEqual(render(root), render())
            (root / CROSSWALK).write_bytes((root / CROSSWALK).read_bytes() + b" ")
            with self.assertRaises(ValueError):
                render(root)

    def test_no_invented_observation_or_target(self):
        self.mutate(lambda m: m.update(individual_observation_utc="1963-11-08T12:00Z"))
        self.mutate(lambda m: m.update(station_for_target_528="9008"))
        self.mutate(lambda m: m.update(physical_constraints_activated=1))
        self.mutate(lambda m: m.update(object_ids_not_printed_in_these_anchors=[527, 529]))
        self.mutate(lambda m: m["anchors"][3].update(box=59))

    def test_crosswalk_cannot_promote_metadata(self):
        self.mutate(lambda m: m["edges"][-1].update(hard_physical_constraint=True),
                    "crosswalk")
        self.mutate(lambda m: m["variables"][5].update(value=True), "crosswalk")
        self.mutate(lambda m: m["hypotheses"][0].update(status="PROVED"), "crosswalk")
        self.mutate(lambda m: m["sources"][0].update(source_sha256="f" * 64),
                    "crosswalk")
        self.mutate(lambda m: m["occurrences"][0].update(original_instrument_measurement=True),
                    "crosswalk")

    def test_parent_does_not_supply_tracking_data(self):
        self.mutate(lambda m: m.update(activation=True), "parent")
        self.mutate(lambda m: m.update(source_occurrence="C241-L45"), "parent")
        self.mutate(lambda m: m.update(independent_instrumental_observations_added=1),
                    "parent")

    def test_optimized_interpreter_rejects_false_source(self):
        snippet = (
            "import json; from pathlib import Path; "
            "from tools.export_sao_ru478_scientific_bridge import build,MANIFEST,CROSSWALK,P17; "
            "a=json.loads(Path(MANIFEST).read_text()); "
            "b=json.loads(Path(CROSSWALK).read_text()); "
            "c=json.loads(Path(P17).read_text()); "
            "a['physical_constraints_activated']=1; build(a,b,c)"
        )
        result = subprocess.run([sys.executable, "-O", "-c", snippet],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)


if __name__ == "__main__":
    unittest.main()
