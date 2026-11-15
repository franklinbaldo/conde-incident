"""CGEO-76: documentary custody and non-promotion of editorial commentary.

Source PDF bytes were fetched and independently SHA-256 checked on Ifro.
These offline tests protect the reviewed JSON interpretation and metadata;
they do NOT imply that all pages have been visually read.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/editorial/cgeo76_uh_nov13_14_custody_20261115.json"
CANON_SHA = "9fc5d3e145934bdad68d109f3f40d09feba976f479a2650c13d0b33f4e3e57f9"
ORIGINALS = {
    "00476": ("1963-11-13", 5369187, 10,
              "89af71800faf3d447cf7fd3a2ee473ba010516beb8dc45dd200d220ad65c8047"),
    "00477": ("1963-11-14", 5209201, 10,
              "0a5170a69e037166ef1fdf502797cef8fc74211b45183af0da775eedc7072fb0"),
}
SOURCE_KEYS = {
    "issue_id", "cover_date", "publication", "url", "http_status",
    "pdf_size_bytes", "pdf_pages", "sha256", "source_custody"
}
ARTICLE_KEYS = {
    "issue_id", "pdf_page", "printed_page", "review", "headline", "credit",
    "subject", "short_literal", "mentions_conde_bahia", "source_of_claim",
    "event_time_literal", "independent_conde_event_witness",
    "phenomenon_time_established"
}
ARTICLE_EXPECTED = {
    "00476": (5, "SATÉLITE", "MOSCOU; FP", False,
              "FP agency dispatch"),
    "00477": (7, "A Guerra Dos Mundos na Versão Baiana",
              "Stanislaw Ponte Preta, signed commentary column", True,
              "EDITORIAL_COMMENTARY_OF_UNESTABLISHED_NEWS_LINEAGE")
}


def canonical(d):
    return hashlib.sha256(json.dumps(
        d, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def validate(d):
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    check(d.get("id") == "CGEO-76" and
          d.get("type") == "HistoricalPressPartialSourceCustodyAndArticleAdjudication" and
          d.get("date_utc") == "2026-11-15" and
          d.get("issue") == "https://github.com/franklinbaldo/conde-incident/issues/871",
          "identity")
    check(d.get("status") == "PARTIAL_ARTICLE_LEVEL_NOT_COMPLETE_ISSUES",
          "false issue completion")
    check(set(d.get("method", {})) == {
        "executor", "acquisition", "inspection", "limitations",
        "source_pdf_bytes_in_git"
    } and d["method"].get("source_pdf_bytes_in_git") is False,
          "method schema or false PDF archive")
    check(len(d.get("sources", [])) == 2, "source count")
    issue_ids = set()
    for source in d.get("sources", []):
        check(set(source) == SOURCE_KEYS, "source schema")
        issue = source.get("issue_id")
        check(issue in ORIGINALS and issue not in issue_ids, "source identity")
        issue_ids.add(issue)
        if issue not in ORIGINALS:
            continue
        date, size, pages, sha = ORIGINALS[issue]
        check(source.get("cover_date") == date and
              type(source.get("pdf_size_bytes")) is int and
              source["pdf_size_bytes"] == size and
              type(source.get("pdf_pages")) is int and
              source["pdf_pages"] == pages and
              source.get("sha256") == sha and
              source.get("url") ==
              f"https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_{issue}.pdf" and
              source.get("http_status") == 200 and
              source.get("source_custody") == "ACQUIRED_AND_HASH_VERIFIED_IFRO",
              "PDF custody changed")
    check(issue_ids == set(ORIGINALS), "missing PDF")
    article_ids = set()
    for article in d.get("inspected_article_regions", []):
        check(set(article) == ARTICLE_KEYS, "article schema")
        issue = article.get("issue_id")
        check(issue in ARTICLE_EXPECTED and issue not in article_ids, "article identity")
        article_ids.add(issue)
        if issue not in ARTICLE_EXPECTED:
            continue
        page, title, credit, mentions, claim = ARTICLE_EXPECTED[issue]
        check(article.get("pdf_page") == article.get("printed_page") == page and
              article.get("headline") == title and article.get("credit") == credit and
              article.get("mentions_conde_bahia") is mentions and
              article.get("source_of_claim") == claim and
              article.get("review") == "ARTICLE_REGION_RENDERED_AND_TEXT_ASSISTED",
              "article provenance changed")
        check(article.get("event_time_literal") is None and
              article.get("independent_conde_event_witness") is False and
              article.get("phenomenon_time_established") is False,
              "unverified event hour or witness")
    check(article_ids == set(ARTICLE_EXPECTED), "missing article")
    c = d.get("coverage", {})
    check(set(c) == {
        "pdf_sources_newly_custodied", "pages_in_new_sources",
        "whole_pages_fully_read_this_round", "article_regions_read_this_round",
        "whole_issues_fully_read_this_round",
        "prior_00472_00475_pages_only_panorama",
        "prior_00472_00475_pages_fully_read",
        "full_00472_00477_census_complete",
        "independent_local_event_time_verified",
        "independent_named_eyewitness_verified", "new_orbital_constraints"
    }, "coverage schema")
    check(c.get("pdf_sources_newly_custodied") == 2 and
          c.get("pages_in_new_sources") == 20 and
          c.get("whole_pages_fully_read_this_round") == 0 and
          c.get("article_regions_read_this_round") == 2 and
          c.get("whole_issues_fully_read_this_round") == 0 and
          c.get("prior_00472_00475_pages_only_panorama") == 46 and
          c.get("prior_00472_00475_pages_fully_read") == 2 and
          c.get("full_00472_00477_census_complete") is False and
          c.get("independent_local_event_time_verified") is False and
          c.get("independent_named_eyewitness_verified") is False and
          c.get("new_orbital_constraints") == 0,
          "inflated coverage or unsupported inference")
    check(d.get("provenance", {}).get("same_issue_not_distinct_observation") is True
          and d["provenance"].get("independent_of_tupi_fbis_event_claim") ==
          "NOT_ESTABLISHED", "editorial dependency promoted")
    for path in d.get("provenance", {}).get("previous_source_records", []):
        check((ROOT / path).is_file(), "unresolved parent provenance")
    check(canonical(d) == CANON_SHA, "approved interpretation changed")
    return errors


class CGEO76(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(PATH.read_text(encoding="utf-8"))

    def test_baseline(self):
        self.assertEqual(validate(self.record), [])

    def test_changed_pdf_sha_rejected(self):
        d = copy.deepcopy(self.record)
        d["sources"][1]["sha256"] = "0" * 64
        self.assertIn("PDF custody changed", validate(d))

    def test_invented_hour_rejected(self):
        d = copy.deepcopy(self.record)
        d["inspected_article_regions"][1]["event_time_literal"] = "19h30"
        self.assertIn("unverified event hour or witness", validate(d))

    def test_invented_witness_rejected(self):
        d = copy.deepcopy(self.record)
        d["inspected_article_regions"][1]["independent_conde_event_witness"] = True
        self.assertIn("unverified event hour or witness", validate(d))

    def test_false_full_read_rejected(self):
        d = copy.deepcopy(self.record)
        d["coverage"]["whole_issues_fully_read_this_round"] = 2
        self.assertIn("inflated coverage or unsupported inference", validate(d))

    def test_unsupported_free_text_claim_rejected(self):
        d = copy.deepcopy(self.record)
        d["inspected_article_regions"][1]["subject"] += " Event time was 19h30."
        self.assertIn("approved interpretation changed", validate(d))

    def test_unreviewed_extra_field_rejected(self):
        d = copy.deepcopy(self.record)
        d["inspected_article_regions"][1]["verified_eyewitness_name"] = "Invented"
        self.assertIn("article schema", validate(d))


if __name__ == "__main__":
    unittest.main()
