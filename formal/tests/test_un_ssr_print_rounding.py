"""C241-P34: adversarial rounding sensitivity, provenance and sharp witness."""
from __future__ import annotations

import copy
import json
import unittest

from formal.scripts import compile_un_ssr_cross_compilation as cross
from formal.scripts import compile_un_ssr_print_rounding as rounding


class PrintRoundingTests(unittest.TestCase):
    def test_26_cell_sharp_witness_replay(self):
        result = rounding.build()
        self.assertEqual(result["schema"], "conde.c241-p34-un-ssr-print-rounding/v1")
        self.assertEqual(result["id"], "C241-P34")
        self.assertEqual(result["parent"], "C241-P23")
        self.assertEqual(len(result["cells"]), 26)
        self.assertEqual(len(result["nasa_sources"]), 9)
        self.assertEqual(result["printed_no_rounding_optimum_centiminute"], 135)
        self.assertEqual(result["rounded_print_optimum_centiminute"], 130)
        self.assertEqual(result["rounded_print_optimum_seconds"], "78.0")
        self.assertEqual(result["rounded_print_optimum_means"],
                         "CLOSED_SYMMETRIC_ENVELOPE_ALLOWING_BOTH_ENDPOINT_TIES")
        self.assertEqual(result["closed_envelope_endpoint_ties_used"], 13)
        self.assertEqual(result["discrete_round_half_up_optimum_centiminute"], 131)
        self.assertEqual(result["discrete_round_half_even_optimum_centiminute"], 131)
        self.assertEqual(result["discrete_round_half_up_or_even_optimum_seconds"], "78.6")
        self.assertEqual(result["half_step_tie_convention_of_historical_printing"], "UNKNOWN")
        self.assertTrue(result["strict_interior_witness_all_26_cells_attained"])
        self.assertEqual(result["sharp_certificate"]["difference_centiminute"], 540)
        self.assertEqual(result["physical_domain"], "THETA_UNCHANGED")
        self.assertEqual(result["independent_tracking_rows_added"], 0)
        self.assertIsNone(result["instrument_covariance"])
        self.assertFalse(result["un_administrative_cutoff_is_sensor_epoch"])
        self.assertFalse(result["publication_date_is_observation_epoch"])
        self.assertFalse(result["cross_agency_common_offset_validated"])
        self.assertEqual(json.loads(rounding.REPORT.read_text()), result)
        self.assertEqual(rounding.LEAN.read_text(), rounding.render_lean(result))
        self.assertNotIn("sorry", rounding.LEAN.read_text())
        self.assertIn("all_26_cells_attain_130", rounding.LEAN.read_text())
        self.assertIn("half_up_discrete_lower_bound", rounding.LEAN.read_text())
        self.assertIn("half_even_discrete_lower_bound", rounding.LEAN.read_text())
        self.assertIn("all_26_strict_interior_attain_131", rounding.LEAN.read_text())
        corrected = 0
        max_residual = 0
        max_strict_residual = 0
        for r in result["cells"]:
            printed = r["printed_centiminute"]
            latent = r["latent_centiminute"]
            delta = r["print_minus_latent_centiminute"]
            e = r["offset_model_residual_centiminute"]
            expected = (result["witness_baselines"][str(r["object"])] +
                        result["witness_offsets"][r["document_or_cutoff"]])
            self.assertEqual(latent, expected + e)
            self.assertEqual(printed - latent, delta)
            self.assertEqual(printed % 10, 0)
            self.assertLessEqual(abs(delta), 5)
            self.assertLessEqual(abs(e), 130)
            strict_delta = r["strict_print_minus_latent_centiminute"]
            strict_latent = r["strict_latent_centiminute"]
            strict_e = r["strict_offset_model_residual_centiminute"]
            self.assertEqual(strict_latent, expected + strict_e)
            self.assertEqual(strict_delta, printed - strict_latent)
            self.assertLessEqual(abs(strict_delta), 4)
            self.assertLessEqual(abs(strict_e), 131)
            # For strictly positive printed periods and a 0.01-minute
            # latent grid, all |q|<=4 values round correctly under half-up
            # and half-even, regardless of the parity of the final digit.
            self.assertGreaterEqual(strict_delta, -4)
            self.assertLessEqual(strict_delta, 4)
            max_strict_residual = max(max_strict_residual, abs(strict_e))
            corrected += delta != 0
            max_residual = max(max_residual, abs(e))
        self.assertEqual(corrected, result["rounding_corrections_nonzero"])
        self.assertGreater(corrected, 0)
        self.assertEqual(max_residual, 130)
        self.assertEqual(max_strict_residual, 131)

    def test_four_cell_certificate_is_sharp(self):
        result = rounding.build()
        gaps = result["sharp_certificate"]["printed_gaps_centiminute"]
        self.assertEqual(gaps, [0, 540])
        gap_delta = abs(gaps[1] - gaps[0])
        # Four residuals and four ROUNDING corrections, each bounded.
        self.assertGreater(gap_delta, 4 * (129 + 5))
        self.assertLessEqual(gap_delta, 4 * (130 + 5))
        # Under either integer-grid deterministic tie convention,
        # the largest four-rounding-term contrast is 18, NOT 20.
        self.assertGreater(gap_delta, 4 * 130 + 18)
        self.assertLessEqual(gap_delta, 4 * 131 + 18)

    def test_no_rounded_input_is_promoted_to_instrument_measurement(self):
        result = rounding.build()
        for key in ("instrument_covariance",):
            self.assertIsNone(result[key])
        self.assertNotIn("sensor_sigma", str(result))
        self.assertEqual(result["physical_domain"], "THETA_UNCHANGED")

    def test_adversarial_identity_and_printed_period_fail_closed(self):
        un = json.loads(cross.UN.read_text(encoding="utf-8"))
        for patch in (
            lambda x: x["docs"][0]["printed_rows"][0].update(nodal_period_min_printed="94.6"),
            lambda x: x["docs"][0]["printed_rows"][2].update(printed_designator="1963-3-B"),
            lambda x: x["docs"][0].update(sha256="0" * 64),
            lambda x: x["docs"][0].update(report_cutoff_printed="2400Z 13 MARCH 1963"),
            lambda x: x["interpretation"].update(un_cutoff_is_sensor_epoch=True),
        ):
            changed = copy.deepcopy(un)
            patch(changed)
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                rounding.build(un=changed)

    def test_nasa_source_tampering_fails_closed(self):
        from tools import tle_ssr_editions_precision_audit as audit
        model = audit.read(audit.MODEL)
        model["docs"][0]["ntrs"] = "00000000000"
        with self.assertRaises(ValueError):
            rounding.build(nasa_model=model)

    def test_render_is_deterministic(self):
        result = rounding.build()
        self.assertEqual(rounding.render_lean(result), rounding.render_lean(rounding.build()))
        self.assertEqual(rounding.REPORT.read_text(),
                         json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    unittest.main()
