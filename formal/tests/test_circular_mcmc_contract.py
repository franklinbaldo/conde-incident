"""Finite exact controls for the Lean circular MCMC structural contract.

These are independent arithmetic cross-checks, not 1963 observations or an
implementation of a posterior sampler.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def accepted_mass(src_weight: int, dst_weight: int, proposal: int) -> Fraction:
    if not 0 < src_weight or not 0 < dst_weight or proposal < 0:
        raise ValueError("positive target weights and nonnegative proposal required")
    return src_weight * proposal * min(Fraction(1), Fraction(dst_weight, src_weight))


def circular_residual(y: int, h: int, theta: int, bias: int) -> int:
    return (y - h - theta - bias) % 360_000


class CircularMCMCFormalContract(unittest.TestCase):
    def test_symmetric_metropolis_flow_equals_exact_min(self):
        for w_i, w_j, q in product(range(1, 8), range(1, 8), range(5)):
            with self.subTest(w_i=w_i, w_j=w_j, q=q):
                exact = Fraction(min(w_i, w_j) * q)
                self.assertEqual(accepted_mass(w_i, w_j, q), exact)
                self.assertEqual(accepted_mass(w_j, w_i, q), exact)

    def test_asymmetric_proposals_are_not_reversible_by_simple_ratio(self):
        self.assertNotEqual(accepted_mass(2, 2, 3), accepted_mass(2, 2, 1))

    def test_group_gauge_on_modular_grid_and_wrap(self):
        rows = [(4, 120, 200_000), (5, -1, 359_999), (4, 200, -1)]
        offsets = {4: 7_000, 5: -8_000}
        for theta, delta in product((-360_000, -1, 0, 1, 359_999),
                                    (-720_000, -3, 0, 3, 720_000)):
            reference = [circular_residual(y, h, theta, offsets[g])
                         for g, y, h in rows]
            gauge = [circular_residual(y, h, theta + delta, offsets[g] - delta)
                     for g, y, h in rows]
            self.assertEqual(reference, gauge)
        self.assertNotEqual(circular_residual(0, 0, 1, 0),
                            circular_residual(0, 0, 0, 0))

    def test_lean_module_is_registered_for_compilation_and_axiom_audit(self):
        module = (ROOT / "formal/Conde1963/CircularMCMC.lean").read_text()
        aggregator = (ROOT / "formal/Conde1963.lean").read_text()
        axiom_audit = (ROOT / "formal/Conde1963/CoreAxioms.lean").read_text()
        self.assertIn("import Conde1963.CircularMCMC", aggregator)
        self.assertIn("import Conde1963.CircularMCMC", axiom_audit)
        theorem_names = (
            "acceptedFlow_detailed_balance", "acceptedFlow_list_balance",
            "asymmetric_proposal_counterexample", "residual_gauge_invariant",
            "residualVector_gauge_invariant", "likelihood_gauge_invariant",
            "fixed_bias_can_break_gauge", "unanchored_phase_has_compensator",
        )
        for name in theorem_names:
            self.assertIn("theorem " + name, module)
            self.assertIn("#print axioms Conde1963.CircularMCMC." + name, axiom_audit)
        self.assertNotIn("sorry", module)
        self.assertNotIn("axiom ", module)


if __name__ == "__main__":
    unittest.main()
