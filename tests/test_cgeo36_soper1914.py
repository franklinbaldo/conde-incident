"""Adversarial tests for CGEO-36 chronology, visual evidence and binary custody."""
import copy
import unittest
from pathlib import Path
from tools.cgeo36_soper1914 import read, verify_contract, verify_asset

class CGEO36Test(unittest.TestCase):
    def setUp(self): self.d=read()
    def mutate(self,change):
        d=copy.deepcopy(self.d)
        change(d)
        with self.assertRaises(ValueError): verify_contract(d)
    def test_real_manifest(self):
        self.assertEqual(verify_contract(self.d),"CGEO36_CONTRACT_PASS")
    def test_year_and_scale(self):
        self.mutate(lambda d:d["source"].update(publication="1963-11"))
        self.mutate(lambda d:d["source"].update(printed_scale_denominator=25000))
    def test_hash_and_count(self):
        self.mutate(lambda d:d["source"].update(pdf_sha256="0"*64))
        self.mutate(lambda d:d["inspected_derivative"].update(bytes=5))
    def test_toponyms_are_distinct(self):
        self.mutate(lambda d:d["inspected_derivative"].update(visible_labels=["Conde"]))
        self.mutate(lambda d:d["inspected_derivative"].update(position_is_image_space_only=False))
    def test_no_equating_sitio_with_modern_village(self):
        self.mutate(lambda d:d["historical_inference"].update(modern_sitio_do_conde_identity_demonstrated=True))
    def test_no_historical_centre_or_impact(self):
        self.mutate(lambda d:d["historical_inference"].update(city_centre_1963_identified=True))
        self.mutate(lambda d:d["historical_inference"].update(reported_fall_location_1963_identified=True))
        self.mutate(lambda d:d["limits"].update(reported_impact_coordinates=[-37,-11]))
    def test_no_unproved_cartographic_independence(self):
        self.mutate(lambda d:d["historical_inference"].update(independent_of_1954_cartographic_survey=True))
        self.mutate(lambda d:d["bibliographic_crosscheck"].update(independently_verified_pixel_identity=True))
    def test_no_orbit_promotion(self):
        self.mutate(lambda d:d["limits"].update(can_constrain_orbital_reentry=True))
    def test_pixel_region_is_fixed(self):
        self.mutate(lambda d:d["inspected_derivative"].update(image_region_xyxy_px=[0,0,10,10]))
    def test_missing_binary_replay_rejected(self):
        with self.assertRaises(FileNotFoundError):
            verify_asset(Path("/nonexistent/1914-map.pdf"),1383563,"0"*64,"pdf")

if __name__=="__main__": unittest.main()
