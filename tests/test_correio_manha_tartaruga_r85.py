"""C241-R85: integrity of four visually read pages of Correio 21660.

The document is a page-scoped negative, not a negative for the edition.
Canonical SHA covers *all* prose and metadata; tests run under python -O.
"""
import copy
import hashlib
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_correio_manha_1963_11_13_C241_TARTARUGA_R85.json"
PREDECESSOR = ROOT / "research/archive/conde_correio_manha_1963_11_13_C241_TARTARUGA_R84.json"
SHA256_INTERPRETATION = "b622c06d161c28e8201f2bdfe493f69859f8207e995b251616122aec71f742cb"
SHA256_PDF = "497cd71b643be03f908e26c2e99100fd24908fb026ca33c8e1667d49ee897bc0"


def no_duplicate_keys(pairs):
    doc = {}
    for key, value in pairs:
        if key in doc:
            raise ValueError("duplicate JSON key: " + key)
        doc[key] = value
    return doc


def load(path=MANIFEST):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)


def canonical_sha256(doc):
    raw = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def require(ok, why):
    if not ok:
        raise ValueError(why)


def check_ancestors():
    """Check actual predecessors with their own full validators, not just IDs."""
    scripts = {}
    for name in ("r81", "r82", "r83", "r84"):
        scripts[name] = runpy.run_path(str(ROOT / ("tests/test_correio_manha_tartaruga_" + name + ".py")))
    r81 = scripts["r81"]["read_document"]()
    r82 = scripts["r82"]["load"]()
    r83 = scripts["r83"]["read"]()
    r84 = scripts["r84"]["load"]()
    scripts["r81"]["validate"](r81)
    scripts["r82"]["validate"](r82, r81)
    scripts["r83"]["validate"](r83, r82)
    scripts["r84"]["validate"](r84, r83)
    return r84


def validate(doc, predecessor):
    require(canonical_sha256(doc) == SHA256_INTERPRETATION, "R85 interpretation changed")
    require(doc["schema"] == "conde.local_clock_press_nucleus_increment/v1", "schema")
    require(doc["id"] == "C241-TARTARUGA-R85" and doc["research_issue"] == 871, "identity")
    require(doc["predecessor_manifest"] == str(PREDECESSOR.relative_to(ROOT)), "predecessor path")
    require(predecessor["id"] == "C241-TARTARUGA-R84", "predecessor identity")
    require(predecessor["scope"]["remaining_unread_first_caderno_pages"] == list(range(5, 13)),
            "R84 coverage")
    source = doc["source"]
    require(source["edition"] == "21660" and source["printed_date"] == "1963-11-13",
            "edition/date")
    require(source["original_sha256"] == SHA256_PDF and source["original_bytes"] == 20333897
            and source["pdf_pages"] == 26, "PDF original custody")
    require((source["first_caderno_pdf_start"], source["first_caderno_pdf_end"],
             source["second_caderno_pdf_start"]) == (1, 12, 13), "caderno limits")
    method = doc["method"]
    require(method["executor"] == "Ifro" and "max_memory_mb=128" in method["control_plane"],
            "external execution")
    require(method["pages_full_visual_review"] == 4 and method["number_overlapping_crops"] == 16,
            "visual coverage")
    require(method["scan_is_not_entire_edition_negative"] is True, "bounded result")
    pages = doc["readings"]
    require(len(pages) == 4 and [p["pdf_page"] for p in pages] == [5, 6, 7, 8],
            "examined page sequence")
    require([p["printed_folio"] for p in pages] == ["4", "5", "6", "7"],
            "printed folios")
    for p in pages:
        require(p["status"] == "EXAMINADA", "not fully examined")
        require(p["conde_article"] is None and p["conde_event_hour_literal"] is None
                and p["independent_eyewitness"] is None
                and p["report_attribution"] is None and p["orbital_constraint_active"] is False,
                "fabricated event evidence")
    require("SATÉLITE" in pages[0]["subjects"], "launch story")
    require("meteorito" in pages[1]["disambiguation"], "meteorite hypothesis caveat")
    require("São Mateus/ES" in pages[1]["disambiguation"], "distinct geography")
    scope = doc["scope"]
    require(scope["newly_examined_pages"] == [5, 6, 7, 8]
            and scope["previously_examined_pages"] == [1, 2, 3, 4],
            "page delta")
    require(scope["cumulatively_examined_first_caderno_pages"] == list(range(1, 9))
            and scope["remaining_unread_first_caderno_pages"] == [9, 10, 11, 12],
            "page census")
    require(scope["first_caderno_fully_examined"] is False
            and scope["second_caderno_read"] is False
            and scope["entire_edition_fully_examined"] is False
            and scope["global_negative_asserted"] is False,
            "unsupported edition-wide negative")
    conclusion = doc["conclusion"]
    require(conclusion["conde_event_hour_literal"] is None
            and conclusion["independent_eyewitness"] is None
            and conclusion["excludes_norad_528_or_637"] is False
            and conclusion["report_independence_from_tupi_fbis_diarios_associados"]
            == "UNDETERMINED", "unsupported orbital attribution")
    return True


