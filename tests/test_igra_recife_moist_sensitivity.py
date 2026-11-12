"""Conditional moist-air density sensitivity: pinned source, missingness, guardrails."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import audit_igra_recife_moist_sensitivity as audit
from audit_igra_recife_window import DAYS


class MoistSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=audit.build()

    def test_full_rebuild_matches_checked_artifact(self):
        audit.check()
        self.assertEqual(json.loads(audit.FILE.read_text()),self.data)

    def test_exact_counts_and_no_cold_extrapolation(self):
        self.assertEqual(self.data["totals"],{
            "pt_levels":81,"rh_present":32,"warm_rh_eligible":22,
            "rh_missing":49,"subzero_rh_excluded":10})
        self.assertEqual([x["warm_rh_eligible_levels"] for x in self.data["profiles"]],[8,6,8])
        for prof in self.data["profiles"]:
            self.assertIsNone(prof["actual_launch_time_utc"])
            for row in prof["conditional_levels"]:
                self.assertGreaterEqual(row["temperature_deg_c"],0)
                self.assertIsNotNone(row["reported_rh_percent"])

    def test_single_source_family_and_no_conde_transfer(self):
        self.assertEqual(self.data["identity"]["upstream"],"ncdc6301")
        self.assertFalse(self.data["identity"]["1963_station_geolocation_reconstructed"])
        m=self.data["model"]
        self.assertFalse(m["density_values_are_observed"])
        self.assertFalse(m["theta_constraint_activated"])
        for key in ("recife_to_conde_transfer_error","instrumental_rh_accuracy_percent",
                    "instrumental_temperature_accuracy_deg_c","temporal_transfer_error"):
            self.assertIsNone(m[key])
        self.assertEqual(len(set(x["source_excerpt_sha256"] for x in self.data["profiles"])),3)

    def test_moist_is_less_dense_at_positive_humidity(self):
        for prof in self.data["profiles"]:
            for row in prof["conditional_levels"]:
                self.assertGreater(row["dry_density_proxy_kg_m3"],row["conditional_moist_density_kg_m3"])
                self.assertLess(row["conditional_delta_moist_minus_dry_kg_m3"],0)
                self.assertGreater(row["conditional_fractional_decrease_pct"],0)

    def test_zero_humidity_yields_exact_dry_density(self):
        s=audit.scenario(1000,25,0)
        self.assertEqual(s["dry_density_proxy_kg_m3"],s["conditional_moist_density_kg_m3"])
        self.assertEqual(s["conditional_delta_moist_minus_dry_kg_m3"],0)

    def test_hand_checked_partial_pressures(self):
        s=audit.scenario(1000,26.9,52)
        self.assertAlmostEqual(s["saturation_vapor_pressure_hpa_model"],
                               6.1094*__import__("math").exp(17.625*26.9/(243.04+26.9)),places=5)
        e=s["partial_vapor_pressure_hpa_model"]
        self.assertAlmostEqual(s["conditional_moist_density_kg_m3"],
                               ((1000-e)*100/287.05+e*100/461.5)/300.05,places=7)

    def test_refuse_subzero_temperature_or_unreported_humidity(self):
        for args in ((700,-3,20),(1000,25,None),(1000,60,30),
                     (0,25,60),(1000,25,-1),(1000,25,101),(1,50,100),
                     (float("nan"),25,20),(1000,float("inf"),20)):
            with self.subTest(args=args),self.assertRaises((TypeError,ValueError)):
                audit.scenario(*args)

    def test_no_pseudoreplication_as_independent_sources(self):
        self.assertEqual(len(self.data["profiles"]),3)
        self.assertIn("one NOAA/IGRA",self.data["identity"]["dependence"])
        self.assertEqual(self.data["model"]["status"],"CONNECTED_PENDING_CALIBRATION")

if __name__=="__main__":
    unittest.main()
