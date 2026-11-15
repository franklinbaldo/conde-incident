import copy,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import cgeo65_uh_bn_inventory_validate as v
class TestCGEO65(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=json.loads(v.FILE.read_text())
 def bad(self,fn):
  d=copy.deepcopy(self.data);fn(d)
  with self.assertRaises((ValueError,KeyError,FileNotFoundError)):v.validate(d)
 def test_good(self):self.assertEqual(v.validate(self.data),(26,288))
 def test_mutated_frozen_sha(self):self.bad(lambda d:d.update(prereg_git_blob_sha="0"*40))
 def test_modified_source_hash(self):self.bad(lambda d:d["issues"][0].update(sha256="garbage"))
 def test_duplicated_issue(self):self.bad(lambda d:d["issues"].__setitem__(0,d["issues"][1]))
 def test_changed_original_url(self):self.bad(lambda d:d["issues"][0].update(url="https://fake.net"))
 def test_404_not_observation(self):self.bad(lambda d:d["issues"][14].update(sha256="1"*64))
 def test_page_denominator(self):self.bad(lambda d:d["coverage"].update(pages_fully_inspected_for_rates=288))
 def test_ocr_not_article_count(self):self.bad(lambda d:d["coverage"].update(articles_confirmed_by_protocol=0))
 def test_no_control_rate(self):self.bad(lambda d:d["coverage"].update(control_baseline_rates={"F03":0}))
 def test_outside_control_week(self):self.bad(lambda d:d["visually_reviewed_pdf_pages"][0].update(scope="CONTROL_OCT14"))
 def test_visual_page_date_not_fabricated(self):
  self.bad(lambda d:d["visually_reviewed_pdf_pages"][3].update(date="1963-10-19"))
 def test_visual_scope_not_reassigned(self):
  self.bad(lambda d:d["visually_reviewed_pdf_pages"][3].update(scope="OUT_OF_SAMPLE"))
 def test_visual_note_not_promoted_to_event_hour(self):
  self.bad(lambda d:d["visually_reviewed_pdf_pages"][3].update(note="Independent Conde fall time 20:44"))
 def test_duplicate_page_does_not_hide_claim(self):
  self.bad(lambda d:d["visually_reviewed_pdf_pages"].append({**d["visually_reviewed_pdf_pages"][3],"note":"Independent Conde fall time 20:44"}))
 def test_no_supports_null(self):self.bad(lambda d:d["conclusion"].update(general="SUPPORTS_NULL"))
 def test_no_orbital_promotion(self):self.bad(lambda d:d["conclusion"].update(orbital_constraint=True))
 def test_real_bytes_required(self):
  with tempfile.TemporaryDirectory() as p:
   with self.assertRaises(FileNotFoundError):v.validate(self.data,p)
