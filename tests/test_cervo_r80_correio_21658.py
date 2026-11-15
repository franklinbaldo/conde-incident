"""Guard bounded scientific interpretation of the Correio 21658 core, C241-R80."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_correio_manha_1963_11_10_C241_CERVO_R80.json"
NOTE = ROOT / "research/editorial/c241_cervo_r80_correio_manha_1963_11_10_p09_19.md"
PDF_SHA = "75dc400708e80022dc9d1a139739068417e65ff47a3c4130bf0b46b9db4929f3"


def validate_record(r):
    assert r["pdf_sha256"] == PDF_SHA
    assert r["pdf_bytes"] == 62742698
    assert r["pdf_pages"] == 97
    assert r["edition"] == "21658"
    assert [(x["caderno"], x["pdf_first"], x["pdf_last"])
            for x in r["cadernos_mapped_not_integrally_read"]] == [
                ("1", 1, 19), ("2", 20, 39), ("3", 40, 68),
                ("4", 69, 76), ("5", 77, 83), ("6", 84, 89),
                ("suplemento_colorido", 90, 97)]
    p = r["pages_examined"]
    assert [x["pdf_page"] for x in p] == list(range(9, 20))
    assert [x["printed_page"] for x in p] == list(range(9, 20))
    assert all(x["status"] == "EXAMINADA" and x["subject"] for x in p)
    assert all(x["conde_event_time_literal"] is None and x["conde_eyewitness"] is None for x in p)
    assert r["first_caderno_complete"] is True
    assert r["first_caderno_pages_integrally_examined"] == 19
    assert r["pages_integrally_examined_in_this_record"] == 11
    assert r["pages_not_integrally_read"] == 78
    assert r["full_edition_examined"] is False
    assert r["related_section"]["pdf_page"] == 19
    assert r["related_section"]["title"] == "Aviação e Astronáutica"
    assert r["related_section"]["hour_of_conde_event"] is None
    assert r["related_section"]["named_eyewitness_at_conde"] is None
    assert r["false_clock"]["pdf_page"] == 14
    assert r["false_clock"]["printed_time"] == "23:40"
    assert r["false_clock"]["relevance"] == "PROGRAMA_DE_TV_NAO_HORA_DO_EVENTO_NEM_RELOGIO_FBIS_TUPI_RADIO_08_NOV"
    assert r["independent_conde_event_hour"] is None
    assert r["source_independence"] == "UNDETERMINED"
    assert r["terminal_time_sigma_hours"] is None
    assert r["active_constraint_528"] is False
    assert r["historical_mcmc"] == "NOT_RUN"
    assert "não lidas" in r["negative_scope"]


class Core21658(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_canonical_scientific_scope(self):
        validate_record(self.record)

    def test_note_and_pdf_identifiers(self):
        n = NOTE.read_text(encoding="utf-8")
        self.assertIn(PDF_SHA, n)
        self.assertIn("78 das 97 páginas", n)
        self.assertIn("Aviação e Astronáutica", n)
        self.assertIn("23h40", n)
        self.assertIn("historical_mcmc=NOT_RUN", n)

    def test_adversarial_invented_conde_hour_rejected(self):
        r = json.loads(json.dumps(self.record))
        r["pages_examined"][0]["conde_event_time_literal"] = "23:40"
        with self.assertRaises(AssertionError):
            validate_record(r)

    def test_adversarial_tv_hour_promoted_rejected(self):
        r = json.loads(json.dumps(self.record))
        r["independent_conde_event_hour"] = "23:40"
        with self.assertRaises(AssertionError):
            validate_record(r)

    def test_adversarial_editional_negative_rejected(self):
        r = json.loads(json.dumps(self.record))
        r["full_edition_examined"] = True
        with self.assertRaises(AssertionError):
            validate_record(r)


if __name__ == "__main__":
    unittest.main()
