"""CGEO-72: verify observed page ledger and resist ungrounded promotions."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "research/editorial"
RECORD = P / "cgeo72_uh_one_complete_issue_20261115.json"
FIDS = ("F01_METAL_SPHERE", "F02_CITY_CENTER", "F03_FOUR_METER_HOLE",
        "F04_WINDOWS", "F05_THICK_GLASS", "F06_HUMAN_BODY",
        "F07_HEAVY_CLOTHES", "F08_INDECIPHERABLE_INSCRIPTIONS")
EXPECTED = {("00442", n) for n in (2, 4, 5, 7, 8)} | {
    ("00447", 4), ("00455", 4), ("00467", 4)}
KEYS = {"publication", "issue_id", "date", "week", "pdf_page",
        "source_url", "source_sha256", "review", "note",
        "confirmed_article_counts", "independent_conde_witness",
        "whole_issue_complete_with_prior_audits"}

def load(name):
    return json.loads((P / name).read_text(encoding="utf-8"))

def git_blob_sha(b):
    return hashlib.sha1(b"blob " + str(len(b)).encode() + bytes([0]) + b).hexdigest()

def validate(d):
    errors = []
    def check(condition, error):
        if not condition:
            errors.append(error)
    prereg_bytes = (ROOT / d["prereg_path"]).read_bytes()
    check(git_blob_sha(prereg_bytes) == d["prereg_git_blob_sha"] ==
          "0d13d9359080699e5f8402ca9b7014d7f1f6d59a",
          "preregistered source mutated")
    inventory = {r["id"]: r for r in load("cgeo65_uh_bn_inventory_20261115.json")["issues"]}
    dates = {r["issue_id"]: r["date"] for r in load("cgeo66_uh_cover_dates_20261115.json")["cover_dates"]}
    prior = set()
    for path in d["prior_audit_paths"]:
        for r in json.loads((ROOT / path).read_text(encoding="utf-8"))["pages"]:
            prior.add((r["issue_id"], r["pdf_page"]))
    observed = set()
    for p in d["pages"]:
        check(set(p) == KEYS, "page schema changed")
        pair = (p["issue_id"], p["pdf_page"])
        check(pair not in observed and pair not in prior, "duplicate page")
        observed.add(pair)
        i = inventory.get(p["issue_id"], {})
        check(i.get("status") == "PDF_BYTES_ACQUIRED", "source unavailable")
        check(i.get("sha256") == p["source_sha256"], "source hash mismatch")
        check(i.get("url") == p["source_url"], "source URL mismatch")
        check(dates.get(p["issue_id"]) == p["date"], "cover date mismatch")
        check(isinstance(p["pdf_page"], int) and 1 <= p["pdf_page"] <= i.get("pages",0),
              "page number outside original")
        check(p["publication"] == "UH_RE" and p["review"].startswith("WHOLE_PAGE_VISUAL"),
              "review provenance")
        check(p["independent_conde_witness"] is False, "invented witness")
        check(p["whole_issue_complete_with_prior_audits"] is (p["issue_id"] == "00442"),
              "complete-issue flag")
        check(set(p["confirmed_article_counts"]) == set(FIDS),
              "motif list altered")
        check(all(type(v) is int and v == 0 for v in p["confirmed_article_counts"].values()),
              "unsupported new occurrence")
    check(observed == EXPECTED, "missing or invented page")
    all_pages = observed | prior
    check({(i, p) for i,p in all_pages if i=="00442"} ==
          {("00442", j) for j in range(1,9)}, "complete issue claim unsupported")
    check(len(all_pages)==20, "denominator mismatch")
    c=d["coverage"]
    check(set(c)=={"new_distinct_pages","prior_cgeo69_pages","prior_cgeo70_pages",
                  "prior_cgeo71_pages","total_distinct_pages_scoped",
                  "by_week_pages_scoped","whole_issues_reviewed_count",
                  "completed_issue_id","completed_issue_pdf_pages",
                  "completed_issue_observed_composite_occurrences",
                  "jb_pages_read","preregistered_slots_changed",
                  "first_pre_event_occurrence","representative_baseline_rate",
                  "general_verdict"}, "coverage schema changed")
    check(c["new_distinct_pages"]==8 and c["total_distinct_pages_scoped"]==20,
          "new/total page count")
    check(c["by_week_pages_scoped"]=={"CONTROL_OCT07":8,"CONTROL_OCT14":4,
                                      "CONTROL_OCT21":4,"TARGET_NOV04":4},
          "wrong week denominators")
    check(c["whole_issues_reviewed_count"]==1 and c["completed_issue_id"]=="00442"
          and c["completed_issue_pdf_pages"]==8, "unsupported issue completion")
    check(c["completed_issue_observed_composite_occurrences"] ==
          dict.fromkeys(FIDS, 0), "unsupported issue rate")
    check(c["jb_pages_read"]==0 and c["preregistered_slots_changed"]==0,
          "prereg/sample changed")
    check(c["first_pre_event_occurrence"] is None and
          c["representative_baseline_rate"] is None and
          c["general_verdict"]=="UNDETERMINED", "unsupported scientific conclusion")
    check(d["lineage_and_limits"]["independent_newspaper_issues_in_this_fatia"]==0,
          "independence inflation")
    return errors

class CGEO72(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(RECORD.read_text(encoding="utf-8"))

    def test_record_valid(self):
        self.assertEqual(validate(self.d), [])

    def test_new_pages_exact(self):
        self.assertEqual({(r["issue_id"],r["pdf_page"]) for r in self.d["pages"]},EXPECTED)

    def test_missing_page_rejected(self):
        d=copy.deepcopy(self.d); d["pages"].pop()
        self.assertIn("missing or invented page",validate(d))

    def test_duplicate_page_rejected(self):
        d=copy.deepcopy(self.d); d["pages"][0]["pdf_page"]=1
        self.assertIn("duplicate page",validate(d))

    def test_source_hash_rejected(self):
        d=copy.deepcopy(self.d); d["pages"][0]["source_sha256"]="0"*64
        self.assertIn("source hash mismatch",validate(d))

    def test_false_witness_rejected(self):
        d=copy.deepcopy(self.d); d["pages"][0]["independent_conde_witness"]=True
        self.assertIn("invented witness",validate(d))

    def test_false_motif_rejected(self):
        d=copy.deepcopy(self.d); d["pages"][0]["confirmed_article_counts"][FIDS[0]]=1
        self.assertIn("unsupported new occurrence",validate(d))

    def test_new_hour_field_rejected(self):
        d=copy.deepcopy(self.d); d["pages"][0]["local_event_time"]="23:00"
        self.assertIn("page schema changed",validate(d))

    def test_false_zero_baseline_rejected(self):
        d=copy.deepcopy(self.d); d["coverage"]["representative_baseline_rate"]=0.0
        self.assertIn("unsupported scientific conclusion",validate(d))

    def test_completed_issue_count_rejected(self):
        d=copy.deepcopy(self.d); d["coverage"]["whole_issues_reviewed_count"]=4
        self.assertIn("unsupported issue completion",validate(d))

if __name__=="__main__":
    unittest.main()
