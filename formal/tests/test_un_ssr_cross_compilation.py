"""C241-P23: enforce UN↔NASA source custody and conditional model boundaries.

The UN January 31 date is an administrative cutoff, not an instrument epoch.
This tests a printed-data model, never a calibrated physical constraint.
"""
from __future__ import annotations

import copy
import json
import unittest

from formal.scripts import compile_un_ssr_cross_compilation as cross


class UnSsrCrossCompilationTests(unittest.TestCase):
    def setUp(self):
        self.un = json.loads(cross.UN.read_text(encoding="utf-8"))

    def test_exact_replay_and_documentary_limits(self):
        result = cross.build()
        self.assertEqual(result["id"], "C241-P23")
        self.assertEqual(len(result["printed_period_cells"]), 26)
        self.assertEqual(len(result["nasa_sources"]), 9)
        self.assertEqual(result["minimum_uniform_residual_centiminute"], 135)
        self.assertEqual(result["prior_nasa_only_minimum_centiminute"], 128)
        self.assertEqual(result["added_threshold_centiminute"], 7)
        self.assertFalse(result["un_cutoff_is_publication"])
        self.assertFalse(result["un_cutoff_is_tracking_epoch"])
        self.assertFalse(result["source_families_are_independent_sensors"])
        self.assertFalse(result["cross_agency_printing_convention_validated"])
        self.assertIsNone(result["instrument_covariances"])
        self.assertIsNone(result["instrument_epochs"])
        self.assertEqual(result["new_instrument_observations"], 0)
        self.assertEqual(result["physical_domain"], "THETA_UNCHANGED")
        witness = result["attaining_witness"]
        self.assertEqual(witness["max_abs_residual"], 135)
        for row in result["printed_period_cells"]:
            predicted = (witness["baselines"][str(row["object"])]
                         + witness["document_offsets"][row["document_or_cutoff"]]
                         + row["residual_centiminute"])
            self.assertEqual(row["period_centiminute"], predicted)
            self.assertLessEqual(abs(row["residual_centiminute"]), 135)
        self.assertEqual(json.loads(cross.REPORT.read_text()), result)
        self.assertEqual(cross.LEAN.read_text(), cross.render_lean(result))
        self.assertIn("cross_agency_lower_bound", cross.LEAN.read_text())
        self.assertIn("cross_agency_attaining_witness", cross.LEAN.read_text())
        self.assertNotIn("sorry", cross.LEAN.read_text())

    def test_adversarial_un_source_mutations_fail_closed(self):
        cases = [
            lambda x: x["docs"][0].update(sha256="0" * 64),
            lambda x: x["docs"][0].update(document_day="1963-01-31"),
            lambda x: x["docs"][0].update(report_cutoff_printed="1963-03-13"),
            lambda x: x["docs"][0].update(relevant_pdf_page_index=2),
            lambda x: x["docs"][0]["printed_rows"][0].update(nodal_period_min_printed="94.8"),
            lambda x: x["docs"][0]["printed_rows"][1].update(printed_designator="1963-3-C"),
            lambda x: x["interpretation"].update(un_cutoff_is_sensor_epoch=True),
            lambda x: x["interpretation"].update(physical_constraints_activated=1),
            lambda x: x["interpretation"].update(independent_sensor_observations_added=1),
        ]
        for i, mutate in enumerate(cases):
            doc = copy.deepcopy(self.un)
            mutate(doc)
            with self.subTest(case=i), self.assertRaises(ValueError):
                cross.build(un=doc)

    def test_nasa_source_corruption_is_not_hidden_by_crossagency_witness(self):
        from tools import tle_ssr_editions_precision_audit as audit
        model = audit.read(audit.MODEL)
        # A syntactically valid but false NTRS pointer must not silently pass.
        model["docs"][0]["ntrs"] = "00000000000"
        with self.assertRaises(ValueError):
            cross.build(un=self.un, nasa_model=model)

    def test_solver_fails_below_sharp_limit(self):
        from formal.scripts import compile_ssr_nine_editions as nasa
        cells, _ = cross.source_rows(un=self.un)
        self.assertIsNone(nasa.feasible(cells, 134))
        self.assertIsNotNone(nasa.feasible(cells, 135))


if __name__ == "__main__":
    unittest.main()
