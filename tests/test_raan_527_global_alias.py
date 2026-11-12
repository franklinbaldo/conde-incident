"""Exact circular winding alias tests: synthetic design, frozen epoch provenance."""
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_527_global_alias import alias_witness, build

SOURCE = ROOT / "research/statistics/raan_527_528_529_1963.json"
FROZEN = ROOT / "research/statistics/raan_chronological_holdout_1963.json"
OUTPUT = ROOT / "research/constraints/raan_527_global_alias_candidate_C241.json"


class GlobalAlias527Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build(SOURCE.read_bytes(), FROZEN.read_bytes())

    def test_counterfactuals_gain_rank_but_not_global_uniqueness(self):
        for design, lag, spacing in zip(self.report["counterfactual_designs"],
                                        ("1/2", "1/1"), ("720/1", "360/1")):
            self.assertEqual(design["delta_days"], lag)
            self.assertEqual(design["rate_alias_spacing_deg_per_day"], spacing)
            self.assertEqual((design["rank_before_second_epoch"],
                              design["rank_after_second_epoch"]), (5, 6))
            self.assertEqual(design["design_wrapped_prediction_shifts_deg"],
                             ["0/1", "0/1"])
            self.assertFalse(design["global_rate_unique_from_two_circular_points"])
            self.assertEqual(design["remaining_global_winding_aliases_without_rate_bound"],
                             "COUNTABLY_INFINITE")
            self.assertEqual(design["evaluation_527_changed_count"], 4)

    def test_all_four_holdouts_are_distinguishable_from_alias(self):
        for design in self.report["counterfactual_designs"]:
            shifts = [Fraction(s) for s in design["evaluation_527_wrapped_shifts_deg"]]
            self.assertEqual(len(shifts), 4)
            self.assertTrue(all(Fraction(0) < x < Fraction(360) for x in shifts))

    def test_angular_wrap_adversarial(self):
        # Two design instants remain identical on S1, despite different rate.
        out = alias_witness(Fraction(10), Fraction(11), [Fraction(11, 3), Fraction(35, 3)])
        self.assertEqual(out["design_wrapped_prediction_shifts_deg"], ["0/1", "0/1"])
        self.assertEqual(out["rate_alias_spacing_deg_per_day"], "360/1")

    def test_invalid_timestamps_rejected(self):
        for new in (Fraction(4), Fraction(5)):
            with self.assertRaises(ValueError):
                alias_witness(Fraction(5), new, [Fraction(7)])
        with self.assertRaises(ValueError):
            alias_witness(Fraction(5), Fraction(6), [])
        with self.assertRaises(ValueError):
            alias_witness(Fraction(5), Fraction(6), [Fraction(6)])

    def test_frozen_report_matches_exact_payload(self):
        expected = json.loads(OUTPUT.read_text())
        self.assertEqual(self.report, expected)
        self.assertEqual(expected["frozen_manifest"]["unique_epochs"], 119)
        self.assertFalse(expected["active_constraint"])
        self.assertIsNone(expected["historical_rate_prior"])
        self.assertEqual(expected["calibrated_historical_mcmc"], "NOT_RUN")

    def test_frozen_inputs_mutation_refused(self):
        data = json.loads(FROZEN.read_text())
        data["memberships"]["527"]["validation"].append(
            data["memberships"]["527"]["evaluation"][0])
        with self.assertRaises((ValueError, AssertionError)):
            build(SOURCE.read_bytes(), json.dumps(data).encode())


if __name__ == "__main__":
    unittest.main()
