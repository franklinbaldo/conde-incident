"""CGEO-70 adversarial tests: prevent fake denominator, witness and chronology."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import cgeo70_uh_four_internal_pages_validate as v

class CGEO70Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.args=[json.loads(p.read_text(encoding="utf-8"))
                  for p in (v.DATA,v.INVENTORY,v.COVERS,v.PREREG,v.PRIOR)]
    def fails(self,mutator):
        d=copy.deepcopy(self.args[0])
        mutator(d)
        with self.assertRaises((ValueError,KeyError,TypeError)):
            v.validate(d,*self.args[1:])
    def test_original(self):
        self.assertEqual(v.validate(*self.args),4)
    def test_wrong_source_sha(self):
        self.fails(lambda d:d["pages"][0].update(source_sha256="0"*64))
    def test_date_shift(self):
        self.fails(lambda d:d["pages"][1].update(date="1963-11-08"))
    def test_week_shift(self):
        self.fails(lambda d:d["pages"][2].update(week="TARGET_NOV04"))
    def test_page_shift(self):
        self.fails(lambda d:d["pages"][0].update(pdf_page=1))
    def test_duplicate_page(self):
        self.fails(lambda d:d["pages"].append(copy.deepcopy(d["pages"][0])))
    def test_mutated_frozen_hash(self):
        self.fails(lambda d:d.update(prereg_blob_sha="0"*40))
    def test_false_metal_sphere(self):
        self.fails(lambda d:d["pages"][1]["confirmed_article_counts"].update(F01_METAL_SPHERE=1))
    def test_false_windows(self):
        self.fails(lambda d:d["pages"][0]["lexical_adjudication"].update(fbis_composite_match=True))
    def test_moon_as_metal_sphere(self):
        self.fails(lambda d:d["pages"][2]["lexical_adjudication"].update(fragment_or_context="F01_METAL_SPHERE"))
    def test_unread_article_as_witness(self):
        self.fails(lambda d:d["pages"][3].update(independent_conde_witness=True))
    def test_false_full_edition(self):
        self.fails(lambda d:d["pages"][3].update(whole_issue_read=True))
    def test_wrong_denominator(self):
        self.fails(lambda d:d["coverage"].update(total_pages_scoped_across_cgeo69_cgeo70=288))
    def test_false_rate(self):
        self.fails(lambda d:d["coverage"].update(full_corpus_baseline_rate=0))
    def test_false_pre_event(self):
        self.fails(lambda d:d["coverage"].update(first_pre_event_occurrence="1963-10-22"))
    def test_false_global_verdict(self):
        self.fails(lambda d:d["coverage"].update(general_verdict="SUPPORTS_NULL"))
    def test_fraud_claim(self):
        self.fails(lambda d:d["lineage_and_limits"].update(deliberate_fraud_proven=True))
    def test_claimed_orbit(self):
        self.fails(lambda d:d["lineage_and_limits"].update(orbital_constraint_activated=True))
    def test_selection_bias_removed(self):
        self.fails(lambda d:d.update(selection_bias="Representative pages"))
    def test_unknown_fragment(self):
        self.fails(lambda d:d["pages"][0]["confirmed_article_counts"].update(UNKNOWN=0))

if __name__=="__main__":
    unittest.main()
