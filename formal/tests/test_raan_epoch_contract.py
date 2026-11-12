"""Cross-check historical secondary RAAN arithmetic with Lean source constants."""
from fractions import Fraction
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal" / "scripts"))
from raan_epoch_contract import (  # noqa: E402
    LEGACY_RAAN_E4, MIRROR_RAAN_E4, EPOCH_OFFSET_US,
    circular_gap_e4, required_rate_floor_deg_day, admissible_under_cap, contract,
)

LEAN = ROOT / "formal/Conde1963/RaanEpochConstraint.lean"
AUDIT = ROOT / "formal/Conde1963/AxiomAudit.lean"


class RaanEpochContractTests(unittest.TestCase):
    def test_actual_transcribed_numbers_and_exact_rounding_floor(self):
        self.assertEqual(circular_gap_e4(LEGACY_RAAN_E4, MIRROR_RAAN_E4), 856259)
        self.assertEqual(required_rate_floor_deg_day(LEGACY_RAAN_E4, MIRROR_RAAN_E4, EPOCH_OFFSET_US),
                         Fraction(535161250, 1167))
        self.assertTrue(Fraction(458578) < required_rate_floor_deg_day(
            LEGACY_RAAN_E4, MIRROR_RAAN_E4, EPOCH_OFFSET_US) < Fraction(458579))

    def test_conditional_rate_gate_can_accept_or_reject(self):
        self.assertFalse(admissible_under_cap(LEGACY_RAAN_E4, MIRROR_RAAN_E4, EPOCH_OFFSET_US,
                                              Fraction(458578)))
        self.assertTrue(admissible_under_cap(LEGACY_RAAN_E4, MIRROR_RAAN_E4, EPOCH_OFFSET_US,
                                             Fraction(458579)))
        self.assertFalse(admissible_under_cap(LEGACY_RAAN_E4, MIRROR_RAAN_E4, EPOCH_OFFSET_US,
                                              Fraction(6, 5)))

    def test_wrap_and_failed_inputs(self):
        self.assertEqual(circular_gap_e4(3599999, 1), 2)
        with self.assertRaises(ValueError):
            circular_gap_e4(3600000, 0)
        with self.assertRaises(ValueError):
            required_rate_floor_deg_day(1, 0, 0)
        with self.assertRaises(ValueError):
            admissible_under_cap(1, 0, 10, Fraction(-1))

    def test_lean_inputs_and_audited_proofs_match_python(self):
        code = LEAN.read_text(encoding="utf-8")
        for name, n in (
            ("c241LegacyRaanE4", 2841520),
            ("c241MirrorRaanE4", 1985261),
            ("c241EpochSeparationUs", 16132608),
            ("c241OneDayUs", 86400000000),
            ("c241CombinedRoundingE4", 1),
        ):
            self.assertRegex(code, rf"def {name} : Nat := {n}\b")
        audit = AUDIT.read_text(encoding="utf-8")
        for name in (
            "c241_raan_gap_floor_is_856258",
            "c241_rate_458578_deg_day_cannot_explain",
            "c241_rate_458579_deg_day_passes_numeric_gate",
        ):
            self.assertIn("theorem " + name, code)
            self.assertIn("#print axioms Conde1963." + name, audit)

    def test_no_geographic_or_authentication_claim_leaks_into_export(self):
        out = contract()
        self.assertEqual(out["record"], "C241-T10")
        self.assertEqual(out["primary_1963_tle_custody"], "NOT_VERIFIED")
        self.assertEqual(out["historical_frame_equivalence"], "NOT_VERIFIED")
        self.assertIsNone(out["model_rate_cap_deg_day"])
        self.assertIsNone(out["conde_region_or_impact"])
        self.assertEqual(out["source_selection"], "MIRROR_REFERENCE_ONLY_LEGACY_RETIRED")
        self.assertEqual(out["legacy_input_role"], "HISTORICAL_FINGERPRINT_ONLY_NOT_MCMC_STATE")
        self.assertTrue(out["physical_raan_is_free_parameter"])
        self.assertEqual(out["original_lean_zip_154_151"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
