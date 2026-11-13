"""C241-P18: source-locked exact minimax deletion and certificate tests."""
from __future__ import annotations

import copy
import json
import unittest

from formal.scripts import compile_ssr_four_editions as source
from formal.scripts import compile_ssr_influence as model

DOCS = tuple(json.loads(path.read_text()) for path in source.LEDGERS)


class TestSsrSourceInfluence(unittest.TestCase):
    def test_source_locked_exact_sensitivity(self):
        r = model.build(DOCS)
        self.assertEqual(r["complete_panel"]["radius_centiminute"], 20)
        self.assertEqual(
            {k: v["radius_centiminute"]
             for k, v in r["leave_one_edition_out"].items()},
            {"1963-04-30": 10, "1963-06-30": 20,
             "1963-07-31": 20, "1963-08-15": 13},
        )
        self.assertEqual(
            {k: v["radius_centiminute"]
             for k, v in r["leave_one_object_out"].items()},
            {"527": 8, "528": 13, "529": 20},
        )
        self.assertEqual(r["physical_admissible_domain"], "THETA_UNCHANGED")
        self.assertIsNone(r["instrument_sigma"])
        self.assertFalse(r["publication_date_is_instrument_epoch"])
        self.assertEqual(r["independent_instrument_observations_added"], 0)

    def test_every_certificate_and_strict_below_failure(self):
        r = model.build(DOCS)
        cases = ([r["complete_panel"]] +
                 list(r["leave_one_edition_out"].values()) +
                 list(r["leave_one_object_out"].values()))
        for case in cases:
            e = case["radius_centiminute"]
            w = case["witness"]
            self.assertIsNone(
                model.fit_at_radius(r["printed_period_by_object"],
                                    tuple(case["objects"]), tuple(case["editions"]), e-1)
                if e else None
            )
            self.assertIsNotNone(model.fit_at_radius(
                r["printed_period_by_object"],
                tuple(case["objects"]), tuple(case["editions"]), e))
            for obj in case["objects"]:
                for j, edition in enumerate(case["editions"]):
                    self.assertEqual(
                        r["printed_period_by_object"][obj][edition],
                        w["baselines"][obj] + w["edition_biases"][j]
                        + w["residuals"][obj][j],
                    )
                    self.assertLessEqual(abs(w["residuals"][obj][j]), e)

    def test_permutation_invariance_and_negative_control(self):
        p = {"527": [100, 100, 100, 100],
             "528": [98, 98, 98, 98],
             "529": [90, 90, 90, 90]}
        self.assertEqual(model.minimum(p, model.OBJECTS, (0, 1, 2, 3))
                         ["radius_centiminute"], 0)
        p["528"][-1] = 94
        self.assertEqual(model.minimum(p, model.OBJECTS, (0, 1, 2, 3))
                         ["radius_centiminute"], 1)
        r = model.build(DOCS)
        full = r["printed_period_by_object"]
        for cases in ((("529", "527", "528"), (3, 1, 0, 2)),
                      (("528", "529", "527"), (2, 3, 1, 0))):
            self.assertEqual(model.minimum(full, *cases)["radius_centiminute"], 20)

    def test_source_mutations_fail_closed(self):
        mutations = [
            (0, lambda doc: doc["april"].update(sha256="0" * 64)),
            (0, lambda doc: doc["april_rows"][1].update(nodal_period_min="94.0")),
            (1, lambda doc: doc["rows"][1].update(norad_crosswalk=529)),
            (2, lambda doc: doc["data_lineage"].update(
                measurement_uncertainty_sigma=0.01)),
            (3, lambda doc: doc["source"].update(printed_page=1)),
            (3, lambda doc: doc["limits"].update(
                publication_date_is_element_epoch=True)),
        ]
        for idx, mutate in mutations:
            docs = copy.deepcopy(DOCS)
            mutate(docs[idx])
            with self.subTest(idx=idx), self.assertRaises(ValueError):
                model.build(tuple(docs))

    def test_generator_and_parent_check(self):
        r = model.build(DOCS)
        self.assertEqual(json.loads(model.REPORT.read_text()), r)
        self.assertEqual(model.LEAN.read_text(), model.render_lean(r))
        self.assertNotIn("sorry", model.LEAN.read_text())
        self.assertNotIn("axiom ", model.LEAN.read_text())
        self.assertIn("without_april_attains_ten", model.LEAN.read_text())
        self.assertIn("without_august_attains_thirteen", model.LEAN.read_text())
        model.run(check=True)


if __name__ == "__main__":
    unittest.main()
