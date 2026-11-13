"""C241-P16 source-mutation, witness and Lean-generator regression tests."""
from __future__ import annotations

import copy
import json
import unittest

from formal.scripts.compile_ssr_four_editions import (
    LEDGERS, REPORT, LEAN, build, panel_minimum, render_lean,
)

DOCS = tuple(json.loads(f.read_text()) for f in LEDGERS)


class TestSsrFourEditions(unittest.TestCase):
    def test_four_source_locked_editions_and_exact_witness(self):
        r = build(DOCS)
        self.assertEqual(r["difference_527_minus_528"], [50, 90, 100, 130])
        self.assertEqual(r["exact_minimax_centiminute"], 20)
        self.assertEqual(r["exact_minimax_seconds"], 12)
        self.assertEqual(r["ratio_to_print_rounding_halfunit"], 4)
        w = r["attaining_witness"]
        for obj, printed in r["printed_period_by_object"].items():
            for i, actual in enumerate(printed):
                residual = w["per_object_edition_residual_centiminute"][obj][i]
                self.assertEqual(actual, w["object_baselines_centiminute"][obj]
                                 + w["shared_edition_bias_centiminute"][i] + residual)
                self.assertLessEqual(abs(residual), r["exact_minimax_centiminute"])
        self.assertEqual(len(r["source_documents"]), 4)
        self.assertEqual(len(r["rejected_edges"]), 5)

    def test_negative_control_symmetric_constant_gaps(self):
        p = {"527": [10, 10, 10, 10], "528": [8, 8, 8, 8],
             "529": [9, 9, 9, 9]}
        self.assertEqual(panel_minimum(p), 0)
        p["528"][-1] = 4
        self.assertEqual(panel_minimum(p), 1)
        with self.assertRaises(ValueError):
            panel_minimum({"527": [1, 2, 3, 4], "528": [1, 2, 3, 4]})

    def test_source_provenance_and_crosswalk_mutation(self):
        mutations = [
            (0, lambda x: x["april"].update(sha256="0" * 64)),
            (0, lambda x: x["april_rows"][1].update(nodal_period_min="94.0")),
            (0, lambda x: x["limits"].update(date_is_orbital_epoch=True)),
            (1, lambda x: x["source"].update(ntrs_id="19630012129")),
            (1, lambda x: x["rows"][1].update(norad_crosswalk=529)),
            (1, lambda x: x["rows"][1].update(period_min="93.8")),
            (1, lambda x: x["limits"].update(independent_sensor_observation=True)),
            (2, lambda x: x["sources"][0].update(sha256="f" * 64)),
            (2, lambda x: x["sources"][0]["rows"][2].update(period_min="94.9")),
            (2, lambda x: x["data_lineage"].update(measurement_uncertainty_sigma=0.001)),
            (3, lambda x: x["rows"][1].update(nodal_period_min="93.2")),
            (3, lambda x: x["limits"].update(publication_date_is_element_epoch=True)),
            (3, lambda x: x["source"].update(printed_page=7)),
        ]
        for idx, fn in mutations:
            docs = copy.deepcopy(DOCS)
            fn(docs[idx])
            with self.subTest(idx=idx, mutation=str(fn)), self.assertRaises(ValueError):
                build(tuple(docs))

    def test_report_and_proof_reproduced_exactly(self):
        r = build(DOCS)
        self.assertEqual(json.loads(REPORT.read_text()), r)
        self.assertEqual(LEAN.read_text(), render_lean(r))
        self.assertIn("shared_edition_model_needs_twenty", LEAN.read_text())
        self.assertIn("all_twelve_cells_attain_twenty", LEAN.read_text())
        self.assertNotIn("sorry", LEAN.read_text())
        self.assertNotIn("axiom ", LEAN.read_text())
        self.assertEqual(r["physical_admissible_domain"], "THETA_UNCHANGED")
        self.assertIsNone(r["actual_tracking_epoch_utc"])
        self.assertIsNone(r["instrument_sigma"])
        self.assertEqual(r["independent_instrument_samples_added"], 0)


if __name__ == "__main__":
    unittest.main()
