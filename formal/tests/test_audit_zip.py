"""Only synthetic *structural* tests; not the 1963 Lean corpus."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_zip import AuditError, audit_archive


def make_archive(path, *, duplicate=True, omit_evidence=False):
    # These are placeholder labels for testing count/collision logic, NOT
    # restored propositions or an assertion of historical content.
    entries = [{"id": f"C{i}"} for i in range(1, 152)]
    if duplicate:
        entries += [{"id": "C44"}, {"id": "C45"}, {"id": "C46"}]
    with ZipFile(path, "w") as zf:
        if not omit_evidence:
            zf.writestr("original/Evidence.lean", "-- SYNTHETIC, no historical claims")
        zf.writestr("original/evidence_registry.json", json.dumps(entries))
        zf.writestr("original/generate.py", "# synthetic placeholder")


class ArchiveAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "synthetic.zip"

    def verify(self, *, sha1=None, sha256=None):
        data = self.path.read_bytes()
        return audit_archive(
            self.path,
            expected_sha1=sha1 or hashlib.sha1(data).hexdigest(),
            expected_sha256=sha256 or hashlib.sha256(data).hexdigest(),
        )

    def test_synthetic_shape_passes_but_does_not_restore_history(self):
        make_archive(self.path)
        result = self.verify()
        self.assertEqual(result["propositions"], 154)
        self.assertEqual(result["distinct_labels"], 151)
        self.assertEqual(result["duplicate_labels"], ["C44", "C45", "C46"])
        self.assertEqual(result["status"], "STRUCTURE_PASS_ONLY")
        self.assertIn("NOT_VERIFIED", result["provenance_status"])
        self.assertIn("NOT_RUN", result["semantic_status"])
        self.assertIn("NOT a Lean recompilation", result["warning"])

    def test_wrong_hash_fails_before_content(self):
        make_archive(self.path)
        with self.assertRaisesRegex(AuditError, "SHA-256 mismatch"):
            self.verify(sha256="0" * 64)

    def test_missing_evidence_fails(self):
        make_archive(self.path, omit_evidence=True)
        with self.assertRaisesRegex(AuditError, "Evidence.lean"):
            self.verify()

    def test_wrong_counts_fail(self):
        make_archive(self.path, duplicate=False)
        with self.assertRaisesRegex(AuditError, "counts/collisions mismatch"):
            self.verify()

    def test_traversal_member_rejected_even_with_valid_digests(self):
        with ZipFile(self.path, "w") as zf:
            zf.writestr("../Evidence.lean", "-- SYNTHETIC")
            zf.writestr("evidence_registry.json", "[]")
        with self.assertRaisesRegex(AuditError, "unsafe ZIP member path"):
            self.verify()

    def test_duplicate_member_path_rejected_even_with_valid_digests(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(self.path, "w") as zf:
                zf.writestr("Evidence.lean", "-- SYNTHETIC A")
                zf.writestr("Evidence.lean", "-- SYNTHETIC B")
                zf.writestr("evidence_registry.json", "[]")
        with self.assertRaisesRegex(AuditError, "duplicate ZIP member path"):
            self.verify()

    def test_missing_provenance_hash_is_not_assumed(self):
        make_archive(self.path)
        with self.assertRaisesRegex(AuditError, "externally recorded 40-hex SHA-1"):
            self.verify(sha1="not-a-real-hash")

    def test_registry_requires_explicit_label_field(self):
        with ZipFile(self.path, "w") as zf:
            zf.writestr("Evidence.lean", "-- SYNTHETIC")
            zf.writestr("evidence_registry.json", json.dumps([{"claim": "C1"}]))
        with self.assertRaisesRegex(AuditError, "explicit key"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
