"""Synthetic adversarial controls: never count as historical observations."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from gaviao_chapter05_recheck import (
    FIELDS, TOLERANCE, L1, L2, checksum, delta, inspect_rows, legacy_elements, legacy_epoch,
)

def row(at, **changes):
    return {"norad_id": 528, "epoch": at, **(legacy_elements() | changes)}

class IndependentChapter05Controls(unittest.TestCase):
    def test_checksum_is_only_syntax(self):
        self.assertEqual(checksum(L1), int(L1[-1]))
        self.assertEqual(checksum(L2), int(L2[-1]))

    def test_six_fields_match_separate_from_epoch(self):
        result = inspect_rows([(3, row(legacy_epoch() + timedelta(days=5)))])
        self.assertEqual((result["complete_six_field_matches"], result["same_epoch_records"]), (1, 0))

    def test_same_epoch_does_not_mean_fields_match(self):
        result = inspect_rows([(1, row(legacy_epoch(), raan=10.0))])
        self.assertEqual((result["complete_six_field_matches"], result["same_epoch_records"]), (0, 1))

    def test_separate_rows_cannot_be_joined_into_false_match(self):
        at = legacy_epoch()
        left = row(at, raan=10.0)
        right = row(at + timedelta(days=1), inclination=65.0)
        result = inspect_rows([(1, left), (2, right)])
        self.assertEqual(result["complete_six_field_matches"], 0)

    def test_angular_wrap_is_circular(self):
        self.assertAlmostEqual(delta("raan", 359.999, 0.001), 0.002)
        self.assertAlmostEqual(delta("inclination", 359.999, 0.001), 359.998)

    def test_float_boundary_accepts_and_rejects(self):
        at = legacy_epoch()
        field = "eccentricity"
        r = inspect_rows([(1, row(at, **{field: legacy_elements()[field] + TOLERANCE[field] * .9}))])
        self.assertEqual(r["complete_six_field_matches"], 1)
        r = inspect_rows([(1, row(at, **{field: legacy_elements()[field] + TOLERANCE[field] * 1.1}))])
        self.assertEqual(r["complete_six_field_matches"], 0)

    def test_reject_non_utc(self):
        with self.assertRaisesRegex(ValueError, "UTC"):
            inspect_rows([(1, row(datetime(1963, 10, 27)))])

    def test_reject_nonfinite(self):
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            inspect_rows([(1, row(legacy_epoch(), raan=float("nan")))])

    def test_no_physical_promotion(self):
        result = inspect_rows([(1, row(legacy_epoch(), raan=10))])
        self.assertEqual(result["physical_parameter_domain"], "NOT_EVALUATED")
        self.assertEqual(result["reentry_or_impact"], "NOT_ESTABLISHED")
        self.assertEqual(result["lean_proof"], "NOT_RUN")

if __name__ == "__main__":
    unittest.main()
