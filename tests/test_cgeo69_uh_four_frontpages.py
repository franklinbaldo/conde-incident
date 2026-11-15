"""CGEO-69: adversarial guards for scoped newspaper-page negatives."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cgeo69_uh_four_frontpages_validate as v


class CGEO69Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.inv, cls.covers, cls.prereg = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in (v.DATA, v.INVENTORY, v.COVERS, v.PREREG)
        ]

    def fails(self, change):
        d = copy.deepcopy(self.doc)
        change(d)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            v.validate(d, self.inv, self.covers, self.prereg)

    def test_original_four_full_pages(self):
        self.assertEqual(v.validate(self.doc, self.inv, self.covers, self.prereg), 4)

    def test_predeclared_slots_cannot_change(self):
        self.fails(lambda d: d["coverage"].update(predeclared_slots_changed=1))

    def test_wrong_source_hash(self):
        self.fails(lambda d: d["pages"][0].update(source_sha256="0" * 64))

    def test_wrong_source_url(self):
        self.fails(lambda d: d["pages"][0].update(source_url="https://example.com/source.pdf"))

    def test_date_shift(self):
        self.fails(lambda d: d["pages"][0].update(date="1963-11-08"))

    def test_week_shift(self):
        self.fails(lambda d: d["pages"][0].update(week="TARGET_NOV04"))

    def test_wrong_page(self):
        self.fails(lambda d: d["pages"][0].update(pdf_page=2))

    def test_not_an_exhaustive_issue(self):
        self.fails(lambda d: d["pages"][0].update(whole_edition_read=True))

    def test_no_false_conde_witness(self):
        self.fails(lambda d: d["pages"][0].update(independent_conde_witness=True))

    def test_no_fabricated_article_match(self):
        self.fails(lambda d: d["pages"][0]["confirmed_article_counts"].update(F01_METAL_SPHERE=1))

    def test_no_missing_fragments(self):
        self.fails(lambda d: d["pages"][0]["confirmed_article_counts"].pop("F08_INDECIPHERABLE_INSCRIPTIONS"))

    def test_no_extra_articles(self):
        self.fails(lambda d: d["pages"][0]["confirmed_article_counts"].update(extra=0))

    def test_no_false_lexical_match(self):
        self.fails(lambda d: d["pages"][1]["ambiguous_lexical_leads"][0].update(fragment_match=True))

    def test_lexical_context_cannot_be_conde(self):
        self.fails(lambda d: d["pages"][2]["ambiguous_lexical_leads"][0].update(context="Conde spacecraft"))

    def test_no_window_from_opening_congress(self):
        self.fails(lambda d: d["pages"][3]["ambiguous_lexical_leads"][0].update(fragment_match=True))

    def test_no_duplicate_front_page(self):
        self.fails(lambda d: d["pages"].append(copy.deepcopy(d["pages"][0])))

    def test_no_count_for_unread_page(self):
        self.fails(lambda d: d["coverage"].update(other_pages_read_in_this_fatia=1))

    def test_no_count_for_unread_edition(self):
        self.fails(lambda d: d["coverage"].update(whole_issues_read=1))

    def test_no_undocumented_baseline_rate(self):
        self.fails(lambda d: d["coverage"].update(baseline_full_corpus=0))

    def test_no_global_verdict(self):
        self.fails(lambda d: d["coverage"].update(general_verdict="SUPPORTS_NULL"))

    def test_no_false_8_nov_chronology(self):
        self.fails(lambda d: d["interpretation"].update(chronology_of_8_nov_known=True))

    def test_no_historical_geocode(self):
        self.fails(lambda d: d["interpretation"].update(historical_center_1963=[-11, -37]))

    def test_no_orbital_constraint(self):
        self.fails(lambda d: d["interpretation"].update(orbital_constraint_activated=True))

    def test_no_assertion_or_optimize_bypass(self):
        self.fails(lambda d: d.update(prereg_blob_sha="0" * 40))

    def test_sampling_claim_is_mandatory(self):
        self.fails(lambda d: d.update(selection_caveat="Sample proves baseline absence"))


if __name__ == "__main__":
    unittest.main()
