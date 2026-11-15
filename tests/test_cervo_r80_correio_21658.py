"""Scientific custody and bounded interpretation tests, including Python -O mode."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_correio_manha_1963_11_10_C241_CERVO_R80.json"
NOTE = ROOT / "research/editorial/c241_cervo_r80_correio_manha_1963_11_10_p09_19.md"
PDF_SHA = "75dc400708e80022dc9d1a139739068417e65ff47a3c4130bf0b46b9db4929f3"
INTERPRETATION_SHA256 = "4a6e8faa1864df4590ca71e9766cfc7cf8cf8e33909ef1375ccf37d617f6ff18"
NOTE_SHA256 = "8156b2aeeebdc1934a5d777abbc4060209c06170427af11b56a4b7f7c6e707e2"


def interpretation_sha256(doc):
    payload = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_note(note):
    unittest.TestCase().assertEqual(
        hashlib.sha256(note.encode("utf-8")).hexdigest(), NOTE_SHA256,
        "editorial note changed without source review",
    )


def validate_record(r):
    """Must not use bare assert: optimization must preserve every invariant."""
    t = unittest.TestCase()
    t.assertEqual(interpretation_sha256(r), INTERPRETATION_SHA256,
                  "complete scientific interpretation changed")
    t.assertEqual(r["pdf_sha256"], PDF_SHA)
    t.assertEqual(r["pdf_bytes"], 62742698)
    t.assertEqual(r["pdf_pages"], 97)
    t.assertEqual(r["edition"], "21658")
    t.assertEqual(
        [(x["caderno"], x["pdf_first"], x["pdf_last"])
         for x in r["cadernos_mapped_not_integrally_read"]],
        [("1", 1, 19), ("2", 20, 39), ("3", 40, 68),
         ("4", 69, 76), ("5", 77, 83), ("6", 84, 89),
         ("suplemento_colorido", 90, 97)],
    )
    pages = r["pages_examined"]
    t.assertEqual([x["pdf_page"] for x in pages], list(range(9, 20)))
    t.assertEqual([x["printed_page"] for x in pages], list(range(9, 20)))
    t.assertTrue(all(x["status"] == "EXAMINADA" and x["subject"] for x in pages))
    for page in pages:
        t.assertIsNone(page["conde_event_time_literal"])
        t.assertIsNone(page["conde_eyewitness"])
    t.assertIs(r["first_caderno_complete"], True)
    t.assertEqual(r["first_caderno_pages_integrally_examined"], 19)
    t.assertEqual(r["pages_integrally_examined_in_this_record"], 11)
    t.assertEqual(r["pages_not_integrally_read"], 78)
    t.assertIs(r["full_edition_examined"], False)
    t.assertEqual(r["related_section"]["pdf_page"], 19)
    t.assertEqual(r["related_section"]["title"], "Aviação e Astronáutica")
    t.assertIsNone(r["related_section"]["hour_of_conde_event"])
    t.assertIsNone(r["related_section"]["named_eyewitness_at_conde"])
    t.assertEqual(r["false_clock"]["pdf_page"], 14)
    t.assertEqual(r["false_clock"]["printed_time"], "23:40")
    t.assertEqual(
        r["false_clock"]["relevance"],
        "PROGRAMA_DE_TV_NAO_HORA_DO_EVENTO_NEM_RELOGIO_FBIS_TUPI_RADIO_08_NOV",
    )
    t.assertIsNone(r["independent_conde_event_hour"])
    t.assertEqual(r["source_independence"], "UNDETERMINED")
    t.assertIsNone(r["terminal_time_sigma_hours"])
    t.assertIs(r["active_constraint_528"], False)
    t.assertEqual(r["historical_mcmc"], "NOT_RUN")
    t.assertIn("não lidas", r["negative_scope"])


class Core21658(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_canonical_scientific_scope(self):
        validate_record(self.record)

    def test_note_and_pdf_identifiers(self):
        note = NOTE.read_text(encoding="utf-8")
        validate_note(note)
        self.assertIn(PDF_SHA, note)
        self.assertIn("78 das 97 páginas", note)
        self.assertIn("Aviação e Astronáutica", note)
        self.assertIn("23h40", note)
        self.assertIn("historical_mcmc=NOT_RUN", note)

    def test_adversarial_subject_prose_rejected(self):
        r = copy.deepcopy(self.record)
        r["pages_examined"][0]["subject"] += "; NASA confirmou Conde às 20h15"
        with self.assertRaises(AssertionError):
            validate_record(r)

    def test_adversarial_note_prose_rejected(self):
        note = NOTE.read_text(encoding="utf-8")
        with self.assertRaises(AssertionError):
            validate_note(note + "\nNASA confirmou queda em Conde às 20h15.\n")

    def test_adversarial_invented_conde_hour_rejected(self):
        r = copy.deepcopy(self.record)
        r["pages_examined"][0]["conde_event_time_literal"] = "23:40"
        with self.assertRaises(AssertionError):
            validate_record(r)

    def test_adversarial_tv_hour_promoted_rejected(self):
        r = copy.deepcopy(self.record)
        r["independent_conde_event_hour"] = "23:40"
        with self.assertRaises(AssertionError):
            validate_record(r)

    def test_adversarial_editional_negative_rejected(self):
        r = copy.deepcopy(self.record)
        r["full_edition_examined"] = True
        with self.assertRaises(AssertionError):
            validate_record(r)


if __name__ == "__main__":
    unittest.main()
