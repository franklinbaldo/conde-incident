"""Exact structural checks and conditional sensitivity; NO historical posterior."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_lineage_identifiability import (
    build_report, design_effect, matrix_rank_exact, phase_prediction,
    row_for_object, wrap_deg,
)

class GaugeAndLineageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / "research/statistics/raan_527_528_529_1963.json").read_bytes()
        cls.frozen = (ROOT / "research/statistics/raan_chronological_holdout_1963.json").read_bytes()
        cls.report = build_report(cls.raw, cls.frozen)

    def test_real_frozen_membership_and_exact_gauge_rank(self):
        r = self.report
        self.assertEqual(
            [r["per_split"][s]["unique_catalogue_epochs"]
             for s in ("fit", "validation", "evaluation")], [61, 23, 35]
        )
        for s in ("fit", "validation", "evaluation"):
            t = r["per_split"][s]
            self.assertEqual(t["exact_rational_rank"], 3)
            self.assertEqual(t["rank_deficiency"], 1)
            self.assertEqual(t["null_direction"], [1, 1, 1, -1])
        self.assertEqual(r["posterior_mcmc_status"], "NOT_RUN")
        self.assertEqual(r["prior_status"], "NOT_SPECIFIED")

    def test_exact_linear_algebra_and_anchor_removes_gauge(self):
        rows = [row_for_object(o) for o in ("527", "528", "529")]
        self.assertEqual(matrix_rank_exact(rows), 3)
        self.assertEqual(matrix_rank_exact(rows + [(0, 0, 0, 1)]), 4)
        self.assertEqual(matrix_rank_exact([rows[0]] * 61), 1)
        with self.assertRaisesRegex(ValueError, "ragged"):
            matrix_rank_exact([(1, 2), (3,)])

    def test_common_rotation_is_unidentifiable_on_circle(self):
        for a in (-720, -181.3, -90, 0, 90, 359.7, 720):
            for phase, dynamics in ((359.9, 0.2), (0.2, -45), (120.5, 140)):
                b = 15
                x = phase_prediction(phase, b, dynamics)
                y = phase_prediction(phase+a, b-a, dynamics)
                self.assertAlmostEqual(x, y, places=10)
        self.assertAlmostEqual(wrap_deg(360.1), 0.1)
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            wrap_deg(float("nan"))

    def test_correlation_design_effect_is_exact_and_not_mcmc_ess(self):
        self.assertEqual(design_effect(61, Fraction(0))["n_effective_scalar_mean"], "61")
        self.assertEqual(design_effect(61, Fraction(1,10))["n_effective_scalar_mean"], "61/7")
        self.assertEqual(design_effect(61, Fraction(1,2))["n_effective_scalar_mean"], "61/31")
        self.assertEqual(design_effect(1, Fraction(9,10))["n_effective_scalar_mean"], "1")
        for n in (1, 15, 24, 22, 61):
            vals = [Fraction(design_effect(n,r)["n_effective_scalar_mean"])
                    for r in (Fraction(0), Fraction(1,10), Fraction(1,2), Fraction(9,10))]
            self.assertEqual(vals, sorted(vals, reverse=True))

    def test_bad_illustrative_correlation_fails_closed(self):
        for n, rho in ((0, Fraction(0)), (3, Fraction(-1,10)),
                       (3, Fraction(1)), (True, Fraction(0))):
            with self.subTest(n=n, rho=rho), self.assertRaises(ValueError):
                design_effect(n, rho)
        with self.assertRaises(ValueError):
            row_for_object("530")

    def test_malformed_source_and_changed_frozen_split_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "mismatch"):
            build_report(self.raw + b" ", self.frozen)
        m = json.loads(self.frozen)
        m["memberships"]["527"]["fit"].pop()
        with self.assertRaisesRegex(ValueError, "mismatch"):
            build_report(self.raw, json.dumps(m).encode())

    def test_source_lineage_assertion_prevents_false_independence(self):
        data = json.loads(self.raw)
        data["provenance"]["lineage"] = "independent sensors"
        with self.assertRaises(ValueError):
            build_report(json.dumps(data).encode(), self.frozen)

    def test_byte_for_byte_manifest_replay(self):
        path = ROOT / "research/statistics/raan_lineage_identifiability_1963.json"
        expected = json.dumps(self.report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        self.assertEqual(expected.encode(), path.read_bytes())
        self.assertEqual(self.report["historical_likelihood_status"], "NOT_CALIBRATED")
        self.assertEqual(self.report["physical_domain_reduction"], "NOT_COMPUTED")

if __name__ == "__main__":
    unittest.main()
