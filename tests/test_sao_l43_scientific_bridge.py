"""Mutant tests for SAO archival routes, without inventing instrumental data."""
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
from export_sao_l43_scientific_bridge import (LEDGER, LEDGER_SHA256, OUT, build,
                                               render)


class SaoArchiveBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / LEDGER).read_text(encoding="utf-8"))

    def mutation(self, edit):
        lock = copy.deepcopy(self.source)
        edit(lock)
        with self.assertRaises(ValueError):
            build(lock, LEDGER_SHA256)

    def test_output_is_current_and_unactivated(self):
        self.assertEqual(render(), OUT.read_bytes())
        item = json.loads(render())
        self.assertEqual(item["source_occurrence"], "C241-L43")
        self.assertEqual(len(item["archive_files"]), 4)
        self.assertEqual(len(item["dependency_graph"]), 12)
        self.assertEqual(len(item["simulator_latent_parameters"]), 3)
        self.assertEqual({p["object_id"] for p in item["simulator_latent_parameters"]},
                         {527, 528, 529})
        self.assertTrue(all(not p["activation"] and not p["match_verified"]
                            and all(v is None for v in p["fields"].values())
                            for p in item["simulator_latent_parameters"]))
        self.assertEqual(item["independent_instrumental_observations_added"], 0)
        self.assertEqual(item["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertFalse(item["activation"])

    def test_source_digest_and_complete_source_scope(self):
        self.assertEqual(hashlib.sha256((ROOT / LEDGER).read_bytes()).hexdigest(),
                         LEDGER_SHA256)
        with self.assertRaises(ValueError):
            build(self.source, "0" * 64)
        self.mutation(lambda x: x.update(source_sha256="0" * 64))
        self.mutation(lambda x: x.update(source_bytes=1))

    def test_archive_locator_invented_or_duplicate(self):
        self.mutation(lambda x: x["archive_entries"][0].update(box=999))
        self.mutation(lambda x: x["archive_entries"][0].update(id="unrelated"))
        self.mutation(lambda x: x["archive_entries"].append(
            copy.deepcopy(x["archive_entries"][0])))

    def test_false_instrumental_observation_rejected(self):
        self.mutation(lambda x: x.update(instrumental_observations_recovered=1))
        self.mutation(lambda x: x.update(original_records_inspected=True))
        self.mutation(lambda x: x.update(instrument_epoch_utc="1963-11-08T12:00:00Z"))
        self.mutation(lambda x: x.update(instrument_uncertainty=0.0))
        self.mutation(lambda x: x.update(sensor_or_station="SAO invented station"))

    def test_object_crosswalk_and_status_rejected(self):
        self.mutation(lambda x: x.update(possible_objects=[528]))
        self.mutation(lambda x: x.update(object_match_verified=True))
        self.mutation(lambda x: x.update(domain_restrictions_activated=1))
        self.mutation(lambda x: x.update(conde_reentry_location="Conde"))

    def test_no_fabricated_finding_aid(self):
        self.mutation(lambda x: x.update(source_url="https://example.invalid/other"))
        self.mutation(lambda x: x.update(
            source_type="ORIGINAL_1963_OPTICAL_OBSERVATION"))

    def test_replay_ledger_bytes_not_just_json_structure(self):
        with TemporaryDirectory() as temporary:
            home = Path(temporary)
            src = home / LEDGER
            src.parent.mkdir(parents=True)
            src.write_bytes((ROOT / LEDGER).read_bytes())
            self.assertEqual(render(home), render())
            src.write_bytes(src.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                render(home)

    def test_python_optimized_does_not_skip_guards(self):
        code = ("from tools.export_sao_l43_scientific_bridge import "
                "LEDGER_SHA256,build; import json; "
                "from pathlib import Path; "
                f"d=json.loads(Path({LEDGER!r}).read_text());"
                "d['domain_restrictions_activated']=1;"
                "build(d,LEDGER_SHA256)")
        run = subprocess.run([sys.executable, "-O", "-c", code],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("ValueError", run.stderr)


if __name__ == "__main__":
    unittest.main()
