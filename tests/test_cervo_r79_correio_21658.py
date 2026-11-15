"""Scientific custody and bounded page reading C241-CERVO-R79.

Checks the interpretation manifest, not the historical authenticity of the PDF.
"""
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_correio_manha_1963_11_10_C241_CERVO_R79.json"
NOTE = ROOT / "research/editorial/c241_cervo_r79_correio_manha_1963_11_10_p01_08.md"
MANIFEST_SHA256 = "dc2b44283f91157ab706e0ae39145575b6008f4c05ce6d66d96629f9a568ec19"
NOTE_SHA256 = "c48e9fe6e78024ca51ddd8ec432d68f9150fb2441ae99cea133cd21ada0be447"
PDF_SHA256 = "75dc400708e80022dc9d1a139739068417e65ff47a3c4130bf0b46b9db4929f3"


class CervoR79Custody(unittest.TestCase):
    def setUp(self):
        self.raw = MANIFEST.read_bytes()
        self.record = json.loads(self.raw)

    def test_canonical_interpretation_unchanged(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), MANIFEST_SHA256)
        self.assertEqual(hashlib.sha256(NOTE.read_bytes()).hexdigest(), NOTE_SHA256)

    def test_source_custody_and_scope(self):
        r = self.record
        self.assertEqual(r["source_id"], "C241-CERVO-R79-CM-19631110-P01-P08")
        self.assertEqual(r["pdf_sha256"], PDF_SHA256)
        self.assertEqual(r["pdf_bytes"], 62742698)
        self.assertEqual(r["pdf_pages"], 97)
        self.assertEqual(r["edition"], "21658")
        self.assertEqual(r["date_of_publication"], "1963-11-10")
        self.assertFalse(r["full_edition_examined"])
        self.assertEqual((r["pages_integrally_read"], r["pages_pending"]), (8, 89))
        self.assertEqual(r["pages_integrally_read"] + r["pages_pending"], 97)

    def test_exhaustive_eight_page_ledger(self):
        pages = self.record["pages_examined"]
        self.assertEqual([p["pdf_page"] for p in pages], list(range(1, 9)))
        self.assertEqual([p["printed_page"] for p in pages], list(range(1, 9)))
        self.assertEqual({p["status"] for p in pages}, {"EXAMINADA"})
        self.assertEqual(len(set(p["pdf_page"] for p in pages)), 8)
        for p in pages:
            self.assertIsNone(p["conde_event_time_literal"])
            self.assertIsNone(p["conde_eyewitness"])
            self.assertTrue(p["subject"])

    def test_article_not_published_day_as_event_time(self):
        r = self.record
        a = r["related_article"]
        self.assertEqual(a["pdf_page"], 8)
        self.assertEqual(a["title"], "PRECIPITAÇÃO DE OBJETOS CONTINUA")
        self.assertEqual(a["previous_source"], "C241-TARTARUGA-R72-CM-19631110")
        self.assertEqual(a["independence_of_underlying_information"], "UNDETERMINED")
        self.assertIsNone(a["event_time_literal"])
        self.assertIsNone(a["eyewitness_at_conde"])
        self.assertIsNone(r["independent_conde_event_hour"])
        self.assertIsNone(r["terminal_time_sigma_hours"])
        self.assertFalse(r["active_constraint_528"])
        self.assertEqual(r["historical_mcmc"], "NOT_RUN")
        self.assertIn("not whole edition", r["negative_scope"].lower())

    def test_note_respects_edition_scope(self):
        text = NOTE.read_text(encoding="utf-8")
        self.assertIn("8/97", text)
        self.assertIn("89/97", text)
        self.assertIn(PDF_SHA256, text)
        self.assertIn("UNDETERMINED", text)
        self.assertIn("EXAMINADA", text)
        self.assertIn("historical_mcmc=NOT_RUN", text)


if __name__ == "__main__":
    unittest.main()
