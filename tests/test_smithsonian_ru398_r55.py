"""Adversarial custody checks, compatible with Python normal and -O."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tools.audit_smithsonian_ru398_r55 import ROOT,SOURCE,audit,replay

class TestR55(unittest.TestCase):
    def setUp(self): self.doc=json.loads(SOURCE.read_text(encoding="utf-8"))
    def invalid(self,path,value):
        v=copy.deepcopy(self.doc)
        o=v
        for key in path[:-1]:o=o[key]
        o[path[-1]]=value
        with self.assertRaises(ValueError):audit(v)

    def test_valid(self):self.assertTrue(audit(self.doc))
    def test_checksum(self):self.invalid(["source","sha256"],"0"*64)
    def test_size(self):self.invalid(["source","downloaded_bytes"],0)
    def test_http(self):self.invalid(["source","http_status"],403)
    def test_printed_page(self):self.invalid(["source","printed_page"],60)
    def test_pdf_page(self):self.invalid(["source","pdf_page_one_based"],62)
    def test_primary_folders_unread(self):self.invalid(["source","archival_folder_contents_retrieved"],True)
    def test_locators(self):self.invalid(["locators",0,"box"],64)
    def test_index_not_original(self):self.invalid(["locators",0,"material"],"original_issue")
    def test_index_contents_unread(self):self.invalid(["locators",0,"folder_item_read"],True)
    def test_soviet_source_not_sensor(self):self.invalid(["locators",1,"material"],"optical_observation")
    def test_soviet_folder_unread(self):self.invalid(["locators",1,"folder_item_read"],True)
    def test_original_not_retrieved(self):self.invalid(["conclusions","stl_vol3_no4_original_retrieved"],True)
    def test_index_not_confirmed(self):self.invalid(["conclusions","stl_vol3_no4_listed_within_index_confirmed"],True)
    def test_units_unread(self):self.invalid(["conclusions","stl_original_unit_legend_read"],True)
    def test_soviet_observation_not_confirmed(self):self.invalid(["conclusions","soviet_log_1963_primary_observations_confirmed"],True)
    def test_targets_not_observed(self):self.invalid(["conclusions","new_norad_527_528_529_measurements"],1)
    def test_sensor_none(self):self.invalid(["conclusions","new_independent_sensors"],1)
    def test_theta_unchanged(self):self.invalid(["conclusions","activated_orbital_constraints"],1)
    def test_no_contact(self):self.invalid(["conclusions","institutional_contacts_sent"],1)
    def test_python_not_pdf(self):self.assertFalse(replay(Path(__file__)))


class TestR55CliMandatoryBytes(unittest.TestCase):
    """No CI success from a manifest-only run or an altered lookalike PDF."""

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "tools.audit_smithsonian_ru398_r55", *args],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=False,
        )

    def test_manifest_only_invocation_fails(self):
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--pdf", result.stderr)
        self.assertNotIn("R55 OK", result.stdout)

    def test_lookalike_pdf_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / "finding-aid.pdf"
            fake.write_bytes(b"%PDF-1.7\n%%EOF\n")
            result = self.cli("--pdf", str(fake))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PDF mismatch", result.stderr)
        self.assertNotIn("R55 OK", result.stdout)
