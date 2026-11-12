"""C179 / C151 physical crosswalk: measured data, conditional math, zero false provenance."""
from pathlib import Path
import math
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal" / "scripts"))
from physical_observable_bridge import (  # noqa: E402
    orbital_observables, recife_winds, conditional_drift,
    meteorological_wind_to_en, build_contract,
)

MATRIX = ROOT / "research" / "evidence_matrix_C001-C238_2026-11-11.md"


class PhysicalObservableBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = MATRIX.read_bytes()
        cls.report = build_contract(cls.data, 50)

    def test_orbital_units_and_kepler_and_j2_are_computed(self):
        orbit = orbital_observables()
        n = orbit["derived_mean_angular_rate_rad_per_s"]
        a = orbit["derived_kepler_proxy_semimajor_km"]
        self.assertAlmostEqual(n, 15.74901460 * 2 * math.pi / 86400.0)
        self.assertAlmostEqual(n * n * a ** 3, 398600.4418, delta=1e-6)
        self.assertGreater(orbit["derived_kepler_proxy_perigee_altitude_km"], 0)
        self.assertAlmostEqual(orbit["derived_first_order_j2_raan_rate_deg_per_day"],
                               -1.173124071, places=8)
        self.assertEqual(orbit["source_occurrence"], "C179#1")
        self.assertEqual(orbit["source_status"], "SECONDARY_MIRROR_NOT_PRIMARY_TRACK")
        self.assertIsNone(orbit["physical_raan_interval_deg"])

    def test_c151_contains_five_measured_recife_winds_not_conde(self):
        wind = self.report["atmospheric_observations"]
        self.assertEqual([r["pressure_hpa"] for r in wind],
                         [850, 700, 500, 300, 250])
        self.assertEqual([r["measured_wind_from_degrees"] for r in wind],
                         [100, 236, 159, 129, 102])
        self.assertEqual([r["measured_wind_speed_m_s"] for r in wind],
                         [4, 4, 6, 15, 17])
        self.assertEqual([r["derived_pressure_pa"] for r in wind],
                         [85000, 70000, 50000, 30000, 25000])
        self.assertTrue(all(r["station"] == "BRM00082900" for r in wind))
        self.assertTrue(all(r["location"].startswith("Recife") for r in wind))
        self.assertTrue(all(r["actual_release_time"] is None for r in wind))
        self.assertTrue(all(r["evidence_occurrence"] == "C151#1" for r in wind))
        self.assertGreater(wind[0]["derived_wind_to_east_m_s"], -4.001)
        self.assertLess(wind[0]["derived_wind_to_east_m_s"], -3.9)

    def test_wind_from_direction_is_converted_to_destination_components(self):
        u, v = meteorological_wind_to_en(10, 90)
        self.assertAlmostEqual(u, -10)
        self.assertAlmostEqual(v, 0, places=12)
        u, v = meteorological_wind_to_en(10, 0)
        self.assertAlmostEqual(u, 0, places=12)
        self.assertAlmostEqual(v, -10, places=12)
        for speed, angle in [(-1, 30), (1, 361), (math.nan, 40)]:
            with self.assertRaises(ValueError):
                meteorological_wind_to_en(speed, angle)

    def test_conditional_drift_sensitivity_not_impact(self):
        rows = recife_winds(self.data)
        slow = conditional_drift(rows, 50)
        fast = conditional_drift(rows, 100)
        self.assertAlmostEqual(slow["derived_descent_time_s"], 9440 / 50)
        self.assertAlmostEqual(fast["derived_descent_time_s"],
                               slow["derived_descent_time_s"] / 2)
        self.assertAlmostEqual(fast["derived_east_displacement_m"],
                               slow["derived_east_displacement_m"] / 2)
        self.assertAlmostEqual(fast["derived_north_displacement_m"],
                               slow["derived_north_displacement_m"] / 2)
        self.assertTrue(slow["not_ground_displacement"])
        self.assertTrue(slow["not_conde_weather"])
        self.assertTrue(slow["not_norad_528_constraint"])
        for bad in [0, -1, math.inf, math.nan]:
            with self.assertRaises(ValueError):
                conditional_drift(rows, bad)

    def test_no_false_cross_location_transfer_or_atmospheric_inference(self):
        output = self.report
        self.assertEqual(output["schema"], "conde.physical-observable-crosswalk/v1")
        self.assertEqual(output["matrix_snapshot"],
                         "a7978c3a75a153b16ab70118a92c434bba674cb7")
        self.assertEqual(output["cross_location_transfer_to_conde"], "NOT_VERIFIED")
        self.assertIsNone(output["actual_conde_wind_profile_1963_11_08"])
        self.assertIsNone(output["calibrated_atmospheric_spatial_temporal_error"])
        self.assertEqual(output["reduction_of_norad528_admissible_domain"], "NOT_RUN")
        self.assertEqual(output["reentry_or_ground_impact_in_conde"], "INDETERMINATE")
        kinds = {d["name"]: d["status"] for d in output["physical_observation_operators"]}
        self.assertEqual(kinds["air_density_from_pressure_temperature"],
                         "NOT_RUN_NO_COLLOCATED_TEMPERATURE_IN_THIS_EXTRACT")
        self.assertEqual(kinds["drag_acceleration"],
                         "NOT_RUN_UNBOUNDED_OBJECT_AND_ATMOSPHERE")

    def test_edited_or_incomplete_evidence_matrix_is_rejected(self):
        with self.assertRaises(ValueError):
            recife_winds(self.data.replace(b"850 hPa 100", b"850 hPa 101", 1))
        with self.assertRaises(ValueError):
            recife_winds(self.data.replace(b"850 hPa 100", b"850 hPa 101", 1))


if __name__ == "__main__":
    unittest.main()
