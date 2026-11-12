"""Negative controls for source-pinned conditional dry finite-layer stability."""
import json
import math
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_igra_recife_dry_richardson as r
import audit_igra_recife_dry_density as density
import audit_igra_recife_window as original


class DryFiniteLayerRichardsonTests(unittest.TestCase):
    def test_reproduces_raw_originals_and_one_source_family(self):
        data = r.build()
        self.assertEqual(data, json.loads(r.OUTPUT.read_text()))
        self.assertEqual(data["source"]["source_independent_families"], 1)
        self.assertEqual([len(p["layers"]) for p in data["profiles"]], [14, 14, 14])
        self.assertEqual([p["recorded_wind_and_temperature_levels"] for p in data["profiles"]], [15, 15, 15])
        self.assertEqual([p["negative_dry_n2_layers"] for p in data["profiles"]], [1, 1, 1])
        for day, profile in zip(original.DAYS, data["profiles"]):
            self.assertEqual(profile["original_excerpt_sha256"], original.DAYS[day][0])
            self.assertIsNone(profile["actual_release_utc"])

    def test_dry_theta_and_richardson_dimensions(self):
        self.assertAlmostEqual(r.potential_temperature(26.85, 1000), 300, places=6)
        self.assertAlmostEqual(r.potential_temperature(26.85, 500),
                               300 * 2 ** (r.DRY_R / r.CP_DRY), places=6)
        for profile in r.build()["profiles"]:
            for layer in profile["layers"]:
                dz = layer["geopotential_top_m"] - layer["geopotential_bottom_m"]
                self.assertGreater(dz, 0)
                self.assertGreater(layer["pressure_bottom_hpa"], layer["pressure_top_hpa"])
                t0 = r.potential_temperature(layer["temperature_bottom_c"], layer["pressure_bottom_hpa"])
                t1 = r.potential_temperature(layer["temperature_top_c"], layer["pressure_top_hpa"])
                n2 = r.G0 / ((t0 + t1) / 2) * (t1 - t0) / dz
                self.assertAlmostEqual(layer["finite_layer_dry_n2_s_minus2"], n2, delta=5.1e-10)
                if layer["finite_layer_dry_richardson"] is not None:
                    shear2 = layer["finite_layer_shear_squared_s_minus2"]
                    self.assertGreater(shear2, 0)
                    self.assertAlmostEqual(layer["finite_layer_dry_richardson"],
                                           n2 / shear2, delta=0.04)

    def test_no_threshold_wind_transfer_turbulence_or_location(self):
        method = r.build()["method"]
        self.assertFalse(method["critical_local_gradient_threshold_applicable"])
        self.assertFalse(method["physical_domain_reduction"])
        self.assertFalse(method["event_location_inferred"])
        for key in ("instrument_uncertainty", "height_transfer_uncertainty",
                    "spatiotemporal_transfer_uncertainty"):
            self.assertIsNone(method[key])
        self.assertIn("PENDING_UNCALIBRATED_TRANSFER", method["graph"][-1]["status"])
        self.assertIn("turbulence", method["not_observed"])

    def test_mismatched_endpoints_are_rejected(self):
        winds = r.read_winds("08")
        with mock.patch.object(r, "read_winds", return_value=[
                {**winds[0], "geopotential_height_m_asl": 999}, *winds[1:]]):
            with self.assertRaisesRegex(ValueError, "co-located"):
                r.build()

    def test_quality_flag_drift_is_rejected(self):
        winds = r.read_winds("07")
        with mock.patch.object(r, "read_winds", return_value=[
                {**winds[0], "geopotential_height_qc_flag": "fake"}, *winds[1:]]):
            with self.assertRaisesRegex(ValueError, "QC"):
                r.build()

    def test_no_divide_by_zero_or_invented_infinite_ri(self):
        row = {"pressure_hpa": 1000, "geopotential_height_m_asl": 100,
               "temperature_deg_c": 25, "u_east_m_s": 1.0, "v_north_m_s": 1.0,
               "wind_speed_m_s": math.sqrt(2)}
        high = {**row, "pressure_hpa": 900, "geopotential_height_m_asl": 1000}
        result = r.finite_layer(row, high)
        self.assertIsNone(result["finite_layer_dry_richardson"])
        with self.assertRaises(ValueError):
            r.finite_layer(high, row)

    def test_corrupted_source_timestamp_and_raw_hash_rejected(self):
        raw = original.load_original("08")
        for bad in (raw.replace(b"12 9999", b"12 1200", 1),
                    raw[:-5] + b"xxxx\n"):
            with self.subTest(bad=bad[:40]):
                with self.assertRaises(ValueError):
                    density.extract("08", bad)


if __name__ == "__main__":
    unittest.main()
