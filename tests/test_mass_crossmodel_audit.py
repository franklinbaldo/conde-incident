"""Adversarial regression of central mass-to-all-models contract."""
import copy
import json
import unittest
from pathlib import Path
from tools.audit_mass_crossmodel import validate

ROOT=Path(__file__).resolve().parents[1]
MODEL=json.loads((ROOT/"research/constraints/C241_mass_crossmodel_routing_2026-11-13.json").read_text())
SOURCE=json.loads((ROOT/"research/constraints/C241_mass_budget_residual_2026-11-13.json").read_text())
MATRIX=(ROOT/"research/evidence_matrix_C001-C238_2026-11-11.md").read_text()

def read(path):
    return (ROOT/path).read_text(encoding="utf-8")

class MassRouting(unittest.TestCase):
    def reject(self,index,mutation):
        src=[copy.deepcopy(MODEL),copy.deepcopy(SOURCE),MATRIX]
        if index==2:src[2]=mutation(src[2])
        else:mutation(src[index])
        with self.assertRaises((ValueError,KeyError,TypeError)):
            validate(*src,read)

    def test_replay_real_repo_model_bindings(self):
        r=validate(MODEL,SOURCE,MATRIX,read)
        self.assertEqual(r["consumers_catalogued"],12)
        self.assertEqual(r["conditional_bridges_implemented"],4)
        self.assertEqual(r["historical_mass_constraints_activated"],0)
        self.assertIsNone(r["physical_historical_mass_range_kg"])

    def test_unverified_528_mass_not_promoted(self):
        self.reject(0,lambda x:x["source"].update(individual_528_mass_kg=20))

    def test_budget_source_not_falsified(self):
        self.reject(1,lambda x:x["source"].update(associated_total_mass_kg_approx=1800))

    def test_source_C61_not_overwritten(self):
        self.reject(2,lambda x:x.replace("~1176 kg","~1276 kg"))

    def test_specific_306_is_payload_only(self):
        self.reject(0,lambda x:x["invariants"].update(
            GCAT_306_is_not_entire_527_physical_mass=False))

    def test_unknown_mass_tolerance_not_set_zero(self):
        self.reject(0,lambda x:x["source"].update(catalogue_uncertainty_kg=0))

    def test_no_default_three_body_mass_basis(self):
        self.reject(0,lambda x:x["scenario_contract"].update(
            must_explicitly_choose_mass_basis=False))

    def test_no_posterior_from_306kg(self):
        self.reject(0,lambda x:x["scenario_contract"].update(
            posterior_prior_from_306kg={"mean":306}))

    def test_no_global_angular_error_from_mass(self):
        self.reject(0,lambda x:x["consumers"][9].update(
            historical_constraint_active=True))

    def test_no_orbital_terminal_time_from_mass_alone(self):
        self.reject(0,lambda x:x["invariants"].update(
            terminal_date_does_not_calibrate_B_without_time_error=False))

    def test_every_consuming_model_must_be_registered(self):
        self.reject(0,lambda x:x["consumers"].pop())

    def test_no_duplicate_model_in_consumer_registry(self):
        self.reject(0,lambda x:x["consumers"].append(copy.deepcopy(x["consumers"][0])))

    def test_old_legacy_MonteCarlo_not_historical_posterior(self):
        self.reject(0,lambda x:next(c for c in x["consumers"]
            if c["id"]=="exploratory-monte-carlo").update(
                historical_constraint_active=True))

    def test_cannot_create_claim_of_inferred_dimensions(self):
        self.reject(0,lambda x:x["invariants"].update(no_1963_object_size_inferred=False))

    def test_real_src_missing_injected_hook_is_caught(self):
        def damaged(path):
            original=read(path)
            return original.replace("conditionalBallisticCompatibility",
                "removed_mass_hook") if path=="src/lib/inverseSolver.ts" else original
        with self.assertRaisesRegex(ValueError,"missing actual adapter"):
            validate(MODEL,SOURCE,MATRIX,damaged)

if __name__=="__main__":unittest.main()
