"""Adversarial provenance and metric checks for the historical Telstar table."""
import importlib.util
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "telstar_1962_prediction_benchmark"
spec = importlib.util.spec_from_file_location(NAME, ROOT / "tools" / (NAME + ".py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TelstarHistoricalBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = mod.CSV.read_bytes()
        cls.rows = mod.load_rows()
        cls.report = mod.summarize(cls.rows)

    def test_nasa_table_is_source_locked(self):
        self.assertEqual(mod.sha(self.raw), mod.CSV_SHA256)
        self.assertEqual(len(self.rows), 38)
        self.assertEqual([p["count"] for p in self.report["passes"]], [8, 7, 7, 8, 8])
        self.assertTrue(all(row["utc"].startswith("1962-") for row in self.rows))

    def test_nasa_original_pdf_is_verified_if_supplied(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            bogus = Path(tmp) / "not-the-paper.pdf"
            bogus.write_bytes(b"%PDF-1.4 bogus\n")
            with self.assertRaisesRegex(ValueError, "custody"):
                mod.verify_pdf(bogus)

    def test_edits_to_source_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "changed"):
            mod.load_rows(self.raw.replace(b"195.16", b"195.17"))
        with self.assertRaisesRegex(ValueError, "changed"):
            mod.load_rows(self.raw.replace(b",124,", b",143,", 1))

    def test_utc_midnight_preserved_not_split_as_independent_pass(self):
        crossing = [r for r in self.rows if r["pass_id"] == 143]
        self.assertEqual(len(crossing), 7)
        self.assertEqual(crossing[0]["utc"], "1962-07-25T23:43Z")
        self.assertEqual(crossing[-1]["utc"], "1962-07-26T00:19Z")

    def test_printed_cells_exact_first_last_and_high_elevation(self):
        first, last = self.rows[0], self.rows[-1]
        self.assertEqual((first["az_obs"], first["az_pred"],
                          first["el_obs"], first["el_pred"]),
                         (Decimal("195.16"), Decimal("195.20"),
                          Decimal("20.50"), Decimal("20.48")))
        self.assertEqual(last["az_obs"], Decimal("78.98"))
        self.assertEqual(last["el_pred"], Decimal("23.63"))
        high = next(r for r in self.rows if r["utc"] == "1962-07-26T00:07Z")
        self.assertEqual(high["el_obs"], Decimal("76.43"))
        self.assertEqual(high["az_pred"] - high["az_obs"], Decimal("-0.08"))

    def test_spherical_angle_avoids_azimuth_singularity(self):
        self.assertAlmostEqual(mod.circular_difference_deg(0.01, 359.99), 0.02, places=9)
        self.assertAlmostEqual(mod.sky_separation_deg(1, 181, 90, 90), 0.0, places=10)
        self.assertAlmostEqual(mod.sky_separation_deg(0, 0, 10, 10), 0.0, places=10)
        self.assertAlmostEqual(mod.sky_separation_deg(0, 0, 10, 11), 1.0, places=9)

    def test_regression_historical_descriptive_statistics(self):
        self.assertAlmostEqual(self.report["all_rows_descriptive_los_rms_deg"],
                               0.0334590, places=7)
        self.assertAlmostEqual(self.report["all_rows_descriptive_los_max_deg"],
                               0.0730545, places=7)
        self.assertEqual(self.report["passes"][-1]["pass_id"], 160)

    def test_not_528_sigma_or_new_blind_holdout(self):
        self.assertEqual(self.report["classification"],
                         "EMPIRICAL_COMPARISON_OTHER_SATELLITE_NOT_528_CALIBRATION")
        eligibility = self.report["eligibility"]
        self.assertIsNone(eligibility["sensor_sigma_for_norad_528"])
        self.assertIsNone(eligibility["orbit_covariance_for_norad_528"])
        self.assertIsNone(eligibility["terminal_timing_distribution_for_norad_528"])
        self.assertFalse(eligibility["calibrated_historical_528_likelihood"])
        self.assertFalse(eligibility["active_conde_geographic_constraint"])
        self.assertEqual(eligibility["historic_528_mcmc"], "NOT_RUN")
        self.assertFalse(self.report["method"]["rows_are_independent_realizations"])
        self.assertFalse(self.report["method"]["rounding_rule_verified"])

    def test_pass_deletion_counts_and_nonpredictive_contract(self):
        diag = self.report["pass_deletion_sensitivity"]
        self.assertEqual(diag["classification"],
                         "PASS_BLOCK_DELETION_SENSITIVITY_NOT_CROSS_VALIDATION")
        self.assertFalse(diag["refits_prediction_model"])
        self.assertFalse(diag["prospective_or_blind_holdout"])
        self.assertFalse(diag["assumes_independent_passes"])
        self.assertFalse(diag["estimates_population_uncertainty"])
        self.assertEqual([(v["excluded_pass_id"], v["remaining_rows"],
                           v["remaining_passes"]) for v in diag["passes"]],
                         [(124,30,4),(133,31,4),(143,31,4),(151,30,4),(160,30,4)])
        self.assertAlmostEqual(diag["min_deletion_rms_deg"], 0.0267494, places=7)
        self.assertAlmostEqual(diag["max_deletion_rms_deg"], 0.0357907, places=7)
        self.assertAlmostEqual(diag["rms_range_deg"], 0.0090413, places=7)

    def test_deletion_diagnostics_are_recomputed_from_source_locked_rows(self):
        for excluded in mod.COUNTS:
            remaining = [r for r in self.rows if r["pass_id"] != excluded]
            squares = [mod.sky_separation_deg(*(float(r[k]) for k in
                        ("az_obs", "az_pred", "el_obs", "el_pred")))**2
                       for r in remaining]
            expected = (sum(squares) / len(squares))**0.5
            got = next(v["descriptive_los_rms_deg"] for v in
                       self.report["pass_deletion_sensitivity"]["passes"]
                       if v["excluded_pass_id"] == excluded)
            self.assertAlmostEqual(got, expected, places=7)
        with self.assertRaisesRegex(ValueError, "pass-membership"):
            mod.pass_deletion_sensitivity(self.rows[:-1])

    def test_generated_report_is_reproducible(self):
        import json
        self.assertEqual(json.loads(mod.OUT.read_text()), self.report)


if __name__ == "__main__":
    unittest.main()
