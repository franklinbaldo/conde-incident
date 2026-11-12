"""C241-L8 synthetic controls, not original 1963 radar observations."""
import csv
import sys
import tempfile
import unittest
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from tle_literal_layout import audit_pair
from tle_mean_motion_secant_audit import COUNTS, DISTINCT, read_rows
from tle_cross_catalog_legacy_audit import (
    EXPECTED, LEGACY, LEGACY_LINE1, LEGACY_LINE2,
    audit_cross_catalog, circular_delta, within_epoch_quantum,
)

from datetime import datetime
EPOCH = datetime.fromisoformat(audit_pair(LEGACY_LINE1, LEGACY_LINE2)["epoch_utc"].replace("Z", "+00:00"))


def sample(index, sat=528, days=0, **changes):
    values = {key: str(value) for key, value in LEGACY.items()}
    values.update({key: str(value) for key, value in changes.items()})
    return {
        "source_row": str(index),
        "norad_id": str(sat),
        "intl_designator": EXPECTED[sat],
        "epoch": (EPOCH + timedelta(days=days)).isoformat(
            timespec="microseconds").replace("+00:00", "Z"),
        **values, "mean_motion_dot": "0", "bstar": "0",
    }


class CrossCatalogLegacyControls(unittest.TestCase):
    def test_six_field_match_in_secondary_528_is_not_primary(self):
        report = audit_cross_catalog([sample(1)], "SYNTHETIC")
        x = report["comparison"]["by_catalog"]["528"]
        self.assertEqual(x["all_six_any_epoch_count"], 1)
        self.assertEqual(x["all_six_at_legacy_epoch_count"], 1)
        self.assertEqual(report["provenance"]["original_norad_pairs_all_45_epochs"],
                         "NOT_RECOVERED")
        self.assertEqual(report["conde_impact"], "INDETERMINATE")

    def test_six_field_match_in_527_is_reported_not_relabelled(self):
        x = audit_cross_catalog([sample(11, sat=527)], "SYNTHETIC")
        self.assertEqual(x["comparison"]["all_six_any_epoch_527_or_529"], 1)
        self.assertEqual(
            x["comparison"]["cross_catalog_copy_hypothesis"],
            "COMPATIBLE_WITH_SECONDARY_NUMBERS_ONLY_NOT_AUTHENTICATED")
        self.assertEqual(x["comparison"]["by_catalog"]["528"]["distinct_epochs"], 0)
        self.assertEqual(x["comparison"]["by_catalog"]["527"][
            "closest_raan_same_record"][0]["source_rows"], [11])

    def test_six_field_match_in_529_is_not_an_instrumental_attribution(self):
        x = audit_cross_catalog([sample(30, sat=529)], "SYNTHETIC")
        self.assertEqual(x["comparison"]["by_catalog"]["529"][
            "all_six_any_epoch_count"], 1)
        self.assertEqual(x["legacy_raan_284_1520_vs_secondary_198_5261"],
                         "UNRESOLVED_PRIMARY_ORIGIN")

    def test_fields_from_different_rows_are_never_mixed(self):
        rows = [sample(1, sat=527, raan="198.5261"),
                sample(2, sat=529, inclination="82.5"),
                sample(3, sat=528, mean_motion="16")]
        x = audit_cross_catalog(rows, "SYNTHETIC")["comparison"]
        self.assertEqual(x["all_six_any_epoch_all_catalogs"], 0)
        self.assertEqual(x["full_legacy_vector_any_catalog_hypothesis"],
                         "NO_SIX_FIELD_MATCH_IN_PINNED_MIRROR")
        self.assertTrue(all(v["most_matched_fields_in_one_record"][0][
            "matched_fields_in_same_record"] < 6 for v in
            x["by_catalog"].values()))

    def test_same_epoch_duplicates_are_one_state_with_both_source_rows(self):
        x = audit_cross_catalog([sample(3), sample(4)], "SYNTHETIC")
        sat = x["comparison"]["by_catalog"]["528"]
        self.assertEqual(sat["rows"], 2)
        self.assertEqual(sat["distinct_epochs"], 1)
        self.assertEqual(sat["closest_raan_same_record"][0]["source_rows"], [3, 4])
        self.assertEqual(len(x["comparison"]["duplicates_preserved_by_source_index"]), 1)

    def test_conflicting_duplicate_epoch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "contradictory"):
            audit_cross_catalog([sample(3), sample(4, raan="300")], "SYNTHETIC")

    def test_norad_cospar_cross_assignment_fails_closed(self):
        broken = sample(1, sat=527)
        broken["intl_designator"] = EXPECTED[529]
        with self.assertRaisesRegex(ValueError, "NORAD/COSPAR"):
            audit_cross_catalog([broken], "SYNTHETIC")

    def test_repeated_row_index_or_catalog_out_of_scope_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "source_row"):
            audit_cross_catalog([sample(1), sample(1, sat=527)], "SYNTHETIC")
        broken = sample(2)
        broken["norad_id"] = "530"
        with self.assertRaisesRegex(ValueError, "catalog"):
            audit_cross_catalog([broken], "SYNTHETIC")

    def test_epoch_precision_is_not_orbital_error(self):
        self.assertTrue(within_epoch_quantum(EPOCH, EPOCH + timedelta(microseconds=432)))
        self.assertFalse(within_epoch_quantum(EPOCH, EPOCH + timedelta(microseconds=433)))
        x = audit_cross_catalog([sample(1, days=1)], "SYNTHETIC")
        v = x["comparison"]["by_catalog"]["528"]
        self.assertEqual(v["all_six_any_epoch_count"], 1)
        self.assertEqual(v["all_six_at_legacy_epoch_count"], 0)

    def test_angles_are_circular_with_no_cross_epoch_stitching(self):
        self.assertEqual(circular_delta(Decimal("359.999"), Decimal("0.001")),
                         Decimal("0.002"))
        self.assertEqual(circular_delta(Decimal("198.5261"), Decimal("284.1520")),
                         Decimal("85.6259"))

    def test_missing_nonfinite_or_off_grid_input_is_rejected(self):
        bad = sample(1)
        bad["mean_motion"] = "NaN"
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            audit_cross_catalog([bad], "SYNTHETIC")
        bad = sample(1)
        bad["epoch"] = "1963-10-27T14:40:00.000001Z"
        with self.assertRaisesRegex(ValueError, "grid"):
            audit_cross_catalog([bad], "SYNTHETIC")
        bad = sample(1)
        del bad["raan"]
        with self.assertRaisesRegex(ValueError, "invalid custody"):
            audit_cross_catalog([bad], "SYNTHETIC")

    def test_pinned_counts_and_sha_are_mandatory_for_real_run(self):
        with self.assertRaisesRegex(ValueError, "row counts"):
            audit_cross_catalog([sample(1)], "SYNTHETIC", counts=COUNTS,
                                distinct=DISTINCT)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "synthetic.csv"
            with path.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(sample(1)))
                writer.writeheader()
                writer.writerow(sample(1))
            with self.assertRaisesRegex(ValueError, "SHA256"):
                read_rows(path)
            result, source_sha = read_rows(path, enforce_sha=False)
            self.assertEqual(len(result), 1)
            self.assertNotEqual(source_sha, "3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231")

    def test_no_physical_lean_or_holdout_from_secondary_data(self):
        x = audit_cross_catalog([sample(1)], "SYNTHETIC")
        self.assertEqual(x["lean_physical_restriction"],
                         "NOT_PROMOTED_NO_PRIMARY_FRAME_ERRORS")
        self.assertEqual(x["calibrated_physics_and_holdout"], "NOT_RUN")
        self.assertIsNone(x["constraint_link"]["measurement_sigma"])
        self.assertFalse(x["constraint_link"]["physical_parameter_domain_reduced"])
        self.assertEqual(x["physical_component_528"],
                         "NOT_IDENTIFIED_BY_ENGINEERING_RECORD")
        self.assertIn("NOT_AUTHENTICATED",
                      x["comparison"]["full_legacy_vector_any_catalog_hypothesis"])


if __name__ == "__main__":
    unittest.main()
