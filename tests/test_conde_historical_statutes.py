"""CGEO-09: documentary links are not a historic municipality polygon."""
import copy
from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from tools.conde_historical_statutes import read_contract, evaluate


class HistoricalStatutesTest(unittest.TestCase):
    def setUp(self):
        self.data = read_contract()

    def load_mutant(self, data):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "contract.json"
            path.write_text(json.dumps(data))
            return read_contract(path)

    def test_primary_original_still_absent(self):
        self.assertEqual(len(self.data["sources"]), 3)
        self.assertTrue(all(s["original_publication_pdf_sha256"] is None for s in self.data["sources"]))
        self.assertFalse(any(s["original_facsimile_inspected"] for s in self.data["sources"]))

    def test_1944_route_is_topology_not_coordinates(self):
        topo = self.data["boundary_1944_topology"]
        self.assertEqual(topo["route_order_hydronyms"][0], "oceano Atlantico / foz do rio Itapicuru")
        self.assertEqual(topo["route_order_hydronyms"][-1], "marco a margem do riacho Caranguejo do rio Branco")
        self.assertIsNone(topo["geometry"])
        self.assertIsNone(topo["coordinate_datum"])

    def test_1953_period_excludes_november_1963_as_stated_period(self):
        s = self.data["sources"][1]
        self.assertLess(date.fromisoformat(s["stated_division_period_end"]), date(1963, 11, 8))
        result = evaluate("1963-11-08", self.data)
        self.assertEqual(result["temporal_status"], "AFTER_EXPLICIT_1953_DIVISION_PERIOD_CONTINUITY_UNVERIFIED")
        self.assertFalse(result["can_constrain_reentry"])

    def test_1953_art2_explicitly_preserves_1944_but_not_1963(self):
        bridge = self.data["legal_1944_1953_bridge"]
        self.assertEqual(bridge["provision"], "art. 2")
        self.assertTrue(bridge["explicit_preservation_in_1953"])
        self.assertTrue(bridge["modified_by_1953_and_annexes"])
        self.assertFalse(bridge["annexes_ii_vi_inspected"])
        self.assertFalse(bridge["conde_jandaira_segment_identity_proven"])
        self.assertFalse(bridge["continuing_unchanged_until_1963_proven"])
        self.assertIsNone(bridge["boundary_geometry_for_1963"])
        link = [edge for edge in self.data["dependency_graph"]["links"]
                if edge["type"] == "EXPLICIT_ART2_NORMATIVE_CARRYOVER_WITH_1953_MODIFICATIONS"]
        self.assertEqual(len(link), 1)
        self.assertEqual(link[0]["target"], "BA-DEC-12978-1944-ANNEX2-LXXIII")
        result = evaluate("1963-11-08", self.data)
        self.assertEqual(result["1944_statute_carryover_in_1953"],
                         "CONNECTED_PENDING_1953_ANNEX_ALTERATIONS_AND_LATER_ACTS")
        self.assertIsNone(result["legal_boundary_for_date"])

    def test_prevent_unverified_1963_continuity_promotion(self):
        for field, value in (
            ("continuing_unchanged_until_1963_proven", True),
            ("conde_jandaira_segment_identity_proven", True),
            ("annexes_ii_vi_inspected", True),
            ("boundary_geometry_for_1963", {"type": "Polygon", "coordinates": []}),
        ):
            with self.subTest(field=field):
                mutant = copy.deepcopy(self.data)
                mutant["legal_1944_1953_bridge"][field] = value
                with self.assertRaisesRegex(ValueError, "legal carryover promotion"):
                    self.load_mutant(mutant)

    def test_prevent_art2_dependency_edge_deletion(self):
        mutant = copy.deepcopy(self.data)
        mutant["dependency_graph"]["links"] = [
            edge for edge in mutant["dependency_graph"]["links"]
            if edge["type"] != "EXPLICIT_ART2_NORMATIVE_CARRYOVER_WITH_1953_MODIFICATIONS"
        ]
        with self.assertRaisesRegex(ValueError, "normative carryover graph edge missing"):
            self.load_mutant(mutant)

    def test_no_geometry_even_within_1953_explicit_period(self):
        for day in ("1944-06-01", "1954-01-01", "1958-12-31", "1963-11-08", "2017-04-28"):
            with self.subTest(day=day):
                e = evaluate(day, self.data)
                self.assertIsNone(e["legal_boundary_for_date"])
                self.assertIsNone(e["point_membership"])
                self.assertFalse(e["can_constrain_reentry"])

    def test_fail_closed_if_geometry_inserted(self):
        a = copy.deepcopy(self.data)
        a["boundary_1944_topology"]["geometry"] = {"type": "Polygon", "coordinates": []}
        with self.assertRaisesRegex(ValueError, "unverified geometry"):
            self.load_mutant(a)

    def test_fail_closed_if_1963_promoted(self):
        a = copy.deepcopy(self.data)
        a["dependency_graph"]["can_constrain_orbital_reentry_1963"] = True
        with self.assertRaisesRegex(ValueError, "missing historical bridge"):
            self.load_mutant(a)

    def test_source_lineage_includes_prior_2017_custody(self):
        graph = self.data["dependency_graph"]
        self.assertEqual(graph["prior_ids"], ["C24", "CGEO-05", "CGEO-06", "CGEO-08"])
        self.assertEqual(graph["links"][-1]["source_id"], "BA-ALEBA-LEI-13720-2017-DO-22166")
        self.assertEqual(len(graph["requires_for_event_date"]), 5)


if __name__ == "__main__":
    unittest.main()
