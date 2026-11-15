"""Negative tests: panoramic reading must never become complete source evidence."""
import copy
import json
import unittest
from tools.audit_ultima_hora_rj_castor_g86 import MANIFEST, validate

class TestG86(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good=json.loads(MANIFEST.read_text(encoding="utf8"))

    def test_canonical(self):
        self.assertTrue(validate(self.good))

    def mutate(self, path, value):
        m=copy.deepcopy(self.good)
        cur=m
        for key in path[:-1]:cur=cur[key]
        cur[path[-1]]=value
        with self.assertRaises(ValueError):validate(m)

    def test_source_sha(self):
        self.mutate(["source","sha256"],"0"*64)
    def test_source_date(self):
        self.mutate(["source","date_from_cover"],"1963-11-10")
    def test_claim_fully_read(self):
        self.mutate(["coverage","full_columns_read"],True)
    def test_claim_full_issue_negative(self):
        self.mutate(["coverage","full_issue_negative_certified"],True)
    def test_claim_full_page_negative(self):
        self.mutate(["coverage","pages",0,"whole_page_negative_certified"],True)
    def test_claim_all_text_legible(self):
        self.mutate(["coverage","pages",4,"small_text_legibility"],"FULL")
    def test_invent_event_time(self):
        self.mutate(["coverage","locally_verified_independent_conde_event_time"],"20:30")
    def test_claim_sunday_absence(self):
        self.mutate(["adjacent_catalog","absence_proven_all_issues"],True)
    def test_pretend_special_not_found(self):
        self.mutate(["adjacent_catalog","nov10_special_edition"],"NO_EDITION")
    def test_make_orbit_constraint(self):
        self.mutate(["interpretation","orbit_exclusion_licensed"],True)
    def test_make_article_witness(self):
        self.mutate(["related_headlines",0,"relevant_event_witness"],True)
    def test_remove_page(self):
        m=copy.deepcopy(self.good);m["coverage"]["pages"].pop()
        with self.assertRaises(ValueError):validate(m)

if __name__=="__main__":
    unittest.main()
