"""Mutation controls for SAO 266 synthetic derived observation independence."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "sao_sr266_l60", Path(__file__).resolve().parents[1] / "tools/tle_sao_sr266_c241_l60.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class SyntheticObservations(unittest.TestCase):
    def setUp(self):
        self.m = mod.load()

    def test_baseline(self):
        self.assertEqual(mod.validate(self.m)["physical_constraints"], 0)

    def test_source_integrity(self):
        for field, value in (("sha256", "0"*64), ("bytes", 0), ("pdf_pages", 10),
                             ("ntrs_id", "19690000807"), ("publication_date", "1963-11-08")):
            mutated = copy.deepcopy(self.m)
            mutated["source"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.validate(mutated)

    def test_scoped_negative_evidence(self):
        for field, value in (("includes_1963_003", True), ("table1_target_count", 13),
                             ("scope", "NEVER_SEEN_BY_ANY_CAMERA"), ("table1_designations", ["63 03 B"])):
            mutated = copy.deepcopy(self.m)
            mutated["published_dataset"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.validate(mutated)

    def test_synthetic_is_not_independent_raw_row(self):
        for field, value in (("method", "RAW_SENSOR_MEASUREMENT"), ("independence_policy", "INDEPENDENT"),
                             ("stations_per_synthetic_pair_min", 1), ("raw_frames_per_station_min", 1),
                             ("raw_frames_per_station_max", 1)):
            mutated = copy.deepcopy(self.m)
            mutated["published_dataset"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.validate(mutated)

    def test_no_fake_utc_teme_sigma(self):
        for field, value in (("time_scale", "UTC"), ("direction_frame", "TEME"),
                             ("timing_uncertainty_msec_context", [0, 0]),
                             ("synthetic_rejection_threshold_arcsec", 0)):
            mutated = copy.deepcopy(self.m)
            mutated["published_dataset"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.validate(mutated)

    def test_528_never_inferred(self):
        target = self.m["target_527_528_529"]
        for key in target:
            mutated = copy.deepcopy(self.m)
            mutated["target_527_528_529"][key] = "1963-11-08T00:00:00Z" if target[key] is None else 1
            with self.subTest(field=key), self.assertRaises(ValueError):
                mod.validate(mutated)

    def test_corrupt_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "source bytes drifted"):
            mod.inspect_pdf(b"%PDF-1.6 tampered")


if __name__ == "__main__":
    unittest.main()
