"""Exact structural RAAN/rate gauges, using frozen nonindependent catalogue epochs."""
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_temporal_gauge import (
    PHASE_GAUGE, RATE_GAUGE, build, certificate, days_from_reference, model_row
)


class TemporalGaugeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "research/statistics/raan_527_528_529_1963.json").read_bytes()
        cls.frozen = (ROOT / "research/statistics/raan_chronological_holdout_1963.json").read_bytes()
        cls.result = build(cls.source, cls.frozen)

    def test_exact_rational_day_preserves_microseconds(self):
        self.assertEqual(days_from_reference("1963-01-01T00:00:00.000001Z"),
                         Fraction(1, 86_400_000_000))
        self.assertEqual(days_from_reference("1963-01-02T00:00:00Z"), Fraction(1))

    def test_invalid_times_cannot_be_silently_assumed(self):
        for value in ("1963-01-01", "1963-01-01T00:00:00+01:00",
                      "1964-01-01T00:00:00Z", "bad", ""):
            with self.subTest(epoch=value), self.assertRaises(ValueError):
                days_from_reference(value)

    def test_exact_two_gauges_for_each_epoch(self):
        for obj in ("527", "528", "529"):
            for day in (Fraction(-7), Fraction(1, 13), Fraction(37, 5)):
                row = model_row(obj, day)
                self.assertEqual(sum(a * b for a, b in zip(row, PHASE_GAUGE)), 0)
                self.assertEqual(sum(a * b for a, b in zip(row, RATE_GAUGE)), 0)

    def test_small_adversarial_design(self):
        rows = [model_row(obj, Fraction(day)) for obj in ("527", "528", "529")
                for day in (0, 1, 5)]
        c = certificate(rows)
        self.assertEqual((c["constant_catalog_offset"]["rank"],
                          c["constant_catalog_offset"]["nullity"]), (6, 1))
        self.assertEqual((c["free_catalog_offset_and_drift"]["rank"],
                          c["free_catalog_offset_and_drift"]["nullity"]), (6, 2))
        self.assertEqual(c["hypothetical_absolute_phase_528_only"]["nullity"], 1)
        self.assertEqual(c["hypothetical_absolute_rate_528_only"]["nullity"], 1)
        self.assertEqual(c["hypothetical_both_anchors_528"]["nullity"], 0)

    def test_only_one_epoch_per_object_worsens_rank(self):
        rows = [model_row(obj, Fraction(42)) for obj in ("527", "528", "529")]
        self.assertEqual(certificate(rows)["free_catalog_offset_and_drift"]["rank"], 3)

    def test_singleton_527_validation_cannot_identify_its_rate(self):
        val = self.result["per_split"]["validation"]
        self.assertEqual(val["object_counts"]["527"], 1)
        self.assertEqual(val["epochs_from_one_secondary_lineage"], 23)
        self.assertEqual(val["exact_structural_design"]
                         ["free_catalog_offset_and_drift"]["rank"], 5)
        self.assertEqual(val["exact_structural_design"]
                         ["hypothetical_both_anchors_528"]["nullity"], 1)

    def test_frozen_split_ranks_and_no_posterior(self):
        self.assertEqual(self.result["all_epochs"]["unique"], 119)
        for p, expected in (("fit", 6), ("validation", 5), ("evaluation", 6)):
            result = self.result["per_split"][p]["exact_structural_design"]
            self.assertEqual(result["free_catalog_offset_and_drift"]["rank"], expected)
            self.assertEqual(result["constant_catalog_offset"]["nullity"],
                             7 - expected)
        self.assertEqual(self.result["historical_posterior"], "NOT_RUN")
        self.assertIsNone(self.result["error_model_historical"])
        self.assertTrue(self.result["holdout"]["retrospective_not_blind"])

    def test_reject_tampered_split(self):
        altered = json.loads(self.frozen)
        altered["memberships"]["528"]["fit"].pop()
        with self.assertRaisesRegex(ValueError, "mismatch"):
            build(self.source, json.dumps(altered).encode())

    def test_reject_false_documentary_independence(self):
        altered = json.loads(self.source)
        altered["provenance"]["lineage"] = "multiple independent sensors"
        with self.assertRaises(ValueError):
            build(json.dumps(altered).encode(), self.frozen)

    def test_replay_bytewise(self):
        encoded = (json.dumps(self.result, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
        self.assertEqual(encoded, (ROOT / "research/statistics/raan_temporal_gauge_C241.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
