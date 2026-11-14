"""Independent negative checks for a dated, fully replayable satellite-observation source."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "tools/verify_baja_miskolc_1965_yearbook.py"
SPEC = importlib.util.spec_from_file_location("lontra_r42", VERIFY)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BajaMiskolcSourceTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(MODULE.MANIFEST.read_text(encoding="utf-8"))

    def reject(self, path, value):
        bad = copy.deepcopy(self.data)
        obj = bad
        for step in path[:-1]:
            obj = obj[step]
        obj[path[-1]] = value
        with self.assertRaises(ValueError):
            MODULE.validate(bad)

    def test_valid_manifest(self):
        self.assertTrue(MODULE.validate(self.data))

    def test_hash_pages_and_chronology(self):
        self.reject(["source", "sha256"], "0" * 64)
        self.reject(["source", "pdf_pages"], 205)
        self.reject(["source", "publication_year"], 1965)
        self.reject(["source", "pages"], [])

    def test_visual_vs_camera(self):
        self.reject(["baja", "nafa_scientific_program_in_report_period"], True)
        self.reject(["baja", "observations_predominantly_visual"], False)
        self.reject(["baja", "nafa_scientific_program_blocker"], "unknown")

    def test_chronograph_not_astrometric_precision(self):
        self.reject(["baja", "readout_accuracy_not_per_position_astrometric_error"], False)
        self.reject(["limits", "position_uncertainty_inferred_from_chronograph"], True)

    def test_aggregate_not_target_observation(self):
        self.reject(["miskolc", "aggregate_positional_measurements"], 2180)
        self.reject(["miskolc", "american_satellite_target_identity_confirmed"], True)
        self.reject(["miskolc", "observations_on_1963_11_07_to_09"], True)
        self.reject(["baja", "specific_527_528_529_observation"], True)

    def test_no_fake_constraints(self):
        self.reject(["limits", "target_observations_identified"], True)
        self.reject(["limits", "orbital_constraints_activated"], 1)
        self.reject(["limits", "new_target_orbital_measurements"], 1)
        self.reject(["limits", "outreach_sent"], True)

    def test_reject_truncated_pdf(self):
        with self.assertRaises(ValueError):
            MODULE.validate(self.data, b"%PDF-1.5\n%%EOF")

    def test_optimized_python_keeps_rejections(self):
        with tempfile.TemporaryDirectory() as td:
            bad = copy.deepcopy(self.data)
            bad["limits"]["orbital_constraints_activated"] = 1
            path = Path(td) / "bad.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            script = "import importlib.util,json,sys; s=importlib.util.spec_from_file_location('v',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.validate(json.load(open(sys.argv[2])))"
            completed = subprocess.run([sys.executable, "-O", "-c", script, str(VERIFY), str(path)], capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("limits.orbital_constraints_activated", completed.stderr)


if __name__ == "__main__":
    unittest.main()
