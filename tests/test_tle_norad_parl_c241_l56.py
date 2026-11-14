"""Adversarial provenance checks in normal and optimized Python."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from tle_norad_parl_c241_l56 import audit,load,verify_pdf


class TestParl(unittest.TestCase):
    def setUp(self): self.model=load()
    def reject(self,fn):
        candidate=copy.deepcopy(self.model);fn(candidate)
        with self.assertRaises(ValueError): audit(candidate)
    def test_ok(self): self.assertEqual(audit(self.model),{"anchors":3,"physics":0})
    def test_parent_sha(self): self.reject(lambda d:d.update(parent_sha256="0"*64))
    def test_parent_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"wrong";p.write_bytes(b"{}")
            with self.assertRaises(ValueError): audit(self.model,parent=p)
    def test_source_hash(self): self.reject(lambda d:d.update(source_sha256="0"*64))
    def test_pdf_page(self): self.reject(lambda d:d["anchors"][2].update(pdf_page_zero_based=71))
    def test_site_conflation(self): self.reject(lambda d:d.update(distinction="same place"))
    def test_unverified_named_observation(self): self.reject(lambda d:d["scope"].update(named_528="yes"))
    def test_unverified_epoch(self): self.reject(lambda d:d["scope"].update(utc_528="1963-11-08T00:00:00Z"))
    def test_unverified_sigma(self): self.reject(lambda d:d["scope"].update(sigma_528=1))
    def test_unverified_receipt(self): self.reject(lambda d:d["scope"].update(data_receipt_528="yes"))
    def test_independence(self): self.reject(lambda d:d["scope"].update(independent_sensors_528=2))
    def test_physics(self): self.reject(lambda d:d["scope"].update(physical_constraint_active=True))
    def test_impact(self): self.reject(lambda d:d["scope"].update(fall_location_528="Conde"))
    def test_duplicate_anchor(self): self.reject(lambda d:d["anchors"].append(copy.deepcopy(d["anchors"][0])))
    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"bad";p.write_text('{"id":"C241-L56","id":"false"}')
            with self.assertRaises(ValueError): load(p)
    def test_truncated_pdf(self):
        with self.assertRaises(ValueError): verify_pdf(b"%PDF-1.4\n%%EOF")
if __name__=="__main__": unittest.main()
