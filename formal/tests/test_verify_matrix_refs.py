"""Synthetic citation regression; no historical-body reconstruction."""
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_matrix_refs import MatrixAuditError, audit_rows, git_blob_sha1

SYNTHETIC = ("## Section A\n| C01 | synthetic report, not a fall |\n"
             "| C44 | soil proxy only |\n| C45 | geology proxy only |\n"
             "| C46 | conditional model only |\n## Section B\n"
             "| C44 | secondary TLE mirror only |\n"
             "| C45 | predicted phase only |\n"
             "| C46 | conditional orbital fit only |\n"
             "| **C197** | same NASA bulletin, not independent |\n").encode()
PINS = {"C01": (2,), "C44": (3, 7), "C45": (4, 8),
        "C46": (5, 9), "C197": (10,)}


class PinnedMatrixTests(unittest.TestCase):
    def test_git_blob_sha1_uses_framing(self):
        self.assertEqual(git_blob_sha1(b"test\n"), hashlib.sha1(b"blob 5\0test\n").hexdigest())
        self.assertNotEqual(git_blob_sha1(SYNTHETIC), hashlib.sha1(SYNTHETIC).hexdigest())

    def test_synthetic_rows_require_disambiguation(self):
        result = audit_rows(SYNTHETIC, pins=PINS, expected_blob=git_blob_sha1(SYNTHETIC))
        self.assertEqual(result["status"], "PINNED_MATRIX_ROWS_PASS_ONLY")
        self.assertEqual(result["ambiguous_ids"], ["C44", "C45", "C46"])
        self.assertEqual(len(result["references"]), 8)
        self.assertIn("NOT_VERIFIED", result["historical_source_status"])
        self.assertIn("NOT_RUN", result["original_lean_registry"])
        self.assertTrue(any(x["id"] == "C197" and x["line"] == 10 for x in result["references"]))

    def test_edited_bytes_cannot_silently_repinned(self):
        with self.assertRaisesRegex(MatrixAuditError, "Git blob mismatch"):
            audit_rows(SYNTHETIC + b"\n", pins=PINS,
                       expected_blob=git_blob_sha1(SYNTHETIC))

    def test_off_by_one_pin_fails_even_with_matching_blob(self):
        with self.assertRaisesRegex(MatrixAuditError, "C01 rows"):
            audit_rows(SYNTHETIC, pins={"C01": (3,)},
                       expected_blob=git_blob_sha1(SYNTHETIC))

    def test_collision_loss_fails_even_with_matching_blob(self):
        with self.assertRaisesRegex(MatrixAuditError, "C44 rows"):
            audit_rows(SYNTHETIC, pins={"C44": (3,)},
                       expected_blob=git_blob_sha1(SYNTHETIC))

    def test_bold_markdown_id_is_accepted(self):
        result = audit_rows(SYNTHETIC, pins={"C197": (10,)},
                            expected_blob=git_blob_sha1(SYNTHETIC))
        self.assertEqual(result["references"][0]["line"], 10)


if __name__ == "__main__":
    unittest.main()
