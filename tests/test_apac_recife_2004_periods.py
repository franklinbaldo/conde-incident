"""Adversarial checks: no 1963 sounding from a surface catalogue."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "apac_audit", ROOT / "tools/audit_apac_recife_2004_periods.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class APACCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = audit.SOURCE.read_bytes()
        cls.data = json.loads(audit.OUTPUT.read_text())

    def test_reproducible_transcription(self):
        self.assertTrue(audit.check(self.data, self.raw))

    def test_pressure_does_not_overlap_november_1963(self):
        rows = {r["variable"]: r for r in self.data["records"]}
        self.assertFalse(rows["surface_pressure"]["period_overlaps_1963_11"])
        self.assertTrue(rows["wind_speed"]["period_overlaps_1963_11"])
        self.assertTrue(rows["temperature_min"]["period_overlaps_1963_11"])
        self.assertTrue(rows["relative_humidity"]["period_overlaps_1963_11"])

    def test_no_day_specific_measurement_or_independent_sounding(self):
        for row in self.data["records"]:
            self.assertIsNone(row["observed_at_1963_11_08"])
            self.assertIsNone(row["verified_november_1963_monthly_value"])
        self.assertIsNone(self.data["uncertainty"]["independent_igra_observation"])
        self.assertFalse(self.data["admissible_domain_reduction"])

    def test_pressure_backdate_fails(self):
        broken = self.raw.replace(b"|hPa|8|1966|", b"|hPa|8|1963|")
        self.assertNotEqual(self.raw, broken)
        with self.assertRaises(ValueError):
            audit.build(broken)

    def test_fabricated_day_measurement_fails(self):
        broken = json.loads(json.dumps(self.data))
        broken["records"][0]["observed_at_1963_11_08"] = 21.6
        with self.assertRaises(ValueError):
            audit.check(broken, self.raw)

    def test_bad_transcription_and_incomplete_data_fail(self):
        with self.assertRaises(ValueError):
            audit.build(self.raw.replace(b"relative_humidity|", b"wind_speed|"))
        with self.assertRaises(ValueError):
            audit.check(self.data, self.raw + b"\n")

    def test_unverified_source_explicit(self):
        self.assertIsNone(self.data["source"]["pdf_sha256"])
        self.assertFalse(self.data["source"]["visual_pdf_verified"])


if __name__ == "__main__":
    unittest.main()
