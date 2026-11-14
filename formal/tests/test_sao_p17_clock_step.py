"""Adversarial checks for the documentary SAO P-17 clock Lean bridge."""
import copy
import json
import unittest

from formal.scripts import compile_sao_p17_clock_step as compiler


class ClockStepTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(compiler.p17.LEDGER.read_text(encoding="utf-8"))

    def test_checked_in_lean_matches_source(self):
        self.assertEqual(compiler.generate(self.record), compiler.OUT.read_text(encoding="utf-8"))

    def test_wrong_cutoff_rejected(self):
        record = copy.deepcopy(self.record)
        record["model"]["boundary_mjd"] = "38335.0"
        with self.assertRaises(ValueError):
            compiler.generate(record)

    def test_wrong_printed_slope_rejected(self):
        record = copy.deepcopy(self.record)
        record["model"]["slope_seconds_per_day"] = "0.001118459"
        with self.assertRaises(ValueError):
            compiler.generate(record)

    def test_wrong_scale_not_utc_rejected(self):
        record = copy.deepcopy(self.record)
        record["model"]["time_scale_output"] = "UTC"
        with self.assertRaises(ValueError):
            compiler.generate(record)

    def test_invented_norad528_rejected(self):
        record = copy.deepcopy(self.record)
        record["epoch_utc_528"] = "1963-11-08T00:00:00Z"
        with self.assertRaises(ValueError):
            compiler.generate(record)

    def test_fixedpoint_exact_and_half_open_boundary(self):
        self.assertEqual(compiler.to_ns(str(compiler.p17.a1_minus_wwv("38341.0"))),
                         2740565438)
        self.assertEqual(compiler.p17.a1_minus_wwv("38334.0")
                         - compiler.p17.a1_minus_wwv("38333.0"),
                         compiler.p17.RATE + compiler.p17.SECOND - compiler.p17.FIRST)
        self.assertIn("100000000 nanoseconds", compiler.generate(self.record))

    def test_rejects_sub_nanosecond_false_precision(self):
        with self.assertRaises(ValueError):
            compiler.to_ns("0.0000000001")


if __name__ == "__main__":
    unittest.main()
