"""C241-P20: exact minimax, nine documentary editions and adversarial locks."""
from __future__ import annotations

import copy
import json
import unittest

from formal.scripts import compile_ssr_nine_editions as m
from tools import tle_ssr_editions_precision_audit as audit


class NineEditionMinimaxTests(unittest.TestCase):
    def test_all_twenty_three_print_cells_and_certificates(self):
        result = m.build()
        self.assertEqual(result["minimum_uniform_error_centiminute"], 128)
        self.assertEqual(result["minimum_uniform_error_seconds"], "76.8")
        self.assertEqual(len(result["sources"]), 9)
        self.assertEqual(len(result["printed_rows"]), 23)
        self.assertEqual(result["certifying_contrast"]["printed_gap_centiminute"], [30, 540])
        cells, _ = m.source_rows()
        self.assertIsNone(m.feasible(cells, 127))
        self.assertIsNotNone(m.feasible(cells, 128))
        witness = result["attaining_witness"]
        for r in result["printed_rows"]:
            o, d, y = r["object"], r["publication"], r["period_centiminute"]
            err = r["residual_centiminute"]
            self.assertEqual(y, witness["object_baselines_centiminute"][o]
                             + witness["edition_offsets_centiminute"][d] + err)
            self.assertLessEqual(abs(err), 128)
        self.assertTrue(result["dec31_528_absent_not_zero"])
        self.assertIsNone(result["tracking_epochs"])
        self.assertIsNone(result["sensor_sigma"])
        self.assertEqual(result["physical_domain"], "THETA_UNCHANGED")
        self.assertEqual(result["independent_instrument_observations_added"], 0)

    def test_generic_solver_not_hardwired_to_128(self):
        additive = {(527, "d1"): 10, (529, "d1"): 8,
                    (527, "d2"): 14, (529, "d2"): 12}
        self.assertEqual(m.minimize(additive)[0], 0)
        additive[529, "d2"] = 8
        self.assertEqual(m.minimize(additive)[0], 1)
        self.assertIsNone(m.feasible(additive, 0))

    def test_mutations_of_source_or_calibration_fail_closed(self):
        model = audit.read(audit.MODEL)
        ledgers = {d["ledger"]: audit.read(d["ledger"]) for d in model["docs"]}
        decay = audit.read(audit.DECAY)
        cases = [
            lambda mo, le: mo["docs"][0].update(pdf_sha256="0" * 64),
            lambda mo, le: mo["docs"][8].update(ntrs="19000000000"),
            lambda mo, le: mo["docs"][5].update(published="1963-11-16"),
            lambda mo, le: mo.update(report_rounding_rule_verified=True),
            lambda mo, le: mo.update(raw_instrument_528_sigma="0.05"),
            lambda mo, le: mo["graph"].update(physical_constraints_active=1),
            lambda mo, le: le[mo["docs"][8]["ledger"]]["sources"][1]["rows"][1].update(period_min="89.3"),
            lambda mo, le: le[mo["docs"][0]["ledger"]]["april_rows"][0].update(nodal_period_min="94.7"),
        ]
        for n, f in enumerate(cases):
            mo, le = copy.deepcopy(model), copy.deepcopy(ledgers)
            try:
                f(mo, le)
            except (IndexError, KeyError) as e:
                self.fail(f"test mutation {n} does not target a real source row: {e}")
            with self.subTest(case=n), self.assertRaises(ValueError):
                m.build(mo, le, decay)

    def test_lean_and_report_exact_replay(self):
        result = m.build()
        self.assertEqual(json.loads(m.REPORT.read_text()), json.loads(json.dumps(result)))
        lean = m.LEAN.read_text()
        self.assertEqual(lean, m.render_lean(result))
        self.assertIn("nine_edition_lower_bound", lean)
        self.assertIn("nine_edition_witness", lean)
        self.assertNotIn("sorry", lean)
        self.assertNotIn("axiom ", lean)


if __name__ == "__main__":
    unittest.main()
