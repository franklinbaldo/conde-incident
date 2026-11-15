"""C241-R82: independent runtime gates for three newly read press pages."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research/archive/conde_correio_manha_1963_11_12_C241_TARTARUGA_R82.json"
PREDECESSOR = ROOT / "research/archive/conde_correio_manha_1963_11_12_14_C241_TARTARUGA_R81.json"
SHA = "a744f75a91462d2246ecf905353143ffe72a9c326ab0462a1241a4db3a2bc606"
EXPECTED_SUBJECTS = [
    "Brasília/Fatos e Personagens: Biblioteca do Trabalhador and atomic-energy meeting; Rio education council; newborn mix-up at maternity hospital; Brigitte Bardot rumor; commercial advertisements.",
    "Brazil-France diplomatic relations; Congresso and party politics; historical article on Anchieta and the foundation of São Paulo; political commentary; essay on free will.",
    "Editorial/opinion page on nationalization of private oil refineries and Capuava. Reprinted commentary cites Jornal do Brasil, Última Hora, O Globo, Diário de São Paulo and Folha de São Paulo from 8–11 November, all concerning petroleum, not the Conde occurrence.",
]
EXPECTED_CLOCKS = [
    ["20h = inauguration of Brasília workers' library", "21h = piano concert in Brasília", "até 22 horas = apartment-sales advertisement"],
    [],
    ["8–11 November 1963 = newspaper publication dates for reprinted petroleum opinion, not local event times"],
]

def pairs_no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key: " + key)
        obj[key] = value
    return obj

def load(path=FILE):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_no_duplicates)

def validate(doc, previous=None):
    def require(ok, message):
        if not ok:
            raise ValueError(message)

    require(set(doc) == {"schema","id","checked_utc_date","research_issue",
                        "predecessor_manifest","source","method","readings",
                        "scope","conclusion"}, "unexpected root fields")
    require(doc["schema"] == "conde.local_clock_press_nucleus_increment/v1", "schema")
    require(doc["id"] == "C241-TARTARUGA-R82" and doc["research_issue"] == 871
            and doc["checked_utc_date"] == "2026-11-15", "identity")
    require(doc["predecessor_manifest"] == str(PREDECESSOR.relative_to(ROOT)), "ancestor path")
    s = doc["source"]
    require(set(s) == {"collection","edition","printed_date","original_url","original_bytes",
                       "original_sha256","pdf_pages","first_caderno_pdf_start",
                       "first_caderno_pdf_end"}, "source fields")
    require(s["collection"] == "Hemeroteca Digital BN, Correio da Manhã, coleção 089842", "archive")
    require(s["edition"] == "21659" and s["printed_date"] == "1963-11-12", "issue/date")
    require(s["original_url"] == "https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_21659.pdf", "source URL")
    require(s["original_sha256"] == SHA and s["original_bytes"] == 20179037
            and s["pdf_pages"] == 28, "original bytes")
    require(s["first_caderno_pdf_start"] == 1 and s["first_caderno_pdf_end"] == 15, "first caderno")
    m = doc["method"]
    require(m["executor"] == "Ifro" and m["control_plane"] ==
            "Jatobá, SSH, explicit max_memory_mb=128", "execution provenance")
    require(m["original_reused_from"] == "/var/tmp/lagarto-r75-20261115/21659.pdf", "original custody")
    require(m["visual_exam"] ==
            "Each page rendered at 175 dpi and inspected in six overlapping crops (2 columns x 3 rows); headlines, body text, captions and advertising included; OCR is auxiliary only.", "visual protocol")
    require(m["render_software"] == "pdftoppm; Pillow"
            and m["page_reading_is_not_edition_negative"] is True, "visual method")
    rows = doc["readings"]
    require(len(rows) == 3, "exactly three pages read")
    for i, row in enumerate(rows):
        p = i + 5
        allowed = {"pdf_page","printed_folio","status","subjects","unrelated_clock_labels",
                   "conde_article","conde_event_hour_literal","independent_eyewitness",
                   "attribution","orbital_constraint_active"}
        if p == 7:
            allowed = allowed | {"printed_folio_note","reprint_attribution_is_independent_conde_source"}
        require(set(row) == allowed, "page fields")
        require(row["pdf_page"] == p and row["status"] == "EXAMINADA", "page/status")
        require(row["printed_folio"] == (str(p) if p < 7 else None), "printed folio")
        require(row["subjects"] == EXPECTED_SUBJECTS[i], "unreviewed prose or new article")
        require(row["unrelated_clock_labels"] == EXPECTED_CLOCKS[i], "false event clock")
        require(row["conde_article"] is None and row["conde_event_hour_literal"] is None
                and row["independent_eyewitness"] is None and row["attribution"] is None,
                "fabricated Conde evidence")
        require(row["orbital_constraint_active"] is False, "premature orbital exclusion")
    require(rows[2]["printed_folio_note"] ==
            "Numeral at top right is not completely unambiguous in the facsimile; do not infer a definitive printed folio.", "folio uncertainty")
    require(rows[2]["reprint_attribution_is_independent_conde_source"] is False, "false independence")
    scope = doc["scope"]
    require(scope["edition"] == "21659", "scope edition")
    require(scope["previously_examined_pages"] == [1,2,3,4], "prior four")
    require(scope["newly_examined_pages"] == [5,6,7], "increment")
    require(scope["cumulatively_examined_pages"] == list(range(1,8)), "cumulative")
    require(scope["remaining_unread_first_caderno_pages"] == list(range(8,16)), "unread not promoted")
    for flag in ["first_caderno_fully_examined","entire_edition_fully_examined","global_negative_asserted"]:
        require(scope[flag] is False, "falsely complete: "+flag)
    require(scope["other_editions_21660_21661"] == "CUSTODIED_SECTION_MAPPED_NOT_VISUALLY_READ", "other editions unread")
    c = doc["conclusion"]
    require(c["classification"] == "THREE_PAGE_LOCAL_NEGATIVE_21659", "classification")
    require(c["conde_event_hour_literal"] is None and c["independent_eyewitness"] is None, "global invented evidence")
    require(c["report_independence_from_tupi_fbis_diarios_associados"] == "UNDETERMINED", "independence")
    require(c["excludes_norad_528_or_637"] is False, "no physical exclusion")
    require(c["next_action"] == "Read Correio da Manhã 21659 first-caderno PDF pages 8–15, then 21660 PDF 1–12 and 21661 PDF 1–13, subject to the current Elefante orders.", "next action")
    if previous is not None:
        require(previous["id"] == "C241-TARTARUGA-R81", "ancestor id")
        require(previous["sources"][0]["sha256"] == s["original_sha256"], "same original")
        require(previous["reading"]["new_pages_fully_examined"] == [1,2,3,4], "ancestor coverage")
        require(previous["reading"]["remaining_first_caderno_pages_not_fully_read"] == list(range(5,16)), "ancestor gap")
    return True

class TestC241R82(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load()
        cls.previous = load(PREDECESSOR)

    def test_baseline_and_ancestor(self):
        self.assertTrue(validate(self.doc, self.previous))

    def reject(self, setter):
        altered = copy.deepcopy(self.doc)
        setter(altered)
        with self.assertRaises(ValueError):
            validate(altered, self.previous)

    def test_hour_invented(self):
        self.reject(lambda d: d["readings"][0].__setitem__("conde_event_hour_literal", "20h15"))

    def test_witness_invented(self):
        self.reject(lambda d: d["readings"][1].__setitem__("independent_eyewitness", "X"))

    def test_reprint_misclassified(self):
        self.reject(lambda d: d["readings"][2].__setitem__("reprint_attribution_is_independent_conde_source", True))

    def test_global_negative_invented(self):
        self.reject(lambda d: d["scope"].__setitem__("global_negative_asserted", True))

    def test_remaining_pages_erased(self):
        self.reject(lambda d: d["scope"].__setitem__("remaining_unread_first_caderno_pages", []))

    def test_folio_invented(self):
        self.reject(lambda d: d["readings"][2].__setitem__("printed_folio", "7"))

    def test_other_editions_promoted(self):
        self.reject(lambda d: d["scope"].__setitem__("other_editions_21660_21661", "FULLY_EXAMINED"))

    def test_orbit_activated(self):
        self.reject(lambda d: d["conclusion"].__setitem__("excludes_norad_528_or_637", True))

    def test_original_hash_modified(self):
        self.reject(lambda d: d["source"].__setitem__("original_sha256", "0"*64))

    def test_unreviewed_prose_changed(self):
        self.reject(lambda d: d["readings"][2].__setitem__("subjects", "NASA proved a crash"))

    def test_extra_field_rejected(self):
        self.reject(lambda d: d.__setitem__("certainty", 1.0))

    def test_duplicate_keys_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"dup.json"
            path.write_text('{"issue":871,"issue":872}',encoding="utf-8")
            with self.assertRaises(ValueError):
                load(path)

if __name__ == "__main__":
    unittest.main()
