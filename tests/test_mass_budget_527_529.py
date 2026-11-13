"""Adversarial checks for a conditional, not historical, three-object mass budget."""
import copy
import json
import unittest
from pathlib import Path
from tools.mass_budget_527_529 import report, optional_nonnegative

ROOT = Path(__file__).resolve().parents[1]
MODEL = json.loads((ROOT/"research/constraints/C241_mass_budget_residual_2026-11-13.json").read_text())
MATRIX = (ROOT/"research/evidence_matrix_C001-C238_2026-11-11.md").read_text()
IDENTITY = json.loads((ROOT/"research/tle_custody/gcat_full_catalog_lineage_C241-L14.json").read_text())

class MassPartition(unittest.TestCase):
    def reject(self, slot, mutation):
        a,b,c=copy.deepcopy(MODEL),MATRIX,copy.deepcopy(IDENTITY)
        if slot == 0:
            mutation(a)
        elif slot == 1:
            b = mutation(b)
        else:
            mutation(c)
        with self.assertRaises((ValueError,TypeError,KeyError)):
            report(a,b,c)

    def test_unknown_error_does_not_produce_bound(self):
        d = report(MODEL,MATRIX,IDENTITY)
        self.assertEqual(d["scenario"]["status"],"UNBOUNDED_BY_GIVEN_CATALOG_ERROR")
        self.assertIsNone(d["scenario"]["individual_mass_upper_exclusive_kg"])
        self.assertFalse(d["historical_domain_reduction"])

    def test_no_error_bound_even_if_x_is_bounded(self):
        d = report(MODEL,MATRIX,IDENTITY,x_max_kg="25")
        self.assertIsNone(d["scenario"]["tracked_mass_sum_max_kg"])

    def test_exact_inventory_and_no_residual_only_as_assumption(self):
        d=report(MODEL,MATRIX,IDENTITY,error_max_kg="0",x_max_kg="0")
        self.assertEqual(d["scenario"]["tracked_mass_sum_min_infimum_kg"],"1176")
        self.assertEqual(d["scenario"]["tracked_mass_sum_max_kg"],"1176")
        self.assertFalse(d["scenario"]["physical_constraint_active"])

    def test_nonzero_X_and_epsilon_limits_three_piece_total(self):
        d=report(MODEL,MATRIX,IDENTITY,error_max_kg="26",x_max_kg="50")
        self.assertEqual(d["scenario"]["tracked_mass_sum_min_infimum_kg"],"1100")
        self.assertEqual(d["scenario"]["tracked_mass_sum_max_kg"],"1202")
        self.assertEqual(d["scenario"]["individual_mass_upper_exclusive_kg"],"1202")

    def test_error_known_without_X_bound_does_not_give_positive_lower_bound(self):
        d=report(MODEL,MATRIX,IDENTITY,error_max_kg="0")
        self.assertEqual(d["scenario"]["tracked_mass_sum_min_infimum_kg"],"0")
        self.assertEqual(d["scenario"]["tracked_mass_sum_max_kg"],"1176")

    def test_untracked_might_dominate_nominal_mass(self):
        d=report(MODEL,MATRIX,IDENTITY,error_max_kg="0",x_max_kg="1000")
        self.assertEqual(d["scenario"]["tracked_mass_sum_min_infimum_kg"],"176")

    def test_untracked_cap_above_inventory_has_zero_infimum(self):
        d=report(MODEL,MATRIX,IDENTITY,error_max_kg="1",x_max_kg="3000")
        self.assertEqual(d["scenario"]["tracked_mass_sum_min_infimum_kg"],"0")

    def test_scenario_inputs_must_be_finite_and_nonnegative(self):
        for v in ("-1","NaN","Infinity","garbage"):
            with self.subTest(v=v), self.assertRaises(ValueError):
                optional_nonnegative(v)

    def test_legacy_C61_cannot_silently_change(self):
        self.reject(1,lambda x:x.replace("~1176 kg","~176 kg"))

    def test_legacy_dry_mass_is_distinct(self):
        self.reject(1,lambda x:x.replace("~306 kg","~1176 kg"))

    def test_wrong_catalogue_crosswalk(self):
        self.reject(2,lambda x:x["catalogue_labels"]["00528"].update(cospar="1963-003C"))

    def test_assumed_exact_inventory_not_proven(self):
        self.reject(0,lambda x:x["source"].update(claim_that_1176_is_closed_orbital_mass_for_three=True))

    def test_unknown_reference_error_not_set_zero(self):
        self.reject(0,lambda x:x["variables"][4].update(value=0))

    def test_untracked_fraction_not_automatically_small(self):
        self.reject(0,lambda x:x["variables"][3].update(automatically_small=True))

    def test_precondition_not_activated(self):
        self.reject(0,lambda x:x["conditional_budget"].update(physically_calibrated_historical_constraint=True))

    def test_individual_528_mass_not_inferred(self):
        self.reject(0,lambda x:x["source"].update(observed_individual_mass_of_528_kg=100))

    def test_shape_not_inferred_from_mass(self):
        self.reject(0,lambda x:x["conditional_derived_bounds"].update(bound_on_individual_diameter_m=1.5))

    def test_density_gauge_not_resolved_by_mass_budget(self):
        self.reject(0,lambda x:x["drag_bridge"].update(shared_atmosphere_scale_unidentified=False))

    def test_graph_edges_preserved(self):
        self.reject(0,lambda x:x["graph_edges"].pop())

    def test_no_false_historical_narrowing(self):
        self.reject(0,lambda x:x["conditional_derived_bounds"].update(numeric_historical_domain_reduction=True))

if __name__ == "__main__":
    unittest.main()
