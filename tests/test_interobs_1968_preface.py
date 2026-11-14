"""Adversarial tests ensure that a 1968 preface cannot become 1963 orbit data."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "tools/verify_interobs_1968_preface.py"
SPEC = importlib.util.spec_from_file_location("interobs_preface", VERIFY)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InterobsPrefaceCustodyTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(MODULE.MANIFEST.read_text(encoding="utf-8"))

    def reject(self, path, value):
        example = copy.deepcopy(self.data)
        node = example
        for item in path[:-1]:
            node = node[item]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            MODULE.validate(example)

    def test_manifest_positive(self):
        self.assertTrue(MODULE.validate(self.data))

    def test_reject_source_tampering(self):
        self.reject(["source", "sha256"], "0" * 64)
        self.reject(["source", "bytes"], 0)
        self.reject(["source", "pdf_page_count"], 60)
        self.reject(["source", "complete_volume_retrieved"], True)

    def test_reject_faked_dates(self):
        self.reject(["source", "document_date"], "1963-11-08")
        self.reject(["source", "covered_observation_year"], 1963)
        self.reject(["source", "preface_printed_page"], 2)

    def test_reject_fake_campaign_coverage(self):
        self.reject(["preface", "november_1963_campaign_confirmed"], True)
        self.reject(["preface", "earlier_folge_1_2_volumes_retrieved"], True)
        self.reject(["preface", "actual_list_1_or_list_2_retrieved"], True)

    def test_reject_false_objects_and_successor(self):
        self.reject(["preface", "satellite_ids_proven_equivalent_to_527_528_529"], True)
        self.reject(["preface", "successor_volume_retrieved"], True)
        self.reject(["preface", "satellite_ids_in_issue_7"], ["527", "528", "529"])

    def test_reject_fake_observations(self):
        self.reject(["limits", "target_observations_identified"], True)
        self.reject(["limits", "raw_instrumental_observations_retrieved"], True)
        self.reject(["limits", "new_target_orbital_measurements"], 1)
        self.reject(["limits", "orbital_constraints_activated"], 1)
        self.reject(["limits", "outreach_sent"], True)

    def test_pdf_replay_rejects_fabrication(self):
        with self.assertRaises(ValueError):
            MODULE.validate(self.data, b"%PDF-1.5\n%%EOF")

    def test_checks_remain_active_under_python_O(self):
        bad = copy.deepcopy(self.data)
        bad["limits"]["orbital_constraints_activated"] = 1
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "tampered.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            program = "import importlib.util,json,sys; s=importlib.util.spec_from_file_location('m',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.validate(json.load(open(sys.argv[2])))"
            result = subprocess.run([sys.executable, "-O", "-c", program, str(VERIFY), str(path)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("false orbital constraint", result.stderr)


if __name__ == "__main__":
    unittest.main()
