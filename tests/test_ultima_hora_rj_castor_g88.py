"""C241-G88: audit a limited five-page visual second pass without promoting negatives."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from tools.audit_ultima_hora_rj_castor_g86 import validate as validate_g86

ROOT = Path(__file__).resolve().parents[1]
G88 = ROOT / "research/archive/ultima_hora_rj_1963_11_09_C241_CASTOR_G88.json"
G86 = ROOT / "research/archive/ultima_hora_rj_1963_11_09_10_C241_CASTOR_G86.json"
CANONICAL_SHA256 = "1cccb44fbfb8dcc964e4b5d56672ee8e7178a45856b30162126d914753b02f75"

def require(condition, detail):
    if not condition:
        raise ValueError(detail)

def validate(doc, parent):
    canonical = json.dumps(
        doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256,
            "G88 full interpreted record changed")
    validate_g86(parent)  # Source-only ancestor mutations must not pass.
    source = doc["source"]
    require(doc["schema"] == "conde.press_visual_review/v1" and doc["id"] == "C241-CASTOR-G88", "id")
    require(doc["date_reviewed"] == "2026-11-15", "review date")
    require(source["sha256"] == parent["source"]["sha256"] == "320aeb075b99fc6f2884904d9e1aa801b9d3f6be2b131ded30093caaaa6ce352", "source SHA")
    require(source["edition"] == parent["source"]["edition"] == "04200", "edition")
    require(source["cover_date"] == parent["source"]["date_from_cover"] == "1963-11-09", "cover date")
    require(source["url"] == parent["source"]["original_url"], "source URL")
    method = doc["method"]
    require(method["pdf_tool"] == "pdftoppm" and method["dpi"] == 190 and method["executor"] == "Ifro", "render")
    require(method["segments"] == "PAGE_UPPER_HALF_AND_LOWER_HALF", "visual scope")
    require(method["inspection"] == "HUMAN_VISUAL_WITH_EMBEDDED_TEXT_ONLY_AS_AUXILIARY", "OCR not negative")
    pages = doc["pages"]
    require(len(pages) == 5 and [p["pdf_page"] for p in pages] == [1,2,3,4,5], "pages")
    for p in pages:
        require(p["printed_page"] == p["pdf_page"], "print pagination")
        require(p["regions_inspected"] == ["upper_half","lower_half"], "regions")
        require(p["legibility"] == "PARTIAL_MICROTEXT_AND_PRINT_DEFECTS", "legibility")
        require(p["column_by_column_complete"] is False and p["whole_page_negative_certified"] is False, "false negative")
        require(p["independent_conde_event_time"] is None, "invented clock")
        require(bool(p["topics"]) and bool(p["assessment"]), "review descriptions")
    scope = doc["scope"]
    require(scope["pages_high_resolution_reviewed"] == 5 and scope["edition_pages"] == 16, "counts")
    require(scope["complete_edition_negative"] is False and scope["stop_criterion_met"] is False, "premature closure")
    require(scope["nov10_special_edition"] == "NOT_ESTABLISHED", "Sunday claim")
    it = doc["interpretation"]
    require(it == {"independent_conde_event_time":None,"contemporary_witness":None,"fbis_clock":"UNRESOLVED","orbit_exclusion_licensed":False,"theta_changed":False}, "unsupported orbital inference")
    return True

class TestG88(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(G88.read_text(encoding="utf-8"))
        cls.parent = json.loads(G86.read_text(encoding="utf-8"))

    def test_canonical(self):
        self.assertTrue(validate(self.doc, self.parent))

    def mutate(self, path, value):
        changed = copy.deepcopy(self.doc)
        node = changed
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(changed, self.parent)

    def test_reject_prose_mutation(self):
        self.mutate(["pages", 0, "assessment"],
                    "NASA confirmed fall in Conde at 20h15")

    def test_reject_ancestor_source_only(self):
        parent = copy.deepcopy(self.parent)
        parent["coverage"]["pages"][0]["topics"] = "NASA confirmed 20h15"
        with self.assertRaises(ValueError):
            validate(self.doc, parent)

    def test_fake_event_clock(self):
        self.mutate(["interpretation","independent_conde_event_time"], "1963-11-08T21:30:00-03:00")

    def test_fabricated_full_page_negative(self):
        self.mutate(["pages",0,"whole_page_negative_certified"], True)

    def test_fabricated_complete_reading(self):
        self.mutate(["pages",2,"column_by_column_complete"], True)

    def test_fabricated_edition_negative(self):
        self.mutate(["scope","complete_edition_negative"], True)

    def test_fake_sunday_edition(self):
        self.mutate(["scope","nov10_special_edition"], "ABSENT_PROVEN")

    def test_fake_sha(self):
        self.mutate(["source","sha256"], "0"*64)

    def test_fabricated_page_count(self):
        self.mutate(["scope","pages_high_resolution_reviewed"], 16)

    def test_fake_orbital_exclusion(self):
        self.mutate(["interpretation","orbit_exclusion_licensed"], True)

if __name__ == "__main__":
    unittest.main()
