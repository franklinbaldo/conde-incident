"""Adversarial tests: printed NASA cross-fields never become observations."""
import copy
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/ssr_crossfield_screen_g37.py"
SPEC = importlib.util.spec_from_file_location("ssr_crossfield_screen_g37", TOOL)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)
LEDGER = json.loads(MOD.SOURCE.read_text())


class TestG37(unittest.TestCase):
    def test_documentary_custody_seven_rows(self):
        out = MOD.build(LEDGER)
        self.assertEqual(len(out["cells"]), 7)
        self.assertEqual(len({x["id"] for x in out["cells"]}), 7)
        self.assertEqual(out["scientific_interpretation"]["recorded_original_instrument_observations"], 0)
        self.assertFalse(out["scientific_interpretation"]["active_domain_reduction"])
        self.assertEqual(out["scientific_interpretation"]["historical_holdout"], "NOT_RUN")

    def test_december_large_noncoepoch_screen(self):
        x = MOD.build(LEDGER)["dec31_529_vs_527_printed_diagnostic"]
        self.assertAlmostEqual(x["529_printed_minus_model_seconds"], -120.7070185, places=3)
        self.assertAlmostEqual(x["527_printed_minus_model_seconds"], 4.592278, places=3)
        lo, hi = x["529_printing_only_interval_seconds"]
        self.assertLess(hi, -110)
        self.assertLess(lo, hi)
        self.assertTrue(x["529_large_offset_flag"])

    def test_printed_erratum_does_not_fix_cross_field_gap(self):
        before = MOD.build(LEDGER)
        changed = copy.deepcopy(LEDGER)
        changed["sources"][-1]["rows"][-1]["period_min"] = "89.6"
        with self.assertRaisesRegex(ValueError, "NASA Dec 31 page"):
            MOD.build(changed)
        self.assertEqual(before["dec31_529_vs_527_printed_diagnostic"]["facsimile_529_period_min"], 89.2)
        # Even if C227's old number were accepted, Kepler would still disagree.
        residual_old_sec = 60 * (89.6 - MOD.period_min(334))
        self.assertLess(residual_old_sec, -90)

    def test_source_sha_and_transcription_immutable(self):
        changed = copy.deepcopy(LEDGER)
        changed["sources"][2]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "hash"):
            MOD.build(changed)
        changed = copy.deepcopy(LEDGER)
        changed["sources"][2]["rows"][-1]["perigee_km"] = 330
        with self.assertRaisesRegex(ValueError, "NASA Dec 31"):
            MOD.build(changed)

    def test_duplicate_object_and_invalid_units_veto(self):
        changed = copy.deepcopy(LEDGER)
        changed["sources"][0]["rows"].append(changed["sources"][0]["rows"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MOD.build(changed)
        changed = copy.deepcopy(LEDGER)
        changed["sources"][0]["rows"][0]["period_min"] = 94.6
        with self.assertRaisesRegex(ValueError, "precision"):
            MOD.build(changed)

    def test_rounding_not_instrumental_sigma(self):
        out = MOD.build(LEDGER)
        for row in out["cells"]:
            self.assertIsNone(row["sensor_epoch_utc"])
            self.assertIsNone(row["instrumental_sigma"])
            self.assertFalse(row["calibrated_orbit_constraint"])
            self.assertLess(row["printing_only_bounds_seconds_NOT_sigma"][0],
                            row["printing_only_bounds_seconds_NOT_sigma"][1])

    def test_artifact_reproducible(self):
        rendered = MOD.render(LEDGER)
        self.assertEqual(json.loads(rendered), MOD.build(LEDGER))
        self.assertEqual(MOD.OUTPUT.read_text(), rendered)


if __name__ == "__main__":
    unittest.main()
