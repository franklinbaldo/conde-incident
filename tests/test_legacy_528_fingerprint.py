"""Synthetic falsifications of legacy NORAD 528 fingerprinting.

These records are NOT historical observations. GitHub Actions separately
downloads and verifies the actual secondary 1963 data before cross-check.
"""
import csv
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_norad_1963 import tle_epoch_utc
from legacy_528_fingerprint import (
    LEGACY, LEGACY_LINE1, LEGACY_LINE2, read_528_csv,
    fingerprint, SERIALIZATION_TOLERANCES,
)
from audit_norad_1963 import validate_raw_tle


def synthetic(*, days=0, microseconds=0, index=1, **replacements):
    epoch = tle_epoch_utc(LEGACY_LINE1) + timedelta(days=days, microseconds=microseconds)
    fields = dict(LEGACY)
    fields.update(replacements)
    return {"source_row": index, "epoch_utc": epoch, "fields": fields}


class LegacyFingerprintControls(unittest.TestCase):
    def test_legacy_checksum_passes_but_custody_remains_unverified(self):
        self.assertEqual(validate_raw_tle(LEGACY_LINE1, LEGACY_LINE2, 528)["checksum"],
                         "PASS_syntax_only")
        report = fingerprint([synthetic()], "synthetic")
        self.assertEqual(report["legacy_tle_checksum"]["authenticity"], "NOT_VERIFIED")
        self.assertEqual(report["source"]["legacy_class"], "UNVERIFIED_LEGACY_CONSTRUCTED_PAIR")
        self.assertEqual(report["legacy_claim"]["elements"]["raan"], 284.1520)

    def test_fields_from_different_epochs_never_form_one_synthetic_tle(self):
        # August has a matching RAAN, October a matching eccentricity. Neither
        # constitutes the six-field vector, and only October has same epoch.
        august = synthetic(index=20, days=-76, eccentricity=0.0017)
        october = synthetic(index=21, raan=198.5261)
        report = fingerprint([august, october], "synthetic")["comparison"]
        self.assertEqual(report["closest_by_raan"][0]["source_row"], 20)
        self.assertEqual(report["closest_by_eccentricity"][0]["source_row"], 21)
        self.assertEqual(report["all_six_elements_match_any_epoch_count"], 0)
        self.assertEqual(report["all_six_match_same_epoch_count"], 0)
        self.assertEqual(report["result"], "NO_SIX_FIELD_MATCH_IN_SECONDARY_MIRROR")

    def test_same_epoch_plus_six_fields_can_match_only_with_provenance_caveat(self):
        report = fingerprint([synthetic()], "synthetic")["comparison"]
        self.assertEqual(report["all_six_elements_match_any_epoch_count"], 1)
        self.assertEqual(report["all_six_match_same_epoch_count"], 1)
        self.assertEqual(report["result"], "SECONDARY_FIELD_MATCH_WITHOUT_PRIMARY_AUTHENTICATION")

    def test_432us_in_epoch_window_but_433us_outside(self):
        inside = fingerprint([synthetic(microseconds=432)], "synthetic")["comparison"]
        outside = fingerprint([synthetic(microseconds=433)], "synthetic")["comparison"]
        self.assertEqual(len(inside["legacy_same_epoch_candidates"]), 1)
        self.assertEqual(len(outside["legacy_same_epoch_candidates"]), 0)

    def test_decimal_tolerance_cannot_bridge_historical_angular_gap(self):
        self.assertLess(SERIALIZATION_TOLERANCES["raan"], 0.179)
        r = fingerprint([synthetic(raan=284.3310852050781)], "synthetic")["comparison"]
        self.assertFalse(r["closest_by_raan"][0]["fields_within_serialization"]["raan"])

    def test_pinned_csv_rejects_drift_and_duplicate_source_row(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "rows.csv"
            columns = ["norad_id", "source_row", "epoch"] + list(LEGACY)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
                for i in range(2):
                    writer.writerow({"norad_id": 528, "source_row": 9,
                                     "epoch": "1963-10-27T14:40:00.000000Z", **LEGACY})
            with self.assertRaisesRegex(ValueError, "SHA256 divergente"):
                read_528_csv(path)
            with self.assertRaisesRegex(ValueError, "índice físico"):
                read_528_csv(path, enforce_sha=False)

    def test_csv_rejects_different_object_in_528_only_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "rows.csv"
            columns = ["norad_id", "source_row", "epoch"] + list(LEGACY)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
                writer.writerow({"norad_id": 529, "source_row": 42,
                                 "epoch": "1963-10-27T14:40:00.000000Z", **LEGACY})
            with self.assertRaisesRegex(ValueError, "outro satélite"):
                read_528_csv(path, enforce_sha=False)


if __name__ == "__main__":
    unittest.main()
