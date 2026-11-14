"""Adversarial tests: target estimability is not full-ledger identification."""
import copy
import json
import unittest

from tools.mass_identifiability_C241 import GCAT, catalog_is_not_mass_inventory
from tools.mass_observation_design_C241 import audit, design, witnesses


class MassNuisanceDesign(unittest.TestCase):
    def test_catalog_has_no_active_mass_equation(self):
        r = audit()
        self.assertEqual(r["scenarios"]["catalog_only"]["rank"], 0)
        self.assertEqual(r["scenarios"]["catalog_only"]["nullity"], 6)
        self.assertFalse(r["historical_constraint_active"])
        self.assertEqual(r["historical_mcmc"], "NOT_RUN")
        self.assertIsNone(r["historical_mass_posterior"])
        self.assertFalse(r["historical_domain_reduction"])

    def test_scenario_total_alone_leaves_528_unidentified(self):
        r = design(total_validated=True)
        self.assertEqual((r["rank"], r["nullity"]), (1, 5))
        self.assertFalse(r["m528_estimable"])

    def test_527_and_529_with_total_do_not_estimate_528(self):
        r = design(total_validated=True,
                   candidate_channels=("mass_527", "mass_529"))
        self.assertEqual((r["rank"], r["nullity"]), (3, 3))
        self.assertFalse(r["m528_estimable"])

    def test_independent_528_only_is_target_not_full_ledger(self):
        r = design(candidate_channels=("mass_528",))
        self.assertTrue(r["m528_estimable"])
        self.assertFalse(r["entire_ledger_identified"])
        self.assertEqual((r["rank"], r["nullity"]), (1, 5))

    def test_three_object_measurements_do_not_resolve_loss_residual_bias(self):
        r = design(total_validated=True,
                   candidate_channels=("mass_527", "mass_528", "mass_529"))
        self.assertEqual((r["rank"], r["nullity"]), (4, 2))
        self.assertTrue(r["m528_estimable"])
        self.assertFalse(r["entire_ledger_identified"])
        with_x = design(total_validated=True,
                        candidate_channels=("mass_527", "mass_528",
                                            "mass_529", "residual_X"))
        self.assertEqual((with_x["rank"], with_x["nullity"]), (5, 1))

    def test_five_other_channels_plus_total_identify_528_conditionally(self):
        r = audit()["scenarios"]["total_plus_five_other_channels"]
        self.assertEqual((r["rank"], r["nullity"]), (6, 0))
        self.assertTrue(r["m528_estimable"])
        self.assertTrue(r["scenario_only"])

    def test_observation_duplicates_and_unknown_channels_rejected(self):
        for channels in (("mass_528", "mass_528"), ("CdA_over_m",),
                         ("TotMass_1176_from_GCAT",)):
            with self.subTest(channels=channels), self.assertRaises(ValueError):
                design(candidate_channels=channels)

    def test_two_indistinguishable_exact_mass_histories(self):
        w = witnesses()
        base = w["baseline_kg"]
        alt = w["same_528_different_X_L_kg"]
        move = w["different_528_same_total_527_529_L_epsilon_kg"]
        self.assertEqual(sum(base), sum(alt))
        self.assertEqual(sum(base), sum(move))
        self.assertEqual(base[1], alt[1])
        self.assertNotEqual(base[1], move[1])
        self.assertFalse(w["is_historical_measurement"])

    def test_catalog_promotion_guard(self):
        catalog = json.loads(GCAT.read_text(encoding="utf-8"))
        bad = copy.deepcopy(catalog)
        bad["conclusion"]["historical_mass_constraint_active"] = True
        with self.assertRaises(ValueError):
            catalog_is_not_mass_inventory(bad)
        bad = copy.deepcopy(catalog)
        bad["rows"]["S00528"]["mass_kg"] = 0
        with self.assertRaises(ValueError):
            catalog_is_not_mass_inventory(bad)

    def test_reproducible_source_and_without_probability(self):
        a = audit()
        self.assertEqual(a, audit())
        self.assertEqual(len(a["source_sha256"]), 64)
        self.assertEqual(a["source_family_independent_mass_measurements"], 0)


if __name__ == "__main__":
    unittest.main()
