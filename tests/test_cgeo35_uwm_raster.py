"""CGEO-35 adversarial pixel-origin and anti-geocoding tests."""
import copy
import unittest
from pathlib import Path
from tools.cgeo34_uwm_jp2 import read, ROOT, MANIFEST as PARENT
from tools.cgeo35_uwm_raster import MANIFEST, verify_contract, verify_raster

class RasterInspectionTest(unittest.TestCase):
    def setUp(self):
        self.d=read(MANIFEST)
        self.parent=read(PARENT)

    def check_mutation(self,mutation):
        bad=copy.deepcopy(self.d)
        mutation(bad)
        with self.assertRaises(ValueError):
            verify_contract(bad,self.parent)

    def test_real_contract(self):
        self.assertEqual(verify_contract(self.d,self.parent),'CGEO35_CONTRACT_PASS')

    def test_not_an_independent_witness(self):
        self.check_mutation(lambda d:d.update(source_same_sheet_as_parent=False))
        self.check_mutation(lambda d:d['historical_context'].update(new_independent_historical_witness=True))

    def test_original_sha_substitution_rejected(self):
        self.check_mutation(lambda d:d.update(source_jp2_sha256='0'*64))

    def test_other_crop_cannot_pretend_verified(self):
        self.check_mutation(lambda d:d['inspection'].update(original_pixel_roi_xyxy=[0,0,100,100]))
        self.check_mutation(lambda d:d['inspection'].update(rgb_pixel_sha256='0'*64))

    def test_ground_coordinates_cannot_be_promoted(self):
        self.check_mutation(lambda d:d['scientific_limits'].update(center_world_coordinates=[-37,-11]))
        self.check_mutation(lambda d:d['scientific_limits'].update(map_pixel_to_world_transform=[1,0,0,0,1,0]))

    def test_falsely_identified_historical_center_rejected(self):
        self.check_mutation(lambda d:d['scientific_limits'].update(historical_city_center_polygon_1963={'type':'Polygon'}))
        self.check_mutation(lambda d:d['scientific_limits'].update(observed_reentry_location=[1,2]))

    def test_orbital_activation_rejected(self):
        self.check_mutation(lambda d:d['scientific_limits'].update(can_constrain_orbital_reentry=True))
        self.check_mutation(lambda d:d['scientific_limits'].update(supports_independent_historical_observation=True))

    def test_toponym_and_pixel_anchor_substitution_rejected(self):
        self.check_mutation(lambda d:d.update(literal_visible_toponyms=['CONDE']))
        self.check_mutation(lambda d:d['image_space_only'].update(conde_symbol_original_px_visual_estimate=[0,0]))

    def test_anachronistic_roads_as_1963_rejected(self):
        self.check_mutation(lambda d:d['historical_context'].update(roads_update_year=1963))

    def test_missing_or_fake_original_cannot_be_replayed(self):
        with self.assertRaises((FileNotFoundError,ValueError)):
            verify_raster(Path('/nonexistent.jp2'),self.d,self.parent)

if __name__=='__main__': unittest.main()
