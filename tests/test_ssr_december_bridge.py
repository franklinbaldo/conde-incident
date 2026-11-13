"""NASA 529 December erratum must be source-locked and remain physically latent."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_ssr_december_bridge import LEDGER, NOVEMBER, OUT, build, render


class DecemberBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text())
        cls.november = json.loads(NOVEMBER.read_text())

    def test_reconciled_period_is_linked_to_lean_and_simulator(self):
        out = build(self.ledger, self.november)
        self.assertEqual(out["erratum_matrix_occurrence"], "C227#1")
        self.assertEqual(out["erratum_verified_printed_min"], "89.2")
        self.assertEqual(out["conditional_differential_range_min"], ["2.80", "3.20"])
        self.assertEqual(out["control_529_printed_delta_min"], "3.0")
        self.assertEqual(out["lean_theorem"], "post_b_529_reconciled_printed_gap_over_527")
        self.assertIn("sensor_epoch_each_row", out["simulator_latent_parameters"])
        self.assertIsNone(out["sensor_epochs_utc"])
        self.assertIsNone(out["sensor_covariance"])
        self.assertFalse(out["active_physical_constraint"])
        self.assertEqual(out["physical_domain_effect"], "THETA_UNCHANGED")

    def test_old_c227_89_6_is_rejected_as_current_measure(self):
        bad = copy.deepcopy(self.ledger)
        bad["sources"][2]["rows"][1]["period_min"] = "89.6"
        with self.assertRaises(ValueError):
            build(bad, self.november)

    def test_december_digest_does_not_fall_back_to_unverified(self):
        bad = copy.deepcopy(self.ledger)
        bad["sources"][2]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            build(bad, self.november)

    def test_asof_date_cannot_be_rewritten_as_terminal_epoch(self):
        bad = copy.deepcopy(self.ledger)
        bad["sources"][2]["as_of_utc"] = "1963-11-08T12:00:00Z"
        with self.assertRaises(ValueError):
            build(bad, self.november)

    def test_upstream_consumer_must_match_verified_november(self):
        bad = copy.deepcopy(self.november)
        bad["canonical_value_min"] = "94.8"
        with self.assertRaisesRegex(ValueError, "November bridge"):
            build(self.ledger, bad)

    def test_report_edition_is_not_independent_instrument(self):
        out = build(self.ledger, self.november)
        self.assertTrue(out["same_institutional_family_not_independent_sensors"])
        self.assertFalse(out["source_to_instrument_mapping_verified"])
        self.assertEqual(out["source_editions"][1]["matrix_context_not_independent_sensor"],
                         ["C227#1"])

    def test_site_bytes_are_reproducible(self):
        self.assertEqual(OUT.read_text(encoding="utf-8"), render())
        self.assertLess(OUT.stat().st_size, 20000)


if __name__ == "__main__":
    unittest.main()
