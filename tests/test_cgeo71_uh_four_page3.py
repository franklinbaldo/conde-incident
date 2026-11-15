"""Mutation tests for the CGEO-71 page-level contract."""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import cgeo71_uh_four_page3_validate as v
class Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.args=v.load()
    def rejects(self,mut):
        d=copy.deepcopy(self.args[0]);mut(d)
        with self.assertRaises((ValueError,KeyError,TypeError)):
            v.validate(d,*self.args[1:])
    def test_genuine(self):self.assertEqual(v.validate(*self.args),4)
    def test_sha(self):self.rejects(lambda d:d["pages"][0].update(source_sha256="0"*64))
    def test_date(self):self.rejects(lambda d:d["pages"][0].update(date="1963-11-08"))
    def test_page(self):self.rejects(lambda d:d["pages"][2].update(pdf_page=1))
    def test_duplicate(self):self.rejects(lambda d:d["pages"].append(d["pages"][0]))
    def test_frozen(self):self.rejects(lambda d:d.update(prereg_blob_sha="0"*40))
    def test_body(self):self.rejects(lambda d:d["pages"][3]["confirmed_article_counts"].update(F06_HUMAN_BODY=1))
    def test_windows(self):self.rejects(lambda d:d["pages"][1]["lexical_adjudication"].update(fbis_composite_match=True))
    def test_source(self):self.rejects(lambda d:d["pages"][1].update(publication="JB_RJ"))
    def test_witness(self):self.rejects(lambda d:d["pages"][3].update(independent_conde_witness=True))
    def test_full_issue(self):self.rejects(lambda d:d["pages"][0].update(whole_issue_read=True))
    def test_rate(self):self.rejects(lambda d:d["coverage"].update(full_corpus_baseline_rate=0))
    def test_denominator(self):self.rejects(lambda d:d["coverage"].update(total_distinct_pages_scoped=288))
    def test_verdict(self):self.rejects(lambda d:d["coverage"].update(general_verdict="SUPPORTS_NULL"))
    def test_fake_hour(self):self.rejects(lambda d:d.update(event_hour="21:00"))
    def test_fraud(self):self.rejects(lambda d:d.update(interpretation="Fraud proven"))
    def test_orbit(self):self.rejects(lambda d:d["lineage_and_limits"].update(orbital_constraint_activated=True))
    def test_extra_fragment(self):self.rejects(lambda d:d["pages"][0]["confirmed_article_counts"].update(F09=0))
    def test_changed_method(self):self.rejects(lambda d:d.update(method="unverified text only"))
    def test_fake_method_hour(self):self.rejects(lambda d:d.update(method=d["method"]+" Event at 21:00"))
    def test_fake_caveat_claim(self):self.rejects(lambda d:d.update(selection_bias=d["selection_bias"]+" The narrative was a fraud."))
    def test_fake_page_claim(self):self.rejects(lambda d:d["pages"][0].update(event_hour="21:00"))
if __name__=="__main__":unittest.main()
