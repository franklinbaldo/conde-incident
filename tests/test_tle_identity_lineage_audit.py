"""C241-T8 adversarial SYNTHETIC controls, not 1963 observations."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tle_identity_lineage_audit import (
    audit_identity, check_catalog_ledger, normalize_designator, EXPECTED,
    CSV_SHA256, file_sha256,
)
from tle_literal_layout import audit_literal_file

LEDGER_PATH = ROOT / "research/tle_custody/catalog_identity_527_529_2026-11-12.json"
PAIR_PATH = ROOT / "research/tle_custody/mirror_528_1963-10-27.tle"


def fixture():
    """Counts and duplicated dates modeled after shape, all records SYNTHETIC."""
    result = []
    index = 0
    for sat, count, distinct in ((527, 21, 20), (528, 45, 45), (529, 57, 54)):
        for pos in range(count):
            # Within same catalog, the final rows copy dates, not states.
            day = (pos % distinct) + 1
            result.append({
                "norad_id": str(sat), "source_row": str(index),
                "epoch": f"1963-01-{day:02d}T00:00:00.000000Z" if day <= 31
                         else f"1963-02-{day - 31:02d}T00:00:00.000000Z",
                "intl_designator": f"63003 {EXPECTED[sat][-1]}",
            })
            index += 1
    return result


def pair_report():
    report = audit_literal_file(PAIR_PATH)
    report["line1_intl_designator_literal"] = \
        PAIR_PATH.read_text(encoding="ascii").splitlines()[0][9:17]
    return report


class CatalogIdentityControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        cls.pair = pair_report()

    def audit(self, rows=None, ledger=None, pair=None):
        return audit_identity(
            fixture() if rows is None else rows,
            copy.deepcopy(self.ledger) if ledger is None else ledger,
            copy.deepcopy(self.pair) if pair is None else pair,
            csv_sha="SYNTHETIC_NO_REAL_CSV",
        )

    def test_tle_and_catalog_notation_normalize_to_same_cospar(self):
        for raw in ("63003 B", "63003  B", "1963-003B", "1963 003 B"):
            self.assertEqual(normalize_designator(raw), "1963-003B")

    def test_wrong_year_launch_piece_format_fail(self):
        for wrong in ("64003 B", "63030 B", "63003", "63003 AB", "1963-003Z?"):
            with self.subTest(raw=wrong), self.assertRaises(ValueError):
                normalize_designator(wrong)

    def test_expected_triplet_maps_to_one_launch_not_one_physical_body(self):
        report = self.audit()
        self.assertEqual(report["shared_launch_identity"], "1963-003")
        self.assertEqual({k: v["cospar"] for k, v in report["catalog_join"].items()},
                         {"527": "1963-003A", "528": "1963-003B",
                          "529": "1963-003C"})
        self.assertEqual({k: v["rows"] for k, v in report["catalog_join"].items()},
                         {"527": 21, "528": 45, "529": 57})
        self.assertEqual(report["physical_component_identity_528"], "NOT_RECOVERED")
        self.assertEqual(report["lean_physical_premise"], "NOT_PROMOTED")
        self.assertEqual(report["record_id"], "C241-L10")
        self.assertEqual(report["constraint_graph"]["state"], "CONNECTED_PENDING_CALIBRATION")
        self.assertIsNone(report["constraint_graph"]["measurement_sigma"])
        self.assertEqual(report["constraint_graph"]["lean_4_35_physical_predicate"], "NOT_PROMOTED")

    def test_duplicate_epoch_still_retained_with_source_row(self):
        report = self.audit()
        self.assertEqual(report["catalog_join"]["527"]["unique_epochs"], 20)
        self.assertEqual(report["catalog_join"]["529"]["unique_epochs"], 54)
        self.assertEqual(len(report["catalog_join"]["528"]["source_rows"]), 45)

    def test_incorrect_catalog_piece_fails_even_if_launch_matches(self):
        rows = fixture()
        row = next(x for x in rows if x["norad_id"] == "528")
        row["intl_designator"] = "63003 C"
        with self.assertRaisesRegex(ValueError, "identity conflict"):
            self.audit(rows=rows)

    def test_duplicate_source_row_and_catalog_mismatch_fail(self):
        rows = fixture()
        rows[1]["source_row"] = rows[0]["source_row"]
        with self.assertRaisesRegex(ValueError, "source_row"):
            self.audit(rows=rows)
        rows = fixture()
        rows[1]["norad_id"] = "00527"
        with self.assertRaisesRegex(ValueError, "NORAD"):
            self.audit(rows=rows)

    def test_truncated_or_wrong_date_counts_fail(self):
        with self.assertRaisesRegex(ValueError, "counts"):
            self.audit(rows=fixture()[:-1])
        rows = fixture()
        rows[0]["epoch"] = "1964-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "UTC"):
            self.audit(rows=rows)

    def test_literal_secondary_tle_has_valid_b_but_no_primary_claim(self):
        self.assertEqual(self.pair["line1_intl_designator_literal"], "63003  B")
        self.assertEqual(self.pair["catalog"], 528)
        self.assertEqual(self.pair["primary_norad_1963_provenance"], "NOT_VERIFIED")
        self.assertEqual(self.audit()["literal_528_cospar"], "1963-003B")

    def test_wrong_literal_piece_fails_closed(self):
        altered = copy.deepcopy(self.pair)
        altered["line1_intl_designator_literal"] = "63003  A"
        with self.assertRaisesRegex(ValueError, "TLE launch designator"):
            self.audit(pair=altered)

    def test_secondary_label_cannot_be_promoted_to_instrumental_independence(self):
        altered = copy.deepcopy(self.ledger)
        altered["provenance"]["independent_radar_observations_demonstrated"] = True
        with self.assertRaisesRegex(ValueError, "cannot promote"):
            self.audit(ledger=altered)
        altered = copy.deepcopy(self.ledger)
        altered["provenance"]["original_fragment_engineering_record"] = True
        with self.assertRaisesRegex(ValueError, "cannot promote"):
            self.audit(ledger=altered)

    def test_secondary_name_changes_and_unsourced_catalogs_fail(self):
        changed = copy.deepcopy(self.ledger)
        changed["sources"]["itau_528"]["display_name"] = "Agena B rocket body"
        with self.assertRaisesRegex(ValueError, "transcription mismatch"):
            self.audit(ledger=changed)
        changed = copy.deepcopy(self.ledger)
        changed["sources"]["new_radar"] = copy.deepcopy(changed["sources"]["itau_528"])
        with self.assertRaisesRegex(ValueError, "source inventory"):
            check_catalog_ledger(changed)

    def test_nasa_is_document_of_day_not_impact_or_fragment_mass(self):
        report = self.audit()
        nasa = report["source"]["nasa_date_only"]
        self.assertIn("mass", nasa["not_evidence_of"])
        self.assertIn("terminal position", nasa["not_evidence_of"])
        self.assertIn("impact", nasa["not_evidence_of"])
        self.assertEqual(report["status_for_conde"], "INDETERMINATE")

    def test_ledger_has_hash_and_tle_pair_is_immutable(self):
        self.assertEqual(len(file_sha256(LEDGER_PATH)), 64)
        self.assertEqual(self.pair["source"]["sha256"],
                         "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd")
        self.assertEqual(len(CSV_SHA256), 64)


if __name__ == "__main__":
    unittest.main()
