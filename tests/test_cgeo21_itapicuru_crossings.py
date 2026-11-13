"""Checks to prevent geocoding Conde 1963 via modern bridges."""
import copy
import json
import unittest
from tools.cgeo21_itapicuru_crossings import CONTRACT, validate


class CrossingChronologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_original(self):
        validate(self.data)

    def test_separate_assets(self):
        self.assertEqual(len(self.data["candidate_assets"]), 2)
        self.assertEqual(self.data["candidate_assets"][0]["type"], "passarela")

    def test_cumulative_edges(self):
        self.assertEqual({x["from"] for x in self.data["links"]},
                         {"CGEO-17", "CGEO-18", "CGEO-19", "CGEO-20"})

    def test_source_tampering(self):
        for index, field, value in [(1, "source_date", "1963-11-08"),
                                    (2, "identifier", "123"),
                                    (3, "announced_event_date", "1963-11-08"),
                                    (4, "sha256", "0" * 64)]:
            with self.subTest(index=index, field=field):
                d = copy.deepcopy(self.data)
                d["sources"][index][field] = value
                with self.assertRaises(ValueError):
                    validate(d)

    def test_unsupported_bridge_history(self):
        changes = [("candidate_assets", 0, "exists_in_1963", True),
                   ("candidate_assets", 1, "construction_date", "1963-01-01"),
                   ("candidate_assets", 1, "inauguration_verified", "2024-12-30"),
                   ("observations", 1, "supports_bridge_absence_before_2015", True),
                   ("observations", 2, "proves_actual_completion", True),
                   ("observations", 3, "proves_event_occurred_on_2024_12_30", True),
                   ("interpretation", None, "same_passarela_and_concrete_bridge", True),
                   ("interpretation", None, "proven_absence_of_bridge_in_1963", True),
                   ("interpretation", None, "historical_1963_side_of_river_from_tupi", "left")]
        for section, index, key, val in changes:
            with self.subTest(field=key):
                d = copy.deepcopy(self.data)
                target = d[section] if index is None else d[section][index]
                target[key] = val
                with self.assertRaises(ValueError):
                    validate(d)

    def test_unearned_orbital_geometries(self):
        for key, value in [("city_center_polygon_1963", [[-37.6, -11.8]]),
                           ("crossing_point_1963", [-37.6, -11.8]),
                           ("crossing_present_1963", True),
                           ("river_bank_of_reported_event_1963", "left"),
                           ("crs", "EPSG:4326"), ("accuracy_m", 10),
                           ("can_constrain_orbital_reentry", True)]:
            with self.subTest(field=key):
                d = copy.deepcopy(self.data)
                d["castor_export"][key] = value
                with self.assertRaises(ValueError):
                    validate(d)


if __name__ == "__main__":
    unittest.main()
