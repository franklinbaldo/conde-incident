"""Fail-closed checks: a screen-space lead must not become a 1963 impact fix."""
import copy
import importlib.util
import unittest
from pathlib import Path
M=Path(__file__).resolve().parents[1]/'tools/cgeo48_nara_overlay.py'
spec=importlib.util.spec_from_file_location('cgeo48',M)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ScreenLeadTests(unittest.TestCase):
    def setUp(self):
        self.data=m.read()
        self.parent=m.read(m.PARENT)
    def bad(self,fn):
        d=copy.deepcopy(self.data);fn(d)
        with self.assertRaises(ValueError):m.validate(d,self.parent)
    def test_authentic_contract(self):
        self.assertLess(m.validate(self.data,self.parent),25)
    def test_hash_must_agree_parent(self):
        self.bad(lambda d:d['reference_scans'][1].update(sha256='0'*64))
    def test_wrong_sheet(self):
        self.bad(lambda d:d.update(nara_degree_square='11S038W'))
    def test_break_registration(self):
        self.bad(lambda d:d['paper_registration_controls_px'].update(overlay_lower_right=[800,1050]))
    def test_move_town_far_from_flightline(self):
        self.bad(lambda d:d['map_label'].update(approximate_symbol_center_px=[200,937]))
    def test_move_flightline_far_from_town(self):
        self.bad(lambda d:d['overlay_00248'].update(candidate_strip_proxy_line_preview_px=[[100,100],[110,110]]))
    def test_no_spot_number_promotion(self):
        self.bad(lambda d:d['overlay_00248']['visible_annotations'].update(unresolved_header_number_is_spot_number=True))
    def test_no_1963_date(self):
        self.bad(lambda d:d['overlay_00248'].update(verified_exposure_date='1963-11-08'))
    def test_no_negative_claim(self):
        self.bad(lambda d:d['overlay_00248'].update(verified_original_negative=True))
    def test_no_georeference(self):
        self.bad(lambda d:d['limitations'].update(georeferenced_footprint_validated=True))
    def test_no_center_polygon(self):
        self.bad(lambda d:d['limitations'].update(historical_center_polygon_1963=[[-37,-11]]))
    def test_no_orbital_contraction(self):
        self.bad(lambda d:d['limitations'].update(orbital_constraints_activated=True))
    def test_no_sgb_flight_identity(self):
        self.bad(lambda d:d['limitations'].update(same_flight_as_sgb_1964_1970=True))
if __name__=='__main__':unittest.main()
