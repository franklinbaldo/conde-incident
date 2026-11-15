"""CGEO-75: frozen two-week negative-observation census.

Offline tests verify provenance and registered stopping rule. They DO NOT
independently certify microprint transcription or any physical event.
"""
import copy
import hashlib
import json
import unittest
from unittest import mock
from pathlib import Path

import test_cgeo74_uh_target_week_census as upstream_audit

ROOT = Path(__file__).resolve().parents[1]
ED = ROOT / "research/editorial"
PATH = ED / "cgeo75_uh_control_week_stop_20261115.json"
PIN = "323a83cb58c84c8e275ef92d4bf5d42ef483c84c365e28e0b405cc43e80e6af7"
PRIOR_PIN = "9e2299f592d13c5dbd5fcbdb62161f95684c72cbf50a6c7f78f4810785a0e8a3"
PREREG_BLOB = "0d13d9359080699e5f8402ca9b7014d7f1f6d59a"
SOURCES = {
    "00440": ("1963-10-07", "9d62fd8ef1b02b482eecebe43a85b5c40c47c74a075698b59c5e014faf335178"),
    "00441": ("1963-10-08", "d848b848d290bc1a76bf027366d6f547f82cad7a01f505aaa5a63bcbbc2eeb2e"),
    "00443": ("1963-10-10", "8d3a2248f2f056c25c6d95b74bd2ac1fef74082657ffbb82aeaca0ec4fc70c93"),
    "00444": ("1963-10-11", "6b3cb55cb4d8c104b6c7d27b8bf3910858cb91df37043c3777c313a2da42fc25"),
}
PAGE_SCHEMA = {"issue_id", "pdf_page", "review", "context",
               "confirmed_fbis_compound_motifs", "independent_conde_witness"}
COVERAGE = {
    "new_distinct_pages", "prior_distinct_pages", "cumulative_distinct_pages",
    "by_week_distinct_pages", "completed_target_issues", "completed_control_oct07_issues",
    "target_week_pdf_pages", "target_week_pages_visually_read",
    "control_oct07_week_pdf_pages", "control_oct07_pages_visually_read",
    "confirmed_compound_motif_articles_new", "confirmed_pre_8_nov_motif_origin",
    "same_day_nov08_f03_lexical_article", "journal_do_brasil_status",
    "baseline_rate_representative", "preregistered_eight_fragments_unchanged",
    "preregistered_fifty_slots_unchanged", "hypotheses_H0_H3_verdict",
    "stopping_rule_met", "stop_after_this_census"
}


