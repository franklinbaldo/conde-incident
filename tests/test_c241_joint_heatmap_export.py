"""G54: real CLI adversarial checks with optimized and ordinary Python.

Fixtures here are deliberately synthetic zero-probability rows, not an orbital
observation or historical posterior. The exporter must fail closed in both modes.
"""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/export_c241_joint_heatmap.py"
LABELS = ("baseline", "orbital_middle", "temporal_12h", "joint_middle_12h")


class HeatmapExportGuards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.summary = root / "summary.json"
        self.cells = root / "cells.csv"
        self.output = root / "site.json"
        self.model = {
            "schema": "conde.c241-joint-orbital-day-scenario-heatmap/v1",
            "id": "SYNTHETIC_G54_TEST_ONLY",
            "sample": {"n": 1500000, "seed": 19631108},
            "historical_Conde_impact_posterior": None,
            "results": {key: {"probability_within_2000km": 0.0} for key in LABELS},
        }
        self.write_sources()

    def write_sources(self, *, rows=400, value="0"):
        self.summary.write_text(json.dumps(self.model), encoding="utf-8")
        with self.cells.open("w", encoding="utf-8", newline="") as fd:
            writer = csv.DictWriter(fd, fieldnames=[k + "_global_probability" for k in LABELS])
            writer.writeheader()
            for _ in range(rows):
                writer.writerow({k + "_global_probability": value for k in LABELS})

    def run_export(self, optimized=False, check=False):
        return subprocess.run(
            [sys.executable, *(["-O"] if optimized else []), str(SCRIPT),
             "--summary", str(self.summary), "--cells", str(self.cells),
             "--output", str(self.output), *(["--check"] if check else [])],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )

    def test_control_works_in_both_interpreters(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.assertEqual(self.run_export(optimized).returncode, 0)
                self.assertEqual(self.run_export(optimized, check=True).returncode, 0)

    def test_false_historical_posterior_is_rejected_even_with_optimized_python(self):
        self.model["historical_Conde_impact_posterior"] = {"claimed_impact": True}
        self.write_sources()
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.assertNotEqual(self.run_export(optimized).returncode, 0)

    def test_negative_cell_is_rejected_even_with_optimized_python(self):
        self.write_sources(value="-0.25")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.assertNotEqual(self.run_export(optimized).returncode, 0)

    def test_short_cell_grid_is_rejected_even_with_optimized_python(self):
        self.write_sources(rows=399)
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.assertNotEqual(self.run_export(optimized).returncode, 0)

    def test_tampered_site_bytes_do_not_pass_check_in_optimized_python(self):
        self.assertEqual(self.run_export().returncode, 0)
        self.output.write_text("{\"tampered\":true}\n", encoding="utf-8")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.assertNotEqual(self.run_export(optimized, check=True).returncode, 0)

    def test_missing_site_file_does_not_pass_check_in_optimized_python(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.assertNotEqual(self.run_export(optimized, check=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
