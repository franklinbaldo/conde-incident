"""Audit links for a *catalog* crosswalk. Does not certify a 528 observation."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/constraints/moonwatch_ru255_1963_archival_graph.json"


class MoonwatchRU255ArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads(DATA.read_text(encoding="utf-8"))

    def test_five_distinct_archival_occurrences(self):
        obs = self.graph["observations"]
        self.assertEqual(len(obs), 5)
        self.assertEqual(len({o["id"] for o in obs}), 5)
        self.assertEqual(
            {o["id"].rsplit("-", 1)[-1] for o in obs},
            {"01", "02", "03", "04", "05"},
        )

    def test_archival_description_is_not_a_1963_observation(self):
        source = self.graph["source"]
        self.assertEqual(source["grade"], "PRIMARY_FOR_COLLECTION_DESCRIPTION_ONLY")
        for o in self.graph["observations"]:
            self.assertEqual(o["source_id"], source["id"])
            self.assertEqual(o["independence_family"], source["independence_family"])
            self.assertIsNone(o["observed_1963_11_08"])
            self.assertEqual(o["status"], "DOCUMENTED_ARCHIVAL_LOCATOR_NOT_OBJECT_OBSERVATION")
            self.assertFalse(o["physical_hard_constraint"])

    def test_all_graph_edges_refer_to_recorded_variables_and_sources(self):
        variables = {v["id"] for v in self.graph["variables"]}
        obs_ids = {o["id"] for o in self.graph["observations"]}
        self.assertEqual(len(variables), len(self.graph["variables"]))
        self.assertEqual(len(self.graph["edges"]), 4)
        for edge in self.graph["edges"]:
            self.assertTrue(edge["evidence_ids"])
            self.assertTrue(edge["input_variables"])
            self.assertTrue(set(edge["evidence_ids"]).issubset(obs_ids))
            self.assertTrue(set(edge["input_variables"]).issubset(variables))
            self.assertFalse(edge["hard_constraint"])
            self.assertTrue(edge["missing"])
            self.assertTrue(edge["status"].startswith("CONNECTED_PENDING_"))

    def test_orbital_sighting_variables_remain_unknown(self):
        for v in self.graph["variables"]:
            if v["id"] != "moonwatch_brazil_1963_station_file_exists":
                self.assertIsNone(v["value"])

    def test_no_fictitious_checksum_or_domain_narrowing(self):
        self.assertIsNone(self.graph["source"]["sha256"])
        self.assertEqual(self.graph["reduction_of_physical_domain"], "NOT_EVALUABLE_WITH_CATALOG_METADATA")
        self.assertTrue(self.graph["negative_results"])

    def test_pinned_catalog_page_and_source(self):
        self.assertIn("SIA.FARU0255.pdf", self.graph["source"]["url"])
        locs = " ".join(o["location"] for o in self.graph["observations"])
        for label in ["box 10", "box 15", "box 21", "box 22"]:
            self.assertIn(label, locs)


if __name__ == "__main__":
    unittest.main()
