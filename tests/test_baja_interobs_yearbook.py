"""Adversarial custody tests, including Python -O where assert statements disappear."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "tools/verify_baja_interobs_yearbook.py"
SPEC = importlib.util.spec_from_file_location("baja_yearbook", VERIFY)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class YearbookCustodyTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(MODULE.MANIFEST.read_text(encoding="utf-8"))

    def reject(self, path, value):
        case = copy.deepcopy(self.data)
        obj = case
        for k in path[:-1]:
            obj = obj[k]
        obj[path[-1]] = value
        with self.assertRaises(ValueError):
            MODULE.validate(case)

    def test_positive_manifest(self):
        self.assertTrue(MODULE.validate(self.data))

    def test_hash_and_page_identity(self):
        self.reject(["source", "sha256"], "0" * 64)
        self.reject(["source", "bytes"], 0)
        self.reject(["source", "page_zero_based"], 119)
        self.reject(["source", "publication_year"], 1966)

    def test_report_period_and_volumes(self):
        self.reject(["report", "reported_observation_years"], [1963])
        self.reject(["report", "cited_publication_volumes"], ["Folge I"])
        self.reject(["report", "states_dataset_from_1963_and_1964_prepared_and_published"], False)

    def test_no_november_claim(self):
        self.reject(["report", "campaign_coverage_1963_11_07_to_09"], True)
        self.reject(["limits", "november_1963_campaign_confirmed"], True)
        self.reject(["limits", "original_campaign_volume_pages_read"], True)

    def test_no_wrong_object_or_count(self):
        self.reject(["report", "listed_satellite_codes_proven_to_be_527_528_529"], True)
        self.reject(["report", "over_7000_measurements_attributable_to_1963"], True)
        self.reject(["limits", "target_observations_identified"], True)
        self.reject(["limits", "new_target_orbital_measurements"], 1)

    def test_no_fake_measurements_or_outreach(self):
        self.reject(["limits", "orbital_constraints_activated"], 1)
        self.reject(["limits", "outreach_sent"], True)
        self.reject(["limits", "raw_instrumental_observations_retrieved"], True)

    def test_reject_fake_pdf_bytes(self):
        with self.assertRaises(ValueError):
            MODULE.validate(self.data, b"%PDF-1.5\n%%EOF")

    def test_checks_survive_python_optimized_mode(self):
        with tempfile.TemporaryDirectory() as td:
            bad = copy.deepcopy(self.data)
            bad["limits"]["orbital_constraints_activated"] = 1
            target = Path(td) / "bad.json"
            target.write_text(json.dumps(bad), encoding="utf-8")
            script = "import importlib.util,json,sys; s=importlib.util.spec_from_file_location('b',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.validate(json.load(open(sys.argv[2])))"
            result = subprocess.run([sys.executable, "-O", "-c", script, str(VERIFY), str(target)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("false orbital constraint", result.stderr)


if __name__ == "__main__":
    unittest.main()
