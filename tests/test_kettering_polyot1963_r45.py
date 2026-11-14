import json
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "research/tle_custody/kettering_polyot1963_C241_LONTRA_R45.json"

class PolyotCatalogueR45Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(FILE.read_text(encoding="utf-8"))

    def test_institutional_locator_and_year(self):
        s = self.d["institutional_source"]
        self.assertEqual(s["locator"], "KET/C/3/10")
        self.assertEqual(s["catalogued_creation_year"], 1963)
        self.assertEqual(s["catalogue_url"], "https://collection.sciencemuseumgroup.org.uk/documents/aa110121264")

    def test_log_graph_track_distinct_not_measurements(self):
        c = self.d["institutional_source"]["described_contents"]
        self.assertTrue({"log of signals", "graph", "track diagram"}.issubset(set(c)))
        self.assertEqual(self.d["retrieval"]["folio_count_read"], 0)

    def test_control_object_not_targets(self):
        c = self.d["control_object"]
        t = self.d["requested_observation"]
        self.assertEqual((c["international_designation"], c["norad_id"]), ("1963-043A", 683))
        self.assertTrue(c["target_mismatch"])
        self.assertNotIn(c["norad_id"], t["target_norad_ids"])
        self.assertEqual(t["target_norad_ids"], [527,528,529])
        self.assertEqual(t["target_designations"], ["1963-003A","1963-003B","1963-003C"])

    def test_creation_year_does_not_date_observations(self):
        c = self.d["control_object"]
        self.assertEqual(c["launch_date"], "1963-11-01")
        self.assertFalse(c["observation_dates_verified"])
        self.assertFalse(c["confirms_measurement_on_1963_11_07_09"])

    def test_no_invented_facsimile_hash_or_coordinates(self):
        r = self.d["retrieval"]
        self.assertTrue(r["catalogue_inspected_via_web_viewer"])
        self.assertFalse(r["facsimile_recovered"])
        self.assertIsNone(r["facsimile_sha256"])
        self.assertIsNone(r["catalogue_html_sha256"])
        self.assertFalse(r["graph_coordinates_verified"])
        self.assertFalse(r["timestamp_of_signal_verified"])

    def test_same_folder_does_not_count_as_independent_evidence(self):
        s = self.d["sibling_context"]
        self.assertEqual(s["earliest_item_year"], 1965)
        self.assertFalse(s["independence_between_items_confirmed"])
        self.assertNotEqual(s["diary_1963"], s["radio_by_year_1963"])

    def test_fail_closed_for_target_constraints(self):
        t = self.d["requested_observation"]
        self.assertFalse(t["target_identity_verified"])
        self.assertFalse(t["target_epoch_utc_verified"])
        self.assertFalse(t["clock_frame_calibration_verified"])
        self.assertFalse(t["genealogy_checked"])
        self.assertEqual(t["independent_measurements_retrieved"], 0)
        self.assertEqual(t["new_orbital_constraints_activated"], 0)

    def test_outreach_and_status(self):
        self.assertFalse(self.d["external_contact_sent"])
        self.assertTrue(self.d["status"].startswith("CATALOGUE_ONLY"))

if __name__ == "__main__":
    unittest.main()
