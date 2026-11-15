"""C241-R83: guard press-reading scope and reject invented Conde event times."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research/archive/conde_correio_manha_1963_11_12_C241_TARTARUGA_R83.json"
PREVIOUS = ROOT / "research/archive/conde_correio_manha_1963_11_12_C241_TARTARUGA_R82.json"
SHA = "a744f75a91462d2246ecf905353143ffe72a9c326ab0462a1241a4db3a2bc606"

EXPECTED_SUBJECTS = [
    "Varig PP-VJA forced landing at Santo Domingo after a false aircraft bomb report; tenant legislation; missing pet snake; labor union news; advertisements.",
    "Draft labor code at Ministry of Justice; MEC employee welfare; missing ruby in Sao Paulo; full-page Super Ford diesel advertisement.",
    "Rotten railroad ties derail passenger train near Austin/Nova Iguacu; road works; Belford Roxo child homicide; local police; lottery and commercial advertising.",
    "Samba congress at MAM; Niteroi civil-service proposals; state firefighter incorporation; fishing yields in Ceara; Pan Am flights advertisement.",
    "Furnas nature excursion on foot; Leopoldina railroad labor dispute; Rio and national weather forecast; Capuava refinery management statement; advertising.",
    "Official Santa Claus feature; evicted families in Guanabara; children's charity campaign; Petrobras hydroelectric plan; TV Excelsior serial advertisement.",
    "Economy and finance; UN meeting in Prague; South America capitalization notices; railway proposals; Air Force Directorate of Engineering public tenders for Fortaleza and Santos Dumont airports.",
    "Currency and securities quotations; agricultural commodities; prospective helicopter factory in Itu; Santo Domingo dollar exchange market; sea and air passenger advertising.",
]
EXPECTED_CLOCKS = [
    ["23h = aircraft radio/departure context, NOT a sky object over Conde"],
    [],
    ["7h30 = train derailment at kilometre 42 in Nova Iguacu", "17h = Belford Roxo family incident"],
    ["10h30/11h30 and 21h05 = Pan Am scheduled flights to Mexico", "21h = samba congress schedule"],
    ["8h30 = Furnas excursion assembly"],
    ["21h = TV Excelsior Os Intocaveis entertainment broadcast"],
    ["13h/14h = bid submission/opening schedules, not fall time"],
    ["11 November = foreign exchange quotation date", "21 November = maritime passenger schedule"],
]
EXPECTED_DISTINCTIONS = [
    "Aircraft false bomb scare was unrelated to a reentry",
    "No space-related article",
    "Rail transport disaster is not satellite descent",
    "Plane advertising and samba meetings do not timestamp Conde",
    "Meteorology concerns weather of named cities, not eyewitness sky observation in Conde",
    "TV Excelsior advertisement is not TV Tupi news nor an event time",
    "Ministry of Aeronautics notices concern airport construction only",
    "Helicopter factory and Santo Domingo forex report are not space-object reports",
]

def no_duplicates(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("duplicate JSON key: " + k)
        result[k] = v
    return result

def read(path=FILE):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)

def validate(doc, predecessor):
    def must(ok, reason):
        if not ok:
            raise ValueError(reason)

    must(set(doc) == {"schema", "id", "checked_utc_date", "research_issue", "predecessor_manifest",
                     "source", "method", "readings", "scope", "conclusion"}, "unexpected root")
    must(doc["schema"] == "conde.local_clock_press_nucleus_increment/v1", "schema")
    must(doc["id"] == "C241-TARTARUGA-R83" and doc["research_issue"] == 871
         and doc["checked_utc_date"] == "2026-11-15", "identity")
    must(doc["predecessor_manifest"] == str(PREVIOUS.relative_to(ROOT)), "predecessor path")
    s = doc["source"]
    must(set(s) == {"collection", "edition", "printed_date", "original_url", "original_bytes",
                    "original_sha256", "pdf_pages", "first_caderno_pdf_start",
                    "first_caderno_pdf_end", "second_caderno_pdf_start"}, "source fields")
    must(s["edition"] == "21659" and s["printed_date"] == "1963-11-12", "edition")
    must(s["original_url"] == "https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_21659.pdf", "URL")
    must(s["original_bytes"] == 20179037 and s["original_sha256"] == SHA, "original custody")
    must(s["pdf_pages"] == 28 and s["first_caderno_pdf_start"] == 1
         and s["first_caderno_pdf_end"] == 15 and s["second_caderno_pdf_start"] == 16, "caderno boundary")
    must(s["collection"] == "Hemeroteca Digital BN, Correio da Manhã, coleção 089842", "collection")
    must(predecessor["id"] == "C241-TARTARUGA-R82", "predecessor ID")
    must(predecessor["source"]["original_sha256"] == s["original_sha256"], "source continuity")
    must(predecessor["scope"]["cumulatively_examined_pages"] == list(range(1, 8)), "predecessor read")
    must(predecessor["scope"]["remaining_unread_first_caderno_pages"] == list(range(8, 16)), "predecessor gap")

    m = doc["method"]
    must(m["executor"] == "Ifro" and "max_memory_mb=128" in m["control_plane"], "execution chain")
    must(m["original_reused_from"] == "/var/tmp/lagarto-r75-20261115/21659.pdf", "source path")
    must(m["pages_full_visual_review"] == 8 and m["number_overlapping_crops"] == 48
         and m["scan_is_not_entire_edition_negative"] is True, "visual method")
    must("165-170 dpi" in m["visual_exam"] and "manual image inspection" in m["visual_exam"], "visual fidelity")
    rows = doc["readings"]
    must(isinstance(rows, list) and len(rows) == 8, "eight new pages")
    allowed = {"pdf_page", "printed_folio", "status", "subjects", "unrelated_clock_labels",
               "disambiguation", "conde_article", "conde_event_hour_literal",
               "independent_eyewitness", "report_attribution", "orbital_constraint_active"}
    for i, row in enumerate(rows):
        p = i + 8
        must(set(row) == allowed, "page fields")
        must(type(row["pdf_page"]) is int and row["pdf_page"] == p and row["status"] == "EXAMINADA", "page/status")
        must(row["printed_folio"] == (None if p == 12 else str(p)), "folio")
        must(row["subjects"] == EXPECTED_SUBJECTS[i], "unreviewed subject")
        must(row["unrelated_clock_labels"] == EXPECTED_CLOCKS[i], "false hour")
        must(row["disambiguation"] == EXPECTED_DISTINCTIONS[i], "uncertified interpretation")
        must(row["conde_article"] is None and row["conde_event_hour_literal"] is None
             and row["independent_eyewitness"] is None and row["report_attribution"] is None,
             "fabricated Conde evidence")
        must(row["orbital_constraint_active"] is False, "orbital inference")
    sc = doc["scope"]
    must(sc["edition"] == "21659" and sc["previously_examined_pages"] == list(range(1, 8)), "previous seven")
    must(sc["newly_examined_pages"] == list(range(8, 16)), "new eight")
    must(sc["cumulatively_examined_first_caderno_pages"] == list(range(1, 16)), "first caderno complete")
    must(sc["remaining_unread_first_caderno_pages"] == [] and sc["first_caderno_fully_examined"] is True, "first section scope")
    must(sc["second_caderno_read"] is False and sc["entire_edition_fully_examined"] is False
         and sc["global_negative_asserted"] is False, "fabricated global negative")
    must(sc["other_editions_21660_21661"] == "CUSTODIED_SECTION_MAPPED_NOT_VISUALLY_READ", "other issues pending")
    c = doc["conclusion"]
    must(c["classification"] == "EIGHT_PAGE_LOCAL_NEGATIVE_21659_FIRST_CADERNO_COMPLETED", "scope classification")
    must(c["conde_event_hour_literal"] is None and c["independent_eyewitness"] is None, "invented evidence")
    must(c["report_independence_from_tupi_fbis_diarios_associados"] == "UNDETERMINED", "source independence")
    must(c["excludes_norad_528_or_637"] is False, "no orbital exclusion")
    must(c["next_action"] == "Read edition 21660 PDF first-caderno pages 1-12 and edition 21661 PDF first-caderno pages 1-13; second cadernos only on explicit space/astronautics signal or new Elefante order.", "next work")
    return True

class TestC241R83(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.pre = read(), read(PREVIOUS)

    def test_baseline_and_predecessor(self):
        self.assertTrue(validate(self.doc, self.pre))

    def reject(self, mutation):
        altered = copy.deepcopy(self.doc)
        mutation(altered)
        with self.assertRaises(ValueError):
            validate(altered, self.pre)

    def test_invented_conde_hour(self):
        self.reject(lambda d: d["readings"][0].__setitem__("conde_event_hour_literal", "23h"))

    def test_false_train_hour_as_conde(self):
        self.reject(lambda d: d["readings"][2].__setitem__("unrelated_clock_labels", []))

    def test_false_tv_hour_as_conde(self):
        self.reject(lambda d: d["readings"][5].__setitem__("disambiguation", "Independent TV Tupi event"))

    def test_fabricated_eyewitness(self):
        self.reject(lambda d: d["readings"][4].__setitem__("independent_eyewitness", "Witness X"))

    def test_fabricated_attribution(self):
        self.reject(lambda d: d["readings"][7].__setitem__("report_attribution", "TV Tupi"))

    def test_page_scope_forgery(self):
        self.reject(lambda d: d["scope"].__setitem__("cumulatively_examined_first_caderno_pages", list(range(1, 29))))

    def test_global_negative_forgery(self):
        self.reject(lambda d: d["scope"].__setitem__("global_negative_asserted", True))

    def test_other_editions_forgery(self):
        self.reject(lambda d: d["scope"].__setitem__("other_editions_21660_21661", "FULLY_EXAMINED"))

    def test_orbit_conclusion_forgery(self):
        self.reject(lambda d: d["conclusion"].__setitem__("excludes_norad_528_or_637", True))

    def test_hash_tamper(self):
        self.reject(lambda d: d["source"].__setitem__("original_sha256", "0"*64))

    def test_unreviewed_subject(self):
        self.reject(lambda d: d["readings"][1].__setitem__("subjects", "Conde proved"))

    def test_overclaim_crops(self):
        self.reject(lambda d: d["method"].__setitem__("number_overlapping_crops", 100))

    def test_extra_field(self):
        self.reject(lambda d: d.__setitem__("certainty", 1))

    def test_duplicate_keys(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"issue":871,"issue":872}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read(path)

if __name__ == "__main__":
    unittest.main()
