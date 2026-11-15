"""C241-R84: verify visual-reading manifest and prevent fabricated Conde time.

Fingerprint covers all interpretation prose, including unrelated news and citations;
failing an in-memory mutation is intentional. No bare assert: works with python -O.
"""
import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_correio_manha_1963_11_13_C241_TARTARUGA_R84.json"
PREDECESSOR = ROOT / "research/archive/conde_correio_manha_1963_11_12_C241_TARTARUGA_R83.json"
FINGERPRINT = "24c7fac81a35d3a587be34c17606dd25a5e1476fdc5da29bdab8d084209819f7"
PDF_SHA = "497cd71b643be03f908e26c2e99100fd24908fb026ca33c8e1667d49ee897bc0"
URL = "https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_21660.pdf"


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load(path=MANIFEST):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def fingerprint(doc):
    payload = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_predecessor(predecessor):
    """Reuse R83's complete interpretation guard, including R82 and R81."""
    guard_path = ROOT / "tests/test_correio_manha_tartaruga_r83.py"
    spec = importlib.util.spec_from_file_location("conde_r83_guard", guard_path)
    if spec is None or spec.loader is None:
        raise ValueError("R83 guard unavailable")
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.validate(predecessor, guard.read(guard.PREVIOUS))


def validate_predecessor(predecessor):
    """Reuse R83's complete interpretation guard, including R82 and R81."""
    guard_path = ROOT / "tests/test_correio_manha_tartaruga_r83.py"
    spec = importlib.util.spec_from_file_location("conde_r83_guard", guard_path)
    if spec is None or spec.loader is None:
        raise ValueError("R83 guard unavailable")
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.validate(predecessor, guard.read(guard.PREVIOUS))


def validate(doc, predecessor):
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    require(fingerprint(doc) == FINGERPRINT, "interpretation fingerprint changed")
    require(doc["schema"] == "conde.local_clock_press_nucleus_increment/v1", "schema")
    require(doc["id"] == "C241-TARTARUGA-R84" and doc["research_issue"] == 871, "identity")
    require(doc["predecessor_manifest"] == str(PREDECESSOR.relative_to(ROOT)), "predecessor path")
    require(predecessor["id"] == "C241-TARTARUGA-R83", "predecessor id")
    validate_predecessor(predecessor)
    validate_predecessor(predecessor)
    require(predecessor["scope"]["first_caderno_fully_examined"] is True, "predecessor caderno")
    require(predecessor["source"]["edition"] == "21659", "predecessor edition")
    source = doc["source"]
    require(source["edition"] == "21660" and source["printed_date"] == "1963-11-13", "new edition")
    require(source["original_url"] == URL and source["original_sha256"] == PDF_SHA, "original custody")
    require(source["original_bytes"] == 20333897 and source["pdf_pages"] == 26, "original size/pages")
    require((source["first_caderno_pdf_start"], source["first_caderno_pdf_end"],
             source["second_caderno_pdf_start"]) == (1, 12, 13), "caderno boundary")
    method = doc["method"]
    require(method["executor"] == "Ifro" and "max_memory_mb=128" in method["control_plane"],
            "executor")
    require(method["pages_full_visual_review"] == 4 and method["number_overlapping_crops"] == 16,
            "visual review count")
    require(method["scan_is_not_entire_edition_negative"] is True, "reading limit")
    rows = doc["readings"]
    require(len(rows) == 4 and [r["pdf_page"] for r in rows] == [1, 2, 3, 4], "new pages")
    require([r["printed_folio"] for r in rows] == ["1", "1 (2.º clichê)", "2", "3"],
            "printed folios")
    require(all(r["status"] == "EXAMINADA" for r in rows), "reading status")
    require(all(r["conde_article"] is None and r["conde_event_hour_literal"] is None
                and r["independent_eyewitness"] is None and r["report_attribution"] is None
                and r["orbital_constraint_active"] is False for r in rows),
            "fabricated page-level event evidence")
    require("2.º CLICHÊ" in rows[1]["subjects"], "second front-page printing")
    scope = doc["scope"]
    require(scope["newly_examined_pages"] == [1, 2, 3, 4], "new page set")
    require(scope["remaining_unread_first_caderno_pages"] == list(range(5, 13)), "unread count")
    require(scope["first_caderno_fully_examined"] is False
            and scope["second_caderno_read"] is False
            and scope["entire_edition_fully_examined"] is False
            and scope["global_negative_asserted"] is False, "unsupported absence")
    conclusion = doc["conclusion"]
    require(conclusion["conde_event_hour_literal"] is None
            and conclusion["independent_eyewitness"] is None
            and conclusion["excludes_norad_528_or_637"] is False, "unsupported orbital inference")
    require(conclusion["report_independence_from_tupi_fbis_diarios_associados"] == "UNDETERMINED",
            "source independence")
    return True


class TestC241R84(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.predecessor = load(), load(PREDECESSOR)

    def test_integrity_and_scope(self):
        self.assertTrue(validate(self.doc, self.predecessor))

    def reject(self, edit):
        mutant = copy.deepcopy(self.doc)
        edit(mutant)
        with self.assertRaises(ValueError):
            validate(mutant, self.predecessor)

    def test_invented_conde_time(self):
        self.reject(lambda d: d["readings"][0].__setitem__("conde_event_hour_literal", "20h15"))

    def test_invented_witness(self):
        self.reject(lambda d: d["readings"][2].__setitem__("independent_eyewitness", "testemunha"))

    def test_invented_agency(self):
        self.reject(lambda d: d["readings"][1].__setitem__("report_attribution", "NASA"))

    def test_fake_orbital_activation(self):
        self.reject(lambda d: d["readings"][3].__setitem__("orbital_constraint_active", True))

    def test_fake_event_claim_in_prose(self):
        self.reject(lambda d: d["readings"][3].__setitem__("subjects", "NASA confirmed Conde at 20h15"))

    def test_invented_global_negative(self):
        self.reject(lambda d: d["scope"].__setitem__("global_negative_asserted", True))

    def test_fake_full_reading(self):
        self.reject(lambda d: d["scope"].__setitem__("first_caderno_fully_examined", True))

    def test_fake_edition_source(self):
        self.reject(lambda d: d["source"].__setitem__("original_sha256", "0" * 64))

    def test_fake_double_independence(self):
        self.reject(lambda d: d["scope"].__setitem__("correction", "two independent newspapers"))

    def test_unread_pages_forgery(self):
        self.reject(lambda d: d["scope"].__setitem__("remaining_unread_first_caderno_pages", []))

    def test_extra_field(self):
        self.reject(lambda d: d.__setitem__("conclusive", True))

    def test_ancestor_r83_prose_rejected(self):
        previous = copy.deepcopy(self.predecessor)
        previous["readings"][0]["subjects"] = (
            "NASA confirmed an object in Conde at 20h15"
        )
        with self.assertRaises(ValueError):
            validate(self.doc, previous)

    def test_ancestor_r83_prose_rejected(self):
        previous = copy.deepcopy(self.predecessor)
        previous["readings"][0]["subjects"] = (
            "NASA confirmed an object in Conde at 20h15"
        )
        with self.assertRaises(ValueError):
            validate(self.doc, previous)

    def test_duplicate_key_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "duplicate.json"
            file.write_text('{"time":null,"time":"20h15"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load(file)


if __name__ == "__main__":
    unittest.main()
