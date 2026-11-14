"""Independent exact-arithmetic adversarial checks of the finite Hastings kernel.

Everything here is synthetic. No NORAD observation, convergence claim, or
historical orbital posterior follows from stationary mass transport.
"""
from itertools import product
from pathlib import Path
from fractions import Fraction
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "formal/Conde1963/HastingsKernel.lean"
SOURCE = ROOT / "formal/Conde1963.lean"
AXIOMS = ROOT / "formal/Conde1963/CoreAxioms.lean"
WORKFLOW = ROOT / ".github/workflows/lean-core.yml"


def kernel(weights, proposals, denominator):
    n = len(weights)
    if denominator <= 0 or n == 0 or any(w <= 0 for w in weights):
        raise ValueError("positive weights and denominator are required")
    if len(proposals) != n or any(
        len(row) != n or any(not isinstance(q, int) or q < 0 for q in row)
        or sum(row) != denominator
        for row in proposals
    ):
        raise ValueError("nonnegative proposal counts and common row sum required")

    flows = [[min(weights[i] * proposals[i][j],
                  weights[j] * proposals[j][i]) for j in range(n)]
             for i in range(n)]
    held = [weights[i] * denominator - sum(flows[i]) for i in range(n)]
    if min(held) < 0:
        raise AssertionError("negative rejection mass")
    transported = [[flows[i][j] + (held[i] if i == j else 0)
                    for j in range(n)] for i in range(n)]
    probabilities = [
        [Fraction(x, weights[i] * denominator) for x in transported[i]]
        for i in range(n)
    ]
    return flows, held, transported, probabilities


class FiniteHastingsContract(unittest.TestCase):
    def assert_stationary(self, weights, proposals, denominator):
        flows, held, transported, probabilities = kernel(
            weights, proposals, denominator
        )
        n = len(weights)
        self.assertTrue(all(x >= 0 for x in held))
        self.assertTrue(all(
            sum(transported[i]) == weights[i] * denominator
            for i in range(n)
        ))
        self.assertTrue(all(
            sum(transported[j][i] for j in range(n))
            == weights[i] * denominator for i in range(n)
        ))
        self.assertTrue(all(
            transported[i][j] == transported[j][i]
            for i in range(n) for j in range(n)
        ))
        self.assertTrue(all(sum(row) == 1 for row in probabilities))
        total_weight = sum(weights)
        self.assertTrue(all(
            sum(Fraction(weights[j], total_weight) * probabilities[j][i]
                for j in range(n)) == Fraction(weights[i], total_weight)
            for i in range(n)
        ))
        return flows, held, transported

    def test_exact_asymmetric_two_state_and_self_loops(self):
        flow, held, transported = self.assert_stationary(
            [2, 1], [[1, 3], [1, 3]], 4
        )
        self.assertEqual(flow, [[2, 1], [1, 3]])
        self.assertEqual(held, [5, 0])
        self.assertEqual(transported, [[7, 1], [1, 3]])

    def test_exhaustive_two_state_denominator_four(self):
        for w0, w1, q0, q1 in product(range(1, 5), range(1, 5),
                                      range(5), range(5)):
            with self.subTest(w=(w0, w1), q=(q0, q1)):
                self.assert_stationary(
                    [w0, w1], [[q0, 4-q0], [q1, 4-q1]], 4
                )

    def test_three_state_asymmetric_missing_reverse(self):
        flow, held, _ = self.assert_stationary(
            [1, 3, 2],
            [[1, 3, 0], [0, 2, 2], [1, 0, 3]], 4
        )
        self.assertEqual(flow[0][1], 0)
        self.assertEqual(flow[1][0], 0)
        self.assertGreaterEqual(held[0], 0)

    def test_rejects_noncommon_denominator_and_negative_counts(self):
        for matrix in (
            [[1, 3], [1, 2]], [[1, 3], [-1, 5]], [[1, 3], [1]],
        ):
            with self.subTest(matrix=matrix):
                with self.assertRaises(ValueError):
                    kernel([2, 1], matrix, 4)
        with self.assertRaises(ValueError):
            kernel([2, 0], [[1, 3], [1, 3]], 4)
        with self.assertRaises(ValueError):
            kernel([2, 1], [[1, 3], [1, 3]], 0)

    def test_registered_lean_proofs_and_real_ci_gate(self):
        module = MODULE.read_text()
        main = SOURCE.read_text()
        audit = AXIOMS.read_text()
        ci = WORKFLOW.read_text()
        self.assertIn("import Conde1963.HastingsKernel", main)
        self.assertIn("import Conde1963.HastingsKernel", audit)
        self.assertIn("test_finite_hastings_kernel.py", ci)
        for name in (
            "acceptedRow_le_capacity", "fullTransport_row_conservation",
            "fullTransport_detailed_balance", "fullTransport_stationary",
            "twoState_rows_equal_four", "twoState_rejections_checked",
        ):
            self.assertIn("theorem " + name, module)
            self.assertIn(
                "#print axioms Conde1963.CircularMCMC." + name, audit
            )
        self.assertNotIn("sorry", module)
        self.assertNotIn("axiom ", module)


if __name__ == "__main__":
    unittest.main()
