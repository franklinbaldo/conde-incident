"""CGEO-77: verify bounded page screening without promoting it to a negative.

Offline assertions never pretend that a PDF was retrieved or that every article
was read. Only the custodied source and the bounded inspection support claims.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/editorial/cgeo77_uh_nov14_visual_page_screen_20261115.json"
SOURCE = ROOT / "research/editorial/cgeo76_uh_nov13_14_custody_20261115.json"
CANON_SHA = "34e86d9a158dcfc82a94043f1ff7140aa4597314ecb513dd44ae24cdb6bf5395"


def canonical(data):
    return hashlib.sha256(json.dumps(
        data, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def validate(data):
    bad = []
    def check(ok, tag):
        if not ok:
            bad.append(tag)

    check(data.get("id") == "CGEO-77" and data.get("type") ==
          "HistoricalPressVisualPageCensusWithBoundedArticleAdjudication", "identity")
    s = data.get("source", {})
    check(s.get("issue_id") == "00477" and s.get("cover_date") == "1963-11-14" and
          s.get("pdf_pages") == 10 and s.get("pdf_size_bytes") == 5209201 and
          s.get("pdf_sha256") ==
          "0a5170a69e037166ef1fdf502797cef8fc74211b45183af0da775eedc7072fb0",
          "original provenance")
    check(s.get("url") ==
          "https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00477.pdf",
          "original URL")
    parent = json.loads(SOURCE.read_text(encoding="utf-8"))
    check(any(x["issue_id"] == "00477" and x["sha256"] == s.get("pdf_sha256")
              for x in parent["sources"]), "inherited custody")
    m = data.get("method", {})
    check(m.get("pdf_committed") is False and
          m.get("renders_committed") is False and
          "not full article-by-article reading" in " ".join(m.get("limitations", [])),
          "bounded review method")
    p = data.get("page_screenings", [])
    check(len(p) == 10 and sorted(x.get("pdf_page") for x in p) == list(range(1, 11)),
          "ten distinct page locators")
    for x in p:
        check(x.get("render_status") == "PANORAMA_IMAGE_REVIEWED" and
              x.get("entire_page_article_read") is False and
              x.get("conde_event_hour_verified") is False and
              x.get("event_hour_literal") is None and
              len(x.get("render_sha256", "")) == 64,
              "false page completion or fabricated hour")
        check(x.get("conde_event_article_fully_read") is (x.get("pdf_page") == 7),
              "focused article scope")
        check(x.get("independent_eyewitness_verified") is
              (False if x.get("pdf_page") == 7 else None), "witness state")
    a = data.get("article_adjudication", {})
    check(a.get("pdf_page") == 7 and a.get("genre") ==
          "SATIRICAL_EDITORIAL_COMMENTARY" and
          a.get("independent_observation") is False and
          a.get("independent_local_event_time") is None and
          a.get("new_witness") is False and
          a.get("same_article_as_cgeo76") is True,
          "commentary misclassified as observation")
    c = data.get("coverage", {})
    check(c.get("distinct_pages_with_panorama_screening") == 10 and
          c.get("pages_fully_read_article_by_article_this_round") == 0 and
          c.get("full_issues_certified_this_round") == 0 and
          c.get("remaining_pages_in_this_issue_requiring_full_article_review") == 10 and
          c.get("priority_one_route_A_complete") is False and
          c.get("new_independent_event_times") == 0,
          "unsupported full negative or route completion")
    check(canonical(data) == CANON_SHA, "source interpretation changed")
    return bad


class CGEO77(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PATH.read_text(encoding="utf-8"))

    def test_baseline(self):
        self.assertEqual(validate(self.data), [])

    def test_source_tamper(self):
        d = copy.deepcopy(self.data)
        d["source"]["pdf_sha256"] = "0" * 64
        self.assertIn("original provenance", validate(d))

    def test_page_fabrication(self):
        d = copy.deepcopy(self.data)
        d["page_screenings"].pop()
        self.assertIn("ten distinct page locators", validate(d))

    def test_false_full_page(self):
        d = copy.deepcopy(self.data)
        d["page_screenings"][0]["entire_page_article_read"] = True
        self.assertIn("false page completion or fabricated hour", validate(d))

    def test_fake_event_time(self):
        d = copy.deepcopy(self.data)
        d["page_screenings"][6]["event_hour_literal"] = "19:30"
        self.assertIn("false page completion or fabricated hour", validate(d))

    def test_fake_eyewitness(self):
        d = copy.deepcopy(self.data)
        d["article_adjudication"]["independent_observation"] = True
        self.assertIn("commentary misclassified as observation", validate(d))

    def test_fake_all_read(self):
        d = copy.deepcopy(self.data)
        d["coverage"]["full_issues_certified_this_round"] = 1
        self.assertIn("unsupported full negative or route completion", validate(d))

    def test_free_text_change(self):
        d = copy.deepcopy(self.data)
        d["scientific_conclusion"] += " Full issue was negative."
        self.assertIn("source interpretation changed", validate(d))


if __name__ == "__main__":
    unittest.main()
