"""Adversarial tests: a proposed mass total is not observed physics."""
import json
import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.mass_partition_C241_L39 import KEYS, LEDGER, audit_ledger, check_candidate


class TestMassPartition(unittest.TestCase):
    def setUp(self):
        self.base = dict(zip(KEYS, (200, 300, 500, 176)))

    def test_ledger(self):
        audit_ledger()

    def test_positive_residual(self):
        self.assertTrue(check_candidate(self.base))

    def test_zero_residual(self):
        self.assertTrue(check_candidate(dict(zip(KEYS, (200, 300, 676, 0)))))

    def test_nonunique_allocation(self):
        self.assertTrue(check_candidate(dict(zip(KEYS, (350, 350, 400, 76)))))
        self.assertTrue(check_candidate(self.base))

    def test_no_equal_mass_assumption(self):
        self.assertTrue(check_candidate(dict(zip(KEYS, (1, 1, 1, 1173)))))

    def test_x_not_small_by_default(self):
        self.assertTrue(check_candidate(dict(zip(KEYS, (0, 0, 0, 1176)))))

    def test_strict_upper_bound_not_derived_without_positivity(self):
        self.assertTrue(check_candidate(dict(zip(KEYS, (1176, 0, 0, 0)))))

    def test_reject_negative_nonfinite_bool_none(self):
        for value in (-1, None, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                check_candidate({**self.base, "x_unaccounted": value})

    def test_reject_missing_or_added_id(self):
        for candidate in ({k: v for k, v in self.base.items() if k != "m_528"},
                          {**self.base, "other": 0}):
            with self.assertRaises(ValueError):
                check_candidate(candidate)

    def test_tolerance_must_be_supplied(self):
        wrong = {**self.base, "m_527": 210}
        self.assertFalse(check_candidate(wrong))
        self.assertTrue(check_candidate(wrong, epsilon=10))
        self.assertFalse(check_candidate(wrong, epsilon=9))
        with self.assertRaises(ValueError):
            check_candidate(wrong, epsilon=-0.1)

    def test_no_promotion_to_historical_measurement(self):
        data = json.loads(LEDGER.read_text())
        data["activation"]["physical_constraint_active"] = True
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "mutant.json"
            p.write_text(json.dumps(data))
            with self.assertRaises(AssertionError):
                audit_ledger(p)

    def test_no_fabricated_hash(self):
        data = json.loads(LEDGER.read_text())
        data["source"]["source_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "mutant.json"
            p.write_text(json.dumps(data))
            with self.assertRaises(AssertionError):
                audit_ledger(p)


if __name__ == "__main__":
    unittest.main()
