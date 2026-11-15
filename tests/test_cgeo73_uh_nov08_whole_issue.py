"""CGEO-73: whole-issue evidence controls for Nov 8, 1963 UH/Recife.

The tests check documentary provenance, the frozen preregistration,
nonoverlapping denominators and interpretation, NOT the remote PDF bytes.
The original PDF's SHA-256 was rechecked independently on Ifro.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ED = ROOT / "research/editorial"
PATH = ED / "cgeo73_uh_nov08_whole_issue_20261115.json"
PINNED_RECORD_SHA256 = "083094b506567ec6dd52c471ab80acfd484eaa843377b1c1a96b8fa144216c04"
PREREG_BLOB = "0d13d9359080699e5f8402ca9b7014d7f1f6d59a"
SOURCE_SHA = "e121d6ea9784bcb77a02e1a6e3c453f23987103940f5993190237c45499a95ec"
PINNED_UPSTREAM = {
    "research/editorial/cgeo65_uh_bn_inventory_20261115.json": "181b9f9279a7caddd7549792f203cc8de811a351aad6a8865f300391c115b671",
    "research/editorial/cgeo66_uh_cover_dates_20261115.json": "c7f6b17b4a79c4afd4d4db842209737e51d7d31e794890991def5b745388abab",
    "research/editorial/cgeo69_uh_four_frontpages_20261115.json": "85c2906f8caf815299dacffa34926ea8e7c06791ff775a627ea37c4476af329c",
    "research/editorial/cgeo70_uh_four_internal_pages_20261115.json": "7ef8147b87cc198e949622626e0ded8577a7eba2cf9a7fa47655970316139520",
    "research/editorial/cgeo71_uh_four_page3_20261115.json": "179fe47ccfc9800203df01b61c02915af67d5a2576ebe3514491be4ff9f5fb14",
    "research/editorial/cgeo72_uh_one_complete_issue_20261115.json": "6450eb53c224c74434392f2eed6600ca306cc0127afb45e59b511cbbf2dd22c9",
}
F03 = "F03_FOUR_METER_HOLE"
PREVIOUS = {("00442", p) for p in range(1, 9)}
PREVIOUS |= {("00447", p) for p in (1, 3, 4, 5)}
PREVIOUS |= {("00455", p) for p in (1, 3, 4, 5)}
PREVIOUS |= {("00467", p) for p in (1, 2, 3, 4)}
PAGES = {"pdf_page", "review", "editorial_context",
         "lexical_f03_hole_other_event_articles",
         "confirmed_conde_event_composite_articles", "independent_conde_witness"}
COVERAGE = {"new_fully_reviewed_pages", "previous_distinct_fully_reviewed_pages",
            "combined_distinct_fully_reviewed_pages", "by_week_distinct_pages",
            "completed_issue_ids", "completed_issue_count", "target_issue_00471_pages",
            "f03_lexical_articles_different_story_same_day",
            "confirmed_fbis_conde_event_composite_articles",
            "journal_do_brasil_pages", "preregistered_date_slots_changed",
            "first_pre_event_occurrence", "representative_baseline_rate", "general_verdict"}


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + bytes([0]) + data).hexdigest()


def canonical_sha(d):
    return hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def validate(d):
    errors = []
    def check(ok, msg):
        if not ok:
            errors.append(msg)
    upstream_paths = {d["source_inventory_path"], d["cover_crosswalk_path"],
                      *d["prior_whole_page_audits"]}
    check(upstream_paths == set(PINNED_UPSTREAM), "upstream lineage changed")
    for path, expected_sha in PINNED_UPSTREAM.items():
        check(canonical_sha(read(path)) == expected_sha,
              "upstream approved interpretation changed: " + path)
    frozen = (ROOT / d["prereg_path"]).read_bytes()
    check(git_blob_sha(frozen) == d["prereg_git_blob_sha"] == PREREG_BLOB,
          "preregistered bytes changed")
    inventory = read(d["source_inventory_path"])["issues"]
    original = next((i for i in inventory if i["id"] == "00471"), None)
    check(original is not None, "inventory missing source")
    src = d["source"]
    check(set(src) == {"publication", "issue_id", "cover_date", "preregistered_week",
                       "url", "sha256", "pdf_pages", "source_relation"}, "source schema")
    if original:
        check(original["status"] == "PDF_BYTES_ACQUIRED" and
              original["url"] == src["url"] and original["sha256"] == SOURCE_SHA ==
              src["sha256"] and original["pages"] == src["pdf_pages"] == 8,
              "source inventory mismatch")
    cover = next((x for x in read(d["cover_crosswalk_path"])["cover_dates"]
                  if x["issue_id"] == "00471"), None)
    check(cover is not None and cover["date"] == src["cover_date"] == "1963-11-08",
          "cover date mismatch")
    check(src["publication"] == "UH_RE" and src["issue_id"] == "00471" and
          src["preregistered_week"] == "TARGET_NOV04", "scope changed")
    prior = set()
    for path in d["prior_whole_page_audits"]:
        for p in read(path)["pages"]:
            pair = (p["issue_id"], p["pdf_page"])
            check(pair not in prior, "prior page duplicate")
            prior.add(pair)
    check(prior == PREVIOUS, "prior denominator altered")
    observed = set()
    for p in d["pages"]:
        check(set(p) == PAGES, "page schema changed")
        n = p["pdf_page"]
        check(type(n) is int and 1 <= n <= 8 and n not in observed, "page duplicate/outside PDF")
        observed.add(n)
        check(p["review"] == "WHOLE_PAGE_VISUAL_1700PX_PDF_TEXT_AUXILIARY",
              "visual review not certified")
        check(type(p["confirmed_conde_event_composite_articles"]) is int and
              p["confirmed_conde_event_composite_articles"] == 0 and
              p["independent_conde_witness"] is False, "unproven event or witness")
        check(type(p["lexical_f03_hole_other_event_articles"]) is int and
              p["lexical_f03_hole_other_event_articles"] == (1 if n == 8 else 0),
              "lexical article count altered")
    check(observed == set(range(1, 9)), "not a full fascicle")
    check(not prior.intersection({("00471", n) for n in observed}), "duplicate prior page")
    c = d["coverage"]
    check(set(c) == COVERAGE, "coverage schema")
    check(c["new_fully_reviewed_pages"] == 8 and
          c["previous_distinct_fully_reviewed_pages"] == len(prior) == 20 and
          c["combined_distinct_fully_reviewed_pages"] == len(prior) + len(observed) == 28,
          "inflated denominator")
    check(c["by_week_distinct_pages"] ==
          {"CONTROL_OCT07": 8, "CONTROL_OCT14": 4,
           "CONTROL_OCT21": 4, "TARGET_NOV04": 12}, "week denominator")
    check(c["completed_issue_ids"] == ["00442", "00471"] and
          c["completed_issue_count"] == 2 and c["target_issue_00471_pages"] == 8,
          "false completed issue count")
    check(c["f03_lexical_articles_different_story_same_day"] == 1 and
          c["confirmed_fbis_conde_event_composite_articles"] == 0, "lexical/event confusion")
    check(c["journal_do_brasil_pages"] == 0 and
          c["preregistered_date_slots_changed"] == 0 and
          c["first_pre_event_occurrence"] is None and
          c["representative_baseline_rate"] is None and
          c["general_verdict"] == "UNDETERMINED", "unsupported inference")
    a = d["article_boundary"]
    check(a["lexical_fragment_id"] == F03 and a["lexical_match_count"] == 1 and
          a["matches_fbis_conde_event"] is False and
          a["same_day_but_known_pre_fbis_publication"] is False and
          a["other_article_window_is_fbis_f04"] is False and
          a["same_page_means_same_article"] is False and
          a["same_newspaper_means_independent_witness"] is False,
          "article genealogy promoted")
    check(canonical_sha(d) == PINNED_RECORD_SHA256,
          "document interpretation changed without review")
    return errors


class CGEO73WholeIssue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(PATH.read_text(encoding="utf-8"))

    def test_valid_source_and_record(self):
        self.assertEqual(validate(self.d), [])

    def test_first_and_last_page_and_eight_total(self):
        self.assertEqual([x["pdf_page"] for x in self.d["pages"]], list(range(1, 9)))

    def test_source_hash_change_rejected(self):
        d = copy.deepcopy(self.d); d["source"]["sha256"] = "0" * 64
        self.assertIn("source inventory mismatch", validate(d))

    def test_source_date_change_rejected(self):
        d = copy.deepcopy(self.d); d["source"]["cover_date"] = "1963-11-09"
        self.assertIn("cover date mismatch", validate(d))

    def test_add_ninth_page_rejected(self):
        d = copy.deepcopy(self.d); d["pages"].append(copy.deepcopy(d["pages"][-1]))
        self.assertIn("page duplicate/outside PDF", validate(d))

    def test_delete_page_rejected(self):
        d = copy.deepcopy(self.d); d["pages"].pop(0)
        self.assertIn("not a full fascicle", validate(d))

    def test_false_event_witness_rejected(self):
        d = copy.deepcopy(self.d); d["pages"][0]["independent_conde_witness"] = True
        self.assertIn("unproven event or witness", validate(d))

    def test_false_local_hour_field_rejected(self):
        d = copy.deepcopy(self.d); d["pages"][0]["conde_hour"] = "20:15"
        self.assertIn("page schema changed", validate(d))

    def test_erase_real_lexical_f03_rejected(self):
        d = copy.deepcopy(self.d); d["pages"][-1]["lexical_f03_hole_other_event_articles"] = 0
        self.assertIn("lexical article count altered", validate(d))

    def test_promote_lexical_f03_to_conde_event_rejected(self):
        d = copy.deepcopy(self.d); d["article_boundary"]["matches_fbis_conde_event"] = True
        self.assertIn("article genealogy promoted", validate(d))

    def test_claim_time_order_rejected(self):
        d = copy.deepcopy(self.d); d["article_boundary"]["same_day_but_known_pre_fbis_publication"] = True
        self.assertIn("article genealogy promoted", validate(d))

    def test_merge_separate_articles_rejected(self):
        d = copy.deepcopy(self.d); d["article_boundary"]["same_page_means_same_article"] = True
        self.assertIn("article genealogy promoted", validate(d))

    def test_inflate_pages_rejected(self):
        d = copy.deepcopy(self.d); d["coverage"]["combined_distinct_fully_reviewed_pages"] = 36
        self.assertIn("inflated denominator", validate(d))

    def test_false_zero_representative_rate_rejected(self):
        d = copy.deepcopy(self.d); d["coverage"]["representative_baseline_rate"] = 0
        self.assertIn("unsupported inference", validate(d))

    def test_false_global_verdict_rejected(self):
        d = copy.deepcopy(self.d); d["coverage"]["general_verdict"] = "SUPPORTS_NULL"
        self.assertIn("unsupported inference", validate(d))

    def test_fake_event_hour_in_free_note_rejected(self):
        d = copy.deepcopy(self.d); d["pages"][2]["editorial_context"] += " Conde at 20:15"
        self.assertIn("document interpretation changed without review", validate(d))

    def test_fabricated_nasa_confirmation_in_method_rejected(self):
        d = copy.deepcopy(self.d); d["method"] += " NASA confirmed satellite 528."
        self.assertIn("document interpretation changed without review", validate(d))

    def test_reinterpret_page_without_review_rejected(self):
        d = copy.deepcopy(self.d); d["pages"][0]["editorial_context"] = "Conde vessel recovered"
        self.assertIn("document interpretation changed without review", validate(d))


    def test_upstream_prior_note_source_only_mutation_rejected(self):
        target = self.d["prior_whole_page_audits"][-1]
        real_read = read

        def mutated(path):
            doc = real_read(path)
            if path == target:
                doc["pages"][0]["note"] += " Synthetic witness in Conde at 20:15."
            return doc

        with patch(f"{__name__}.read", side_effect=mutated):
            self.assertIn("upstream approved interpretation changed: " + target,
                          validate(self.d))

    def test_upstream_inventory_source_only_mutation_rejected(self):
        target = self.d["source_inventory_path"]
        real_read = read

        def mutated(path):
            doc = real_read(path)
            if path == target:
                doc["synthetic_claim"] = "NASA confirms Conde fall at 20:15."
            return doc

        with patch(f"{__name__}.read", side_effect=mutated):
            self.assertIn("upstream approved interpretation changed: " + target,
                          validate(self.d))

if __name__ == "__main__":
    unittest.main()
