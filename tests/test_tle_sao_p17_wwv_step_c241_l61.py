"""C241-L61 adversarial: Nov-1963 branch gate and no false UTC/528 promotion."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import tle_sao_p17_wwv_step_c241_l61 as sut

class TestP17Clock(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(sut.LEDGER.read_text(encoding="utf-8"))
    def test_canonical(self):
        self.assertEqual(sut.check(self.data)["activated_528_constraints"],0)
    def test_first_branch(self):
        self.assertEqual(sut.a1_minus_wwv("38030.0"),Decimal("2.292725"))
    def test_november_branch(self):
        self.assertEqual(sut.a1_minus_wwv("38334.0"),Decimal("2.732736232"))
    def test_november_eighth(self):
        self.assertEqual(sut.a1_minus_wwv("38341"),Decimal("2.740565438"))
    def test_exact_100_ms_step(self):
        t=Decimal("38334")
        before=Decimal("2.292725")+sut.RATE*(t-sut.MJD_START)
        self.assertEqual(sut.a1_minus_wwv(t)-before,Decimal("0.100000"))
    def test_range_and_type(self):
        for t in ("38029.999","38395","NaN","Infinity",38341.0,True):
            with self.subTest(t=t),self.assertRaises(ValueError):
                sut.a1_minus_wwv(t)
    def test_wrong_boundary_rejected(self):
        bad=copy.deepcopy(self.data)
        bad["model"]["branches"][1]["start_mjd"]="38335.0"
        with self.assertRaises(ValueError): sut.check(bad)
    def test_wrong_offset_rejected(self):
        bad=copy.deepcopy(self.data)
        bad["model"]["branches"][1]["intercept_seconds"]="2.292725"
        with self.assertRaises(ValueError): sut.check(bad)
    def test_wrong_station_rejected(self):
        bad=copy.deepcopy(self.data)
        bad["station_table_context"][0]["site"]="Cold Lake, Canada"
        with self.assertRaises(ValueError): sut.check(bad)
    def test_premature_utc_rejected(self):
        bad=copy.deepcopy(self.data)
        bad["model"]["utc_conversion_proven"]=True
        with self.assertRaises(ValueError): sut.check(bad)
    def test_528_fabrication_rejected(self):
        for field in ("input_528_observation","station_for_528","epoch_utc_528","covariance_528"):
            bad=copy.deepcopy(self.data)
            bad[field]={"fabricated":"yes"}
            with self.subTest(field=field),self.assertRaises(ValueError):
                sut.check(bad)
    def test_new_sensor_or_hard_constraint_rejected(self):
        for key,val in (("independent_528_observations_added",1),("hard_constraints_activated",1),("physical_model_modified",True)):
            bad=copy.deepcopy(self.data);bad[key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):
                sut.check(bad)
    def test_modified_pdf_rejected_before_pypdf(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"not-original.pdf"
            p.write_bytes(b"%PDF-fake")
            with self.assertRaises(ValueError): sut.verify_pdf(p)

if __name__=="__main__":unittest.main()
