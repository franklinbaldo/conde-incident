"""C241-G90: full-page versus partial visual read must not become an orbital constraint."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from test_ultima_hora_rj_castor_g89 import validate as validate_g89, G89

ROOT = Path(__file__).resolve().parents[1]
G90 = ROOT / "research/archive/ultima_hora_rj_1963_11_09_C241_CASTOR_G90.json"
CANONICAL_SHA256 = "c800cf2ec6cf2930d45aba7ac6ac4c8471adb7dd324f885833c5d222fa6cbdd3"

def require(value, explanation):
    if not value:
        raise ValueError(explanation)

def validate(d, parent=None):
    if parent is None:
        parent = json.loads(G89.read_text(encoding="utf-8"))
    validate_g89(parent)
    canonical = json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256, "full G90 interpretation changed")
    require(d["schema"] == "conde.press_visual_review/v1" and d["id"] == "C241-CASTOR-G90", "identity")
    require(d["source"]["sha256"] == parent["source"]["sha256"] and d["source"]["edition"] == "04200", "custody")
    require(d["source"]["parent_review"].endswith("_G89.json"), "parent")
    m = d["method"]
    require(m["dpi"] == 190 and m["executor"] == "Ifro" and m["tool"] == "pdftoppm" and m["ocr_as_negative"] is False, "visual method")
    require(len(m["region_protocol"]) == 6 and m["review"] == "DIRECT_VISUAL_AT_ARTICLE_SCALE", "coverage")
    p7, p8 = d["pages"]
    require([p7["pdf_page"], p8["pdf_page"]] == [7, 8], "page selection")
    require(p7["page_status"] == "EXAMINADA" and p7["page_negative_for_conde_event_report"] is True, "p7 negative")
    require(p8["page_status"] == "ILEGIVEL_PARCIAL" and p8["page_negative_for_conde_event_report"] is False and bool(p8["unreadable_regions"]), "p8 partial")
    for p in (p7, p8):
        require(p["regions_seen"] == m["region_protocol"] and len(p["editorial_sections"]) >= 5, "article coverage")
        require(p["independent_event_hour"] is None and p["independent_witness"] is None, "invented eyewitness")
    i = d["interpretation"]
    require(i["pdf_pages_with_new_page_level_negative"] == [7] and i["pdf_pages_with_partial_read"] == [8], "false page negative")
    require(i["new_historical_event_time"] is None and i["fbis_clock"] == "UNRESOLVED", "fake time")
    require(i["orbit_exclusion_licensed"] is False and i["theta_changed"] is False, "orbital overclaim")
    require(i["complete_edition_negative"] is False and i["nov10_special_edition"] == "NOT_ESTABLISHED" and i["stop_criterion_met"] is False, "scope overclaim")
    return True

class TestG90(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(G90.read_text(encoding="utf-8"))
        cls.parent = json.loads(G89.read_text(encoding="utf-8"))

    def test_original(self):
        self.assertTrue(validate(self.doc, self.parent))

    def change(self, path, value):
        d = copy.deepcopy(self.doc)
        node = d
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(d, self.parent)

    def test_fake_time(self):
        self.change(["pages", 0, "independent_event_hour"], "1963-11-08T20:15:00-03:00")
    def test_fake_witness_in_prose(self):
        self.change(["pages", 0, "disambiguation"], "A witness in Conde recorded 20h15")
    def test_fake_title_in_prose(self):
        self.change(["pages", 1, "editorial_sections", 0], "NASA confirms Conde 20h15")
    def test_promote_partial_page(self):
        self.change(["pages", 1, "page_negative_for_conde_event_report"], True)
    def test_promote_entire_edition(self):
        self.change(["interpretation", "complete_edition_negative"], True)
    def test_fake_sunday_absence(self):
        self.change(["interpretation", "nov10_special_edition"], "PROVEN_ABSENT")
    def test_fake_orbit_exclusion(self):
        self.change(["interpretation", "orbit_exclusion_licensed"], True)
    def test_fake_source_sha(self):
        self.change(["source", "sha256"], "0" * 64)
    def test_fake_visual_method(self):
        self.change(["method", "review"], "OCR_ONLY")
    def test_fake_p8_complete_in_explanation(self):
        self.change(["pages", 1, "disambiguation"], "The whole edition is proven negative")
    def test_fake_parent_revision(self):
        parent = copy.deepcopy(self.parent)
        parent["pages"][0]["editorial_sections"][0] = "NASA witnesses at 20h15"
        with self.assertRaises(ValueError):
            validate(self.doc, parent)

if __name__ == "__main__":
    unittest.main()
