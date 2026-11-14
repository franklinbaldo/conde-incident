"""Guard against turning a selected 1963 SAO catalogue into a fake 528 sensor."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from tle_sao_p17_coverage_c241_l44 import check,read_ledger,EXPECTED,live_check

class ScopeGate(unittest.TestCase):
    def setUp(self): self.model=read_ledger()
    def mutate_rejected(self,fn):
        m=copy.deepcopy(self.model)
        fn(m)
        with self.assertRaises(ValueError): check(m)
    def test_baseline(self):
        self.assertEqual(check(self.model)["included_satellites"],11)
    def test_missing_satellite(self):
        self.mutate_rejected(lambda m:m["included_designations"].pop())
    def test_fabricated_528_line(self):
        self.mutate_rejected(lambda m:m["observed_targets_in_this_publication"].append("1963-003B"))
    def test_fabricated_station(self):
        self.mutate_rejected(lambda m:m.update(station_for_527_528_529="SAO-1"))
    def test_fabricated_instrument_epoch(self):
        self.mutate_rejected(lambda m:m.update(epoch_utc_for_527_528_529="1963-11-08T00:00:00Z"))
    def test_claim_global_absence(self):
        self.mutate_rejected(lambda m:m.update(inference="NO_TRACKING_OF_528_EXISTED"))
    def test_forged_hash(self):
        self.mutate_rejected(lambda m:m["source"].update(sha256="0"*64))
    def test_invented_sigma(self):
        self.mutate_rejected(lambda m:m["context_not_target_sigma"].update(position_rms_for_printed_rows_arcsec=0))
    def test_activate_impact(self):
        self.mutate_rejected(lambda m:m.update(conde_impact_location="CONFIRMED"))
    def test_change_source_date(self):
        self.mutate_rejected(lambda m:m["source"].update(published="1963-12-31"))
    def test_wrong_original_bytes(self):
        with self.assertRaises(ValueError): live_check(b"%PDF-1.5")
if __name__=="__main__": unittest.main()
