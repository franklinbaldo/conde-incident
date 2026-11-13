"""Adversarial tests: a proposed mass total is not observed physics."""
import json
import subprocess
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
            with self.assertRaises(ValueError):
                audit_ledger(p)

    def test_no_fabricated_hash(self):
        data = json.loads(LEDGER.read_text())
        data["source"]["source_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "mutant.json"
            p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                audit_ledger(p)


    def test_optimized_python_still_rejects_historical_promotion(self):
        data = json.loads(LEDGER.read_text(encoding="utf-8"))
        data["activation"]["physical_constraint_active"] = True
        with tempfile.TemporaryDirectory() as directory:
            mutant = Path(directory) / "forged.json"
            mutant.write_text(json.dumps(data), encoding="utf-8")
            code = ("import sys; from pathlib import Path; "
                    "from tools.mass_partition_C241_L39 import audit_ledger; "
                    "audit_ledger(Path(sys.argv[1]))")
            for optimize in (False, True):
                with self.subTest(optimize=optimize):
                    args = [sys.executable, "-B"]
                    if optimize:
                        args.append("-O")
                    result = subprocess.run(
                        [*args, "-c", code, str(mutant)],
                        cwd=ROOT, capture_output=True, text=True, check=False,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("ValueError", result.stderr)

    def test_optimized_python_accepts_real_conditional_ledger(self):
        code = "from tools.mass_partition_C241_L39 import audit_ledger; audit_ledger()"
        result = subprocess.run(
            [sys.executable, "-B", "-O", "-c", code],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_fail_closed_on_mutated_epistemology_and_extra_fields(self):
        originals = json.loads(LEDGER.read_text(encoding="utf-8"))
        variants = [
            lambda d: d["assumptions"].update(x_is_small="PROVEN"),
            lambda d: d["assumptions"].update(masses_nonnegative=False),
            lambda d: d["activation"].update(used_to_fit_drag=True),
            lambda d: d["source"].update(primary_publication="fabricated NASA log"),
            lambda d: d["source"].update(instrumental_528_tracking_added=1),
            lambda d: d.update(nominal_total_kg=1176.0),
            lambda d: d.update(scope="HISTORICALLY_OBSERVED"),
            lambda d: d["links"].update(independent_mass_provenance="PROVEN"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "mutant.json"
            for index, mutate in enumerate(variants):
                with self.subTest(variant=index):
                    data = json.loads(json.dumps(originals))
                    mutate(data)
                    file.write_text(json.dumps(data), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        audit_ledger(file)

    def test_duplicate_json_keys_are_not_silently_accepted(self):
        source = LEDGER.read_text(encoding="utf-8")
        forged = source.replace('"schema":', '"schema": "ignored", "schema":', 1)
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "duplicates.json"
            file.write_text(forged, encoding="utf-8")
            with self.assertRaises(ValueError):
                audit_ledger(file)


if __name__ == "__main__":
    unittest.main()
