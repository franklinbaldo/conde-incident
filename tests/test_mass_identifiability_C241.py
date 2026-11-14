"""C241 adversarial mass-rank tests, all scenarios counterfactual."""
import copy
import json
import unittest
from pathlib import Path
from tools.mass_identifiability_C241 import (
    GCAT, audit, catalog_is_not_mass_inventory, exact_drag_counterexample,
    rank, scenario_rows,
)


class MassIdentifiability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(Path(GCAT).read_text(encoding="utf-8"))

    def test_current_catalog_not_three_mass_inventory(self):
        self.assertTrue(catalog_is_not_mass_inventory(self.catalog))
        result = audit()
        self.assertEqual(result["historical_mass_observation_rank"], 0)
        self.assertEqual(result["historical_mass_nullity"], 4)
        self.assertFalse(result["physical_domain_reduction"])
        self.assertIsNone(result["historical_mass_posterior"])

    def test_catalog_zero_is_not_zero_physical_mass(self):
        mutated = copy.deepcopy(self.catalog)
        mutated["rows"]["S00528"]["mass_kg"] = 0
        with self.assertRaises(ValueError):
            catalog_is_not_mass_inventory(mutated)

    def test_no_false_triple_sum(self):
        mutated = copy.deepcopy(self.catalog)
        mutated["derived_checks"]["three_norad_objects_mass_sum_kg"] = 1176
        with self.assertRaises(ValueError):
            catalog_is_not_mass_inventory(mutated)

    def test_cannot_activate_constraint_without_engineering_basis(self):
        mutated = copy.deepcopy(self.catalog)
        mutated["conclusion"]["historical_mass_constraint_active"] = True
        with self.assertRaises(ValueError):
            catalog_is_not_mass_inventory(mutated)

    def test_exact_conditional_rank_and_nuisance_directions(self):
        rows = scenario_rows(inventory_assumed=True)
        self.assertEqual(rank(rows), 1)
        for v in ((1, -1, 0, 0), (1, 0, -1, 0), (1, 0, 0, -1)):
            self.assertEqual(sum(a*b for a, b in zip(rows[0], v)), 0)

    def test_two_mass_measurements_leave_one_free_mode(self):
        rows = scenario_rows(inventory_assumed=True,
                             independent_mass_objects=("528", "529"))
        self.assertEqual(rank(rows), 3)

    def test_three_mass_measurements_only_conditionally_identify_all(self):
        rows = scenario_rows(inventory_assumed=True,
                             independent_mass_objects=("527", "528", "529"))
        self.assertEqual(rank(rows), 4)
        self.assertEqual(rank(scenario_rows(
            independent_mass_objects=("527", "528", "529"))), 3)

    def test_no_double_counting_duplicate_catalog_source(self):
        with self.assertRaises(ValueError):
            scenario_rows(independent_mass_objects=("527", "527"))

    def test_drag_observables_do_not_resolve_unknown_cd_area(self):
        witness = exact_drag_counterexample(
            (500, 200, 100, 376), (10, 5, 2), 50)
        self.assertTrue(all(witness.values()))

    def test_invalid_drag_counterexamples_rejected(self):
        for delta in (0, 200, -500):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                exact_drag_counterexample(
                    (500, 200, 100, 376), (10, 5, 2), delta)

    def test_exact_rank_independent_of_float_tolerance(self):
        self.assertEqual(rank([[1, 1, 1, 1], [1, 1, 1, 1]]), 1)
        self.assertEqual(rank([[1, 1, 1, 1], [1, 1, 1, 2]]), 2)


if __name__ == "__main__":
    unittest.main()
