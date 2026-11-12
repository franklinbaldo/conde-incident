"""Matrix-to-Lean contracts: deterministic coverage, no evidence promotion."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal" / "scripts"))
from evidence_registry import (  # noqa: E402
    InventoryError, audit, contracts, parse_rows, render_lean
)

MATRIX = ROOT / "research" / "evidence_matrix_C001-C238_2026-11-11.md"
LEAN = ROOT / "formal" / "Conde1963" / "MatrixEvidence.lean"


class MatrixEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = MATRIX.read_bytes()
        cls.rows = parse_rows(cls.raw)

    def test_full_documentary_inventory(self):
        report = audit(self.raw, self.rows)
        self.assertEqual(report["occurrences"], 241)
        self.assertEqual(report["unique_labels"], 238)
        self.assertEqual(report["collision_labels"], ["C44", "C45", "C46"])

    def test_collisions_not_overwritten(self):
        for number, expected_lines in {
            44: [164, 175], 45: [165, 176], 46: [166, 177]
        }.items():
            records = [r for r in self.rows if r["number"] == number]
            self.assertEqual([r["occurrence"] for r in records], [1, 2])
            self.assertEqual([r["line"] for r in records], expected_lines)

    def test_generated_lean_in_repository_matches_matrix_exactly(self):
        self.assertEqual(LEAN.read_text(encoding="utf-8"), render_lean(self.rows))

    def test_mutated_source_blob_is_rejected(self):
        tampered = self.raw.replace(b"| C01 |", b"| C99 |", 1)
        self.assertNotEqual(tampered, self.raw)
        with self.assertRaisesRegex(InventoryError, "blob changed"):
            audit(tampered, parse_rows(tampered))

    def test_missing_row_rejected_even_without_blob_guard(self):
        fewer = [r for r in self.rows if r["number"] != 238]
        with self.assertRaisesRegex(InventoryError, "241 rows"):
            audit(self.raw, fewer, strict_hash=False)

    def test_duplicate_occurrence_rejected(self):
        corrupted = [dict(row) for row in self.rows]
        second = next(r for r in corrupted if r["number"] == 44 and r["occurrence"] == 2)
        second["occurrence"] = 1
        with self.assertRaisesRegex(InventoryError, "occurrence"):
            audit(self.raw, corrupted, strict_hash=False)

    def test_unjustified_filter_promotion_rejected(self):
        corrupted = [dict(row) for row in self.rows]
        corrupted[0]["role"] = "nasaReportedDecayDay"
        with self.assertRaisesRegex(InventoryError, "unreviewed physical promotion"):
            audit(self.raw, corrupted, strict_hash=False)


    def test_uncertainty_is_explicit_for_every_record(self):
        out = contracts(self.rows)
        self.assertEqual(out["schema_version"], 2)
        self.assertEqual(len(out["entries"]), 241)
        self.assertEqual(
            sum(x["epistemic_uncertainty"] == "requiresIndividualAssessment"
                for x in out["entries"]), 238
        )
        self.assertTrue(all(x["epistemic_uncertainty"] and x["uncertainty_basis"]
                            for x in out["entries"]))
        self.assertTrue(all(x["numeric_error_bounds"] is None
                            for x in out["entries"]))
        self.assertEqual([x["id"] for x in out["entries"]
                          if x["epistemic_uncertainty"] ==
                          "reportedCatalogueDayActualDayUnknown"], ["C131", "C197"])

    def test_promoting_uncertainty_without_review_is_rejected(self):
        altered = [dict(row) for row in self.rows]
        altered[0]["uncertainty"] = "reportedCatalogueDayActualDayUnknown"
        with self.assertRaisesRegex(InventoryError, "uncertainty promotion"):
            audit(self.raw, altered, strict_hash=False)

    def test_export_preserves_all_rows_and_lineage_limits(self):
        out = contracts(self.rows)
        self.assertEqual(len(out["entries"]), 241)
        same_source = [x for x in out["entries"] if x["source_chain"]]
        self.assertEqual([x["id"] for x in same_source], ["C131", "C197"])
        self.assertEqual(len({(x["id"], x["occurrence"]) for x in out["entries"]}), 241)
        self.assertTrue(all(x["citation"].endswith(f'#L{x["line"]}')
                            for x in out["entries"]))
        self.assertTrue(all(x["source_status"] == "MATRIX_ONLY_NOT_REINSPECTED_THIS_RUN"
                            for x in out["entries"]))
        self.assertEqual(sum(x["physical_encoding"] ==
            "NASA_CATALOGUED_DATE_HYPOTHESIS_NOT_HARD_FILTER" for x in out["entries"]), 2)


if __name__ == "__main__":
    unittest.main()
