"""CGEO-74: signed target-week facsimile observations and bounded denominators.

Offline tests confirm consistency and prevent silent re-interpretation; they
cannot independently certify human reading of the original scanned microtext.
"""
import copy
import hashlib
import json
import unittest
from unittest import mock
from pathlib import Path

import test_cgeo73_uh_nov08_whole_issue as upstream_audit

ROOT = Path(__file__).resolve().parents[1]
ED = ROOT / "research/editorial"
PATH = ED / "cgeo74_uh_target_week_census_20261115.json"
PINNED_CANONICAL = "9e2299f592d13c5dbd5fcbdb62161f95684c72cbf50a6c7f78f4810785a0e8a3"
UPSTREAM_CANONICAL = "083094b506567ec6dd52c471ab80acfd484eaa843377b1c1a96b8fa144216c04"
PREREG_BLOB = "0d13d9359080699e5f8402ca9b7014d7f1f6d59a"
SOURCES = {
    "00467": ("1963-11-04", "82c0345dccc9c7d48db3512b134b84b0d1d39579410b5f91530109674bd995f9"),
    "00468": ("1963-11-05", "b4cc898a2f7fcc6a427f4a0c707045b5bad8d8c819e8034b96d4a4ebcec54eaf"),
    "00469": ("1963-11-06", "c1ab434f4253288892f4959d1d39789690e77a5f0be3f801b98c371c5c0641a0"),
    "00470": ("1963-11-07", "da04933d49f7a41571701163f341ab67fcb9ab3bcf76f0e620d32f793e889157"),
}
EXPECTED_PAGE_SCHEMA = {"issue_id", "pdf_page", "review", "context", "confirmed_fbis_compound_motifs", "independent_conde_witness"}
EXPECTED_COVERAGE = {"new_distinct_pages", "prior_distinct_pages", "cumulative_distinct_pages", "by_week_distinct_pages", "completed_target_issues", "target_week_issues_completed", "target_week_issues_required", "target_week_pdf_pages", "target_week_pages_visually_read", "completed_control_oct07_issues", "control_oct07_issues_required", "confirmed_compound_motif_articles_in_new_pages", "confirmed_pre_8_nov_motif_origin", "same_day_nov08_f03_lexical_article", "journal_do_brasil_status", "baseline_rate_representative", "preregistered_eight_fragments_unchanged", "preregistered_fifty_slots_unchanged", "hypotheses_H0_H3_verdict"}

def data(path):
    return json.loads((ED / path).read_text(encoding="utf-8"))

def canonical(d):
    return hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()

def git_blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def validate(d):
    errors = []
    def check(ok, msg):
        if not ok:
            errors.append(msg)
    check(d.get("id") == "CGEO-74" and d.get("type") == "NarrativeNullTargetWeekCensus", "type or id changed")
    check(d.get("prereg_path") == "research/editorial/cgeo64_null_narrative_prereg_20261114.json", "prereg path changed")
    check(git_blob(ROOT / d["prereg_path"]) == d["prereg_git_blob_sha"] == PREREG_BLOB, "frozen prereg changed")
    check(d.get("prior_cumulative_manifest") == "research/editorial/cgeo73_uh_nov08_whole_issue_20261115.json", "prior lineage")
    prior = data("cgeo73_uh_nov08_whole_issue_20261115.json")
    check(canonical(prior) == UPSTREAM_CANONICAL, "prior interpretation changed")
    # A pinned immediate manifest must not mask changes in its ancestor sources.
    check(not upstream_audit.validate(prior), "prior source ancestry changed")
    inventory = {x["id"]: x for x in data("cgeo65_uh_bn_inventory_20261115.json")["issues"]}
    covers = {x["issue_id"]: x["date"] for x in data("cgeo66_uh_cover_dates_20261115.json")["cover_dates"]}
    source_ids = set()
    for src in d["source_pdfs"]:
        issue = src["issue_id"]
        check(issue not in source_ids and issue in SOURCES, "source duplicated or unknown")
        source_ids.add(issue)
        if issue not in SOURCES:
            continue
        date, sha = SOURCES[issue]
        check(src["sha256"] == inventory[issue]["sha256"] == sha and
              src["pdf_pages"] == inventory[issue]["pages"] == 10 and
              src["pdf_url"] == inventory[issue]["url"] and
              src["date"] == covers[issue] == date, "source provenance changed")
    check(source_ids == set(SOURCES), "missing source")
    expected = {("00467", n) for n in range(5, 11)}
    for issue in ("00468", "00469", "00470"):
        expected.update({(issue, n) for n in range(1, 11)})
    found = set()
    for row in d["new_visually_reviewed_pages"]:
        check(set(row) == EXPECTED_PAGE_SCHEMA, "page schema changed")
        key = (row["issue_id"], row["pdf_page"])
        check(key not in found and key in expected, "page out of frozen sample")
        found.add(key)
        check(row["review"] == "FULL_PAGE_VISUAL_RENDER_1650_TO_1750PX_WITH_EMBEDDED_TEXT_LEADS" and
              row["confirmed_fbis_compound_motifs"] == 0 and
              type(row["confirmed_fbis_compound_motifs"]) is int and
              row["independent_conde_witness"] is False, "unsupported event or witness")
    check(found == expected, "unread pages cannot be counted")
    for src in d["source_pdfs"]:
        check(src["visual_pages_new"] == sorted([n for issue, n in found if issue == src["issue_id"]]), "source/page mismatch")
    check(len(prior["pages"]) == 8 and prior["coverage"]["combined_distinct_fully_reviewed_pages"] == 28, "prior denominator")
    c = d["coverage"]
    check(set(c) == EXPECTED_COVERAGE, "coverage schema changed")
    check(c["new_distinct_pages"] == len(found) == 36 and
          c["prior_distinct_pages"] == 28 and c["cumulative_distinct_pages"] == 64, "total denominator")
    check(c["by_week_distinct_pages"] == {"TARGET_NOV04":48, "CONTROL_OCT07":8, "CONTROL_OCT14":4, "CONTROL_OCT21":4}, "week denominator")
    check(c["completed_target_issues"] == ["00467","00468","00469","00470","00471"] and
          c["target_week_issues_completed"] == c["target_week_issues_required"] == 5 and
          c["target_week_pdf_pages"] == c["target_week_pages_visually_read"] == 48 and
          c["completed_control_oct07_issues"] == ["00442"] and
          c["control_oct07_issues_required"] == 5, "false full-week coverage")
    check(c["confirmed_compound_motif_articles_in_new_pages"] == 0 and
          c["confirmed_pre_8_nov_motif_origin"] is None and
          c["same_day_nov08_f03_lexical_article"] == 1, "lexical/event conflation")
    check(c["journal_do_brasil_status"] == "HTTP_403_NOT_ACQUIRED_NOT_READ" and
          c["baseline_rate_representative"] is None and
          c["preregistered_eight_fragments_unchanged"] is True and
          c["preregistered_fifty_slots_unchanged"] is True and
          c["hypotheses_H0_H3_verdict"] == "UNDETERMINED", "unsupported interpretation")
    check(d["genealogy"]["pre_event_compound_fbis_motif_confirmed"] is False and
          d["genealogy"]["independent_conde_witness_identified"] is False, "genealogy promoted")
    check(canonical(d) == PINNED_CANONICAL, "document interpretation changed without review")
    return errors

