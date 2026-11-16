"""C241-G97: observed newspaper nucleus must not manufacture event time or orbit exclusion."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "research/archive/ultima_hora_rj_1963_11_12_C241_CASTOR_G97.json"
PARENT = ROOT / "research/archive/ultima_hora_rio_police_and_covers_LONTRA_R84.json"
CANONICAL_SHA256 = "952492eb62fa57dd6565db7bf3bc14ca21c1e277dbad6d20e809af5e62f7a05b"
SOURCE_SHA256 = "4a78697979a3f71c8e28bb94e40a2d2c3c44532ab6e8180a47ee985680f69e94"
PAGES = [2, 4, 5, 6, 8, 9, 10]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def validate(doc, parent=None):
    if parent is None:
        parent = json.loads(PARENT.read_text(encoding="utf-8"))
    canonical = json.dumps(doc, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256,
            "canonical interpretation / evidence changed")
    require(doc["schema"] == "conde.press_visual_review/v1"
            and doc["id"] == "C241-CASTOR-G97" and doc["issue"] == 871, "identity")
    src = doc["source"]
    cover = next(x for x in parent["cover_identifications"] if x["edition"] == "04202")
    require(cover["sha256"] == SOURCE_SHA256 and cover["bytes"] == 12325627
            and cover["pdf_pages"] == 18
            and cover["date_printed"] == "1963-11-12", "parent custody")
    require(src["sha256"] == SOURCE_SHA256 and src["sha256"] == cover["sha256"]
            and src["url"] == cover["url"]
            and src["bytes"] == 12325627 and src["pdf_pages"] == 18
            and src["edition"] == "04202"
            and src["date_from_cover"] == "1963-11-12", "original identity")
    method = doc["method"]
    require(method["source_hash_rechecked"] is True
            and method["source_download_http_status"] == 200
            and method["pdf_panorama_all_18_pages"] is True
            and method["visual_quadrants_each_reviewed_page"] == 4
            and method["quadrant_x"] == [[0, .55], [.45, 1]]
            and method["quadrant_y"] == [[0, .57], [.43, 1]]
            and method["ocr_as_negative"] is False, "visual method")
    pages = doc["pages"]
    require([p["pdf_page"] for p in pages] == PAGES
            and [p["printed_page"] for p in pages] == PAGES
            and doc["scope"]["nucleus_internal_pages"] == PAGES
            and doc["scope"]["pdf_cover_page_1"] == "ALREADY_REVIEWED_BY_LONTRA_R84",
            "scoped pages")
    require([p["render_dpi"] for p in pages] == [105, 120, 120, 155, 155, 105, 155],
            "actual render settings")
    for page in pages:
        n = page["pdf_page"]
        require(page["page_status"] == "EXAMINADA"
                and page["source_scope"] == f"ONLY_PDF_PAGE_{n}"
                and page["visual_quadrants"] == 4
                and page["visual_quadrants_overlap"] is True
                and len(page["headlines_or_sections"]) >= 1
                and page["page_negative_for_conde_event_report"] is True
                and page["independent_event_hour"] is None
                and page["independent_witness"] is None, "scoped negative")
    require("zero hora" in pages[1]["disambiguation"].lower()
            and "Marte" in pages[4]["disambiguation"]
            and "TV Excelsior" in pages[5]["disambiguation"],
            "false clock / false spacecraft disambiguations")
    scope = doc["scope"]
    require(scope["other_pages"] == "PANORAMA_ONLY_NOT_EXAMINED"
            and scope["whole_edition_negative"] is False
            and scope["complete_corpus_negative"] is False
            and scope["complete_core_lot"] is True, "stop scope")
    interp = doc["interpretation"]
    require(interp["new_historical_event_time"] is None
            and interp["fbis_clock"] == "UNRESOLVED"
            and interp["fbis_2330_gmt_branch_utc"] == "1963-11-08T23:30:00Z"
            and interp["fbis_2330_rio_local_branch_utc"] == "1963-11-09T01:30:00Z"
            and interp["orbit_exclusion_licensed"] is False
            and interp["theta_changed"] is False
            and interp["moonwatch_confirmed_instrument"] is False, "orbit gate")
    return True


class TestCastorG97(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DOC.read_text(encoding="utf-8"))

    def test_custody_scope_and_gates(self):
        self.assertTrue(validate(self.doc))

    def mutate(self, path, value):
        candidate = copy.deepcopy(self.doc)
        node = candidate
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(candidate)

    def test_fake_event_hour(self):
        self.mutate(["pages", 4, "independent_event_hour"], "20h15")

    def test_fake_witness(self):
        self.mutate(["pages", 6, "independent_witness"], "Morador de Conde")

    def test_false_full_edition(self):
        self.mutate(["scope", "whole_edition_negative"], True)

    def test_false_ocr(self):
        self.mutate(["method", "ocr_as_negative"], True)

    def test_false_orbit_exclusion(self):
        self.mutate(["interpretation", "orbit_exclusion_licensed"], True)

    def test_false_clock(self):
        self.mutate(["interpretation", "fbis_clock"], "PROVEN_GMT")

    def test_false_headline(self):
        self.mutate(["pages", 4, "headlines_or_sections", 0], "Esfera caiu em Conde")

    def test_false_television_clock(self):
        self.mutate(["pages", 5, "disambiguation"], "20h15 é a queda em Conde")

    def test_false_mars_spacecraft(self):
        self.mutate(["pages", 4, "disambiguation"], "Marte confirma 528")

    def test_false_source(self):
        self.mutate(["source", "sha256"], "0"*64)

    def test_parent_custody_changed(self):
        parent = json.loads(PARENT.read_text(encoding="utf-8"))
        entry = next(x for x in parent["cover_identifications"] if x["edition"] == "04202")
        entry["sha256"] = "0"*64
        with self.assertRaises(ValueError):
            validate(self.doc, parent)


if __name__ == "__main__":
    unittest.main()
