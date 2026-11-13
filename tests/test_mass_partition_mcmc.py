"""Adversarial Bayesian mass partition: prior sensitivity vs historical posterior."""
import copy
import json
import math
import random
import unittest
from pathlib import Path
from tools.mass_partition_mcmc import (
    PREDECLARED_PRIORS, OBJECTS, prior_profile, fractions, log_target,
    one_chain, run_synthetic, validate_synthetic_fixture, historical_gate,
    read_sources,
)

ROOT=Path(__file__).resolve().parents[1]
FIX=json.loads((ROOT/"tests/fixtures/mass_partition_synthetic_c241.json").read_text())

class MassMcmc(unittest.TestCase):
    def test_historical_model_provenance_loaded(self):
        m,semantics=read_sources()
        self.assertFalse(m["conditional_budget"]["physically_calibrated_historical_constraint"])
        self.assertEqual(semantics["sources"]["payload"]["Mass_kg"],306)
        self.assertFalse(semantics["physical_model"]["m527_equals_306_directly"])

    def test_no_historical_likelihood_no_posterior(self):
        model,semantics=read_sources()
        r=historical_gate(model,semantics)
        self.assertFalse(r["historical_mcmc_executed"])
        self.assertIsNone(r["historical_likelihood"])
        self.assertIsNone(r["posterior_most_probable_allocation"])
        self.assertFalse(r["physical_domain_reduced"])
        self.assertTrue(r["mass_of_orbiting_527_composite_is_not_306kg_verified"])
        self.assertEqual(r["catalogue_mass_basis_conflict_kg"],30)

    def test_prior_sensitivity_is_not_evidence(self):
        a=prior_profile(PREDECLARED_PRIORS["symmetrical"])
        b=prior_profile(PREDECLARED_PRIORS["residual_small_assumption"])
        self.assertEqual(a["X"],294)
        self.assertLess(b["X"],a["X"])
        self.assertNotEqual(a["527"],b["527"])

    def test_mass_partition_sums_to_total_under_synthetic_condition(self):
        alpha,sigma,observations=validate_synthetic_fixture(FIX)
        c=one_chain(alpha,sigma,observations,23,110,200)
        for d in c["draws"]:
            self.assertAlmostEqual(sum(d["masses_kg"]),1176+d["epsilon_kg"],places=8)
            self.assertTrue(all(x>0 for x in d["masses_kg"]))

    def test_dirichlet_log_ratio_jacobian_matches_prior_shape(self):
        # At y=0 fractions each 1/4; shifting one coordinate lowers
        # symmetric Dirichlet(1,1,1,1) density on unconstrained logits.
        self.assertGreater(log_target([0,0,0],0,[1,1,1,1],50,[]),
                           log_target([5,0,0],0,[1,1,1,1],50,[]))

    def test_log_ratio_softmax_normalized(self):
        f=fractions([2,-2,1])
        self.assertAlmostEqual(sum(f),1.0)
        self.assertTrue(all(x>0 for x in f))

    def test_softmax_rejects_nonfinite(self):
        with self.assertRaises(ValueError):
            fractions([0,float("nan"),0])

    def test_invalid_dirichlet(self):
        for alpha in ([0,1,1,1],[-1,1,1,1],[1,1,1],[1,1,1,float("inf")]):
            with self.subTest(alpha=alpha),self.assertRaises(ValueError):
                prior_profile(alpha)

    def test_synthetic_mass_basis_is_explicit(self):
        wrong=copy.deepcopy(FIX)
        del wrong["mass_basis"]
        with self.assertRaises(ValueError):
            validate_synthetic_fixture(wrong)

    def test_insertion_mass_basis_changes_only_hypothetical_total(self):
        alpha,sigma,obs=validate_synthetic_fixture(FIX)
        c=one_chain(alpha,sigma,obs,23,110,200,total_reference_mass_kg=1206.)
        for d in c["draws"]:
            self.assertAlmostEqual(sum(d["masses_kg"]),1206+d["epsilon_kg"],places=8)
        switched=copy.deepcopy(FIX)
        switched["mass_basis"]="SUM_MASS_INSERTION"
        self.assertEqual(validate_synthetic_fixture(switched)[0],alpha)

    def test_missing_306_as_m527_observation_does_not_create_posterior(self):
        m,semantics=read_sources()
        r=historical_gate(m,semantics)
        self.assertEqual(r["catalogue_payload_527_component_mass_kg"],306)
        self.assertIsNone(r["posterior_most_probable_allocation"])
        self.assertTrue(r["component_306kg_is_not_direct_mass_observation_of_528"])

    def test_historical_mode_cannot_run_synthetic(self):
        wrong=copy.deepcopy(FIX)
        wrong["mode"]="HISTORICAL"
        with self.assertRaises(ValueError):
            validate_synthetic_fixture(wrong)

    def test_synthetic_observations_need_explicit_source_label(self):
        wrong=copy.deepcopy(FIX)
        wrong["synthetic_mass_observations"][0]["source_class"]="NASA_PRIMARY"
        with self.assertRaises(ValueError):
            validate_synthetic_fixture(wrong)

    def test_synthetic_sigma_required(self):
        wrong=copy.deepcopy(FIX)
        wrong["synthetic_mass_observations"][0]["sigma_kg"]=0
        with self.assertRaises(ValueError):
            validate_synthetic_fixture(wrong)

    def test_total_mass_error_sigma_is_explicit(self):
        wrong=copy.deepcopy(FIX)
        del wrong["reference_error_sigma_kg"]
        with self.assertRaises(KeyError):
            validate_synthetic_fixture(wrong)

    def test_duplicate_mass_observations_cannot_double_count(self):
        wrong=copy.deepcopy(FIX)
        wrong["synthetic_mass_observations"].append(dict(wrong["synthetic_mass_observations"][0]))
        with self.assertRaises(ValueError):
            validate_synthetic_fixture(wrong)

    def test_reproducibility_seed_and_independent_chains(self):
        a,s,o=validate_synthetic_fixture(FIX)
        c=one_chain(a,s,o,1004,120,200)
        d=one_chain(a,s,o,1004,120,200)
        e=one_chain(a,s,o,1005,120,200)
        self.assertEqual(c,d)
        self.assertNotEqual(c["draws"],e["draws"])

    def test_synthetic_engine_does_not_claim_historical_posterior(self):
        out=run_synthetic(FIX,seed=2005,warmup=120,draws=200)
        self.assertEqual(out["chains"],4)
        self.assertTrue(out["observations_are_invented_for_test"])
        self.assertFalse(out["historical_masses_inferred"])
        self.assertFalse(out["physical_domain_reduced"])
        self.assertEqual(set(out["mass_summary"]),set(OBJECTS))
        for obj in out["mass_summary"].values():
            self.assertGreaterEqual(obj["q95_kg"],obj["q05_kg"])
            self.assertGreater(obj["median_kg"],0)
            self.assertIn("rhat_rank_and_folded",obj["diagnostic"])

    def test_reference_uncertainty_cannot_be_negative(self):
        wrong=copy.deepcopy(FIX)
        wrong["reference_error_sigma_kg"]=-1
        with self.assertRaises(ValueError):
            validate_synthetic_fixture(wrong)

if __name__=="__main__":
    unittest.main()
