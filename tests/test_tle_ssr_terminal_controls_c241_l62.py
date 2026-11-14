"""C241-L62 adversarial tests run normally and under -O."""
import copy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import tle_ssr_terminal_controls_c241_l62 as audit

class TerminalControlsTest(unittest.TestCase):
    def setUp(self):self.d=audit.load()
    def test_baseline(self):self.assertTrue(audit.validate(self.d))
    def mutant(self, fn):
        data=copy.deepcopy(self.d);fn(data)
        with self.assertRaises(ValueError):audit.validate(data)
    def test_day_not_utc(self):self.mutant(lambda d:d["controls"][0].__setitem__("terminal_utc","1963-11-26T00:00:00Z"))
    def test_no_interval_fabrication(self):self.mutant(lambda d:d["controls"][1].__setitem__("terminal_interval_utc",["00:00Z","23:59Z"]))
    def test_no_station_fabrication(self):self.mutant(lambda d:d["controls"][0].__setitem__("station","Shemya"))
    def test_no_sigma_fabrication(self):self.mutant(lambda d:d["controls"][1].__setitem__("measurement_error",0))
    def test_no_instrument_fabrication(self):self.mutant(lambda d:d["controls"][0].__setitem__("original_instrument_log","fabricated"))
    def test_no_independence_promotion(self):self.mutant(lambda d:d["source"].__setitem__("compiled_data_is_independent_instrumental_observation",True))
    def test_no_528_promotion(self):self.mutant(lambda d:d["inference"].__setitem__("NORAD_528_constraints_added",1))
    def test_no_timestamp_count_promotion(self):self.mutant(lambda d:d["inference"].__setitem__("terminal_timestamp_measurements_added",1))
    def test_no_identity_arithmetic(self):self.mutant(lambda d:d["controls"][0].__setitem__("norad_id",293))
    def test_no_date_changed(self):self.mutant(lambda d:d["controls"][1].__setitem__("printed_decay_day","25 NOV 63"))
    def test_no_date_swap(self):self.mutant(lambda d:d["controls"].reverse())
    def test_no_custody_hash_drift(self):self.mutant(lambda d:d["source"].__setitem__("pdf_sha256","0"*64))
    def test_no_source_duplication(self):self.mutant(lambda d:d["source"].__setitem__("same_pdf_as_existing_C241_L18",False))
    def test_no_308_promotion(self):self.mutant(lambda d:d["unresolved"][0].__setitem__("terminal_utc","1963-10-30T00:00:00Z"))
    def test_no_668_promotion(self):self.mutant(lambda d:d["unresolved"][1].__setitem__("primary_terminal_time_status","CONFIRMED"))
    def test_duplicate_key(self):
        with self.assertRaises(ValueError):audit.reject_duplicates([("decay",1),("decay",2)])
    def test_wrong_pdf(self):
        with self.assertRaises(ValueError):audit.verify_pdf(ROOT/"AGENTS.md")

if __name__=="__main__":unittest.main()
