"""CGEO-77: offline contract for examined pages and temporal false positives.

A passing test protects a documented editorial interpretation, not the
availability or contents of the remote PDF. Recheck original bytes separately.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/editorial/cgeo77_uh_nov09_14_page_scope_20261115.json"
CANON_SHA = "982a8d263571e4160fc2a5ce40efb3897bf476cec1d68f35875578fed578c2ed"
SOURCES = {
    "00472": ("1963-11-09", 10, 5275519, "8564c0c8c26857e0feda54fc5da0f9d3ca0c34c8de02c44e3074aa79a101cece"),
    "00477": ("1963-11-14", 10, 5209201, "0a5170a69e037166ef1fdf502797cef8fc74211b45183af0da775eedc7072fb0"),
}
EXPECTED_PAGES = {("00472", 1), ("00477", 7)}
PHRASES = {
    "duas horas de automóvel da capital": "TRAVEL_DURATION_NOT_TIME_OF_EVENT",
    "24 horas": "NEWS_PROPAGATION_DURATION_NOT_TIME_OF_EVENT",
}


def canonical(record):
    encoded = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate(record):
    errors = []
    def check(ok, message):
        if not ok:
            errors.append(message)

    check(record.get("id") == "CGEO-77" and
          record.get("type") == "HistoricalPressPageScopeAndTemporalPhraseAdjudication" and
          record.get("status") == "PARTIAL_PAGES_NOT_COMPLETE_ISSUES", "identity")
    check(record.get("issue") == "https://github.com/franklinbaldo/conde-incident/issues/871", "issue")
    method = record.get("method", {})
    check(method.get("original_pdfs_committed") is False and
          "4000px" in method.get("visual", "") and
          "no new OCR" in method.get("text_layer", ""), "method")
    got_sources = {s.get("issue_id"): s for s in record.get("sources", [])}
    check(len(record.get("sources", [])) == 2 and set(got_sources) == set(SOURCES), "source set")
    for issue, (date, pages, size, digest) in SOURCES.items():
        s = got_sources.get(issue, {})
        check(s.get("cover_date") == date and
              s.get("url") == f"https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_{issue}.pdf" and
              type(s.get("pdf_pages")) is int and s["pdf_pages"] == pages and
              type(s.get("size_bytes")) is int and s["size_bytes"] == size and
              s.get("sha256") == digest and
              s.get("custody", "").startswith("REPLAYED_HASH_MATCHES_"), "custody " + issue)
    page_reviews = record.get("page_reviews", {})
    check(set(page_reviews) == set(SOURCES), "page issue set")
    integral = set()
    for issue in SOURCES:
        pages = page_reviews.get(issue, [])
        check(len(pages) == 10, "page count " + issue)
        check([p.get("pdf_page") for p in pages] == list(range(1, 11)), "page order " + issue)
        for p in pages:
            key = (issue, p.get("pdf_page"))
            check(p.get("printed_page") == p.get("pdf_page"), "page identity")
            if key in EXPECTED_PAGES:
                check(p.get("status") == ("LIDO_INTEGRAL_COM_MENCAO" if issue == "00477" else
                                         "LIDO_INTEGRAL_SEM_MENCAO"), "reviewed status")
                integral.add(key)
            else:
                check(p.get("status") == "PANORAMA_ONLY_NOT_A_NEGATIVE", "false negative")
    check(integral == EXPECTED_PAGES, "integral page set")
    durations = record.get("temporal_false_positives", [])
    check(len(durations) == 2 and
          {d.get("short_literal"): d.get("kind") for d in durations} == PHRASES, "temporal phrases")
    for item in durations:
        check(item.get("issue_id") == "00477" and item.get("pdf_page") == 7 and
              item.get("phenomenon_hour") is False and
              item.get("credit", "").startswith("Stanislaw Ponte Preta"), "temporal provenance")
    lineage = record.get("documentary_lineage", {})
    check(lineage.get("report_on_conde_in_00477_p7") == "SATIRICAL_RETELLING_OF_ALREADY_CIRCULATING_CLAIM" and
          lineage.get("independent_eyewitness") is False and
          lineage.get("agency_or_original_reporter_for_event") is None and
          lineage.get("independent_of_tupi_fbis") == "NOT_ESTABLISHED" and
          lineage.get("new_phenomenon_hour") is None and
          lineage.get("orbit_candidate_decision") is None, "independence or clock promoted")
    expected_coverage = {
        "pages_in_two_PDFs": 20, "integral_pages_newly_certified": 2,
        "panorama_only_pages": 18, "previously_integral_pages_other_editions": 2,
        "package_total_pages": 68, "package_integral_pages_after_this_round": 4,
        "package_pages_not_integral": 64, "whole_editions_fully_read": 0,
    }
    check(record.get("coverage") == expected_coverage, "coverage inflation")
    check(canonical(record) == CANON_SHA, "approved interpretation changed")
    return errors


class CGEO77(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_baseline(self):
        self.assertEqual(validate(self.record), [])

    def test_missing_pdf_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["sources"].pop()
        self.assertIn("source set", validate(altered))

    def test_changed_source_sha_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["sources"][1]["sha256"] = "0" * 64
        self.assertIn("custody 00477", validate(altered))

    def test_fabricated_full_issue_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["coverage"]["whole_editions_fully_read"] = 2
        self.assertIn("coverage inflation", validate(altered))

    def test_panorama_promoted_to_negative_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["page_reviews"]["00472"][1]["status"] = "LIDO_INTEGRAL_SEM_MENCAO"
        self.assertIn("false negative", validate(altered))

    def test_real_conde_mention_erased_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["page_reviews"]["00477"][6]["status"] = "LIDO_INTEGRAL_SEM_MENCAO"
        self.assertIn("reviewed status", validate(altered))

    def test_travel_duration_promoted_to_event_hour_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["temporal_false_positives"][0]["phenomenon_hour"] = True
        self.assertIn("temporal provenance", validate(altered))

    def test_twentyfour_hours_relabelled_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["temporal_false_positives"][1]["kind"] = "EVENT_TIME"
        self.assertIn("temporal phrases", validate(altered))

    def test_invented_witness_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["documentary_lineage"]["independent_eyewitness"] = True
        self.assertIn("independence or clock promoted", validate(altered))

    def test_invented_literal_clock_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["documentary_lineage"]["new_phenomenon_hour"] = "20h15"
        self.assertIn("independence or clock promoted", validate(altered))

    def test_free_text_temporal_claim_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["page_reviews"]["00477"][6]["notes"] += " Witness saw fall at 20h15."
        self.assertIn("approved interpretation changed", validate(altered))

    def test_extra_field_rejected(self):
        altered = copy.deepcopy(self.record)
        altered["documentary_lineage"]["new_verified_witness"] = "invented name"
        self.assertIn("approved interpretation changed", validate(altered))


if __name__ == "__main__":
    unittest.main()
