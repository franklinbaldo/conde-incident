"""C241: adversarial checks for source-locked Python confidence penalties.

All sigmas here are laboratory assumptions, NEVER 1963 NASA calibration.
"""
from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

from tools.c241_confidence_weighted_heatmap import (
    Residual, shortest_angle, cholesky, gaussian_penalty,
    validate_frozen_report, weight_frozen_scenarios, report_all,
)

ROOT=Path(__file__).resolve().parents[1]
INPUT=json.loads((ROOT/"research/statistics/c241_528_unweighted_2000km_scenarios.json").read_text())

def item(delta: float, sigma: float | None = 1., occurrence: str = "C241-TEST-1"):
    return Residual(occurrence,"ONE_SYNTHETIC_LINEAGE","inclination","deg",
                    0.,delta,sigma,"ASSUMED_SCENARIO",
                    "EXPLICIT_SYNTHETIC_TEST_ONLY",False)

class ConfidencePenalties(unittest.TestCase):
    def test_original_1_5m_report_pinned_and_counts_preserved(self):
        validate_frozen_report(INPUT)
        self.assertEqual(sum(s["draws"] for s in INPUT["scenarios"]),1_500_000)
        self.assertEqual(sum(s["within_2000km"] for s in INPUT["scenarios"]),25_489)

    def test_unit_sigma_likelihood_penalty(self):
        actual=gaussian_penalty([item(1.)])
        self.assertAlmostEqual(actual["penalty"],.5)
        self.assertAlmostEqual(actual["relative_weight"],math.exp(-.5))
        self.assertFalse(actual["calibrated"])

    def test_same_deviation_higher_confidence_means_lower_relative_weight(self):
        tight=gaussian_penalty([item(1.,.1)])
        loose=gaussian_penalty([item(1.,10.)])
        self.assertLess(tight["relative_weight"],loose["relative_weight"])

    def test_angular_wrap_handles_359_degree_difference_as_one(self):
        self.assertAlmostEqual(shortest_angle(359.),-1.)
        ang=Residual("C241-TEST-A","ONE_SYNTHETIC_LINEAGE",
                     "raan","deg",1.,360.,1.,"ASSUMED_SCENARIO",
                     "EXPLICIT_SYNTHETIC_TEST_ONLY",True)
        self.assertAlmostEqual(gaussian_penalty([ang])["penalty"],.5)

    def test_correlation_downweights_double_counted_same_signed_errors(self):
        samples=[item(1.,1.,"C241-TEST-1"),item(1.,1.,"C241-TEST-2")]
        independent=gaussian_penalty(samples,[[1.,0.],[0.,1.]])
        correlated=gaussian_penalty(samples,[[1.,.9],[.9,1.]])
        self.assertLess(correlated["penalty"],independent["penalty"])
        self.assertGreater(correlated["relative_weight"],independent["relative_weight"])

    def test_correlation_changes_error_shape_not_generic_boost(self):
        samples=[item(1.,1.,"C241-TEST-1"),item(-1.,1.,"C241-TEST-2")]
        independent=gaussian_penalty(samples,[[1.,0.],[0.,1.]])
        correlated=gaussian_penalty(samples,[[1.,.9],[.9,1.]])
        self.assertGreater(correlated["penalty"],independent["penalty"])

    def test_multi_source_requires_explicit_correlation(self):
        with self.assertRaisesRegex(ValueError,"correlation"):
            gaussian_penalty([item(1.,1.,"C241-1"),item(1.,1.,"C241-2")])

    def test_two_identical_occurrences_not_independent_measurements(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            gaussian_penalty([item(1.),item(1.)],[[1.,0.],[0.,1.]])

    def test_mixed_lineage_without_audit_is_refused(self):
        one=item(1.,"1.")
        two=Residual("C241-2","SECOND_FAMILY","RAAN","deg",0.,1.,1.,
                     "ASSUMED_SCENARIO","LAB",False)
        with self.assertRaisesRegex(ValueError,"lineage"):
            gaussian_penalty([one,two],[[1.,0.],[0.,1.]])

    def test_missing_uncertainty_must_not_be_zero_or_default(self):
        for sigma in (None,0.,-1.,float("nan"),float("inf")):
            with self.subTest(sigma=sigma),self.assertRaisesRegex(ValueError,"sigma"):
                gaussian_penalty([item(1.,sigma)])

    def test_missing_sigma_rationale_is_refused(self):
        bad=Residual("C241-1","FAMILY","inclination","deg",0.,1.,1.,
                     "ASSUMED_SCENARIO",None,False)
        with self.assertRaisesRegex(ValueError,"provenance"):
            gaussian_penalty([bad])

    def test_covariance_singular_and_non_symmetric_rejected(self):
        for corr in (
            [[1.,1.],[1.,1.]],[[1.,.2],[.8,1.]],
            [[1.,2.],[2.,1.]],[[1.,.2],[.2,0.]],
        ):
            with self.subTest(corr=corr),self.assertRaises(ValueError):
                cholesky(corr)

    def test_scalar_identity_correlation(self):
        self.assertAlmostEqual(cholesky([[1.]])[0][0],1.)
        result=gaussian_penalty([item(0.)])
        self.assertEqual(result["relative_weight"],1.)

    def test_balanced_hit_reallocation_is_not_authenticated_by_aggregate(self):
        tampered=copy.deepcopy(INPUT)
        # 25,489 total hits and the original declared upstream SHA remain intact.
        tampered["scenarios"][0]["within_2000km"]+=1000
        tampered["scenarios"][6]["within_2000km"]-=1000
        self.assertEqual(sum(x["within_2000km"] for x in tampered["scenarios"]),25489)
        self.assertEqual(tampered["source"],INPUT["source"])
        with self.assertRaisesRegex(ValueError,"audited snapshot"):
            validate_frozen_report(tampered)

    def test_balanced_draw_reallocation_is_not_authenticated_by_aggregate(self):
        tampered=copy.deepcopy(INPUT)
        tampered["scenarios"][0]["draws"]+=300
        tampered["scenarios"][6]["draws"]-=300
        self.assertEqual(sum(x["draws"] for x in tampered["scenarios"]),1500000)
        with self.assertRaisesRegex(ValueError,"audited snapshot"):
            validate_frozen_report(tampered)

    def test_provenance_claims_not_exempt_from_full_payload_digest(self):
        tampered=copy.deepcopy(INPUT)
        tampered["integrity_constraints"]["NASA_terminal_time_sigma_known"]=True
        with self.assertRaisesRegex(ValueError,"audited snapshot"):
            validate_frozen_report(tampered)

    def test_original_count_mutation_rejected(self):
        damaged=copy.deepcopy(INPUT)
        damaged["scenarios"][0]["draws"]+=1
        with self.assertRaises(ValueError):
            validate_frozen_report(damaged)

    def test_fake_historical_tracking_mutation_rejected(self):
        damaged=copy.deepcopy(INPUT)
        damaged["source"]["independent_primary_observation"]=True
        with self.assertRaises(ValueError):
            validate_frozen_report(damaged)

    def test_unjustified_sigma_promoted_as_historical_rejected(self):
        damaged=copy.deepcopy(INPUT)
        damaged["confidence_status"]["phase_sigma_deg"]=1.
        with self.assertRaises(ValueError):
            validate_frozen_report(damaged)

    def test_sensitivity_grid_is_all_explicitly_assumed(self):
        out=report_all(INPUT)
        self.assertIsNone(out["historical_posterior"])
        self.assertIsNone(out["impact_probability"])
        self.assertEqual(out["source"],"SECONDARY_TLE_J2_SYNTHETIC_1_5M_SAMPLES")
        self.assertAlmostEqual(out["baseline_equal_draw_percent"],1.6992666666666667)
        self.assertEqual(set(out["sensitivity"]),{
            "tight_hypothesis","intermediate_hypothesis","broad_hypothesis",
            "intermediate_neg_correlation","intermediate_pos_correlation"})

    def test_tight_prior_changes_scenario_frequency_not_truth(self):
        r=report_all(INPUT)["sensitivity"]
        self.assertGreater(r["tight_hypothesis"]["weighted_percent"],
                           r["intermediate_hypothesis"]["weighted_percent"])
        self.assertGreater(r["intermediate_hypothesis"]["weighted_percent"],
                           r["broad_hypothesis"]["weighted_percent"])
        self.assertTrue(all(x["probability_of_ground_impact"] is None
                            and x["ablation_survival_probability"] is None
                            and not x["historical_sigma_calibrated"]
                            for x in r.values()))

    def test_unreported_uncertainty_parameters_cannot_be_silently_defaulted(self):
        for kw in (
            {"phase_sigma_deg":None,"ndot_sigma_rev_day2":.01,"rho":0.},
            {"phase_sigma_deg":10.,"ndot_sigma_rev_day2":None,"rho":0.},
            {"phase_sigma_deg":10.,"ndot_sigma_rev_day2":.01,"rho":None},
        ):
            with self.subTest(kw=kw),self.assertRaises(ValueError):
                weight_frozen_scenarios(INPUT,**kw)

    def test_correlation_near_plus_one_is_valid_but_singular_is_not(self):
        result=weight_frozen_scenarios(
            INPUT,phase_sigma_deg=90.,ndot_sigma_rev_day2=.02,rho=.99)
        self.assertTrue(0<result["weighted_percent"]<100)
        with self.assertRaises(ValueError):
            weight_frozen_scenarios(INPUT,phase_sigma_deg=90.,
                                    ndot_sigma_rev_day2=.02,rho=1.)

if __name__=="__main__":
    unittest.main()
