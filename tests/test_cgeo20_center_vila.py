"""CGEO-20 regression tests for historical geolocation claims."""
import copy
import json
import unittest
from tools.cgeo20_center_vila import CONTRACT, validate


class CGEO20Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_source_and_checked_pages(self):
        validate(self.d)
        self.assertEqual(self.d["sources"][0]["document_date"], "2020-02-26")
        self.assertEqual(self.d["sources"][0]["pages_visually_inspected"], [1, 2])

    def test_distinct_names_only(self):
        self.assertEqual({u["name"] for u in self.d["named_localities"]},
                         {"Centro da cidade", "Vila do Conde"})
        self.assertIsNone(self.d["castor_export"]["center_1963_point"])

    def test_connected_graph(self):
        self.assertEqual({e["from"] for e in self.d["dependency_edges"]},
                         {"CGEO-17", "CGEO-18", "CGEO-19"})

    def test_adversarial_promotions_rejected(self):
        replacements = [
            ("interpretation", "2020_source_proves_1963_urban_extent", True),
            ("interpretation", "2014_bridge_proves_1963_bridge", True),
            ("interpretation", "same_2020_process_multiple_independent_observers", True),
            ("interpretation", "senhor_do_bonfim_is_nossa_senhora_do_monte", True),
            ("interpretation", "1958_severiano_lima_is_2020_severino_vieira", True),
            ("interpretation", "1963_center_is_2020_centro", True),
            ("interpretation", "1963_center_is_2020_vila", False),
            ("castor_export", "center_1963_point", [-37.62, -11.80]),
            ("castor_export", "bridge_present_1963", True),
            ("castor_export", "can_constrain_orbital_reentry", True),
        ]
        for section, name, val in replacements:
            with self.subTest(field=name):
                changed = copy.deepcopy(self.d)
                changed[section][name] = val
                with self.assertRaises(ValueError):
                    validate(changed)

    def test_retroprojecting_modern_wording_rejected(self):
        changed = copy.deepcopy(self.d)
        changed["observations"][0]["applies_in_1963"] = True
        with self.assertRaises(ValueError):
            validate(changed)

    def test_mislabeling_vila_as_centro_rejected(self):
        changed = copy.deepcopy(self.d)
        changed["named_localities"][1]["name"] = "Centro da cidade"
        with self.assertRaises(ValueError):
            validate(changed)


if __name__ == "__main__":
    unittest.main()
