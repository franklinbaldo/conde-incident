"""CGEO-54: reject false photo identity and geographic claims."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("cgeo54",ROOT/"tools/cgeo54_nara_adjacent_overlay_index.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Cgeo54Tests(unittest.TestCase):
    def setUp(self):
        self.d=json.loads(m.FILE.read_text(encoding="utf8"))

    def reject(self, f):
        d=copy.deepcopy(self.d)
        f(d)
        with self.assertRaises(ValueError):
            m.validate(d)

    def test_contract(self):
        self.assertEqual(m.validate(self.d),63)
    def test_wrong_naid(self):
        self.reject(lambda d:d["records"][0].update(naid="46716637"))
    def test_swapped_square(self):
        self.reject(lambda d:d["records"][0].update(square="11S037W"))
    def test_duplicated_scan(self):
        self.reject(lambda d:d["records"][1]["scans"].append("m1765-317-00007.jpg"))
    def test_extra_scan(self):
        self.reject(lambda d:d["records"][4]["scans"].append("m1765-317-00299.jpg"))
    def test_missing_scan(self):
        self.reject(lambda d:d["records"][4]["scans"].pop())
    def test_zero_hit_as_absence(self):
        self.reject(lambda d:d["interpretation"].update(zero_hit_squares_are_proven_absent=True))
    def test_fake_photo(self):
        self.reject(lambda d:d["interpretation"].update(original_aerial_photographs_acquired=63))
    def test_fake_independence(self):
        self.reject(lambda d:d["interpretation"].update(independent_photographic_observations=7))
    def test_invented_center(self):
        self.reject(lambda d:d["limitations"].update(historical_city_center_geometry_1963=[-11,-37]))
    def test_invented_spot(self):
        self.reject(lambda d:d["limitations"].update(spot_number_for_125374="125374"))
    def test_invented_orbit(self):
        self.reject(lambda d:d["limitations"].update(orbital_constraint_activated=True))
    def test_non_json_html(self):
        with self.assertRaises(ValueError):
            m.parse_response(200,"text/html",b"<html></html>")
    def test_malformed_json(self):
        with self.assertRaises(ValueError):
            m.parse_response(200,"application/json",b"<html></html>")
    def test_count_contradiction(self):
        b=b'{"body":{"hits":{"hits":[{},{}],"total":{"value":1}}}}'
        with self.assertRaises(ValueError):
            m.parse_response(200,"application/json",b)
    def test_valid_api_sample(self):
        b=b'{"body":{"hits":{"hits":[],"total":{"value":0}}}}'
        self.assertEqual(m.parse_response(200,"application/json",b)["body"]["hits"]["total"]["value"],0)
    def test_no_scan_anchor(self):
        b={"body":{"hits":{"hits":[{"_id":"46716877","_source":{"record":{"title":"Overlay indexes for degree square 12S037W","levelOfDescription":"fileUnit","scopeAndContentNote":"Latitude: 12S\\nLongitude: 037W","digitalObjects":[]}}}],"total":{"value":1}}}}
        with self.assertRaises(ValueError):
            m.check_live_record(b,"12S037W","46716877",429,432)

if __name__=="__main__":
    unittest.main()
