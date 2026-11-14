"""Adversarial checks for translation custody and target-identification limits."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/verify_interobs_ftd_translation.py"
SPEC = importlib.util.spec_from_file_location("audit_ftd", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)

class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(AUDIT.MANIFEST.read_text(encoding="utf-8"))
    def broken(self, *keys, value):
        x = copy.deepcopy(self.d)
        obj = x
        for k in keys[:-1]:
            obj = obj[k]
        obj[keys[-1]] = value
        with self.assertRaises(ValueError):
            AUDIT.validate(x)
    def test_manifest(self):
        self.assertTrue(AUDIT.validate(self.d))
    def test_no_invented_local_bytes(self):
        self.broken("access","full_pdf_bytes",value=123456)
        self.broken("access","full_pdf_sha256",value="a"*64)
        self.broken("access","local_pdf_download_success",value=True)
        self.broken("access","downloaded_pdf_replay",value="PASS")
    def test_no_invented_original(self):
        self.broken("document","original_copy_retrieved",value=True)
        self.broken("access","original_russian_facsimile_retrieved",value=True)
    def test_no_target_claim(self):
        self.broken("scope","target_observations_identified",value=True)
        self.broken("scope","target_specific_1963_11_07_to_09_campaign_confirmed",value=True)
        self.broken("scope","independent_target_sensor_claimed",value=True)
    def test_not_exact_counts_or_timestamps(self):
        self.broken("report","positions_are_approximate",value=False)
        self.broken("report","first_detailed_observation_month",value="November")
    def test_no_orbit_promotion(self):
        self.broken("scope","orbital_constraints_activated",value=1)
        self.broken("scope","new_instrumental_target_measurements",value=1)
    def test_wrong_source_dates_rejected(self):
        self.broken("document","translation_date",value="1969-04-09")
        self.broken("document","original_year",value=1963)
    def test_python_optimized_does_not_skip_guards(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            x = copy.deepcopy(self.d)
            x["scope"]["orbital_constraints_activated"] = 1
            p.write_text(json.dumps(x),encoding="utf-8")
            run = subprocess.run([sys.executable,"-O",str(SCRIPT),"--manifest",str(p)],
                                 capture_output=True,text=True)
            self.assertNotEqual(run.returncode,0)
            self.assertIn("false orbital constraint",run.stderr)

if __name__ == "__main__":
    unittest.main()
