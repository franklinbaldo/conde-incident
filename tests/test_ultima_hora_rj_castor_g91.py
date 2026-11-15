"""C241-G91: independent visual reading of p6 cannot become event time/orbital exclusion."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from test_ultima_hora_rj_castor_g90 import validate as validate_g90, G90

ROOT = Path(__file__).resolve().parents[1]
G91 = ROOT / "research/archive/ultima_hora_rj_1963_11_09_C241_CASTOR_G91.json"
CANONICAL_SHA256 = "61692ff3f0f90be044eb61e87e9d99322201eec7e07ebefe1ddc46facea4a666"

def require(p, m):
    if not p:
        raise ValueError(m)

def validate(doc, parent=None):
    if parent is None:
        parent = json.loads(G90.read_text(encoding="utf-8"))
    validate_g90(parent)
    canonical = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256, "canonical G91 evidence content changed")
    require(doc["schema"] == "conde.press_visual_review/v1" and doc["id"] == "C241-CASTOR-G91", "identity")
    s = doc["source"]
    require(s["sha256"] == parent["source"]["sha256"] and s["edition"] == "04200" and s["bytes"] == 10778040, "source custody")
    require(s["parent_review"].endswith("_G90.json"), "ancestor")
    m = doc["method"]
    require(m["executor"] == "Ifro" and m["dpi"] == 190 and m["source_hash_rechecked"] is True, "visual method")
    require(m["visual_tiles"] == 12 and m["ocr_as_negative"] is False, "not OCR negative")
    require(len(doc["pages"]) == 1, "one page")
    p = doc["pages"][0]
    require(p["pdf_page"] == 6 and p["printed_page"] == 6, "page 6 only")
    require(p["page_status"] == "EXAMINADA" and p["page_negative_for_conde_event_report"] is True, "scoped page read")
    require(len(p["regions_seen"]) == 12 and len(p["editorial_sections"]) >= 20, "coverage")
    require(p["independent_event_hour"] is None and p["independent_witness"] is None, "false event")
    i = doc["interpretation"]
    require(i["pdf_pages_with_new_page_level_negative"] == [6], "only page 6")
    require(i["new_historical_event_time"] is None and i["fbis_clock"] == "UNRESOLVED", "false clock")
    require(i["orbit_exclusion_licensed"] is False and i["theta_changed"] is False, "false orbital exclusion")
    require(i["complete_edition_negative"] is False and i["stop_criterion_met"] is False, "false edition complete")
    require(i["nov10_special_edition"] == "NOT_ESTABLISHED", "Sunday special not ruled out")
    return True

class TestG91(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(G91.read_text(encoding="utf-8"))

    def test_original(self):
        self.assertTrue(validate(self.doc))

    def tamper(self, path, value):
        d = copy.deepcopy(self.doc)
        target = d
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(d)

    def test_fake_time(self):
        self.tamper(["pages",0,"independent_event_hour"], "1963-11-08T20:15:00-03:00")
    def test_fake_witness_in_prose(self):
        self.tamper(["pages",0,"disambiguation"], "Witness at 20h15 in Conde")
    def test_fake_story_in_headline(self):
        self.tamper(["pages",0,"editorial_sections",0], "NASA finds Conde sphere at 20h15")
    def test_promote_edition(self):
        self.tamper(["interpretation","complete_edition_negative"], True)
    def test_invent_sunday_absence(self):
        self.tamper(["interpretation","nov10_special_edition"], "PROVEN_ABSENT")
    def test_exclude_orbit(self):
        self.tamper(["interpretation","orbit_exclusion_licensed"], True)
    def test_fake_pdf_sha(self):
        self.tamper(["source","sha256"], "0"*64)
    def test_pretend_ocr_is_complete(self):
        self.tamper(["method","ocr_as_negative"], True)
    def test_change_scope(self):
        self.tamper(["pages",0,"source_scope"], "ENTIRE_EDITION")
    def test_mutate_parent_prose(self):
        parent = json.loads(G90.read_text(encoding="utf-8"))
        parent["pages"][0]["disambiguation"] = "Witness at 20h15"
        with self.assertRaises(ValueError):
            validate(self.doc, parent)

if __name__ == "__main__":
    unittest.main()
