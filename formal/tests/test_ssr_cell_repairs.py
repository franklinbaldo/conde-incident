"""C241-P19: source-lock and exact minimal repair falsification tests."""
from __future__ import annotations

import copy
import json
import unittest

from formal.scripts import compile_ssr_four_editions as source
from formal.scripts import compile_ssr_cell_repairs as model

DOCS = tuple(json.loads(path.read_text()) for path in source.LEDGERS)


class TestSsrCellRepairs(unittest.TestCase):
    def test_two_disjoint_original_violations_and_uniqueness(self):
        result = model.build(DOCS)
        rect = result["two_disjoint_contradiction_rectangles"]
        self.assertEqual([r["contrast_centiminute"] for r in rect], [-40, -30])
        self.assertTrue(set(map(tuple,rect[0]["indices"])).isdisjoint(
                        set(map(tuple,rect[1]["indices"]))))
        cert = result["exact_enumeration"]
        self.assertEqual(cert["minimum_exception_count"], 2)
        self.assertEqual(len(cert["optimal_sets"]), 1)
        self.assertEqual(cert["optimal_sets"][0]["excluded"], [[0, 0], [1, 3]])
        self.assertEqual(result["physical_admissible_domain"], "THETA_UNCHANGED")
        self.assertIsNone(result["instrument_sigma"])

    def test_all_zero_and_single_deletions_fail_independently(self):
        p = model.build(DOCS)["printed_period_by_object"]
        self.assertIsNone(model.fit(p, model.CELLS))
        for excluded in model.CELLS:
            keep = tuple(c for c in model.CELLS if c != excluded)
            with self.subTest(excluded=excluded):
                self.assertIsNone(model.fit(p, keep))

    def test_two_deletion_witness_exact_and_bounded(self):
        result = model.build(DOCS)
        cert = result["exact_enumeration"]["optimal_sets"][0]["witness"]
        self.assertEqual(len(cert["retained"]), 10)
        for cell in cert["retained"]:
            obj, j = cell["object"], cell["edition_index"]
            self.assertEqual(cell["printed_centiminute"],
                             cert["baselines"][obj]+cert["edition_offsets"][j]+
                             cell["residual_centiminute"])
            self.assertLessEqual(abs(cell["residual_centiminute"]), 5)

    def test_negative_control_fits_without_removal(self):
        p = {"527":[9460]*4, "528":[9410]*4, "529":[9390]*4}
        self.assertEqual(model.exhaustive_minimum(p)["minimum_exception_count"], 0)
        self.assertIsNotNone(model.fit(p, model.CELLS))

    def test_source_identity_and_epoch_mutations_rejected(self):
        for idx, mutate in (
            (0, lambda d: d["april"].update(sha256="0"*64)),
            (1, lambda d: d["rows"][1].update(norad_crosswalk=529)),
            (2, lambda d: d["data_lineage"].update(
                measurement_uncertainty_sigma=0.1)),
            (3, lambda d: d["limits"].update(publication_date_is_element_epoch=True)),
            (3, lambda d: d["rows"][1].update(nodal_period_min="93.2")),
        ):
            docs = copy.deepcopy(DOCS)
            mutate(docs[idx])
            with self.subTest(idx=idx), self.assertRaises(ValueError):
                model.build(tuple(docs))

    def test_locked_outputs_and_no_sorry(self):
        result = model.build(DOCS)
        self.assertEqual(json.loads(model.REPORT.read_text()), result)
        self.assertEqual(model.LEAN.read_text(), model.render_lean(result))
        self.assertNotIn("sorry", model.LEAN.read_text())
        self.assertNotIn("axiom ", model.LEAN.read_text())
        self.assertIn("no_single_print_cell_exception", model.LEAN.read_text())
        model.run(True)


if __name__ == "__main__":
    unittest.main()

# The required P19 CI step also audits P20 against the nine-edition source locks.
from formal.tests.test_ssr_nine_editions import NineEditionMinimaxTests
