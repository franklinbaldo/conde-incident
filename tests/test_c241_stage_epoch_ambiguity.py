"""Adversarial checks for the non-identifiability of event mass from GCAT."""
import copy
import json
import unittest
from fractions import Fraction

from tools.c241_stage_epoch_ambiguity import (
    GCAT, audit, audit_catalog, closed_inventory_with_527_equals_total,
    hypothetical_stage_at_event,
)


class StageEpochAmbiguity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(GCAT.read_text(encoding="utf-8"))

    def test_nominal_30_is_not_a_fuel_burn_observation(self):
        r = audit()
        self.assertEqual(r["catalog_nominal_difference_kg"], "30")
        self.assertFalse(r["fuel_consumed_identified_by_catalog"])
        self.assertFalse(r["event_mass_and_epoch_identified_by_catalog"])
        self.assertIsNone(r["historical_posterior"])
        self.assertEqual(r["historical_mcmc"], "NOT_RUN")

    def test_two_distinct_event_masses_fit_the_same_catalog(self):
        self.assertEqual(hypothetical_stage_at_event(self.catalog, "0"), 870)
        self.assertEqual(hypothetical_stage_at_event(self.catalog, "30"), 900)
        self.assertEqual(hypothetical_stage_at_event(self.catalog, "15/2"), Fraction(1755, 2))
        self.assertFalse(audit()["historical_domain_reduction"])

    def test_no_double_counting_full_527_and_closed_total(self):
        self.assertFalse(closed_inventory_with_527_equals_total(1176, 1, 1, 0))
        self.assertFalse(closed_inventory_with_527_equals_total(1176, 0, 0, 1))
        self.assertTrue(closed_inventory_with_527_equals_total(1176, 0, 0, 0))

    def test_no_numeric_inference_from_unknown_528_529(self):
        self.assertIsNone(self.catalog["rows"]["S00528"]["mass_kg"])
        self.assertIsNone(self.catalog["rows"]["S00529"]["mass_kg"])
        self.assertFalse(audit()["historical_constraint_active"])

    def test_reject_unsupported_event_propellant(self):
        for remaining in (-1, 31, "nan", 3.0, True):
            with self.subTest(remaining=remaining), self.assertRaises(ValueError):
                hypothetical_stage_at_event(self.catalog, remaining)

    def test_guard_fails_closed_on_relabelled_catalog(self):
        mutants = [
            ("rows", "S00527", "total_mass_kg", 1206),
            ("rows", "A00324", "dry_mass_kg", 900),
            ("rows", "S00528", "mass_kg", 0),
            ("conclusion", None, "historical_mass_constraint_active", True),
        ]
        for section, obj, key, value in mutants:
            with self.subTest(key=key):
                data = copy.deepcopy(self.catalog)
                target = data[section] if obj is None else data[section][obj]
                target[key] = value
                with self.assertRaises(ValueError):
                    audit_catalog(data)

    def test_witnesses_do_not_count_as_independent_observations(self):
        r = audit()
        self.assertEqual(len(r["hypothetical_stage_event_mass_witnesses_kg"]), 2)
        self.assertEqual(r["source_occurrence"], "C241-L40")
        self.assertEqual(len(r["source_sha256"]), 64)
        self.assertEqual(len(r["document_needed"]), 3)


if __name__ == "__main__":
    unittest.main()
