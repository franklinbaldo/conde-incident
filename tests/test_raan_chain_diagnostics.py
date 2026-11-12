"""Deterministic synthetic diagnostics; never claims a posterior for Conde."""
import math
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from raan_chain_diagnostics import diagnose_circular_chains, _rank_normalize
from statistics import NormalDist


class CircularChainDiagnosticsTests(unittest.TestCase):
    def test_four_mixed_chains_across_360_boundary(self):
        rng = random.Random(21963)
        chains = [[rng.gauss(359.5, 7.0) % 360.0 for _ in range(512)]
                  for _ in range(4)]
        result = diagnose_circular_chains(chains)
        self.assertTrue(result.passes_numerical_gate(), result)
        self.assertLess(result.worst_rhat, 1.01)
        self.assertGreater(result.minimum_bulk_ess, 400)
        self.assertGreater(result.minimum_tail_ess, 400)
        rotated = diagnose_circular_chains([[x + 360.0 for x in c] for c in chains])
        self.assertAlmostEqual(result.worst_rhat, rotated.worst_rhat, delta=1e-10)

    def test_stuck_chains_different_modes_fail_rhat(self):
        rng = random.Random(343)
        chains = [[(angle + rng.gauss(0, 1)) % 360 for _ in range(256)]
                  for angle in (5, 5, 175, 175)]
        result = diagnose_circular_chains(chains)
        self.assertGreater(result.worst_rhat, 1.1)
        self.assertFalse(result.passes_numerical_gate())

    def test_high_autocorrelation_depresses_ess(self):
        rng = random.Random(919)
        chains = []
        for _ in range(4):
            x = 0.0
            chain = []
            for _ in range(384):
                x = 0.995 * x + rng.gauss(0, 0.5)
                chain.append(80 + x)
            chains.append(chain)
        result = diagnose_circular_chains(chains)
        self.assertLess(result.minimum_bulk_ess, 400)
        self.assertFalse(result.passes_numerical_gate())

    def test_reject_short_ragged_nonfinite_or_constant(self):
        good = [[float(j) for j in range(48)] for _ in range(4)]
        for bad in (good[:3], [c[:16] for c in good],
                    good[:-1] + [good[-1][:-1]],
                    good[:-1] + [[float('nan')] + good[-1][1:]],
                    good[:-1] + [[True] + good[-1][1:]],
                    [[10.0]*48 for _ in range(4)]):
            with self.subTest(kind=str(bad)[:45]), self.assertRaises(ValueError):
                diagnose_circular_chains(bad)

    def test_rank_normal_scores_match_published_formula(self):
        # Vehtari et al. / Stan rank offset is S - 1/4, not S + 1/4.
        result = _rank_normalize([[1., 2.], [3., 4.]])
        s = 4
        nd = NormalDist()
        self.assertAlmostEqual(result[0][0], nd.inv_cdf((1 - 0.375)/(s - 0.25)))
        self.assertAlmostEqual(result[1][1], nd.inv_cdf((4 - 0.375)/(s - 0.25)))
        tied = _rank_normalize([[1., 1.], [3., 4.]])
        self.assertAlmostEqual(tied[0][0], tied[0][1])

    def test_no_historical_dataset_is_sampled(self):
        # This API ONLY reads explicit chains, no implicit historical posterior.
        with self.assertRaises(ValueError):
            diagnose_circular_chains([])


if __name__ == '__main__':
    unittest.main()