class CGEO74TargetWeek(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(PATH.read_text(encoding="utf-8"))
    def test_original_record(self):
        self.assertEqual(validate(self.d), [])
    def test_changed_ancestor_interpretation_rejected(self):
        original_read = upstream_audit.read
        def changed(path):
            record = original_read(path)
            if path.endswith("cgeo72_uh_one_complete_issue_20261115.json"):
                record["pages"][0]["note"] += " [synthetic] Conde 20:15 eyewitness"
            return record
        with mock.patch.object(upstream_audit, "read", side_effect=changed):
            self.assertIn("prior source ancestry changed", validate(self.d))

    def test_changed_ancestor_inventory_rejected(self):
        original_read = upstream_audit.read
        def changed(path):
            record = original_read(path)
            if path.endswith("cgeo65_uh_bn_inventory_20261115.json"):
                record["issues"][0]["status"] = "SYNTHETIC_FAKE"
            return record
        with mock.patch.object(upstream_audit, "read", side_effect=changed):
            self.assertIn("prior source ancestry changed", validate(self.d))

    def test_source_hash_falsification_rejected(self):
        d=copy.deepcopy(self.d); d["source_pdfs"][0]["sha256"]="0"*64
        self.assertIn("source provenance changed", validate(d))
    def test_missing_full_page_rejected(self):
        d=copy.deepcopy(self.d); d["new_visually_reviewed_pages"].pop()
        self.assertIn("unread pages cannot be counted", validate(d))
    def test_duplicate_page_rejected(self):
        d=copy.deepcopy(self.d); d["new_visually_reviewed_pages"].append(d["new_visually_reviewed_pages"][0])
        self.assertIn("page out of frozen sample", validate(d))
    def test_fake_witness_rejected(self):
        d=copy.deepcopy(self.d); d["new_visually_reviewed_pages"][0]["independent_conde_witness"]=True
        self.assertIn("unsupported event or witness", validate(d))
    def test_hidden_new_local_hour_rejected(self):
        d=copy.deepcopy(self.d); d["new_visually_reviewed_pages"][0]["event_hour"]="20:15"
        self.assertIn("page schema changed", validate(d))
    def test_false_rate_zero_rejected(self):
        d=copy.deepcopy(self.d); d["coverage"]["baseline_rate_representative"]=0
        self.assertIn("unsupported interpretation", validate(d))
    def test_deceptive_motive_conclusion_rejected(self):
        d=copy.deepcopy(self.d); d["genealogy"]["pre_event_compound_fbis_motif_confirmed"]=True
        self.assertIn("genealogy promoted", validate(d))
    def test_fabricated_note_rejected(self):
        d=copy.deepcopy(self.d); d["new_visually_reviewed_pages"][0]["context"] += " NASA confirms Conde"
        self.assertIn("document interpretation changed without review", validate(d))
    def test_fabricated_method_rejected(self):
        d=copy.deepcopy(self.d); d["method"] += " Space-Track confirmed impact."
        self.assertIn("document interpretation changed without review", validate(d))
    def test_wrong_cover_date_rejected(self):
        d=copy.deepcopy(self.d); d["source_pdfs"][1]["date"]="1963-11-08"
        self.assertIn("source provenance changed", validate(d))
    def test_fake_completed_control_week_rejected(self):
        d=copy.deepcopy(self.d); d["coverage"]["completed_control_oct07_issues"].append("00440")
        self.assertIn("false full-week coverage", validate(d))
    def test_other_october_pages_not_zeroed(self):
        self.assertIn("NOT", self.d["limits"][-1].upper())
