"""C241-P21: publication-deletion robustness and adversarial source locks."""
from __future__ import annotations
import copy
from itertools import combinations
import json
import unittest
from formal.scripts import compile_ssr_edition_survivors as m
from formal.scripts import compile_ssr_nine_editions as p
from tools import tle_ssr_editions_precision_audit as audit


class EditionSurvivorTests(unittest.TestCase):
    def test_maximum_subset_and_witness(self):
        r = m.build()
        self.assertEqual(len(r["sources"]), 9)
        self.assertEqual(r["maximum_retained_editions"], 2)
        self.assertEqual(r["min_removed_editions"], 7)
        self.assertEqual(r["pairs_passing_527_529_screen"], [
            ["1963-06-30", "1963-07-31"],
            ["1963-06-30", "1963-08-15"],
            ["1963-07-31", "1963-08-15"],
        ])
        self.assertEqual(r["exact_feasible_pairs"], [["1963-06-30", "1963-07-31"]])
        self.assertEqual(r["exact_feasible_triples"], [])
        self.assertEqual(len(r["witness"]["residuals"]), 6)
        for row in r["witness"]["residuals"]:
            self.assertEqual(row["printed"], r["witness"]["baselines"][row["object"]]
                             + r["witness"]["offsets"][row["publication"]]
                             + row["residual"])
            self.assertLessEqual(abs(row["residual"]), 5)
        self.assertIsNone(r["instrument_epochs"])
        self.assertIsNone(r["instrument_sigma"])
        self.assertEqual(r["physical_domain"], "THETA_UNCHANGED")

    def test_contrast_bound_independent_of_solver(self):
        cells, _ = p.source_rows()
        days = sorted({d for _, d in cells})
        for a, b in combinations(days, 2):
            if p.feasible(m.subcells(cells, (a, b)), 5):
                self.assertTrue(all(abs(x["change"]) <= 20
                                    for x in m.pair_screens(cells, a, b)))
        self.assertTrue(any(abs(x["change"]) > 20
                            for x in m.pair_screens(cells, days[0], days[-1])))
        self.assertIsNone(p.feasible(cells, 5))
        self.assertIsNotNone(p.feasible(cells, 128))

    def test_mutations_rejected(self):
        model = audit.read(audit.MODEL)
        ledgers = {d["ledger"]: audit.read(d["ledger"]) for d in model["docs"]}
        decay = audit.read(audit.DECAY)
        for mutate in (
            lambda mo: mo["docs"][0].update(pdf_sha256="0" * 64),
            lambda mo: mo["docs"][3].update(published="1963-08-16"),
            lambda mo: mo.update(raw_instrument_528_sigma="0.05"),
            lambda mo: mo["graph"].update(physical_constraints_active=1),
        ):
            changed = copy.deepcopy(model)
            mutate(changed)
            with self.assertRaises(ValueError):
                m.build(changed, copy.deepcopy(ledgers), decay)

    def test_generated_outputs_are_source_locked(self):
        r = m.build()
        self.assertEqual(json.loads(m.REPORT.read_text()), json.loads(json.dumps(r)))
        lean = m.LEAN.read_text()
        self.assertEqual(lean, m.render_lean(r))
        self.assertIn("no_three_screened", lean)
        self.assertIn("june_july_attaining_witness", lean)
        self.assertNotIn("sorry", lean)
        self.assertNotIn("axiom ", lean)


if __name__ == "__main__":
    unittest.main()
