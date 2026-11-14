"""Adversarial checks for SAO P-17 selection vs instrumental orbital evidence."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_sao_p17_scientific_bridge import (LEDGER, LEDGER_SHA256,
    L43, L43_SHA256, OUT, build, render)


class P17BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / LEDGER).read_text())
        cls.parent = json.loads((ROOT / L43).read_text())

    def assert_mutant_rejected(self, mutate, parent=False):
        model = copy.deepcopy(self.manifest)
        old = copy.deepcopy(self.parent)
        mutate(old if parent else model)
        with self.assertRaises(ValueError):
            build(model, LEDGER_SHA256, old, L43_SHA256)

    def test_exact_replay_and_scoped_negative(self):
        blob = render()
        self.assertEqual(blob, OUT.read_bytes())
        item = json.loads(blob)
        self.assertEqual(item["source_occurrence"], "C241-L44")
        self.assertEqual(item["source"]["published"], "1968-05-14")
        self.assertEqual(item["source"]["observations_interval"], ["1963-10-01", "1963-12-31"])
        self.assertEqual(len(item["printed_catalogue_rows"]), 11)
        self.assertEqual(len(item["dependency_graph"]), 21)
        self.assertEqual(len(item["simulator_latent_parameters"]), 3)
        self.assertEqual(item["negative_finding_scope"],
                         "527_528_529_NOT_IN_THIS_SELECTED_P17_PRINTED_CATALOGUE")
        self.assertFalse(item["activation"])
        self.assertEqual(item["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertEqual(item["independent_instrumental_observations_added"], 0)
        self.assertTrue(all(p["activation"] is False and
                            p["global_sao_nonobservation_proved"] is False and
                            all(value is None for value in p["observables"].values())
                            for p in item["simulator_latent_parameters"]))
        self.assertEqual([p["object_id"] for p in item["simulator_latent_parameters"]],
                         [527, 528, 529])
        self.assertFalse(item["methodology_applies_only_to_listed_observations"]
                         ["transfer_precision_to_527_528_529"])

    def test_pinned_input_bytes(self):
        self.assertEqual(hashlib.sha256((ROOT / LEDGER).read_bytes()).hexdigest(), LEDGER_SHA256)
        self.assertEqual(hashlib.sha256((ROOT / L43).read_bytes()).hexdigest(), L43_SHA256)
        with self.assertRaises(ValueError):
            build(self.manifest, "0" * 64, self.parent, L43_SHA256)
        with self.assertRaises(ValueError):
            build(self.manifest, LEDGER_SHA256, self.parent, "0" * 64)
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            for relative in (LEDGER, L43):
                path = home / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / relative).read_bytes())
            self.assertEqual(render(home), render())
            (home / LEDGER).write_bytes((home / LEDGER).read_bytes() + b" ")
            with self.assertRaises(ValueError):
                render(home)

    def test_no_forged_designation_or_scope(self):
        self.assert_mutant_rejected(lambda m: m["included_designations"].append("1963-003B"))
        self.assert_mutant_rejected(lambda m: m["included_counts"].pop())
        self.assert_mutant_rejected(lambda m: m.update(inference="GLOBAL_NONOBSERVATION"))
        self.assert_mutant_rejected(lambda m: m["source"].update(published="1963-11-08"))
        self.assert_mutant_rejected(lambda m: m["source"].update(sha256="0" * 64))

    def test_no_target_instrumental_data_inferred(self):
        self.assert_mutant_rejected(lambda m: m.update(epoch_utc_for_527_528_529="1963-11-08T00:00:00Z"))
        self.assert_mutant_rejected(lambda m: m.update(orbital_covariance_for_527_528_529=[[1]]))
        self.assert_mutant_rejected(lambda m: m.update(independent_target_measurements_recovered=1))
        self.assert_mutant_rejected(lambda m: m.update(physical_constraints_activated=1))
        self.assert_mutant_rejected(lambda m: m.update(observed_targets_in_this_publication=["1963-003B"]))

    def test_clock_frame_and_context_sigma_must_not_be_reassigned(self):
        self.assert_mutant_rejected(lambda m: m.update(time_reference="UTC measured directly"))
        self.assert_mutant_rejected(lambda m: m.update(star_reference="TEME"))
        self.assert_mutant_rejected(lambda m: m["context_not_target_sigma"].update(
            clock_uncertainty_range_milliseconds=[0.5, 1]))
        self.assert_mutant_rejected(lambda m: m["observational_fields_documented_for_listed_objects"].pop())

    def test_parent_is_finding_aid_not_additional_sensor(self):
        self.assert_mutant_rejected(lambda m: m.update(activation=True), parent=True)
        self.assert_mutant_rejected(lambda m: m.update(independent_instrumental_observations_added=1), parent=True)
        self.assert_mutant_rejected(lambda m: m.update(source_occurrence="C241-L44"), parent=True)
        self.assert_mutant_rejected(lambda m: m["archive_files"].clear(), parent=True)

    def test_optimized_python_does_not_elide_gates(self):
        snippet = ("import json; from pathlib import Path; "
                   "from tools.export_sao_p17_scientific_bridge import build,LEDGER,L43,LEDGER_SHA256,L43_SHA256; "
                   "a=json.loads(Path(LEDGER).read_text()); b=json.loads(Path(L43).read_text()); "
                   "a['epoch_utc_for_527_528_529']='1963-11-08T00:00:00Z'; "
                   "build(a,LEDGER_SHA256,b,L43_SHA256)")
        result = subprocess.run([sys.executable, "-O", "-c", snippet], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)


if __name__ == "__main__":
    unittest.main()
