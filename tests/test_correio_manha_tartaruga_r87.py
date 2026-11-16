"""C241-R87: full visual reading of Correio 21660 first caderno (13 Nov 1963)."""
import copy
import hashlib
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research/archive/conde_correio_manha_1963_11_13_C241_TARTARUGA_R87.json"
R85 = ROOT / "research/archive/conde_correio_manha_1963_11_13_C241_TARTARUGA_R85.json"
R86 = ROOT / "research/archive/conde_correio_manha_1963_11_14_C241_TARTARUGA_R86.json"
EXPECTED_PDF_SHA = "497cd71b643be03f908e26c2e99100fd24908fb026ca33c8e1667d49ee897bc0"
EXPECTED_INTERPRETATION_SHA = "a83f3f4c5c9017ec86b8128349a2c5cba4bf05af1c246038fee56b9dbc5f7fe8"


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load(path=FILE):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)


def require(ok, what):
    if not ok:
        raise ValueError(what)


def interpretation_sha(d):
    content = json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate(d, r85, r86):
    require(d["id"] == "C241-TARTARUGA-R87" and d["research_issue"] == 871, "manifest identity")
    require(d["schema"] == "conde.local_clock_press_nucleus_increment/v1", "schema")
    require(d["predecessor_manifest"] == str(R86.relative_to(ROOT))
            and d["previous_integral_manifest"] == str(R85.relative_to(ROOT)), "ancestry")
    require(r85["scope"]["remaining_unread_first_caderno_pages"] == [9, 10, 11, 12]
            and r86["sources"][0]["new_pages_certified_integral"] == [], "predecessor census")
    source = d["source"]
    require(source["edition"] == "21660" and source["printed_date"] == "1963-11-13"
            and source["original_bytes"] == 20333897 and source["pdf_pages"] == 26
            and source["first_caderno_pdf_pages"] == [1, 12]
            and source["second_caderno_starts_pdf_page"] == 13
            and source["original_sha256"] == EXPECTED_PDF_SHA, "PDF custody")
    method = d["method"]
    require(method["heavy_executor"].startswith("Ifro")
            and "max_memory_mb=128" in method["control_plane"]
            and method["new_pages_fully_examined"] == 4
            and method["new_visual_crops"] == 24
            and "3200px" in method["visual_exam"], "visual method")
    readings = d["readings"]
    require([p["pdf_page"] for p in readings] == [9, 10, 11, 12], "page sequence")
    require([p["printed_folio"] for p in readings] == ["8", "9", "10", "11"], "folio")
    for p in readings:
        require(p["status"] == "EXAMINADA"
                and p["conde_article"] is None
                and p["conde_event_hour_literal"] is None
                and p["independent_eyewitness"] is None
                and p["orbital_constraint_active"] is False, "invented event reading")
    require("TV-Tupi" in readings[1]["subjects"]
            and "13/11" in readings[1]["disambiguation"]
            and "8/11" in readings[1]["disambiguation"], "Tupi chronology")
    require("mercadorias" in readings[3]["subjects"], "page 12 subject")
    scope = d["scope"]
    require(scope["previously_integral_pages"] == list(range(1, 9))
            and scope["newly_integral_pages"] == [9, 10, 11, 12]
            and scope["cumulatively_integral_first_caderno_pages"] == list(range(1, 13))
            and scope["remaining_first_caderno_pages"] == [], "caderno coverage")
    require(scope["first_caderno_fully_examined"] is True
            and scope["second_caderno_fully_examined"] is False
            and scope["entire_edition_fully_examined"] is False
            and scope["global_edition_negative_asserted"] is False
            and scope["negative_only_for_examined_first_caderno"] is True, "false edition negative")
    conclusion = d["conclusion"]
    require(conclusion["conde_event_hour_literal"] is None
            and conclusion["independent_event_eyewitness"] is None
            and conclusion["orbital_constraints_for_528_or_637"] is False
            and conclusion["independent_time_found"] is False, "false physical inference")
    require(interpretation_sha(d) == EXPECTED_INTERPRETATION_SHA, "interpretation altered")
    return True


class TestC241R87(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load()
        cls.r85 = json.loads(R85.read_text(encoding="utf-8"))
        cls.r86 = json.loads(R86.read_text(encoding="utf-8"))
        r85_validator = runpy.run_path(str(ROOT / "tests/test_correio_manha_tartaruga_r85.py"))
        r86_validator = runpy.run_path(str(ROOT / "tests/test_correio_manha_tartaruga_r86.py"))
        r85_validator["validate"](cls.r85, r85_validator["check_ancestors"]())
        r86_validator["validate"](cls.r86)

    def test_real_manifest(self):
        self.assertTrue(validate(self.doc, self.r85, self.r86))

    def reject_mutation(self, field_change):
        d = copy.deepcopy(self.doc)
        field_change(d)
        with self.assertRaises(ValueError):
            validate(d, self.r85, self.r86)

    def test_false_hour(self):
        self.reject_mutation(lambda d: d["readings"][1].__setitem__("conde_event_hour_literal", "20h15"))

    def test_unsupported_eyewitness(self):
        self.reject_mutation(lambda d: d["readings"][0].__setitem__("independent_eyewitness", "Maria"))

    def test_false_orbit(self):
        self.reject_mutation(lambda d: d["conclusion"].__setitem__("orbital_constraints_for_528_or_637", True))

    def test_false_global_negative(self):
        self.reject_mutation(lambda d: d["scope"].__setitem__("global_edition_negative_asserted", True))

    def test_false_complete_edition(self):
        self.reject_mutation(lambda d: d["scope"].__setitem__("entire_edition_fully_examined", True))

    def test_wrong_tupi_program_day(self):
        self.reject_mutation(lambda d: d["readings"][1].__setitem__("disambiguation", "Horário do episódio em Conde em 8/11."))

    def test_wrong_pdf_sha(self):
        self.reject_mutation(lambda d: d["source"].__setitem__("original_sha256", "0" * 64))

    def test_mutated_json_on_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "altered.json"
            d = copy.deepcopy(self.doc)
            d["readings"][1]["conde_event_hour_literal"] = "20h15"
            path.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(load(path), self.r85, self.r86)

    def test_duplicate_key_on_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.json"
            path.write_text('{"event_time":null,"event_time":"20h15"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load(path)


if __name__ == "__main__":
    unittest.main()
