"""C241-T9: synthetic controls, never historical observations."""
import copy
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tle_drag_term_lineage_audit import audit, implicit_exponent, validate_rows
from tle_literal_layout import audit_literal_file

PAIR = ROOT / "research/tle_custody/mirror_528_1963-10-27.tle"
EPOCH = "1963-10-27T14:40:16.132512Z"


def row(idx=3017, sat=528, epoch=EPOCH, dot="0.00686563", bstar="0"):
    return {"source_row": str(idx), "norad_id": str(sat), "epoch": epoch,
            "mean_motion_dot": dot, "bstar": bstar}


def check(rows, pair=None, **kwargs):
    return audit(rows, pair or audit_literal_file(PAIR), "SYNTHETIC_CSV", **kwargs)


class Line1CustodyControls(unittest.TestCase):
    def test_signed_implicit_exponent(self):
        self.assertEqual(implicit_exponent("-12345-6"), Decimal("-0.00000012345"))
        self.assertEqual(implicit_exponent("+12345+2"), Decimal("12.345"))
        self.assertEqual(implicit_exponent("+00000-0"), Decimal("0"))
        self.assertEqual(implicit_exponent(" 12345-1"), Decimal("0.012345"))

    def test_invalid_exponent_fails(self):
        for value in ("12345-6", "+1234-6", "+12345x6", "+12345-00", "x1234-6"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "exponent"):
                implicit_exponent(value)

    def test_same_epoch_as_encoded_half(self):
        result = check([row()])
        q = result["same_epoch_528"]
        self.assertEqual(q["literal_n_dot_over_two"], "0.00686563")
        self.assertEqual(q["twice_literal_field"], "0.01373126")
        self.assertEqual(q["numeric_scale_test"], "MATCHES_TLE_ENCODED_HALF")
        self.assertTrue(q["bstar_matches"])
        self.assertEqual(q["parquet_n_ddot_over_six"], "COLUMN_ABSENT")
        self.assertEqual(result["lean_physical_premise"], "NOT_PROMOTED")

    def test_same_epoch_double_is_alternative_not_assumed(self):
        q = check([row(dot="0.01373126")])["same_epoch_528"]
        self.assertEqual(q["numeric_scale_test"], "MATCHES_TWICE_TLE_FIELD")
        self.assertFalse(q["matches"]["as_tle_encoded_half"])

    def test_neither_scaling_keeps_negative_result(self):
        q = check([row(dot="0.9")])["same_epoch_528"]
        self.assertEqual(q["numeric_scale_test"], "NEITHER_CONVENTION_MATCHES")

    def test_bstar_mismatch_is_independently_reported(self):
        q = check([row(bstar="0.001")])["same_epoch_528"]
        self.assertFalse(q["bstar_matches"])

    def test_zero_field_cannot_discriminate_factor(self):
        pair = copy.deepcopy(audit_literal_file(PAIR))
        pair["line1_other_fields"]["mean_motion_first_derivative_half"] = " .00000000"
        q = check([row(dot="0")], pair)["same_epoch_528"]
        self.assertEqual(q["numeric_scale_test"], "NON_DISCRIMINATING_ZERO_OR_ROUNDING")

    def test_duplicate_source_row_and_catalog_fail(self):
        with self.assertRaisesRegex(ValueError, "source_row"):
            validate_rows([row(), row(sat=527)])
        with self.assertRaisesRegex(ValueError, "catalog"):
            validate_rows([row(sat=999)])

    def test_invalid_epoch_and_values_fail(self):
        with self.assertRaisesRegex(ValueError, "epoch"):
            validate_rows([row(epoch="1963-10-27T14:40:16.132512+01:00")])
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            validate_rows([row(dot="NaN")])
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            validate_rows([row(bstar="Infinity")])
        with self.assertRaisesRegex(ValueError, "invalid"):
            validate_rows([row(dot="not-a-number")])
        v = row()
        del v["bstar"]
        with self.assertRaisesRegex(ValueError, "invalid"):
            validate_rows([v])

    def test_no_inexact_or_ambiguous_epoch_join(self):
        with self.assertRaisesRegex(ValueError, "same-epoch"):
            check([row(epoch="1963-10-27T14:40:16.132945Z")])
        self.assertEqual(check([row(epoch="1963-10-27T14:40:16.132944Z")])[
            "same_epoch_528"]["source_row"], 3017)
        with self.assertRaisesRegex(ValueError, "same-epoch"):
            check([row(), row(idx=3018)])

    def test_counts_and_empty_rejected(self):
        with self.assertRaisesRegex(ValueError, "counts"):
            check([row()], expected_counts={527: 21, 528: 45, 529: 57})
        with self.assertRaisesRegex(ValueError, "empty"):
            validate_rows([])

    def test_provenance_and_scope(self):
        r = check([row()])
        self.assertEqual(r["provenance"]["original_1963_norad_lines"], "NOT_RECOVERED")
        self.assertEqual(r["provenance"]["independent_tracking"], "NOT_ESTABLISHED")
        self.assertEqual(r["raan_conflict"], "UNRESOLVED_PRIMARY_ORIGIN")
        self.assertEqual(r["conde"], "INDETERMINATE")
        self.assertEqual(r["by_norad"]["528"]["rows"], 1)
        self.assertEqual(r["by_norad"]["528"]["bstar_zero"], 1)


if __name__ == "__main__":
    unittest.main()
