"""CGEO-16: municipality PPA visual context may not silently become event geometry."""
import json
import unittest
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "research/geo/cgeo16_ppa2021_visual_context.json"


class CGEO16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_identity_excludes_portuguese_and_brazilian_homonyms(self):
        scope = self.record["scope"]
        self.assertEqual(scope["ibge_code"], "2908606")
        self.assertEqual(scope["state"], "BA")
        self.assertIn("Vila do Conde/Portugal", scope["exclude_homonyms"])

    def test_source_is_a_specific_official_page_not_an_assumed_1963_photo(self):
        s = self.record["source"]
        self.assertEqual(s["publication_date"], "2021-12-21")
        self.assertEqual(s["official_diario_page_number"], 14)
        self.assertEqual(s["pdf_page_index_zero_based"], 13)
        self.assertEqual(s["ppa_internal_page_number"], 13)
        self.assertTrue(s["document_render_inspected"])
        self.assertFalse(s["capture_of_photograph_authenticated"])

    def test_render_is_not_claimed_as_byte_hash_verification(self):
        s = self.record["source"]
        self.assertFalse(s["document_bytes_acquired"])
        self.assertIsNone(s["document_sha256"])

    def test_two_photo_contexts_have_different_classes(self):
        obs = self.record["observations"]
        self.assertEqual({r["content_class"] for r in obs},
                         {"commercial_street_photo", "beach_waterfront_photo"})
        self.assertEqual(len({r["id"] for r in obs}), len(obs))

    def test_neither_photo_has_a_verified_capture_date_or_position(self):
        for item in self.record["observations"]:
            with self.subTest(image=item["id"]):
                for field in ("capture_date", "photographer", "camera_coordinates",
                              "photographed_street_name", "neighborhood",
                              "belongs_to_historic_vila", "equals_center_of_city_1963",
                              "image_file_sha256", "reuse_license"):
                    self.assertIsNone(item[field], field)

    def test_no_gps_reference_is_backdated(self):
        out = self.record["castor_export"]
        for field in ("location_of_1963_report", "historical_center_polygon",
                      "impact_point", "datum", "crs", "horizontal_uncertainty_m"):
            self.assertIsNone(out[field], field)
        self.assertFalse(out["can_constrain_orbital_reentry"])

    def test_uncertainty_is_connected_not_zero(self):
        out = self.record["castor_export"]
        self.assertEqual(out["graph_state"], "CONNECTED_PENDING_SPATIAL_IDENTIFICATION")
        self.assertGreaterEqual(len(out["pending_dependencies"]), 3)

    def test_two_pictures_in_one_pdf_are_not_independent_sources(self):
        lineage = self.record["lineage"]
        self.assertTrue(lineage["publication_groups_images"])
        self.assertEqual(lineage["independent_1963_observations"], 0)

    def test_reference_is_a_pdf_and_not_republished_media(self):
        self.assertTrue(self.record["source"]["url"].startswith("https://www.camaraconde.ba.gov.br/"))
        self.assertIn(".pdf", self.record["source"]["url"])
        self.assertTrue(all(x["reuse_license"] is None for x in self.record["observations"]))


if __name__ == "__main__":
    unittest.main()
