"""Adversarial checks for source-locked precipitation, not a reentry claim."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_ghcnd_conde_bridge import (
    REPORT, GRAPH, OBSERVABLE, CARAVELAS, OUT, build, render
)


class RainBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents = [json.loads((ROOT / p).read_text())
                       for p in (REPORT, GRAPH, OBSERVABLE, CARAVELAS)]

    def mutate(self, idx=None, change=None):
        docs = copy.deepcopy(self.parents)
        if idx is not None:
            change(docs[idx])
        return build(*docs, {})

    def test_valid_archival_candidate_is_not_fall_constraint(self):
        bridge = self.mutate()
        self.assertEqual(bridge["station"]["daily_precipitation_tenths_mm"],
                         [0, 35, 0])
        self.assertEqual(bridge["comparison_station"]["daily_precipitation_tenths_mm"],
                         [0, 24, 0])
        self.assertEqual(bridge["observations_count"], 33)
        self.assertEqual(len(bridge["station_source_ids"]), 11)
        self.assertEqual(len(bridge["source_dependency_graph"]), 6)
        self.assertFalse(bridge["activation"])
        self.assertEqual(bridge["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertEqual(bridge["comparison_independence"],
                         "UNKNOWN_DISTINCT_ARCHIVAL_PRODUCTS")
        for key in ("station_coordinates_verified_1963", "rainfall_at_incident_site",
                    "observation_time_within_day", "instrument_error_covariance",
                    "terminal_epoch_528", "independent_instruments_count",
                    "simulator_value"):
            self.assertIsNone(bridge[key])

    def test_full_station_file_hash_swap_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["stations"][0].update(whole_file_sha256="0"*64))

    def test_station_identity_swap_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["stations"][0].update(id="BR048340980"))

    def test_raw_precipitation_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["stations"][0]["daily"][1].update(
                precipitation_mm=35.0))

    def test_day_clock_promotion_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["not_proved"].update(
                observation_time_within_day="12:00 UTC"))

    def test_false_calibration_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d.update(instrument_error_model=0.1))

    def test_fabricated_fall_edge_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d["edges"][4].update(type="PROVES_528_FALL"))

    def test_false_ghcnd_and_isd_independence_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d["edges"][5].update(
                type="TWO_INDEPENDENT_INSTRUMENTS"))

    def test_undocumented_rainfall_source_flag_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["stations"][0]["daily"][1].update(
                source_flag="S"))

    def test_c151_context_swap_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(2, lambda d: next(
                x for x in d["edges"] if x["source_id"] == "NOAA_IGRA_RECIFE_1963"
            ).update(matrix_occurrence="matrix:abc:C179#1"))

    def test_caravelas_wind_false_activation_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(3, lambda d: d.update(activation=True))

    def test_lean_source_and_site_are_reproducible(self):
        self.assertEqual(OUT.read_bytes(), render())
        lean = (ROOT / "formal/Conde1963/GhcndCondeCandidate.lean").read_text()
        for value in ("MET-GHCND-CONDE-19631107-09-01", "BR048346820",
                      "f99557d7cb4187ea412b85b205ad2b04bf7449c0b89d27d4f546f75cbc717d53",
                      "BR048340980", "[0, 35, 0]", "[0, 24, 0]",
                      "observingDayClock := none", "orbitalTransfer := none"):
            self.assertIn(value, lean)
        self.assertIn("import Conde1963.GhcndCondeCandidate",
                      (ROOT / "formal/Conde1963.lean").read_text())
        self.assertLessEqual(OUT.stat().st_size, 20_000)


if __name__ == "__main__":
    unittest.main()
