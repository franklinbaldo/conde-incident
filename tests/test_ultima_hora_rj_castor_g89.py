"""C241-G89: keep two page-level visual negatives from becoming a false edition-wide negative."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G89 = ROOT / "research/archive/ultima_hora_rj_1963_11_09_C241_CASTOR_G89.json"
G88 = ROOT / "research/archive/ultima_hora_rj_1963_11_09_C241_CASTOR_G88.json"

def require(ok, label):
    if not ok:
        raise ValueError(label)

def validate(d, parent):
    require(d["schema"] == "conde.press_visual_review/v1" and d["id"] == "C241-CASTOR-G89", "identity")
    s=d["source"]
    require(s["sha256"] == parent["source"]["sha256"] == "320aeb075b99fc6f2884904d9e1aa801b9d3f6be2b131ded30093caaaa6ce352", "custody")
    require(s["edition"] == "04200" and s["date_from_cover"] == "1963-11-09" and s["pdf_pages"] == 16, "source identification")
    require(s["url"] == parent["source"]["url"], "source URL")
    m=d["method"]
    require(m["executor"] == "Ifro" and m["tool"] == "pdftoppm" and m["dpi"] == 190 and m["review"] == "DIRECT_VISUAL_AT_ARTICLE_SCALE", "render evidence")
    require(m["region_protocol"] == ["upper_half","lower_half"] and m["ocr_as_negative"] is False, "visual coverage")
    pages=d["pages"]
    require([p["pdf_page"] for p in pages] == [9,13] and [p["printed_page"] for p in pages] == [1,5], "page scope")
    for p in pages:
        require(p["regions_seen"] == ["upper_half","lower_half"] and p["page_negative_for_conde_event_report"] is True, "page review")
        require(p["independent_event_hour"] is None and p["independent_witness"] is None, "invented event")
        require(p["source_scope"] == "ONLY_PDF_PAGE_"+str(p["pdf_page"]), "scope")
        require(len(p["editorial_sections"]) >= 3 and bool(p["disambiguation"]), "editorial units")
    a=d["additional_visual_scope"]
    require(a["pages_seen_at_1900px"] == list(range(7,17)) and a["counts_as_page_complete"] is False, "panorama not a full read")
    i=d["interpretation"]
    require(i["pdf_pages_with_new_page_level_negative"] == [9,13], "unsupported page negative")
    require(i["new_historical_event_time"] is None and i["fbis_clock"] == "UNRESOLVED", "clock")
    require(i["orbit_exclusion_licensed"] is False and i["theta_changed"] is False, "orbit")
    require(i["complete_edition_negative"] is False and i["nov10_special_edition"] == "NOT_ESTABLISHED" and i["stop_criterion_met"] is False, "overclaim")
    return True

class TestG89(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(G89.read_text(encoding="utf-8"))
        cls.parent=json.loads(G88.read_text(encoding="utf-8"))
    def test_original(self):
        self.assertTrue(validate(self.doc,self.parent))
    def mutate(self,path,value):
        d=copy.deepcopy(self.doc); node=d
        for k in path[:-1]: node=node[k]
        node[path[-1]]=value
        with self.assertRaises(ValueError):
            validate(d,self.parent)
    def test_fake_full_edition_negative(self):
        self.mutate(["interpretation","complete_edition_negative"],True)
    def test_fake_hour(self):
        self.mutate(["pages",0,"independent_event_hour"],"1963-11-08T21:00:00-03:00")
    def test_fake_third_page(self):
        self.mutate(["interpretation","pdf_pages_with_new_page_level_negative"],[9,10,13])
    def test_fake_partial_as_complete(self):
        self.mutate(["additional_visual_scope","counts_as_page_complete"],True)
    def test_fake_sunday_absence(self):
        self.mutate(["interpretation","nov10_special_edition"],"PROVEN_ABSENT")
    def test_fake_orbital_exclusion(self):
        self.mutate(["interpretation","orbit_exclusion_licensed"],True)
    def test_fake_source_hash(self):
        self.mutate(["source","sha256"],"0"*64)
    def test_fake_visual_method(self):
        self.mutate(["method","review"],"OCR_ONLY")
if __name__ == "__main__":
    unittest.main()
