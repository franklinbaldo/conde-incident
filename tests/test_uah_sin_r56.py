"""Adversarial replay of secondary Soviet instrument text, both -O and normal."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tools.audit_uah_sin_r56 import ROOT, SOURCE, audit, replay


class TestR56(unittest.TestCase):
    def setUp(self):
        self.source = json.loads(SOURCE.read_text(encoding="utf-8"))

    def altered(self, path, value):
        d = copy.deepcopy(self.source)
        target = d
        for k in path[:-1]:
            target = target[k]
        target[path[-1]] = value
        with self.assertRaises(ValueError):
            audit(d)

    def test_valid(self): self.assertTrue(audit(self.source))
    def test_pdf_hash(self): self.altered(["source", "sha256"], "0" * 64)
    def test_pdf_bytes(self): self.altered(["source", "downloaded_bytes"], 100)
    def test_http_403(self): self.altered(["source", "http_status"], 403)
    def test_page_count(self): self.altered(["source", "pages"], 27)
    def test_page_inspection(self): self.altered(["source", "visually_inspected_pdf_pages_one_based"], [1])
    def test_original_paper_false(self): self.altered(["instrument_digest", "original_russian_paper_retrieved"], True)
    def test_secondary_report_false(self): self.altered(["instrument_digest", "us_intelligence_report_retrieved"], True)
    def test_not_observation(self): self.altered(["instrument_digest", "observation_record_in_digest"], True)
    def test_shutter_units(self): self.altered(["instrument_digest", "shutter_open_delay_seconds"], 2.2)
    def test_voltage(self): self.altered(["instrument_digest", "chronograph_delay_seconds_at_210_v"], 0.0254)
    def test_intermediate_report(self): self.altered(["instrument_digest", "secondary_us_report_number"], "0000")
    def test_context_not_sensor(self): self.altered(["context", "context_is_independent_satellite_measurement"], True)
    def test_no_target_rows(self): self.altered(["conclusions", "observations_norad_527_528_529"], [{"norad": 528}])
    def test_no_target_epochs(self): self.altered(["conclusions", "instrument_epochs_1963_11_07_to_09"], ["1963-11-08T00:00:00Z"])
    def test_no_transfer(self): self.altered(["conclusions", "instrument_delays_transferable_to_527_528_529"], True)
    def test_no_constraints(self): self.altered(["conclusions", "activated_orbital_constraints"], 1)
    def test_no_contacts(self): self.altered(["conclusions", "institutional_contacts_sent"], 1)
    def test_code_is_not_pdf(self): self.assertFalse(replay(Path(__file__)))


class TestMandatoryRealBytes(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, "-m", "tools.audit_uah_sin_r56", *args],
                              cwd=ROOT, capture_output=True, text=True, timeout=15, check=False)

    def test_manifest_only_does_not_pass(self):
        r = self.cli()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--pdf", r.stderr)

    def test_fake_pdf_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "mock.pdf"
            p.write_bytes(b"%PDF-1.7\n%%EOF\n")
            r = self.cli("--pdf", str(p))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("PDF bytes mismatch", r.stderr)
