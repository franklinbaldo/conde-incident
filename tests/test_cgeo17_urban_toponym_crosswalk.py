"""CGEO-17: historic street names and present addresses must not become 1963 coordinates."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/cgeo17_1958_urban_toponym_crosswalk.json"
CUSTODY = ROOT / "research/geo/ibge_1958_conde_photo_custody.json"


class CGEO17CrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.custody = json.loads(CUSTODY.read_text(encoding="utf-8"))

    def test_real_custody_reference_and_sha(self):
        self.assertEqual(self.data["source"]["custody_id"], self.custody["id"])
        self.assertEqual(self.data["source"]["ibge_pdf_sha256"],
                         self.custody["source"]["pdf_sha256"])
        self.assertEqual(self.data["source"]["publication_year"], 1958)
        self.assertFalse(self.data["source"]["source_photo_capture_dates_authenticated"])

    def test_each_anchor_is_an_unchanged_captioned_photo(self):
        photos = {p["id"]: p for p in self.custody["photos"]}
        anchors = self.data["historic_anchors"]
        self.assertEqual(len(anchors), 4)
        self.assertEqual(len({a["photo_id"] for a in anchors}), len(anchors))
        for a in anchors:
            with self.subTest(a=a["id"]):
                p = photos[a["photo_id"]]
                self.assertEqual(a["printed_page"], p["printed_page"])
                self.assertEqual(a["verbatim_normalized"],
                                 p["caption_visually_inspected"])
                self.assertIsNone(a["location"])
                self.assertIsNone(a["camera_point"])
                self.assertIsNone(a["photo_capture_date"])

    def test_distinct_places_cannot_be_joined_by_string_similarity(self):
        risks = self.data["toponym_risks"]
        self.assertGreaterEqual(len(risks), 4)
        for r in risks:
            self.assertFalse(r["identity_confirmed"])
            self.assertTrue(r["rule"])
        names = {r["name_a"] + " / " + r["name_b"] for r in risks}
        self.assertTrue(any("Severiano Lima" in n and "Severino Vieira" in n for n in names))
        self.assertTrue(any("Senhor do Bonfim" in n and "Nossa Senhora do Monte" in n for n in names))

    def test_modern_records_have_sources_but_no_backdated_geometry(self):
        ids = {a["id"] for a in self.data["historic_anchors"]}
        self.assertGreaterEqual(len(self.data["modern_occurrences"]), 4)
        for record in self.data["modern_occurrences"]:
            with self.subTest(record=record["id"]):
                self.assertIn(record["reference_to_historic"], ids)
                self.assertTrue(record["source_url"].startswith("https://"))
                self.assertIsNone(record["geometric_position"])
                candidate_fields = [k for k in record if k.startswith("same_")]
                self.assertEqual(len(candidate_fields), 1)
                self.assertIsNone(record[candidate_fields[0]])

    def test_1963_spatial_contract_is_entirely_null(self):
        c = self.data["castor_export"]
        for field in ("historical_center_point", "historical_center_polygon",
                      "photo_camera_positions_1958", "legal_boundary_1963",
                      "impact_point_1963", "horizontal_accuracy_m", "crs"):
            self.assertIsNone(c[field])
        self.assertFalse(c["can_constrain_orbital_reentry"])
        self.assertEqual(c["epistemic_status"],
                         "NAMED_1958_URBAN_FEATURES_NOT_GEOREFERENCED")
        self.assertGreaterEqual(len(c["pending"]), 3)

    def test_not_double_counting_source_or_municipality(self):
        m = self.data["municipality"]
        self.assertEqual((m["ibge_code"], m["uf"]), ("2908606", "BA"))
        self.assertIn("Conde/PB", m["excluded_homonyms"])
        self.assertIn("Condeúba/BA", m["excluded_homonyms"])
        self.assertEqual(self.data["source"]["source_family"],
                         "IBGE 1958 volume XX, única linhagem editorial")
        self.assertIn("LON-IBGE1958-CONDE-01",
                      {x["to"] for x in self.data["dependency_graph"]})


if __name__ == "__main__":
    unittest.main()
