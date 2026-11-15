"""C241-G93: two newspaper pages are not an event clock or full-edition negative."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from test_ultima_hora_rj_castor_g92 import validate as validate_g92, G92

ROOT = Path(__file__).resolve().parents[1]
G93 = ROOT / "research/archive/ultima_hora_rj_1963_11_09_C241_CASTOR_G93.json"
CANONICAL_SHA256 = "ec43ceaf1eec236c90cecad0f07207318c9f409a29cda19eb82e428d4f257c96"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(doc, parent=None):
    if parent is None:
        parent = json.loads(G92.read_text(encoding="utf-8"))
    validate_g92(parent)
    canonical = json.dumps(
        doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256,
            "canonical G93 evidence content changed")
    require(doc["schema"] == "conde.press_visual_review/v1"
            and doc["id"] == "C241-CASTOR-G93" and doc["issue"] == 871,
            "identity")
    src = doc["source"]
    require(src["sha256"] == parent["source"]["sha256"]
            and src["bytes"] == 10778040 and src["pdf_pages"] == 16
            and src["edition"] == "04200"
            and src["date_from_cover"] == "1963-11-09"
            and src["parent_review"].endswith("_G92.json"), "source custody")
    method = doc["method"]
    require(method["executor"] == "Ifro" and method["dpi"] == 240
            and method["source_hash_rechecked"] is True
            and method["pdf_rendered_again"] is True
            and method["region_protocol"] == "TWO_OVERLAPPING_HALVES_X_THREE_OVERLAPPING_BANDS"
            and method["visual_tiles_per_page"] == 6
            and method["half_x_fractions"] == [[0, .54], [.46, 1]]
            and method["band_y_fractions"] == [[0, .36], [.32, .69], [.65, 1]]
            and method["ocr_as_negative"] is False
            and method["review"] == "DIRECT_VISUAL_WHOLE_PAGE_ARTICLE_SCALE",
            "visual method")
    pages = doc["pages"]
    require([p["pdf_page"] for p in pages] == [1, 2]
            and [p["printed_page"] for p in pages] == [1, 2],
            "page identity")
    for number, page in zip((1, 2), pages):
        require(page["page_status"] == "EXAMINADA"
                and page["source_scope"] == f"ONLY_PDF_PAGE_{number}"
                and page["page_negative_for_conde_event_report"] is True
                and page["regions_seen"] == [
                    "top_left", "top_right", "middle_left", "middle_right",
                    "bottom_left", "bottom_right"]
                and len(page["editorial_sections"]) >= 12
                and page["independent_event_hour"] is None
                and page["independent_witness"] is None,
                "scoped page review")
    interpretation = doc["interpretation"]
    require(interpretation["pdf_pages_with_new_page_level_negative"] == [1, 2]
            and interpretation["new_historical_event_time"] is None
            and interpretation["fbis_clock"] == "UNRESOLVED"
            and interpretation["orbit_exclusion_licensed"] is False
            and interpretation["theta_changed"] is False,
            "event clock and orbit remain undetermined")
    require(interpretation["complete_edition_negative"] is False
            and interpretation["nov10_special_edition"] == "NOT_ESTABLISHED"
            and interpretation["pdf_page_8_status"] == "ILEGÍVEL_PARCIAL"
            and interpretation["castor_assigned_core_lot_complete"] is True
            and interpretation["stop_criterion_met"] is False,
            "local completion is not whole-corpus closeout")
    return True


class TestG93(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(G93.read_text(encoding="utf-8"))

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

    def test_fake_hour_page_one(self):
        self.mutate(["pages", 0, "independent_event_hour"], "20h15")

    def test_fake_hour_page_two(self):
        self.mutate(["pages", 1, "independent_event_hour"], "23h30")

    def test_fake_witness(self):
        self.mutate(["pages", 1, "independent_witness"], "Testemunha em Conde")

    def test_fake_headline(self):
        self.mutate(["pages", 0, "editorial_sections", 0],
                    "Esfera caiu em Conde às 20h15")

    def test_false_whole_edition(self):
        self.mutate(["interpretation", "complete_edition_negative"], True)

    def test_false_whole_corpus_stop(self):
        self.mutate(["interpretation", "stop_criterion_met"], True)

    def test_false_clock(self):
        self.mutate(["interpretation", "fbis_clock"], "PROVEN_RIO_LOCAL")

    def test_false_exclusion(self):
        self.mutate(["interpretation", "orbit_exclusion_licensed"], True)

    def test_false_sunday(self):
        self.mutate(["interpretation", "nov10_special_edition"], "ABSENT")

    def test_false_ocr_method(self):
        self.mutate(["method", "ocr_as_negative"], True)

    def test_false_source(self):
        self.mutate(["source", "sha256"], "0" * 64)

    def test_false_scope(self):
        self.mutate(["pages", 1, "source_scope"], "WHOLE_EDITION")

    def test_false_page_eight(self):
        self.mutate(["interpretation", "pdf_page_8_status"], "EXAMINADA")

    def test_prose_change_is_detected(self):
        self.mutate(["pages", 0, "disambiguation"], "Alguém viu queda em Conde.")

    def test_parent_mutation_cannot_pass(self):
        parent = json.loads(G92.read_text(encoding="utf-8"))
        parent["pages"][0]["disambiguation"] = "Testemunha e hora inventadas"
        with self.assertRaises(ValueError):
            validate(self.doc, parent)


if __name__ == "__main__":
    unittest.main()
