"""Regression against silent historical ID collisions during Lean corpus recovery."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal/scripts"))
from audit_legacy_154 import audit, parse_evidence, parse_matrix  # noqa: E402


class LegacyEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = (ROOT / "formal/Conde1963/Evidence.lean").read_bytes()
        cls.matrix = (ROOT / "research/evidence_matrix_C001-C238_2026-11-11.md").read_bytes()
        cls.report = audit(cls.evidence, cls.matrix)

    def test_154_entries_151_labels_and_c44_c46_occurrences(self):
        report = self.report
        self.assertEqual((report["legacy_rows"], report["legacy_distinct_claim_ids"]), (154, 151))
        self.assertEqual(report["legacy_duplicate_variants"],
                         ["C44#1", "C44#2", "C45#1", "C45#2", "C46#1", "C46#2"])

    def test_146_exact_records_and_eight_recycled_aliases(self):
        self.assertEqual(self.report["identical_current_occurrences"], 146)
        self.assertEqual([x["old_key"] for x in self.report["claim_aliases_requiring_snapshot_qualified_ids"]],
                         [f"C{i}" for i in range(144, 152)])
        for legacy in self.report["claim_aliases_requiring_snapshot_qualified_ids"]:
            self.assertNotEqual(legacy["old_claim"], legacy["current_claim"])

    def test_c151_legacy_kinematics_is_not_current_recife_wind(self):
        evidence = {r["key"]: r for r in parse_evidence(self.evidence)}
        matrix = parse_matrix(self.matrix)
        self.assertIn("triangulação", evidence["C151"]["summary"])
        self.assertIn("Ventos medidos", matrix[151][0])
        self.assertNotIn("Ventos medidos", evidence["C151"]["source"])

    def test_byte_change_in_legacy_corpus_must_fail(self):
        mutated = self.evidence.replace(b"Esfera met", b"Esfera Xet", 1)
        self.assertNotEqual(mutated, self.evidence)
        with self.assertRaisesRegex(ValueError, "pinned local preserved bytes"):
            audit(mutated, self.matrix)

    def test_matrix_relabeling_requires_new_explicit_audit(self):
        mutated = self.matrix.replace(b"Ventos medidos em 8/11", b"Ventos estimados em 8/11", 1)
        self.assertNotEqual(mutated, self.matrix)
        with self.assertRaisesRegex(ValueError, "matrix snapshot differs"):
            audit(self.evidence, mutated)


if __name__ == "__main__":
    unittest.main()
