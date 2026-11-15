"""CGEO-79: audit conservative page coverage and unrelated clock traps.

Offline checks freeze the reviewed interpretation; PASS does not re-fetch the PDF.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path

PATH = (Path(__file__).resolve().parents[1] /
        "research/editorial/cgeo79_uh_00472_pages5_6_20261115.json")
EXPECTED_DOC_SHA = "407e80d7b1a7243108268b29a29c932fdc6d67a3b5c4db15dbf1d1bdcbf9fd68"
PDF_SHA = "8564c0c8c26857e0feda54fc5da0f9d3ca0c34c8de02c44e3074aa79a101cece"


def validate(doc):
    problems = []
    frozen = hashlib.sha256(json.dumps(
        doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if frozen != EXPECTED_DOC_SHA:
        problems.append("frozen interpretation")

    def require(condition, message):
        if not condition:
            problems.append(message)

    require(doc.get("id") == "CGEO-79" and doc.get("status") ==
            "PARTIAL_ISSUE_NO_EVENT_CLOCK", "identity")
    source = doc.get("source", {})
    require(source.get("edition") == "00472" and
            source.get("cover_date") == "1963-11-09" and
            source.get("size_bytes") == 5275519 and
            source.get("pdf_pages") == 10 and
            source.get("sha256") == PDF_SHA, "source")
    method = doc.get("method", {})
    require(method.get("original_pdf_sha256_rechecked") is True and
            method.get("new_ocr") is False and
            method.get("printed_folio_assumed_from_pdf_index") is False,
            "method")
    reviews = doc.get("page_reviews", [])
    require([(r.get("pdf_page"), r.get("printed_page"), r.get("status"))
             for r in reviews] ==
            [(5, 5, "LIDO_INTEGRAL_SEM_MENCAO"),
             (6, None, "ILEGIVEL_PARCIAL")], "page scoped findings")
    for r in reviews:
        require(r.get("event_hour") is None and
                r.get("eyewitnesses") == [], "no inferred witness/clock")
    coverage = doc.get("coverage", {})
    require((coverage.get("package_total_pdf_pages"),
             coverage.get("previously_certified_integral"),
             coverage.get("newly_certified_integral"),
             coverage.get("integral_after_this_round"),
             coverage.get("not_yet_integral"),
             coverage.get("complete_issues")) ==
            (68, 6, 1, 7, 61, 0), "scope totals")
    genealogy = doc.get("genealogy", {})
    require(genealogy.get("new_independent_eyewitness") is False and
            genealogy.get("new_independent_hour") is None and
            genealogy.get("orbit_candidate") is None, "genealogy")
    temporal = doc.get("temporal_false_positives", [])
    require(len(temporal) == 3 and all(
        x.get("phenomenon_hour") is False and
        x.get("kind", "").endswith("_NOT_EVENT") for x in temporal),
        "unrelated clock traps")
    return problems


class TestCgeo79(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads(PATH.read_text(encoding="utf-8"))

    def fresh(self):
        return copy.deepcopy(self.reference)

    def test_reference(self):
        self.assertEqual(validate(self.fresh()), [])

    def test_negative_mutants(self):
        mutations = (
            ("fabricated_clock", lambda x: x["page_reviews"][0].__setitem__(
                "event_hour", "20:15")),
            ("invented_witness", lambda x: x["page_reviews"][1].__setitem__(
                "eyewitnesses", ["new independent witness"])),
            ("promote_partial", lambda x: x["page_reviews"][1].__setitem__(
                "status", "LIDO_INTEGRAL_SEM_MENCAO")),
            ("invent_folio", lambda x: x["page_reviews"][1].__setitem__(
                "printed_page", 6)),
            ("inflate_coverage", lambda x: x["coverage"].__setitem__(
                "integral_after_this_round", 68)),
            ("false_time_equivalence", lambda x:
             x["temporal_false_positives"][1].__setitem__(
                 "phenomenon_hour", True)),
            ("invent_headline", lambda x: x["page_reviews"][0]["topics"].append(
                "NASA records 20:15 descent at Conde")),
            ("silent_prose_edit", lambda x: x["page_reviews"][1].__setitem__(
                "notes", "The incident was confirmed at 5h30.")),
            ("custody_downgrade", lambda x: x["source"].__setitem__(
                "custody", "NOT_VERIFIED")),
            ("new_undeclared_field", lambda x: x.__setitem__(
                "event_clock", "5h30")),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                doc = self.fresh()
                mutate(doc)
                self.assertIn("frozen interpretation", validate(doc))


if __name__ == "__main__":
    unittest.main()
