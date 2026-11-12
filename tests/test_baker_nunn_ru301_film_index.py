"""RU301 Smithsonian film finding aid: audit data and epistemic scope.

These tests prove consistency of documentary *locators* only.
They do not certify an original film's target or a satellite trajectory.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "research" / "constraints" / "baker_nunn_ru301_1963_film_index.json"
EXPECTED = {
    "1963-11-01": [14881],
    "1963-11-02": [14882],
    "1963-11-03": [14883, 14884, 14885, 14886, 14887],
    "1963-11-04": [14892, 14894],
    "1963-11-05": [14896, 14897, 14898, 14899, 14900, 14902],
}
BOX2 = {14881, 14882, 14883, 14886, 14887, 14892, 14894, 14896, 14897, 14902}


class BakerNunnRU301Inventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads(INPUT.read_text(encoding="utf-8"))

    def test_source_is_archival_inventory_not_orbital_measurement(self):
        g = self.graph
        self.assertEqual(g["schema"], "conde.archival-instrument-crosswalk/v1")
        self.assertEqual(g["source"]["id"], "SIA-FARU0301")
        self.assertEqual(g["source"]["source_independence_family"], "SMITHSONIAN_SAO_INSTITUTIONAL_ARCHIVE")
        self.assertTrue(g["source"]["original_url"].endswith("SIA.FARU0301.pdf"))
        self.assertIsNone(g["source"]["source_sha256"])
        self.assertEqual(g["physical_domain"], "NOT_EVALUABLE_FROM_METADATA")

    def test_all_fifteen_film_ids_and_days_from_both_original_pages(self):
        films = self.graph["film_index_entries"]
        actual = {}
        for f in films:
            actual.setdefault(f["catalog_record_date"], []).append(f["observation_number"])
        self.assertEqual({d: sorted(ns) for d, ns in actual.items()}, EXPECTED)
        self.assertEqual(len(films), 15)
        self.assertEqual(len(set(f["id"] for f in films)), 15)
        self.assertTrue(all(f["station_code"] == "SC-8" for f in films))

    def test_crossbox_finding_aid_lineage(self):
        for f in self.graph["film_index_entries"]:
            location = "RU301:box2:printed6" if f["observation_number"] in BOX2 else "RU301:box17:printed34"
            self.assertEqual(f["source_occurrence"], location)
            self.assertEqual(f["independence_family"], "SMITHSONIAN_SAO_INSTITUTIONAL_ARCHIVE")

    def test_no_528_target_or_fabricated_sensor_data(self):
        for f in self.graph["film_index_entries"]:
            self.assertIsNone(f["object_catalog_id"])
            self.assertIsNone(f["observation_epoch_utc"])
            self.assertIsNone(f["angular_values"])
            self.assertIsNone(f["angular_uncertainty"])
            self.assertFalse(f["film_sheet_content_inspected"])
            self.assertFalse(f["hard_physical_constraint"])
            self.assertEqual(f["status"], "ORIGINAL_FILM_INDEX_METADATA_NOT_SENSOR_OBSERVATION")

    def test_no_8nov_is_a_selected_catalog_negative_only(self):
        self.assertNotIn("1963-11-08", {f["catalog_record_date"] for f in self.graph["film_index_entries"]})
        var = next(v for v in self.graph["variables"] if v["id"] == "RU301_1963_11_08_film_in_selected_archive")
        self.assertIs(var["value"], False)
        self.assertIn("institutional RU301 finding aid", var["scope"])

    def test_latent_unknowns_remain_connected_and_pending(self):
        g = self.graph
        names = {v["id"] for v in g["variables"]}
        source_ids = {s["id"] for s in g["document_occurrences"]}
        self.assertEqual(len(source_ids), 3)
        self.assertEqual(len(g["edges"]), 3)
        for edge in g["edges"]:
            self.assertTrue(set(edge["source_ids"]).issubset(source_ids))
            self.assertTrue(set(edge["input_variables"]).issubset(names))
            self.assertFalse(edge["hard_constraint"])
            self.assertTrue(edge["missing"])
        for v in g["variables"]:
            if v["kind"].startswith("latent_"):
                self.assertIsNone(v["value"])
        self.assertEqual(g["edges"][1]["status"], "CONNECTED_PENDING_AUTHENTIC_528_MEASUREMENT")

    def test_no_false_independence_or_corroboration(self):
        self.assertEqual(len({f["independence_family"] for f in self.graph["film_index_entries"]}), 1)
        self.assertIn("smithsonian", self.graph["provenance_dependencies"][0].lower())
        self.assertFalse(any(f["object_identity_status"].endswith("CONFIRMED") for f in self.graph["film_index_entries"]))


if __name__ == "__main__":
    unittest.main()
