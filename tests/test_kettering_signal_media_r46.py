import json
import unittest
from pathlib import Path

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "research/tle_custody/kettering_signal_media_C241_LONTRA_R46.json"
)


class KetteringSignalMediaR46Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.sources = {s["shelfmark"]: s for s in cls.data["sources"]}

    def test_exact_archival_identity_and_scope(self):
        self.assertEqual(self.data["id"], "C241-LONTRA-R46")
        self.assertEqual(set(self.sources), {"KET/E/19", "KET/C/3/06"})
        self.assertEqual(self.data["archive_identifier"], "KET")
        self.assertEqual(len(self.data["sources"]), 2)

    def test_institutional_locator_type_is_explicit(self):
        tape = self.sources["KET/E/19"]
        folder = self.sources["KET/C/3/06"]
        self.assertEqual(tape["locator_granularity"], "parent_inventory")
        self.assertEqual(folder["locator_granularity"], "item_inventory")
        for record in (tape, folder):
            self.assertTrue(record["catalogue_url"].startswith("https://collection.sciencemuseumgroup.org.uk/"))

    def test_paper_tapes_do_not_date_each_record(self):
        tape = self.sources["KET/E/19"]
        self.assertIn("Cosmos 13", tape["mentioned_objects"])
        self.assertIn("Voskhod 2", tape["mentioned_objects"])
        self.assertFalse(tape["date_of_each_record_established"])
        self.assertFalse(tape["paper_tape_physical_original_inspected"])

    def test_1963_bulletin_does_not_prove_folios(self):
        record = self.sources["KET/C/3/06"]
        self.assertEqual(record["catalogued_year"], 1963)
        self.assertEqual(record["target_in_catalogue"], "Cosmos 13 1963-06A")
        bulletin = record["related_external_document"]
        self.assertEqual(bulletin["date_in_catalogue"], "1963-08")
        self.assertFalse(bulletin["bulletin_original_retrieved"])
        self.assertIsNone(bulletin["bulletin_sha256"])

    def test_no_fake_binary_hash_or_signal_values(self):
        for record in self.data["sources"]:
            self.assertFalse(record["facsimile_retrieved"])
            self.assertIsNone(record["facsimile_sha256"])
            self.assertIsNone(record["facsimile_bytes"])
        self.assertFalse(self.sources["KET/E/19"]["signal_values_transcribed"])
        self.assertIsNone(self.data["source_handling"]["catalogue_html_sha256"])

    def test_cross_medium_not_two_sensors(self):
        graph = self.data["genealogy"]
        self.assertTrue(graph["paper_tape_and_folder_may_refer_to_same_cosmos_13_signals"])
        self.assertFalse(graph["independent_instrumental_origins_demonstrated"])
        self.assertTrue(graph["multiple_formats_must_not_be_counted_as_independent_measurements"])
        self.assertTrue(graph["dsir_bulletin_is_external_document_not_proof_of_independent_sensor"])

    def test_no_transfer_of_control_object_to_targets(self):
        t = self.data["requested_target"]
        self.assertEqual(t["norad"], [527, 528, 529])
        self.assertEqual(t["designations"], ["1963-003A", "1963-003B", "1963-003C"])
        self.assertEqual(t["date_window_utc"], ["1963-11-07", "1963-11-09"])
        self.assertFalse(t["explicitly_named_in_either_catalogue"])
        self.assertEqual(t["identified_measurements_retrieved"], 0)

    def test_fail_closed_when_clock_and_frame_missing(self):
        t = self.data["requested_target"]
        for name in ("observation_utc_verified", "observer_station_verified",
                     "frame_and_clock_verified", "instrumental_errors_verified"):
            self.assertFalse(t[name])
        self.assertEqual(t["new_orbital_constraints_activated"], 0)

    def test_negative_scope_and_outreach(self):
        self.assertTrue(self.data["status"].startswith("CATALOGUE_ONLY"))
        state = self.data["source_handling"]
        self.assertTrue(state["not_a_negative_search_of_unseen_folios"])
        self.assertFalse(state["external_contact_sent"])


if __name__ == "__main__":
    unittest.main()
