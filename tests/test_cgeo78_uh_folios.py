"""CGEO-78: page-scoped audit, never a replacement for visual source inspection.

The offline checks reject fabricated event clocks, an invented witness, and
inflated page coverage. A PASS does not prove archival accessibility.
"""
import copy
import json
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "research/editorial/cgeo78_uh_00472_folio_and_pages_20261115.json"
SHA = "8564c0c8c26857e0feda54fc5da0f9d3ca0c34c8de02c44e3074aa79a101cece"
EXPECTED = [(2, None, "LIDO_INTEGRAL_SEM_MENCAO"),
            (3, 7, "LIDO_INTEGRAL_SEM_MENCAO"),
            (4, 3, "ILEGIVEL_PARCIAL")]
EXPECTED_COVERAGE = {
    "package_total_pdf_pages": 68,
    "previously_certified_integral": 4,
    "newly_certified_integral": 2,
    "integral_after_this_round": 6,
    "not_yet_integral": 62,
    "partially_read_in_this_round": 1,
    "complete_issues": 0,
}


def validate(doc):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    check(doc.get("id") == "CGEO-78" and
          doc.get("status") == "PARTIAL_ISSUE_NO_EVENT_CLOCK" and
          doc.get("priority", "").endswith("/871"), "identity")
    s = doc.get("source", {})
    check(s.get("edition") == "00472" and s.get("cover_date") == "1963-11-09" and
          s.get("pdf_pages") == 10 and s.get("size_bytes") == 5275519 and
          s.get("sha256") == SHA and
          s.get("url") == "https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00472.pdf",
          "original PDF")
    method = doc.get("method", {})
    check(method.get("original_pdf_sha256_rechecked") is True and
          method.get("new_ocr") is False and
          method.get("official_pdf_embedded_in_repo") is False and
          method.get("source_is_an_independent_new_witness") is False and
          "four quadrants" in method.get("visual", ""), "method")
    reviews = doc.get("page_reviews", [])
    check(len(reviews) == 3 and
          [(r.get("pdf_page"), r.get("printed_page"), r.get("status"))
           for r in reviews] == EXPECTED, "page coverage/status/folios")
    for r in reviews:
        check(r.get("event_hour") is None and r.get("eyewitnesses") == [],
              "unsupported event-hour or witness")
        check(bool(r.get("topics")) and bool(r.get("notes")), "documentary context")
    if len(reviews) == 3:
        check(reviews[2].get("unreadable_area") and
              "not certified" in reviews[2].get("unreadable_area", ""),
              "partial region misrepresented")
        check(reviews[0].get("printed_folio") == "NOT_CONFIRMED" and
              "PAGINA_7" in reviews[1].get("printed_folio", "") and
              "PAGINA_3" in reviews[2].get("printed_folio", ""),
              "folio provenance")
    p = doc.get("pagination_caution", {})
    check(p.get("pdf_index_is_not_printed_folio") is True and
          p.get("do_not_autofill_printed_page_from_pdf_index") is True and
          p.get("observed_mapping") == [{"pdf_page": 3, "printed_page": 7},
                                        {"pdf_page": 4, "printed_page": 3}],
          "printed/PDF folio confusion")
    g = doc.get("genealogy", {})
    check(g.get("new_independent_eyewitness") is False and
          g.get("new_independent_hour") is None and
          g.get("orbit_candidate") is None and
          g.get("source_independence") == "NO_NEW_INCIDENT_SOURCE_IDENTIFIED",
          "independence promotion")
    check(doc.get("coverage") == EXPECTED_COVERAGE, "inflated coverage")
    return errors


class CGEO78(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(PATH.read_text(encoding="utf-8"))

    def changed(self):
        return copy.deepcopy(self.doc)

    def test_baseline(self):
        self.assertEqual(validate(self.doc), [])

    def test_wrong_source_digest(self):
        d = self.changed()
        d["source"]["sha256"] = "0" * 64
        self.assertIn("original PDF", validate(d))

    def test_wrong_edition(self):
        d = self.changed()
        d["source"]["edition"] = "00477"
        self.assertIn("original PDF", validate(d))

    def test_invented_event_hour(self):
        d = self.changed()
        d["page_reviews"][1]["event_hour"] = "23h43"
        self.assertIn("unsupported event-hour or witness", validate(d))

    def test_invented_witness(self):
        d = self.changed()
        d["page_reviews"][0]["eyewitnesses"] = ["invented"]
        self.assertIn("unsupported event-hour or witness", validate(d))

    def test_invented_independent_source(self):
        d = self.changed()
        d["genealogy"]["new_independent_eyewitness"] = True
        self.assertIn("independence promotion", validate(d))

    def test_invented_orbit_attribution(self):
        d = self.changed()
        d["genealogy"]["orbit_candidate"] = 528
        self.assertIn("independence promotion", validate(d))

    def test_promote_partial_page(self):
        d = self.changed()
        d["page_reviews"][2]["status"] = "LIDO_INTEGRAL_SEM_MENCAO"
        self.assertIn("page coverage/status/folios", validate(d))

    def test_inflate_count(self):
        d = self.changed()
        d["coverage"]["integral_after_this_round"] = 68
        self.assertIn("inflated coverage", validate(d))

    def test_swap_pdf_and_printed_numbers(self):
        d = self.changed()
        d["page_reviews"][1]["printed_page"] = 3
        self.assertIn("page coverage/status/folios", validate(d))

    def test_forget_pagination_guard(self):
        d = self.changed()
        d["pagination_caution"]["do_not_autofill_printed_page_from_pdf_index"] = False
        self.assertIn("printed/PDF folio confusion", validate(d))

    def test_ocr_promotion(self):
        d = self.changed()
        d["method"]["new_ocr"] = True
        self.assertIn("method", validate(d))


if __name__ == "__main__":
    unittest.main()
