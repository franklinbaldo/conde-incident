"""C241-P11: reject source tampering and measure genuine November holdout."""
import copy
import json
from pathlib import Path
import unittest

from formal.scripts.compile_ssr_november import (
    LEDGER, OCTOBER, SURVIVORS, BRIDGE, REPORT, LEAN, compile_report, render_lean,
)

LED = json.loads(LEDGER.read_text())
OCT = json.loads(OCTOBER.read_text())
SURV = json.loads(SURVIVORS.read_text())
LINK = json.loads(BRIDGE.read_text())


class TestNovemberPrintedMeasures(unittest.TestCase):
    def test_original_16_fields_from_november_facsimiles(self):
        r = compile_report(LED, OCT, SURV)
        a, c = r["objects"]
        self.assertEqual(a["printed_values_scaled"][1]["period_min"], 9460)
        self.assertEqual(a["printed_values_scaled"][2]["period_min"], 9460)
        self.assertEqual(c["printed_values_scaled"][1]["period_min"], 9260)
        self.assertEqual(c["printed_values_scaled"][2]["period_min"], 9220)
        self.assertEqual(a["printed_values_scaled"][2]["apogee_km"], 1066)
        self.assertEqual(c["printed_values_scaled"][2]["apogee_km"], 780)
        self.assertEqual(c["printed_values_scaled"][2]["perigee_km"], 736)
        self.assertEqual(c["printed_values_scaled"][2]["inclination_deg"], 8186)
        self.assertEqual(r["source_ids"], ["C241-L12", "C241-L19#1", "C241-L18:19640002493", "C197#1"])

    def test_november_c_period_decline_not_shared_with_a(self):
        a, c = compile_report(LED, OCT, SURV)["objects"]
        self.assertEqual(a["oct15_minus_nov15_and_nov15_minus_nov30_bounds"]["period_min"][1], [-10, 10])
        self.assertEqual(c["oct15_minus_nov15_and_nov15_minus_nov30_bounds"]["period_min"][1], [30, 50])
        self.assertEqual(a["oct15_minus_nov15_and_nov15_minus_nov30_bounds"]["apogee_km"][1], [4, 8])
        self.assertEqual(c["oct15_minus_nov15_and_nov15_minus_nov30_bounds"]["apogee_km"][1], [58, 62])

    def test_3a_apogee_control_rejects_universal_extrapolation(self):
        a, c = compile_report(LED, OCT, SURV)["objects"]
        self.assertGreater(
            a["nov30_publication_holdout"]["apogee_km"]["linear_from_oct15_nov15_error"],
            a["nov30_publication_holdout"]["apogee_km"]["persist_last_error"],
        )
        self.assertLess(
            c["nov30_publication_holdout"]["apogee_km"]["linear_from_oct15_nov15_error"],
            c["nov30_publication_holdout"]["apogee_km"]["persist_last_error"],
        )
        self.assertLess(
            c["nov30_publication_holdout"]["period_min"]["linear_from_oct15_nov15_error"],
            c["nov30_publication_holdout"]["period_min"]["persist_last_error"],
        )

    def test_bad_november_30_legacy_period_948_fails(self):
        old = copy.deepcopy(SURV)
        old["sources"][1]["rows"][0]["period_min"] = "94.8"
        with self.assertRaisesRegex(ValueError, "transcription mismatch"):
            compile_report(LED, OCT, old)

    def test_source_hash_or_page_mutation_fails(self):
        for f, value in (("sha256", "0"*64), ("page_index", 5),
                         ("bytes", 0), ("ntrs", "19640002492")):
            old = copy.deepcopy(SURV)
            old["sources"][1][{"ntrs": "ntrs_id", "page_index": "pdf_page_index"}.get(f, f)] = value
            with self.subTest(f=f), self.assertRaises(ValueError):
                compile_report(LED, OCT, old)

    def test_new_row_swap_or_duplicate_fails(self):
        altered = copy.deepcopy(SURV)
        altered["sources"][1]["rows"][1]["designator"] = "1963-003A"
        with self.assertRaises(ValueError):
            compile_report(LED, OCT, altered)
        altered = copy.deepcopy(SURV)
        altered["sources"][1]["rows"].append(copy.deepcopy(altered["sources"][1]["rows"][1]))
        with self.assertRaises(ValueError):
            compile_report(LED, OCT, altered)

    def test_primary_october_row_mutation_fails(self):
        altered = copy.deepcopy(OCT)
        altered["catalog_rows"][0]["nodal_period_min_printed"] = "94.8"
        with self.assertRaisesRegex(ValueError, "October primary facsimile row"):
            compile_report(LED, altered, SURV)

    def test_no_fictitious_sensor_epoch_or_covar(self):
        for key in ("publication_date_is_observation_epoch",
                    "instrumental_epoch_known", "individual_sensor_known",
                    "covariance_known", "physical_constraint_activated"):
            altered = copy.deepcopy(LED)
            altered["limits"][key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                compile_report(altered, OCT, SURV)

    def test_bridge_binds_real_527_period_without_sensor_epoch(self):
        binding = compile_report(LED, OCT, SURV, LINK)["source_locked_bridge"]
        self.assertEqual(binding["canonical_527_nov30_period_min"], "94.6")
        self.assertEqual(binding["nov15_to_nov30_527_publication_delta_min"], "0.0")
        self.assertEqual(binding["linked_occurrences"],
                         ["C241-L19#1", "C241-L18:19640002493"])
        self.assertFalse(binding["constraint_activation"])
        self.assertIsNone(binding["observed_epoch"])
        self.assertIsNone(binding["sensor_sigma"])

    def test_bridge_tampering_and_promotion_are_rejected(self):
        mutants = [
            ("canonical_value_min", "94.8"),
            ("canonical_value_seconds", "5688"),
            ("documentary_delta_min", "0.2"),
            ("simulator_observation_epoch_utc", "1963-11-30T12:00:00Z"),
            ("simulator_instrument_error", 0),
            ("simulator_calibrated_value", "94.6"),
            ("active_physical_constraint", True),
            ("checked_control_cells", 14),
        ]
        for field, replacement in mutants:
            mutant = copy.deepcopy(LINK)
            mutant[field] = replacement
            with self.subTest(field=field), self.assertRaises(ValueError):
                compile_report(LED, OCT, SURV, mutant)
        for field, replacement in (("pdf_sha256", "0"*64),
                                   ("published_on", "1963-11-29"),
                                   ("matrix_context", ["C197#1"]),
                                   ("occurrence_id", "C197#1")):
            mutant = copy.deepcopy(LINK)
            mutant["linked_sources"][1][field] = replacement
            with self.subTest(field=field), self.assertRaises(ValueError):
                compile_report(LED, OCT, SURV, mutant)

    def test_report_and_lean_are_deterministic(self):
        r = compile_report(LED, OCT, SURV)
        self.assertEqual(json.loads(REPORT.read_text()), r)
        self.assertEqual(LEAN.read_text(), render_lean(r))
        self.assertIn("printed_november_period_3c_gt_3a", LEAN.read_text())
        self.assertEqual(r["physical_admissible_domain_change"], "NONE")
        self.assertEqual(r["instrumental_validation"], "NOT_RUN_NO_ORIGINAL_SENSOR_EPOCH_FRAME_COVARIANCE")


if __name__ == "__main__":
    unittest.main()
