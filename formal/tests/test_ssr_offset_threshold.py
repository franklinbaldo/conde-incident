"""Adversarial source custody and exact minimax robustness of C241-P13."""
import copy
import json
import unittest

from formal.scripts.compile_ssr_offset_threshold import (
    NOV, OCT, SUR, DEC, GRAPH, REPORT, LEAN, build, minimax_radius, render_lean,
)

ORIGINALS = [json.loads(x.read_text()) for x in (NOV, OCT, SUR, DEC, GRAPH)]


class TestOffsetThreshold(unittest.TestCase):
    def test_exact_minimax_with_attaining_witness(self):
        r = build(*ORIGINALS)
        self.assertEqual(r["printed_object_differences_centimin"], [200, 240, 300])
        self.assertEqual(r["exact_minimum_uniform_residual_centimin"], 25)
        self.assertEqual(r["minimum_to_half_unit_factor"], 5)
        self.assertFalse(r["active_physical_constraint"])
        self.assertIsNone(r["instrument_epoch_utc"])
        self.assertFalse(r["independent_tracking_sensors"])
        self.assertEqual(r["admissible_domain"], "THETA_UNCHANGED")
        w = r["attaining_witness"]
        for obj in ("527", "529"):
            for j, center in enumerate(r["printed_period_centimin"][obj]):
                residual = w[f"residual_{obj}_centimin"][j]
                self.assertLessEqual(abs(residual), 25)
                self.assertEqual(center, w[f"base_{obj}_centimin"] +
                                 w["shared_edition_bias_centimin"][j] + residual)

    def test_negative_controls_and_integer_boundaries(self):
        self.assertEqual(minimax_radius({"527": [10, 10, 10], "529": [8, 8, 8]}), 0)
        self.assertEqual(minimax_radius({"527": [10, 10, 10], "529": [8, 7, 6]}), 1)
        self.assertEqual(minimax_radius({"527": [10, 10], "529": [10, 5]}), 2)
        self.assertEqual(minimax_radius({"527": [9460]*3, "529": [9260, 9220, 9180]}), 20)
        for bad in ({"527": [1], "529": [1]}, {"527": [1, 2], "529": [1]},
                    {"527": [1, True], "529": [1, 2]}):
            with self.assertRaises(ValueError):
                minimax_radius(bad)

    def test_source_hash_and_cell_tampering_is_rejected(self):
        for pos, mutator in (
            (0, lambda x: x["documents"][0].update(sha256="0"*64)),
            (0, lambda x: x["documents"][0]["rows"][1].update(period_min="92.7")),
            (3, lambda x: x["rows"][1].update(period_min="91.5")),
            (3, lambda x: x["source"].update(sha256="a"*64)),
            (3, lambda x: x["limits"].update(instrumental_epoch_utc="1963-12-15T12:00Z")),
        ):
            docs = copy.deepcopy(ORIGINALS)
            mutator(docs[pos])
            with self.subTest(pos=pos), self.assertRaises(ValueError):
                build(*docs)

    def test_deterministic_generated_proof_and_no_unchecked_axioms(self):
        r = build(*ORIGINALS)
        self.assertEqual(json.loads(REPORT.read_text()), r)
        self.assertEqual(LEAN.read_text(), render_lean(r))
        self.assertIn("theorem shared_edition_bias_requires_25_centimin", LEAN.read_text())
        self.assertIn("theorem all_six_editions_attain_25_centimin", LEAN.read_text())
        self.assertNotIn("sorry", LEAN.read_text())
        self.assertNotIn("axiom ", LEAN.read_text())


if __name__ == "__main__":
    unittest.main()