def canonical(d):
    return hashlib.sha256(json.dumps(
        d, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode()).hexdigest()


def load(name):
    return json.loads((ED / name).read_text(encoding="utf8"))


def blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def validate(d):
    e = []

    def require(condition, message):
        if not condition:
            e.append(message)

    require(d.get("id") == "CGEO-75" and
            d.get("type") == "NarrativeNullControlWeekStopCensus", "identity")
    require(d.get("prereg_path") ==
            "research/editorial/cgeo64_null_narrative_prereg_20261114.json", "prereg path")
    require(blob(ROOT / "research/editorial/cgeo64_null_narrative_prereg_20261114.json") ==
            d.get("prereg_git_blob_sha") == PREREG_BLOB, "frozen prereg")
    require(d.get("prior_cumulative_manifest") ==
            "research/editorial/cgeo74_uh_target_week_census_20261115.json", "prior path")
    prior = load("cgeo74_uh_target_week_census_20261115.json")
    require(canonical(prior) == d.get("prior_canonical_sha256") == PRIOR_PIN, "prior canon")
    require(prior["coverage"]["cumulative_distinct_pages"] == 64 and
            prior["coverage"]["by_week_distinct_pages"] ==
            {"TARGET_NOV04": 48, "CONTROL_OCT07": 8,
             "CONTROL_OCT14": 4, "CONTROL_OCT21": 4}, "prior coverage")
    # An unchanged immediate manifest cannot certify modified ancestral sources.
    require(not upstream_audit.validate(prior), "prior source ancestry changed")
    inventory = {x["id"]: x for x in load("cgeo65_uh_bn_inventory_20261115.json")["issues"]}
    dates = {x["issue_id"]: x["date"] for x in
             load("cgeo66_uh_cover_dates_20261115.json")["cover_dates"]}
    actual = set()
    for source in d["source_pdfs"]:
        issue = source["issue_id"]
        require(issue in SOURCES and issue not in actual, "unexpected source")
        actual.add(issue)
        if issue not in SOURCES:
            continue
        date, sha = SOURCES[issue]
        require(source["date"] == dates[issue] == date and
                source["sha256"] == inventory[issue]["sha256"] == sha and
                source["pdf_url"] == inventory[issue]["url"] and
                source["pdf_pages"] == inventory[issue]["pages"] == 10, "source custody")
        require(source["visual_pages_new"] == list(range(1, 11)), "source page range")
    require(actual == set(SOURCES), "missing original source")
    pages = set()
    for page in d["new_visually_reviewed_pages"]:
        require(set(page) == PAGE_SCHEMA, "unexpected page field")
        key = (page["issue_id"], page["pdf_page"])
        require(key not in pages and key in
                {(issue, n) for issue in SOURCES for n in range(1, 11)},
                "duplicate/unfrozen page")
        pages.add(key)
        require(page["review"] == "FULL_PAGE_VISUAL_RENDER_1650PX_WITH_EMBEDDED_TEXT_LEADS" and
                type(page["confirmed_fbis_compound_motifs"]) is int and
                page["confirmed_fbis_compound_motifs"] == 0 and
                page["independent_conde_witness"] is False, "unsupported occurrence")
    require(pages == {(issue, n) for issue in SOURCES for n in range(1, 11)},
            "incomplete control sample")
    c = d["coverage"]
    require(set(c) == COVERAGE, "coverage schema changed")
    require(c["new_distinct_pages"] == len(pages) == 40 and
            c["prior_distinct_pages"] == 64 and
            c["cumulative_distinct_pages"] == 104, "denominator")
    require(c["by_week_distinct_pages"] ==
            {"TARGET_NOV04": 48, "CONTROL_OCT07": 48,
             "CONTROL_OCT14": 4, "CONTROL_OCT21": 4}, "week denominator")
    require(c["completed_target_issues"] ==
            ["00467", "00468", "00469", "00470", "00471"] and
            c["completed_control_oct07_issues"] ==
            ["00440", "00441", "00442", "00443", "00444"] and
            c["target_week_pdf_pages"] == c["target_week_pages_visually_read"] == 48 and
            c["control_oct07_week_pdf_pages"] ==
            c["control_oct07_pages_visually_read"] == 48 and
            c["stopping_rule_met"] is True and
            c["stop_after_this_census"] is True, "stop gate not met")
    require(c["confirmed_compound_motif_articles_new"] == 0 and
            c["confirmed_pre_8_nov_motif_origin"] is None and
            c["same_day_nov08_f03_lexical_article"] == 1 and
            c["baseline_rate_representative"] is None and
            c["hypotheses_H0_H3_verdict"] == "UNDETERMINED", "invalid hypothesis inference")
    require(c["journal_do_brasil_status"] == "HTTP_403_NOT_ACQUIRED_NOT_READ" and
            c["preregistered_eight_fragments_unchanged"] is True and
            c["preregistered_fifty_slots_unchanged"] is True,
            "access failure or frozen design masked")
    require(d["genealogy"]["pre_8_nov_composite_fbis_motif_found"] is False and
            d["genealogy"]["independent_conde_witness_identified"] is False and
            d["genealogy"]["proof_of_editorial_borrowing"] is False and
            d["genealogy"]["claim_of_fabrication"] is False, "invented provenance")
    require(canonical(d) == PIN, "pinned interpretation changed")
    return e


class CGEO75ControlStop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(PATH.read_text(encoding="utf8"))

    def test_original_is_valid(self):
        self.assertEqual(validate(self.d), [])

    def mutate(self, update, error):
        d = copy.deepcopy(self.d)
        update(d)
        self.assertIn(error, validate(d))

    def test_ancestor_interpretation_source_only_mutation_rejected(self):
        original_read = upstream_audit.upstream_audit.read

        def mutate(path):
            record = original_read(path)
            if path.endswith("cgeo72_uh_one_complete_issue_20261115.json"):
                record["pages"][0]["note"] += " [SYNTHETIC] Conde eyewitness 20:15"
            return record

        with mock.patch.object(upstream_audit.upstream_audit, "read", side_effect=mutate):
            self.assertIn("prior source ancestry changed", validate(self.d))

    def test_ancestor_inventory_source_only_mutation_rejected(self):
        original_read = upstream_audit.upstream_audit.read

        def mutate(path):
            record = original_read(path)
            if path.endswith("cgeo65_uh_bn_inventory_20261115.json"):
                record["issues"][0]["status"] = "SYNTHETIC_FAKE"
            return record

        with mock.patch.object(upstream_audit.upstream_audit, "read", side_effect=mutate):
            self.assertIn("prior source ancestry changed", validate(self.d))

    def test_source_hash(self):
        self.mutate(lambda d: d["source_pdfs"][0].update(sha256="0" * 64), "source custody")

    def test_source_cover_date(self):
        self.mutate(lambda d: d["source_pdfs"][0].update(date="1963-11-08"), "source custody")

    def test_source_pages_dropped(self):
        self.mutate(lambda d: d["source_pdfs"][0]["visual_pages_new"].pop(), "source page range")

    def test_duplicated_page(self):
        self.mutate(lambda d: d["new_visually_reviewed_pages"].append(
            d["new_visually_reviewed_pages"][0]), "duplicate/unfrozen page")

    def test_unread_page(self):
        self.mutate(lambda d: d["new_visually_reviewed_pages"].pop(), "incomplete control sample")

    def test_false_witness(self):
        self.mutate(lambda d: d["new_visually_reviewed_pages"][0].update(
            independent_conde_witness=True), "unsupported occurrence")

    def test_false_fbis_motif(self):
        self.mutate(lambda d: d["new_visually_reviewed_pages"][0].update(
            confirmed_fbis_compound_motifs=1), "unsupported occurrence")

    def test_hidden_event_hour(self):
        self.mutate(lambda d: d["new_visually_reviewed_pages"][0].update(
            local_event_hour="20:15"), "unexpected page field")

    def test_false_denominator(self):
        self.mutate(lambda d: d["coverage"].update(cumulative_distinct_pages=105),
                    "denominator")

    def test_false_zero_baseline(self):
        self.mutate(lambda d: d["coverage"].update(baseline_rate_representative=0),
                    "invalid hypothesis inference")

    def test_false_verdict(self):
        self.mutate(lambda d: d["coverage"].update(hypotheses_H0_H3_verdict="REJECTED"),
                    "invalid hypothesis inference")

    def test_false_40_out_of_40_target(self):
        self.mutate(lambda d: d["coverage"].update(target_week_pages_visually_read=40),
                    "stop gate not met")

    def test_false_fabricated_witness_in_commentary(self):
        self.mutate(lambda d: d["new_visually_reviewed_pages"][0].update(
            context="A NASA witness said the sphere landed at 20h15 in Conde."),
            "pinned interpretation changed")

    def test_fabricated_methods_rejected(self):
        self.mutate(lambda d: d.update(method=d["method"] +
                    " Satellite 528 is now confirmed."), "pinned interpretation changed")

    def test_fabricated_borrowing(self):
        self.mutate(lambda d: d["genealogy"].update(
            proof_of_editorial_borrowing=True), "invented provenance")

    def test_frozen_slots_not_zeroed(self):
        self.mutate(lambda d: d["coverage"].update(
            journal_do_brasil_status="ZERO_MATCHES"), "access failure or frozen design masked")

    def test_stop_removal(self):
        self.mutate(lambda d: d["coverage"].update(stop_after_this_census=False),
                    "stop gate not met")


if __name__ == "__main__":
    unittest.main()
