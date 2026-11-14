"""CGEO-56: ensure overclaims fail with and without Python assertions."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("cgeo56",ROOT/"tools/cgeo56_nara_sortie_family.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class TestCGEO56(unittest.TestCase):
    def setUp(self): self.d=json.loads(m.SOURCE.read_text(encoding="utf8"))
    def reject(self,fn):
        d=copy.deepcopy(self.d); fn(d)
        with self.assertRaises(ValueError): m.validate(d)
    def test_positive(self): self.assertEqual(m.validate(self.d),4)
    def test_source_lineage(self): self.reject(lambda d:d.update(parent="CGEO-50"))
    def test_source_family(self): self.reject(lambda d:d.update(source="random mirror"))
    def test_drop_image(self): self.reject(lambda d:d["scans"].pop())
    def test_swap_scans(self): self.reject(lambda d:d["scans"].reverse())
    def test_fake_digest(self): self.reject(lambda d:d["scans"][0].update(sha256="f"*64))
    def test_fake_size(self): self.reject(lambda d:d["scans"][1].update(bytes=5))
    def test_fake_op(self): self.reject(lambda d:d["scans"][1].update(op_file_no="125370"))
    def test_fake_sortie(self): self.reject(lambda d:d["scans"][2].update(orgn_sortie_reading="ROLL 601 2-3017"))
    def test_fake_date(self): self.reject(lambda d:d["scans"][0].update(header_date_reading="NOV 1963"))
    def test_certain_handwriting(self): self.reject(lambda d:d["scans"][1].update(header_reading_status="certified"))
    def test_roll_footprint(self): self.reject(lambda d:d["scans"][1].update(additional_visible_note="ROLL 1"))
    def test_same_photo_claim(self): self.reject(lambda d:d["pairs"][0].update(interpretation="same frame"))
    def test_cross_square_missing(self): self.reject(lambda d:d["pairs"][0].update(sheets=["00248","00248"]))
    def test_false_frame_join(self): self.reject(lambda d:d["cross_sheet_frame_label_example"].update(meaning="identical photograph"))
    def test_fake_photo_count(self): self.reject(lambda d:d["counts"].update(original_individual_aerial_photographs_acquired=4))
    def test_fake_ground_control(self): self.reject(lambda d:d["counts"].update(demonstrated_1963_ground_control_points=1))
    def test_inferred_spot(self): self.reject(lambda d:d["limits"].update(verified_spot_number="125374"))
    def test_inferred_can(self): self.reject(lambda d:d["limits"].update(negative_can="ON000000"))
    def test_assumed_utc(self): self.reject(lambda d:d["limits"].update(individual_exposure_utc="1942-09-07T12:00:00Z"))
    def test_inferred_city(self): self.reject(lambda d:d["limits"].update(conde_1963_city_center=[-11,-37]))
    def test_invented_orbit(self): self.reject(lambda d:d["limits"].update(orbital_constraint_activated=True))
if __name__=="__main__": unittest.main()
