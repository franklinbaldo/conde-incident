import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "research" / "tle_custody" / "kettering_radio_1960_1973_C241_LONTRA_R44.json"

class RadioCatalogR44Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(P.read_text(encoding="utf-8"))

    def test_unique_locator(self):
        self.assertEqual(self.data["id"], "C241-LONTRA-R44")
        self.assertEqual(self.data["new_locator"]["id"], "KET/A/6")

    def test_claim_scope_not_observation(self):
        d = self.data["new_locator"]
        self.assertTrue(d["has_1963_material_in_catalogue_date_range"])
        self.assertFalse(d["has_verified_pages_for_1963"])
        self.assertFalse(d["has_november_1963_observation_line"])
        self.assertFalse(d["has_confirmed_527_528_529"])

    def test_no_originals_or_invented_hash(self):
        r = self.data["retrieval"]
        self.assertFalse(r["catalogue_binary_downloaded"])
        self.assertFalse(r["facsimile_retrieved"])
        self.assertIsNone(r["catalogue_html_sha256"])
        self.assertIsNone(r["facsimile_sha256"])
        self.assertEqual(r["facsimile_pages_read"], 0)

    def test_access_denial_not_archival_absence(self):
        r = self.data["retrieval"]
        self.assertEqual(r["direct_get_from_jatoba"]["http_status"], 403)
        self.assertTrue(r["catalogue_inspected_via_web_viewer"])
        self.assertNotIn("NOT_FOUND", self.data["status"])

    def test_distinct_control_date_ranges(self):
        ids = {x["id"] for x in self.data["scope_controls"]}
        self.assertEqual(ids, {"KET/A/5/2", "KET/A/3/1"})
        for control in self.data["scope_controls"]:
            self.assertIn("not proof", control["negative_scope"].lower())

    def test_no_target_constraints(self):
        targets = self.data["targets"]
        self.assertEqual(targets["norad_ids"], [527, 528, 529])
        self.assertFalse(targets["identification_verified"])
        self.assertFalse(targets["dated_observation_verified"])
        self.assertEqual(targets["independent_measurements_retrieved"], 0)
        self.assertEqual(targets["new_orbital_constraints_activated"], 0)

    def test_no_unapproved_outreach(self):
        self.assertFalse(self.data["outreach_sent"])

    def test_origin_is_institutional(self):
        self.assertEqual(self.data["new_locator"]["catalogue_url"], "https://collection.sciencemuseumgroup.org.uk/documents/aa110118055")

if __name__ == "__main__":
    unittest.main()
