"""Adversarial guards for the unresolved Ferret-3 1500-kg source family."""
import copy
import json
import unittest
from tools.ferret_mass_crosssource_C241 import LEDGER, GCAT, audit


class FerretMassCrosssource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.secondary = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.gcat = json.loads(GCAT.read_text(encoding="utf-8"))

    def test_real_crosssource_is_a_secondary_candidate(self):
        result = audit(self.secondary, self.gcat)
        self.assertEqual(result["repeated_nominal_ferret_mass_kg"], 1500)
        self.assertEqual(result["comparison_nominal_kg"], 324)
        self.assertEqual(result["comparison_launch_components_nominal_kg"], 294)
        self.assertEqual(result["historical_partition_mass_rank"], 0)
        self.assertEqual(result["hypothetical_authenticated_inventory_rank"], 1)
        self.assertIsNone(result["historical_mass_posterior"])
        self.assertFalse(result["geographical_domain_reduction"])

    def reject(self, section, key, value):
        mutated = copy.deepcopy(self.secondary)
        mutated[section][key] = value
        with self.assertRaises(ValueError):
            audit(mutated, self.gcat)

    def test_wrong_archived_page_sha_fails(self):
        self.reject("captured_page", "sha256", "0" * 64)

    def test_mass_is_not_a_measured_527_composite(self):
        self.reject("interpretation", "source_supports_1500_as_measured_mass_of_527", True)

    def test_no_historical_inventory(self):
        self.reject("interpretation", "source_supports_separation_inventory", True)

    def test_cannot_activate_constraint(self):
        self.reject("interpretation", "historical_constraint_active", True)

    def test_no_528_mass_from_ferret_listing(self):
        self.reject("interpretation", "attribution_to_528_kg", 1500)

    def test_no_independence_from_three_repeat_entries(self):
        self.reject("interpretation", "independent_instrument_or_engineering_measurement", True)

    def test_arithmetic_gap_not_physical_loss(self):
        self.reject("interpretation", "numerical_differences_are_physical_losses", True)

    def test_repeated_1500_detected(self):
        mutated = copy.deepcopy(self.secondary)
        mutated["entries"][1]["reported_mass_kg"] = 1480
        with self.assertRaises(ValueError):
            audit(mutated, self.gcat)

    def test_gcat_false_sum_rejected(self):
        mutated = copy.deepcopy(self.gcat)
        mutated["derived_checks"]["three_norad_objects_mass_sum_kg"] = 1176
        with self.assertRaises(ValueError):
            audit(self.secondary, mutated)


if __name__ == "__main__":
    unittest.main()
