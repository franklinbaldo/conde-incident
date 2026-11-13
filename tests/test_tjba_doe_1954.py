"""Contraprovas contra falsificação de custódia e promoção documental."""

import copy
import json
import os
import unittest
from pathlib import Path

from tools.verify_tjba_doe_1954 import MANIFEST, verify_manifest, verify_pdf


def original_pdf() -> Path:
    return Path(os.environ.get(
        "CONDE_TJBA_JAN_1954_PDF",
        "/workspace/lontra-round21-cache/DOE_Bahia_jan_1954_Archidoc.pdf",
    ))


class TestJan1954Volume(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_catalog_manifest(self):
        self.assertEqual(verify_manifest(self.data), [])

    def test_wrong_resource_is_rejected(self):
        tampered = copy.deepcopy(self.data)
        tampered["download_resource_id"] = "dfdig000000000000000000000009008"
        self.assertTrue(verify_manifest(tampered))

    def test_unsupported_legal_conclusion_is_rejected(self):
        tampered = copy.deepcopy(self.data)
        tampered["lei_628_1953_publication_date_proven"] = True
        self.assertTrue(verify_manifest(tampered))

    def test_cross_month_dependency_is_preserved(self):
        tampered = copy.deepcopy(self.data)
        tampered["related_previous_volume_id"] = None
        self.assertTrue(verify_manifest(tampered))

    def test_wrong_digest_against_source(self):
        p = original_pdf()
        if not p.exists():
            self.skipTest("full primary PDF not cached here")
        tampered = copy.deepcopy(self.data)
        tampered["pdf_sha256"] = "0" * 64
        self.assertIn("SHA256 mismatch", verify_pdf(p, tampered))

    def test_replay_of_primary_pdf(self):
        p = original_pdf()
        if not p.exists():
            self.skipTest("full primary PDF not cached here")
        self.assertEqual(verify_pdf(p, self.data), [])


if __name__ == "__main__":
    unittest.main()
