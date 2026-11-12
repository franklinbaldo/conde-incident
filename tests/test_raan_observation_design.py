"""Adversarial counterfactual observation-design tests, not orbital inference."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_observation_design import _scenario, candidate_designs, report
from raan_lineage_identifiability import phase_prediction


class DiscriminatingObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / "research/statistics/raan_527_528_529_1963.json").read_bytes()
        cls.frozen = (ROOT / "research/statistics/raan_chronological_holdout_1963.json").read_bytes()
        cls.actual = report(cls.raw, cls.frozen)

    def test_exact_historical_manifest_and_no_false_posterior(self):
        self.assertEqual(self.actual["frozen_holdout"]["unique_epochs"], {
            "fit": 61, "validation": 23, "evaluation": 35})
        self.assertEqual(set(self.actual["frozen_holdout"]["gauge_rank_every_block"].values()), {3})
        self.assertEqual(self.actual["historical_mcmc"], "NOT_RUN")
        self.assertIsNone(self.actual["historical_error_covariance"])
        self.assertFalse(self.actual["observation_available"])

    def test_repeated_same_lineage_does_not_break_gauge(self):
        d = candidate_designs()[0]
        self.assertEqual((d["rank_before_candidate"], d["rank_after_candidate"]), (3, 3))
        self.assertEqual(d["remaining_nullity"], 1)
        self.assertFalse(d["global_absolute_phase_identified"])

    def test_relative_contrast_cannot_anchor_raan(self):
        d = candidate_designs()[1]
        self.assertEqual((d["rank_after_candidate"], d["remaining_nullity"]), (3, 1))

    def test_new_independent_lineage_without_calibration_still_has_gauge(self):
        for d in candidate_designs()[2:4]:
            self.assertEqual(d["rank_after_candidate"], 4)
            self.assertEqual(d["parameter_count_after"], 5)
            self.assertEqual(d["remaining_nullity"], 1)
            self.assertFalse(d["global_absolute_phase_identified"])

    def test_absolute_phase_or_bias_calibration_breaks_one_gauge_only(self):
        for d in candidate_designs()[4:]:
            self.assertEqual(d["rank_after_candidate"], 4)
            self.assertEqual(d["remaining_nullity"], 0)
            self.assertTrue(d["global_absolute_phase_identified"])
            self.assertEqual(d["candidate_status"], "COUNTERFACTUAL_NO_OBSERVATION_RECOVERED")

    def test_joint_shift_invariance_across_distinct_unknown_sources(self):
        for shift in (-1080.0, -371.6, -1.0, 0.0, 180.0, 721.2):
            for phase, bias, dyn in ((359.9, 15.0, 10.0), (0.1, 321.5, -35.7)):
                self.assertAlmostEqual(
                    phase_prediction(phase, bias, dyn),
                    phase_prediction(phase+shift, bias-shift, dyn), places=9)

    def test_wrong_row_width_rejected(self):
        with self.assertRaisesRegex(ValueError, "dimension mismatch"):
            _scenario("bad", [(1, 2, 3)], new_uncalibrated_lineage=True,
                      type_of_evidence="test", independence_requirement="test")

    def test_tampered_frozen_holdout_fails(self):
        bad = json.loads(self.frozen)
        bad["memberships"]["528"]["fit"].pop()
        with self.assertRaisesRegex(ValueError, "mismatch"):
            report(self.raw, json.dumps(bad).encode())

    def test_tampered_provenance_fails(self):
        bad = json.loads(self.raw)
        bad["provenance"]["lineage"] = "invented independent sensors"
        with self.assertRaises(ValueError):
            report(json.dumps(bad).encode(), self.frozen)

    def test_reproducible_json_byte_for_byte(self):
        expected = (json.dumps(self.actual, ensure_ascii=False, sort_keys=True, indent=2)+"\n").encode()
        actual = (ROOT/"research/statistics/raan_observation_design_C241.json").read_bytes()
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
