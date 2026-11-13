"""Counterfactual third-epoch alias lattice and conditional robust design tests."""
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_527_third_epoch_design import (  # noqa: E402
    build, circular_distance_from_zero, design, rational_gcd,
)

SOURCE = ROOT / "research/statistics/raan_527_528_529_1963.json"
FROZEN = ROOT / "research/statistics/raan_chronological_holdout_1963.json"
REPORT = ROOT / "research/constraints/raan_527_third_epoch_design_C241.json"


class ThirdEpochDesignTests(unittest.TestCase):
    def test_exact_lattice_and_864_microsecond_tick(self):
        tick = Fraction(1, 100000000)
        self.assertEqual(rational_gcd((Fraction(1), Fraction(1)+tick)), tick)
        out = design(Fraction(1), Fraction(1)+tick)
        self.assertEqual(out["global_alias_spacing_deg_per_day_exact_noise_free"],
                         "36000000000/1")
        self.assertEqual(out["first_aliases_circular_discrimination_deg"][0],
                         "9/2500000")
        self.assertEqual(out["sufficient_per_angle_error_for_disjoint_candidate_bands_deg_strictly_below"],
                         "90/100000001")

    def test_alias_k_gcd_is_identical_at_all_three_times(self):
        for t2 in (Fraction(6, 5), Fraction(3, 2),
                   Fraction(100000001, 100000000)):
            quantum = rational_gcd((Fraction(1), t2))
            beta_change = Fraction(360) / quantum
            self.assertEqual(beta_change % 360, 0)
            self.assertEqual((beta_change*t2) % 360, 0)

    def test_half_day_observation_keeps_even_aliases(self):
        out = design(Fraction(1), Fraction(3, 2), 4)
        self.assertEqual(out["first_aliases_circular_discrimination_deg"],
                         ["180/1", "0/1", "180/1", "0/1"])
        self.assertFalse(out["first_k_all_distinguishable_exact"])
        self.assertIsNone(out["sufficient_per_angle_error_for_disjoint_candidate_bands_deg_strictly_below"])

    def test_one_fifth_day_discriminates_first_four_conditionally(self):
        out = design(Fraction(1), Fraction(6, 5), 4)
        self.assertEqual(out["first_aliases_circular_discrimination_deg"],
                         ["72/1", "144/1", "144/1", "72/1"])
        self.assertEqual(out["global_alias_spacing_deg_per_day_exact_noise_free"], "1800/1")
        self.assertEqual(out["bounded_error_residual_factor"], "12/5")
        self.assertEqual(out["sufficient_per_angle_error_for_disjoint_candidate_bands_deg_strictly_below"], "15/1")
        self.assertTrue(out["first_k_all_distinguishable_exact"])

    def test_pigeonhole_bound_for_first_k_aliases(self):
        # Any K+1 circle points 0,r,...,K*r have a pair separated <=1/(K+1).
        # r=1+1/(K+1) attains this upper bound for the FIRST K branches.
        for k in (1, 2, 3, 4, 9):
            r = Fraction(1) + Fraction(1, k+1)
            minimum = min(circular_distance_from_zero(360*j*r)
                          for j in range(1, k+1))
            self.assertEqual(minimum, Fraction(360, k+1))
            self.assertEqual(design(Fraction(1), r, k)["min_discrimination_first_k_deg"],
                             f"{minimum.numerator}/{minimum.denominator}")

    def test_no_unknown_instrumental_epsilon_is_substituted(self):
        report = build(SOURCE.read_bytes(), FROZEN.read_bytes())
        self.assertIsNone(report["historical_angular_error"])
        self.assertIsNone(report["historical_timestamp_error"])
        self.assertIsNone(report["historical_physical_rate_interval"])
        self.assertIsNone(report["forward_physical_operator"])
        self.assertFalse(report["active_constraint"])
        self.assertEqual(report["historical_mcmc"], "NOT_RUN")
        self.assertFalse(report["frozen_holdout"]["evaluation_observations_used_for_fit"])

    def test_replay_payload_and_lineage(self):
        actual = build(SOURCE.read_bytes(), FROZEN.read_bytes())
        self.assertEqual(actual, json.loads(REPORT.read_text()))
        self.assertEqual(actual["source"]["documentary_lineages"], 1)
        self.assertEqual(actual["frozen_holdout"]["split_counts"], [61, 23, 35])
        self.assertEqual(len(actual["frozen_holdout"]["evaluation_527_epochs_utc"]), 4)

    def test_mutated_frozen_split_rejected(self):
        split = json.loads(FROZEN.read_text())
        split["memberships"]["527"]["validation"].append(
            split["memberships"]["527"]["evaluation"][0])
        with self.assertRaises((ValueError, AssertionError)):
            build(SOURCE.read_bytes(), json.dumps(split).encode())

    def test_invalid_designs_and_gcd(self):
        for lags in ((), (Fraction(0),), (Fraction(-1), Fraction(2))):
            with self.assertRaises(ValueError):
                rational_gcd(lags)
        for a, b in ((Fraction(0), Fraction(1)),
                     (Fraction(1), Fraction(1)),
                     (Fraction(1), Fraction(1, 2))):
            with self.assertRaises(ValueError):
                design(a, b)
        for k in (0, -1, True):
            with self.assertRaises(ValueError):
                design(Fraction(1), Fraction(6, 5), k)


if __name__ == "__main__":
    unittest.main()
