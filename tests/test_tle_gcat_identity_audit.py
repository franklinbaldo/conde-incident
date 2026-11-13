"""C241-L13: synthetic adversarial controls for catalog-taxonomy custody."""
import copy
import json
import unittest
from pathlib import Path

from tools.tle_gcat_identity_audit import audit, find_gcat_row, validate_ledger

LEDGER = (Path(__file__).resolve().parents[1] /
          "research/tle_custody/gcat_identity_527_529_C241-L13.json")
# A constructed input for parser testing, NOT a captured primary source.
SYNTHETIC_GCAT = (
    b"A00324       00527       1963-003   1963-003A      R2           "
    b"Agena B 2313                 Agena B 2313      1963 Jan 16  "
    b"R07069     1963 Jan 16 2206  Earth    1969 Jan  9       R\n"
)


class GcatIdentityTests(unittest.TestCase):
    def setUp(self):
        self.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def reject(self, fn):
        trial = copy.deepcopy(self.ledger)
        fn(trial)
        with self.assertRaises((ValueError, TypeError, KeyError)):
            validate_ledger(trial)

    def test_locked_ledger(self):
        self.assertEqual(validate_ledger(self.ledger)["conde_outcome"], "INDETERMINATE")

    def test_without_online_bytes_is_explicit(self):
        x = audit(self.ledger)
        self.assertIsNone(x["gcat_source_sha256"])
        self.assertFalse(x["gcat_row_matches_expected_fields"])
        self.assertIsNone(x["norad_528_engineering_component"])

    def test_synthetic_row_matches_pattern_but_not_history(self):
        x = audit(self.ledger, SYNTHETIC_GCAT)
        self.assertTrue(x["gcat_row_matches_expected_fields"])
        self.assertEqual(len(x["gcat_source_sha256"]), 64)
        self.assertIsNone(x["norad_529_engineering_component"])

    def test_missing_auxiliary_row_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            find_gcat_row(b"A00325 00533 1963-004 1963-004A R2\n")

    def test_relabel_527_as_payload_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            find_gcat_row(SYNTHETIC_GCAT.replace(b"R2", b"P ", 1))

    def test_incorrect_norad_528_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            find_gcat_row(SYNTHETIC_GCAT.replace(b"00527", b"00528"))

    def test_duplicate_row_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            find_gcat_row(SYNTHETIC_GCAT + SYNTHETIC_GCAT)

    def test_incorrect_designator_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            find_gcat_row(SYNTHETIC_GCAT.replace(b"1963-003A", b"1963-003B"))

    def test_missing_decay_date_rejected(self):
        with self.assertRaisesRegex(ValueError, "decay-date"):
            find_gcat_row(SYNTHETIC_GCAT.replace(b"1969 Jan  9", b"1970 Feb  8"))

    def test_physical_528_fabricated(self):
        self.reject(lambda d: d["comparison"].update(physical_piece_528="Agena engine"))

    def test_sigma_fabricated(self):
        self.reject(lambda d: d["comparison"].update(instrumental_sigma_528=0.0001))

    def test_frame_fabricated(self):
        self.reject(lambda d: d["comparison"].update(frame_528="TEME"))

    def test_false_transfer_527_to_528(self):
        self.reject(lambda d: d["comparison"].update(identity_transfer_from_527_to_528=True))

    def test_false_transfer_527_to_529(self):
        self.reject(lambda d: d["comparison"].update(identity_transfer_from_527_to_529=True))

    def test_launder_legacy_raan(self):
        self.reject(lambda d: d["comparison"].update(legacy_raan_2841520_observed=True))

    def test_launder_secondary_raan(self):
        self.reject(lambda d: d["comparison"].update(
            secondary_raan_1985261_authenticated_primary=True))

    def test_false_instrumental_independence(self):
        self.reject(lambda d: d["comparison"].update(
            tracking_lineage_independence="INDEPENDENT"))

    def test_gcataux_not_a_global_negative(self):
        self.reject(lambda d: d["comparison"].update(
            gcat_auxcat_absence_is_not_global_catalog_absence=False))

    def test_source_hash_not_made_up(self):
        self.reject(lambda d: d["sources"][1].update(source_sha256="0" * 64))

    def test_gcat_classification_cannot_be_relabelled(self):
        self.reject(lambda d: d["sources"][1].update(classification_code="P"))

    def test_debris_cannot_be_given_engineering_identity(self):
        self.reject(lambda d: d["sources"][3].update(engineering_piece="panel"))

    def test_nasa_not_raw_sensor(self):
        self.reject(lambda d: d["sources"][0].update(raw_sensor_records=["imagined"]))

    def test_no_lean_or_site_promotion(self):
        self.reject(lambda d: d["comparison"].update(conde_outcome="IMPACT_PROVEN"))

    def test_edges_are_not_sensor_observations(self):
        self.reject(lambda d: d["edges"][0].update(independent_sensor=True))


if __name__ == "__main__":
    unittest.main()
