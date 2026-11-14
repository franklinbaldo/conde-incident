"""CGEO-53 fail-closed regressions: response format, source identity and epistemology."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cgeo53", ROOT / "tools/cgeo53_nara_v3_catalog.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture(q="11S037W", rec_id="46716637", title="Overlay indexes for degree square 11S037W"):
    return json.dumps({"body":{"hits":{"total":{"value":1},"hits":[
        {"_id":rec_id,"_source":{"record":{"title":title,"levelOfDescription":"fileUnit"}}}
    ]}}}).encode()

class Cgeo53Tests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(m.DATA.read_text(encoding="utf8"))
    def reject(self,mutate):
        d=copy.deepcopy(self.data)
        mutate(d)
        with self.assertRaises(ValueError):
            m.validate(d)
    def test_contract(self):
        self.assertEqual(m.validate(self.data),4)
    def test_fake_spot(self):
        self.reject(lambda d:d["archival_lineage"].update(spot_number="125374"))
    def test_fake_film(self):
        self.reject(lambda d:d["interpretation"].update(individual_frame_found=True))
    def test_fake_geometry(self):
        self.reject(lambda d:d["limitations"].update(center_geometry_1963=[-11,-37]))
    def test_false_negative_count(self):
        self.reject(lambda d:d["interpretation"].update(numeric_query_hits_are_relevant_negatives=True))
    def test_fake_coverage(self):
        self.reject(lambda d:d["interpretation"].update(search_result_counts_are_complete_photo_inventory=True))
    def test_false_nara_api(self):
        self.reject(lambda d:d.update(endpoint="https://catalog.archives.gov/api/v2/records/search"))
    def test_false_id(self):
        self.reject(lambda d:d["queries"][0].update(matched_naid="125374"))
    def test_false_hash(self):
        self.reject(lambda d:d["queries"][0].update(sha256="0"*64))
    def test_html_shell_200(self):
        with self.assertRaisesRegex(ValueError,"HTML"):
            m.parse_response(200,"text/html",b"<html>SPA</html>")
    def test_json_content_type_but_html_body(self):
        with self.assertRaisesRegex(ValueError,"Non-JSON"):
            m.parse_response(200,"application/json",b"<html>SPA</html>")
    def test_http_403(self):
        with self.assertRaisesRegex(ValueError,"HTTP"):
            m.parse_response(403,"application/json",fixture())
    def test_malformed_hits(self):
        with self.assertRaises(ValueError):
            m.parse_response(200,"application/json",b'{"body":{"hits":{"total":{"value":1}}}}')
    def test_total_smaller_than_hits(self):
        d=json.loads(fixture());d["body"]["hits"]["total"]["value"]=0
        with self.assertRaisesRegex(ValueError,"Impossible"):
            m.parse_response(200,"application/json",json.dumps(d).encode())
    def test_valid_json_and_correct_record(self):
        d=m.parse_response(200,"application/json; charset=utf-8",fixture())
        self.assertEqual(m.verify_cell_hits(d,"11S037W","46716637")["_id"],"46716637")
    def test_unrelated_valid_json(self):
        d=m.parse_response(200,"application/json",fixture(rec_id="999"))
        with self.assertRaisesRegex(ValueError,"not found"):
            m.verify_cell_hits(d,"11S037W","46716637")
    def test_broken_level(self):
        d=m.parse_response(200,"application/json",fixture())
        d["body"]["hits"]["hits"][0]["_source"]["record"]["levelOfDescription"]="item"
        with self.assertRaises(ValueError):
            m.verify_cell_hits(d,"11S037W","46716637")
    def test_wrong_square_title(self):
        d=m.parse_response(200,"application/json",fixture(title="Overlay for other square"))
        with self.assertRaises(ValueError):
            m.verify_cell_hits(d,"11S037W","46716637")

if __name__ == "__main__":
    unittest.main()
