"""CGEO-55 controls: provenance and negative claims must reject, even under -O."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cgeo55",ROOT/"tools/cgeo55_nara_visual_overlays.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TestCGEO55(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(m.SOURCE.read_text(encoding="utf8"))

    def reject(self, mutation):
        d = copy.deepcopy(self.doc)
        mutation(d)
        with self.assertRaises(ValueError):
            m.validate(d)

    def test_verified_six_images(self):
        self.assertEqual(m.validate(self.doc),6)
    def test_missing_sheet(self):
        self.reject(lambda d: d["scans"].pop())
    def test_reordered_sheet(self):
        self.reject(lambda d: d["scans"].reverse())
    def test_fake_sha(self):
        self.reject(lambda d: d["scans"][2].update(sha256="0"*64))
    def test_swapped_square(self):
        self.reject(lambda d: d["scans"][2].update(square="11S037W"))
    def test_wrong_op_number(self):
        self.reject(lambda d: d["scans"][3].update(op_file_no="125374"))
    def test_op_is_not_spot(self):
        self.reject(lambda d: d["cross_square_matches"][0].update(meaning="same exposure"))
    def test_op_pair_reversal(self):
        self.reject(lambda d: d["cross_square_matches"][1].update(sheets=["00248","00431"]))
    def test_cover_not_aerial_photo(self):
        self.reject(lambda d: d["scans"][0].update(role="original_individual_aerial_frame"))
    def test_photo_count_never_six(self):
        self.reject(lambda d: d["interpretation"].update(original_individual_aerial_frames_acquired=6))
    def test_geo_alignment_not_proven(self):
        self.reject(lambda d: d["interpretation"].update(spatial_overlap_of_exposures_proven=True))
    def test_no_spot_number(self):
        self.reject(lambda d: d["limits"].update(spot_number="125374"))
    def test_no_georeferenced_footprint(self):
        self.reject(lambda d: d["limits"].update(flight_footprint_georeferenced=[[-11.8,-37.6]]))
    def test_no_capture_date_inferred(self):
        self.reject(lambda d: d["limits"].update(date_of_individual_exposure="1942-09-27"))
    def test_no_center_geometry(self):
        self.reject(lambda d: d["limits"].update(historical_city_center_geometry_1963=[-11.8,-37.6]))
    def test_no_invented_reentry(self):
        self.reject(lambda d: d["limits"].update(orbital_constraint_activated=True))
    def test_wrong_catalog_naid(self):
        self.reject(lambda d: d["catalog"].update(naid="46716637"))
    def test_reference_chart_label(self):
        self.reject(lambda d: d["scans"][1].update(visible_annotation="Unknown chart"))

if __name__ == "__main__":
    unittest.main()
