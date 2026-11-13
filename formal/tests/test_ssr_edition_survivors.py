"""C241-P21: publication-deletion robustness and adversarial source locks."""
from __future__ import annotations
import copy
from itertools import combinations
import json
import unittest
from formal.scripts import compile_ssr_edition_survivors as m
from formal.scripts import compile_ssr_jackknife as jackknife
from formal.scripts import compile_un_ssr_cross_compilation as unx
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

    def test_c241_p22_jackknife_ci_gate(self):
        # This test is invoked by the existing pinned P21 workflow step.
        result = jackknife.build()
        self.assertEqual(len(result['delete_one']), 9)
        self.assertEqual(json.loads(jackknife.REPORT.read_text()), result)
        self.assertEqual(jackknife.LEAN.read_text(), jackknife.render_lean(result))
        self.assertEqual([r['minimum_residual_centiminute']
                          for r in result['delete_one']],
                         [120, 128, 128, 128, 128, 128, 128, 128, 68])

    def test_c241_p23_cross_agency_un_cutoff_and_nasa(self):
        result = unx.build()
        self.assertEqual(len(result['printed_period_cells']), 26)
        self.assertEqual(result['minimum_uniform_residual_centiminute'], 135)
        self.assertEqual(result['contrasting_cells']['gaps_centiminute'], [0, 540])
        self.assertEqual(result['prior_nasa_only_minimum_centiminute'], 128)
        self.assertFalse(result['un_cutoff_is_publication'])
        self.assertFalse(result['un_cutoff_is_tracking_epoch'])
        self.assertEqual(result['new_instrument_observations'], 0)
        self.assertEqual(result['physical_domain'], 'THETA_UNCHANGED')
        self.assertEqual(json.loads(unx.REPORT.read_text()), result)
        self.assertEqual(unx.LEAN.read_text(), unx.render_lean(result))
        cells, _ = unx.source_rows()
        self.assertIsNone(p.feasible(cells, 134))
        self.assertIsNotNone(p.feasible(cells, 135))

    def test_c241_p23_un_source_mutations_fail_closed(self):
        source = json.loads(unx.UN.read_text())
        for mutate in (
            lambda u: u['docs'][0]['printed_rows'][2].update(nodal_period_min_printed='89.6'),
            lambda u: u['docs'][0]['printed_rows'][1].update(norad_from_nasa_1977=529),
            lambda u: u['docs'][0].update(document_day='1963-01-31'),
            lambda u: u['docs'][0].update(sha256='0' * 64),
            lambda u: u['interpretation'].update(un_cutoff_is_sensor_epoch=True),
            lambda u: u['interpretation'].update(independent_sensor_observations_added=1),
            lambda u: u['interpretation'].update(physical_constraints_activated=1),
        ):
            altered = copy.deepcopy(source)
            mutate(altered)
            with self.assertRaises(ValueError):
                unx.build(altered)

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
