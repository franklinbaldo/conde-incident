"""Adversarial checks for 1962 Exhibit 5 (source is not an individual sensor)."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("moa", ROOT/"tools/tle_gsfc_norad_moa_audit.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
data = json.loads(mod.LEDGER.read_text())
parent = json.loads(mod.PARENT.read_text())

class TestMoA(unittest.TestCase):
    def test_source_and_unknowns(self):
        result=mod.validate(data,parent)
        self.assertEqual(result["channels_connected"],5)
        self.assertEqual(result["physical_constraints_activated"],0)
        self.assertFalse(result["pdf_replayed"])

    def test_source_mutations(self):
        for key,value in (
            ("published_on","1963-11-08"),
            ("agreement_date","1963-11"),
            ("pdf_sha256","0"*64),
            ("pdf_bytes",123),
            ("printed_pages",[7,14]),
            ("effective_for_object_1963_003","YES"),
        ):
            with self.subTest(field=key):
                bad=copy.deepcopy(data)
                bad["document"][key]=value
                with self.assertRaises(ValueError): mod.validate(bad,parent)

    def test_directions_and_scopes(self):
        for key,value in (
            ("from","GSFC"),("to","NAVSPASUR"),
            ("qualifier","APPLIES_TO_NORAD528"),("printed_page",16),
        ):
            with self.subTest(field=key):
                bad=copy.deepcopy(data)
                bad["channels"][0][key]=value
                with self.assertRaises(ValueError): mod.validate(bad,parent)
        for hours in (0,24):
            bad=copy.deepcopy(data)
            bad["navspasur_nominal_hours"]=hours
            with self.assertRaises(ValueError): mod.validate(bad,parent)

    def test_no_fake_object_measurements(self):
        for key,value in (
            ("station","Cold Lake"),("sensor","radar"),
            ("epoch_utc","1963-11-08T00:00:00Z"),
            ("frame","TEME"),("sigma",0.1),
            ("observation_id","UNVERIFIED"),
        ):
            with self.subTest(field=key):
                bad=copy.deepcopy(data)
                bad["objects"][1][key]=value
                with self.assertRaises(ValueError): mod.validate(bad,parent)

    def test_no_independence_promotion(self):
        for key,value in (
            ("independence","INDEPENDENT"),
            ("activation","PHYSICAL"),
            ("physical_domain_effect","THETA_REDUCED"),
        ):
            bad=copy.deepcopy(data)
            bad[key]=value
            with self.assertRaises(ValueError): mod.validate(bad,parent)
        bad=copy.deepcopy(parent)
        bad["pdf_sha256"]="f"*64
        with self.assertRaises(ValueError): mod.validate(data,bad)

    def test_reject_altered_pdf(self):
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/"fake.pdf"
            file.write_bytes(b"%PDF-1.4 fake")
            with self.assertRaises(ValueError): mod.validate(data,parent,file)

if __name__=="__main__":
    unittest.main()
