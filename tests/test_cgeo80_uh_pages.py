"""CGEO-80: independent event clock remains null despite unrelated times.
Deterministic offline contract; not proof of live source availability.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path

PATH = (Path(__file__).resolve().parents[1] /
        "research/editorial/cgeo80_uh_00472_pages7_10_20261115.json")
EXPECTED_SHA = "97b9eaf039068d1c6d6d3e4c2bc0ee4b686f6d6cc4ae791e2c660cfc69d3f6f4"
PDF_SHA = "8564c0c8c26857e0feda54fc5da0f9d3ca0c34c8de02c44e3074aa79a101cece"


def validate(doc):
    errors = []
    digest = hashlib.sha256(json.dumps(
        doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if digest != EXPECTED_SHA:
        errors.append("frozen record")
    if doc.get("id") != "CGEO-80" or doc.get("status") != "PARTIAL_ISSUE_NO_EVENT_CLOCK":
        errors.append("identity")
    src = doc.get("source", {})
    if (src.get("edition"), src.get("cover_date"), src.get("pdf_pages"),
            src.get("size_bytes"), src.get("sha256")) != (
            "00472", "1963-11-09", 10, 5275519, PDF_SHA):
        errors.append("source")
    method = doc.get("method", {})
    if not method.get("original_pdf_sha256_rechecked") or method.get("new_ocr") or (
            method.get("printed_folio_assumed_from_pdf_index")):
        errors.append("method")
    expected = [(7, None, "LIDO_INTEGRAL_SEM_MENCAO"),
                (8, 8, "LIDO_INTEGRAL_SEM_MENCAO"),
                (9, 9, "ILEGIVEL_PARCIAL"),
                (10, None, "LIDO_INTEGRAL_SEM_MENCAO")]
    pages = doc.get("page_reviews", [])
    if [(p.get("pdf_page"), p.get("printed_page"), p.get("status"))
            for p in pages] != expected:
        errors.append("page scope")
    if any(p.get("event_hour") is not None or p.get("eyewitnesses") != []
           for p in pages):
        errors.append("invented event evidence")
    if not pages[2].get("unreadable_area"):
        errors.append("illegibility must be retained")
    c = doc.get("coverage", {})
    if tuple(c.get(k) for k in (
            "package_total_pdf_pages", "previously_certified_integral",
            "newly_certified_integral", "integral_after_this_round",
            "not_yet_integral", "partially_read_in_this_round",
            "complete_issues")) != (68, 7, 3, 10, 58, 1, 0):
        errors.append("coverage")
    if any(x.get("phenomenon_hour") is not False or not
           x.get("kind", "").endswith("_NOT_EVENT")
           for x in doc.get("temporal_false_positives", [])):
        errors.append("false event clock")
    if any(x.get("incident_location") is not False for x in
           doc.get("geographic_false_positives", [])):
        errors.append("geographic mismatch")
    g = doc.get("genealogy", {})
    if (g.get("new_independent_hour") is not None or
            g.get("new_independent_eyewitness") is not False or
            g.get("orbit_candidate") is not None):
        errors.append("genealogy")
    return errors


class TestCgeo80(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = json.loads(PATH.read_text(encoding="utf-8"))

    def test_reference(self):
        self.assertEqual(validate(copy.deepcopy(self.ref)), [])

    def test_adversarial_mutations(self):
        changes = (
            ("invent_clock", lambda x: x["page_reviews"][0].__setitem__("event_hour", "17h30")),
            ("invent_witness", lambda x: x["page_reviews"][1].__setitem__("eyewitnesses", ["observer"])),
            ("promote_classifieds", lambda x: x["page_reviews"][2].__setitem__("status", "LIDO_INTEGRAL_SEM_MENCAO")),
            ("erase_illegibility", lambda x: x["page_reviews"][2].__setitem__("unreadable_area", None)),
            ("assume_folio", lambda x: x["page_reviews"][3].__setitem__("printed_page", 10)),
            ("inflate_denominator", lambda x: x["coverage"].__setitem__("integral_after_this_round", 68)),
            ("false_clock", lambda x: x["temporal_false_positives"][2].__setitem__("phenomenon_hour", True)),
            ("false_location", lambda x: x["geographic_false_positives"][0].__setitem__("incident_location", True)),
            ("silent_prose_edit", lambda x: x["page_reviews"][0].__setitem__("notes", "Conde witnessed at 22h")),
            ("corrupt_sha", lambda x: x["source"].__setitem__("sha256", "0"*64)),
        )
        for name, fn in changes:
            with self.subTest(name=name):
                doc = copy.deepcopy(self.ref)
                fn(doc)
                self.assertNotEqual(validate(doc), [], name)


if __name__ == "__main__":
    unittest.main()
