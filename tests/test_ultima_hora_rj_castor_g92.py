"""C241-G92: page 4 review cannot silently become testimony or orbital exclusion."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from test_ultima_hora_rj_castor_g91 import validate as validate_g91, G91

ROOT = Path(__file__).resolve().parents[1]
G92 = ROOT / "research/archive/ultima_hora_rj_1963_11_09_C241_CASTOR_G92.json"
CANONICAL_SHA256 = "53add0794bbaf04b5f5960cd72f014cf10d8187b5fb4ba8b482a2e7185ef8259"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(doc, parent=None):
    if parent is None:
        parent = json.loads(G91.read_text(encoding="utf-8"))
    validate_g91(parent)
    canonical = json.dumps(
        doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256,
            "canonical G92 evidence content changed")
    require(doc["schema"] == "conde.press_visual_review/v1" and
            doc["id"] == "C241-CASTOR-G92" and doc["issue"] == 871, "identity")
    s = doc["source"]
    require(s["sha256"] == parent["source"]["sha256"] and
            s["bytes"] == 10778040 and s["edition"] == "04200" and
            s["pdf_pages"] == 16 and
            s["parent_review"].endswith("_G91.json"), "source custody and chain")
    m = doc["method"]
    require(m["executor"] == "Ifro" and m["dpi"] == 190 and
            m["source_hash_rechecked"] is True and
            m["region_protocol"] == "FULL_WIDTH_3_OVERLAPPING_BANDS" and
            m["visual_tiles"] == 3 and
            m["band_y_fractions"] == [[0, .36], [.29, .71], [.68, 1]] and
            m["ocr_as_negative"] is False, "visual method")
    require(len(doc["pages"]) == 1, "one page")
    p = doc["pages"][0]
    require(p["pdf_page"] == 4 and p["printed_page"] == 4, "page 4 only")
    require(p["page_status"] == "EXAMINADA" and
            p["page_negative_for_conde_event_report"] is True and
            p["source_scope"] == "ONLY_PDF_PAGE_4" and
            len(p["regions_seen"]) == 3 and len(p["editorial_sections"]) >= 9,
            "scoped visual review")
    require(p["independent_event_hour"] is None and
            p["independent_witness"] is None, "false testimony")
    i = doc["interpretation"]
    require(i["pdf_pages_with_new_page_level_negative"] == [4], "only page 4")
    require(i["new_historical_event_time"] is None and
            i["fbis_clock"] == "UNRESOLVED", "clock not authenticated")
    require(i["orbit_exclusion_licensed"] is False and
            i["theta_changed"] is False, "no orbital exclusion")
    require(i["complete_edition_negative"] is False and
            i["stop_criterion_met"] is False and
            i["nov10_special_edition"] == "NOT_ESTABLISHED",
            "no entire-edition or Sunday negative")
    return True


class TestG92(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(G92.read_text(encoding="utf-8"))

    def test_original(self):
        self.assertTrue(validate(self.doc))

    def mutate(self, path, value):
        candidate = copy.deepcopy(self.doc)
        target = candidate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(candidate)

    def test_fake_event_hour(self):
        self.mutate(["pages", 0, "independent_event_hour"], "20h15")

    def test_fake_witness_prose(self):
        self.mutate(["pages", 0, "disambiguation"], "João viu esfera 20h15")

    def test_fake_headline(self):
        self.mutate(["pages", 0, "editorial_sections", 0],
                    "Esfera caiu em Conde às 20h15")

    def test_false_complete_edition(self):
        self.mutate(["interpretation", "complete_edition_negative"], True)

    def test_false_special_absence(self):
        self.mutate(["interpretation", "nov10_special_edition"], "ABSENT")

    def test_false_clock(self):
        self.mutate(["interpretation", "fbis_clock"], "PROVEN_RIO_LOCAL")

    def test_false_orbital_exclusion(self):
        self.mutate(["interpretation", "orbit_exclusion_licensed"], True)

    def test_false_sha(self):
        self.mutate(["source", "sha256"], "0" * 64)

    def test_false_ocr_negative(self):
        self.mutate(["method", "ocr_as_negative"], True)

    def test_false_scope(self):
        self.mutate(["pages", 0, "source_scope"], "WHOLE_EDITION")

    def test_parent_source_only_mutation(self):
        parent = json.loads(G91.read_text(encoding="utf-8"))
        parent["pages"][0]["disambiguation"] = "Evento 20h15 em Conde"
        with self.assertRaises(ValueError):
            validate(self.doc, parent)


if __name__ == "__main__":
    unittest.main()
