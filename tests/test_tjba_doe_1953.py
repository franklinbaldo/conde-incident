"""Adversarial tests for December 1953 monthly gazette custody."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.verify_tjba_doe_1953 import MANIFEST, verify_manifest, verify_pdf

BASE = json.loads(MANIFEST.read_text(encoding="utf-8"))


class TjbaDoe1953Tests(unittest.TestCase):
    def test_verified_monthly_volume_metadata(self):
        self.assertEqual(verify_manifest(BASE), [])

    def test_not_yet_read_law_cannot_be_promoted(self):
        for key in (
            "lei_628_1953_text_located_in_this_volume",
            "lei_628_1953_publication_date_proven",
            "annex_vi_text_corrected_against_1953_print",
            "acts_1959_1963_exhaustively_checked",
            "legal_boundary_1963_demonstrated",
            "orbital_constraint_activated",
        ):
            bad = copy.deepcopy(BASE)
            bad[key] = True
            self.assertTrue(verify_manifest(bad), key)

    def test_source_identity_and_size_cannot_be_swapped(self):
        for key, value in (
            ("catalog_node_id", "arbitrary"),
            ("download_resource_id", "arbitrary"),
            ("pdf_bytes", 123),
            ("pdf_sha256", "0" * 64),
            ("pdf_pages_tree_count", 822),
            ("archivist_status", "LAW_VERIFIED"),
            ("http_status", 404),
            ("download_url", "https://example.org/1953.pdf"),
        ):
            bad = copy.deepcopy(BASE)
            bad[key] = value
            self.assertTrue(verify_manifest(bad), key)

    def test_binary_replay_positive_and_adversarial(self):
        binary = b"%PDF-1.5\n1 0 obj\n<<>>\nendobj\nstartxref\n10\n%%EOF\n"
        local = copy.deepcopy(BASE)
        local["pdf_bytes"] = len(binary)
        local["pdf_sha256"] = hashlib.sha256(binary).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.pdf"
            path.write_bytes(binary)
            self.assertEqual(verify_pdf(path, local), [])
            path.write_bytes(binary[:-7])
            self.assertTrue(verify_pdf(path, local))
            altered = b"NOPE-1.5" + binary[8:]
            local["pdf_bytes"] = len(altered)
            local["pdf_sha256"] = hashlib.sha256(altered).hexdigest()
            path.write_bytes(altered)
            self.assertIn("PDF magic mismatch", verify_pdf(path, local))

    def test_integrity_not_equivalent_to_transcription(self):
        self.assertFalse(BASE["lei_628_1953_text_located_in_this_volume"])
        self.assertFalse(BASE["legal_boundary_1963_demonstrated"])
        self.assertEqual(BASE["pdf_page_objects_count"], 823)


if __name__ == "__main__":
    unittest.main()
