import copy
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/"tools/tle_norad_spadats_context_audit.py"
spec=importlib.util.spec_from_file_location("l46",PATH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class TestC241L46(unittest.TestCase):
    def setUp(self):self.d=mod.load()
    def test_real_source_scope(self):self.assertTrue(mod.verify_ledger(self.d))
    def test_no_fake_target_measurement(self):
        for k,v in [("norad",688),("designator","1963-044B"),("observation_utc","1963-11-08T00:00:00Z"),("station","Shemya"),("sigma",0),("decay_hour_utc","2210Z"),("reentry_location","Conde"),("activation",True)]:
            with self.subTest(k=k):
                x=copy.deepcopy(self.d);x["target"][k]=v
                with self.assertRaises(ValueError):mod.verify_ledger(x)
    def test_crosswalk_and_interval(self):
        for k,v in [("object_ids",[527,528]),("launch","1963-003"),("measurement_528",{"time":"1963-11-08"})]:
            with self.subTest(k=k):
                x=copy.deepcopy(self.d);x["sources"][0][k]=v
                with self.assertRaises(ValueError):mod.verify_ledger(x)
        for k,v in [("object_id",528),("date_utc","1963-11-08"),("start","0000Z"),("kind","MEASURED_528")]:
            with self.subTest(k=k):
                x=copy.deepcopy(self.d);x["sources"][1]["decay_window"][k]=v
                with self.assertRaises(ValueError):mod.verify_ledger(x)
    def test_duplicate_json(self):
        with self.assertRaises(ValueError):mod.no_dupes([("x",1),("x",2)])
    def test_fake_pdf_rejected(self):
        with self.assertRaises(ValueError):mod.verify_pdf(self.d["sources"][0],b"%PDF-1.4\\n%%EOF")
if __name__=="__main__":unittest.main()