class TestC241R85(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load()
        cls.predecessor = check_ancestors()

    def test_integrity_and_bounded_result(self):
        self.assertTrue(validate(self.doc, self.predecessor))

    def reject(self, edit):
        mutant = copy.deepcopy(self.doc)
        edit(mutant)
        with self.assertRaises(ValueError):
            validate(mutant, self.predecessor)

    def test_fake_hour(self):
        self.reject(lambda d: d["readings"][1].__setitem__("conde_event_hour_literal", "20h15"))

    def test_fake_conde_in_prose(self):
        self.reject(lambda d: d["readings"][1].__setitem__("subjects", "Conde Bahia confirmed"))

    def test_false_meteorite_confirmation(self):
        self.reject(lambda d: d["readings"][1].__setitem__("disambiguation", "Meteorite proved to be 528"))

    def test_wrong_place(self):
        self.reject(lambda d: d["readings"][1].__setitem__("disambiguation", "Conde/BA impact"))

    def test_fake_satellite_identity(self):
        self.reject(lambda d: d["readings"][0].__setitem__("subjects", "Soviet satellite 528"))

    def test_fake_agency(self):
        self.reject(lambda d: d["readings"][0].__setitem__("report_attribution", "NASA"))

    def test_fake_witness(self):
        self.reject(lambda d: d["readings"][2].__setitem__("independent_eyewitness", "Jose Silva"))

    def test_orbital_activation(self):
        self.reject(lambda d: d["readings"][2].__setitem__("orbital_constraint_active", True))

    def test_no_global_negative(self):
        self.reject(lambda d: d["scope"].__setitem__("global_negative_asserted", True))

    def test_no_full_edition(self):
        self.reject(lambda d: d["scope"].__setitem__("first_caderno_fully_examined", True))

    def test_unread_pages(self):
        self.reject(lambda d: d["scope"].__setitem__("remaining_unread_first_caderno_pages", []))

    def test_pdf_hash(self):
        self.reject(lambda d: d["source"].__setitem__("original_sha256", "0" * 64))

    def test_extra_prose(self):
        self.reject(lambda d: d["method"].__setitem__("visual_exam", "NASA confirms Conde"))

    def test_extra_field(self):
        self.reject(lambda d: d.__setitem__("verified_event_hour", "20h15"))

    def test_mutated_file_on_disk_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mutant.json"
            mutant = copy.deepcopy(self.doc)
            mutant["readings"][1]["conde_event_hour_literal"] = "20h15"
            path.write_text(json.dumps(mutant, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(load(path), self.predecessor)

    def test_duplicate_key_on_disk_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mutant.json"
            path.write_text('{"hour":null,"hour":"20h15"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load(path)


if __name__ == "__main__":
    unittest.main()
