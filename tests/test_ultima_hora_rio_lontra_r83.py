"""Lontra R83: preserve original UH Rio 04201 custody and the five-page scope."""
import copy
import hashlib
import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/ultima_hora_rio_04201_LONTRA_R83.json"
URL = "https://hemeroteca-pdf.bn.gov.br/386030/per386030_1963_04201.pdf"
SOURCE_SHA = "b7ce4a3437633fe712fc49df6a0b1f86289912360830b9c979afea1ffa8bd134"
INTERPRETATION_SHA256 = "6f1c9d1aa32c8f2fd09507aef29992de09494f36442658b645fd7bc3935fb750"
ASSIGNED = [1, 2, 4, 6, 8]


def require(value, message):
    if not value:
        raise ValueError(message)


def interpretation_sha256(doc):
    # Pins the complete reviewed interpretation, not merely the source PDF hash.
    payload = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate(doc):
    require(interpretation_sha256(doc) == INTERPRETATION_SHA256,
            "complete interpretation changed; review against the original pages")
    require(doc["schema"] == "conde.press_visual_review/v1", "schema")
    require(doc["id"] == "C241-LONTRA-R83" and doc["refs_issue"] == 871, "identity")
    src = doc["source"]
    require(src["collection_id"] == "386030" and src["edition"] == "04201", "edition")
    require(src["date_printed"] == "1963-11-11" and src["url"] == URL, "date/url")
    require(src["sha256"] == SOURCE_SHA and src["bytes"] == 19995184, "source custody")
    require(src["pdf_pages"] == 32 and src["magic_pdf"] and src["eof"], "pdf integrity")
    method = doc["method"]
    require(method["review"] == "DIRECT_VISUAL_AT_ARTICLE_SCALE"
            and method["full_page_and_quadrants"] and not method["ocr_as_negative"], "review method")
    pages = doc["pages"]
    require(len(pages) == 5 and [p["pdf_page"] for p in pages] == ASSIGNED, "page scope")
    require(len({p["pdf_page"] for p in pages}) == 5, "duplicates")
    for page in pages:
        require(page["printed_page"] == page["pdf_page"], "folio")
        require(page["pdf_url"] == URL + "#page=" + str(page["pdf_page"]), "facsimile page")
        require(page["status"] == "EXAMINADA"
                and page["review_protocol"] == "PANORAMA_PLUS_FOUR_ENLARGED_QUADRANTS", "page review")
        require(not page["event_report_conde_ba"]
                and page["independent_event_hour"] is None
                and page["independent_witness"] is None
                and not page["orbital_measurement_found"], "invented evidence")
        require(bool(page["topics"]) and bool(page["false_positive_guard"]), "article/guard")
    require("Polet I" in pages[3]["topics"], "space article lost")
    require("não a seção policial" in pages[4]["false_positive_guard"], "p8 mistaken section")
    res = doc["interpretation"]
    require(res["assigned_pdf_pages"] == ASSIGNED and res["pages_examined"] == 5, "denominator")
    require(res["unread_pdf_pages"] == 27 and not res["whole_edition_negative"], "edition overclaim")
    require(res["independent_event_hour"] is None
            and res["independent_witness"] is None
            and not res["conde_ba_report_found"]
            and not res["orbital_constraint_changed"]
            and res["fbis_clock"] == "UNRESOLVED", "false conclusion")
    require(res["stop_after_this_lot"], "scope stop")
    later = doc["other_accessible_candidates"]
    require([x["edition"] for x in later] == ["04202", "04203", "04204"], "later issue candidates")
    for x in later:
        require(x["http_head"] == 200 and x["calendar_date_not_verified"]
                and x["not_read"], "assumed later edition date/reading")
    require(len(doc["limits"]) >= 3, "limitations")
    return True


class TestLontraR83(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest(self):
        self.assertTrue(validate(self.doc))

    def reject(self, change):
        doc = copy.deepcopy(self.doc)
        change(doc)
        with self.assertRaises(ValueError):
            validate(doc)

    def test_fabricated_article_in_topics(self):
        self.reject(lambda d: d["pages"][0].update(
            topics=d["pages"][0]["topics"] + "; NASA confirma queda em Conde às 20h15"))

    def test_fabricated_folio_note(self):
        self.reject(lambda d: d["pages"][2].update(
            false_positive_guard="Testemunha independente viu o objeto em Conde às 20h15"))

    def test_wrong_source(self):
        self.reject(lambda d: d["source"].update(sha256="0" * 64))

    def test_repeated_page(self):
        self.reject(lambda d: d["pages"][4].update(pdf_page=6))

    def test_fabricated_event_time(self):
        self.reject(lambda d: d["pages"][3].update(independent_event_hour="20h43"))

    def test_fabricated_witness(self):
        self.reject(lambda d: d["pages"][0].update(independent_witness="X"))

    def test_entire_edition_overclaim(self):
        self.reject(lambda d: d["interpretation"].update(whole_edition_negative=True))

    def test_unread_editions_not_promoted(self):
        self.reject(lambda d: d["other_accessible_candidates"][0].update(not_read=False))

    def test_no_ocr_only_negative(self):
        self.reject(lambda d: d["method"].update(ocr_as_negative=True))

    def test_p8_section_mismatch_preserved(self):
        self.reject(lambda d: d["pages"][4].update(false_positive_guard="Polícia lida"))

    def test_source_bytes_replay_when_supplied(self):
        path = os.environ.get("LONTRA_R83_PDF")
        if not path:
            self.skipTest("Live source file absent; use LONTRA_R83_PDF on external executor")
        data = Path(path).read_bytes()
        self.assertEqual(len(data), 19995184)
        self.assertEqual(hashlib.sha256(data).hexdigest(), SOURCE_SHA)
        self.assertTrue(data.startswith(b"%PDF-"))
        self.assertIn(b"%%EOF", data[-256:])


if __name__ == "__main__":
    unittest.main()
