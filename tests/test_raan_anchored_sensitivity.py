"""Synthetic numerical checks: a prior is not an instrument or historical posterior."""
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_circular_likelihood import (
    Datum, OffsetAnchor, LOG_TAU, log_i0, marginal_log_density,
    predictive_log_density, anchored_marginal_log_density,
    anchored_predictive_log_density,
)


def row(i, observed, predicted=0.0, kappa=2.0, group="catalog"):
    return Datum(528, f"synthetic-{i}", group, observed, predicted, kappa,
                 "synthetic-operator", "synthetic-calibration")


def anchor(mean=0.0, strength=0.0, group="catalog"):
    return OffsetAnchor(group, mean, strength,
                        "synthetic-offset-prior", "synthetic-independent-source-assumption")


def quad_log_marginal(rows, prior, n=12000):
    """Independent direct integration over shared offset, not analytic Bessel resultant."""
    from math import cos, exp, log, pi
    angles = [(math.radians(x.observed_raan_deg-x.predicted_raan_deg), x.kappa)
              for x in rows]
    lamb = prior.concentration
    mean = math.radians(prior.mean_deg)
    v = []
    for j in range(n):
        b = 2*pi*j/n
        v.append(exp(lamb * (cos(b-mean)-1) +
                     sum(k*(cos(r-b)-1) for r,k in angles)))
    return (math.log(math.fsum(v)/n) + lamb + sum(k for _,k in angles)
            - sum(log_i0(k) for _,k in angles) - log_i0(lamb)
            - len(rows)*LOG_TAU)


class AnchoredCircularSensitivity(unittest.TestCase):
    def test_uniform_prior_is_original_likelihood(self):
        rows = [row(1,359.9),row(2,0.1, kappa=12),
                row(3,89,group="another")]
        for mu in (-720, -15, 0, 180, 800):
            anchors = [anchor(mu,0),anchor(mu+20,0,"another")]
            self.assertAlmostEqual(anchored_marginal_log_density(rows,anchors),
                                   marginal_log_density(rows),delta=2e-11)

    def test_singleton_free_offset_no_phase_information(self):
        for phase in (0,179,360,789):
            self.assertAlmostEqual(anchored_marginal_log_density(
                [row(1,phase)],[anchor(0,0)]),-LOG_TAU,delta=2e-11)

    def test_informative_synthetic_anchor_changes_singleton_contrast(self):
        near=[row(1,0,kappa=5)]
        far=[row(1,180,kappa=5)]
        margins=[]
        for lam in (0,0.1,1,5,20):
            margins.append(anchored_marginal_log_density(near,[anchor(0,lam)]) -
                           anchored_marginal_log_density(far,[anchor(0,lam)]))
        self.assertAlmostEqual(margins[0],0,delta=1e-12)
        self.assertTrue(all(x<y for x,y in zip(margins,margins[1:])))
        self.assertGreater(margins[-1],5)

    def test_direct_quadrature(self):
        rows=[row(1,9,predicted=4,kappa=1.2),
              row(2,355,predicted=7,kappa=2.8)]
        for lam,mean in ((0,0),(.2,-180),(1.5,26),(7,55)):
            self.assertAlmostEqual(
                anchored_marginal_log_density(rows,[anchor(mean,lam)]),
                quad_log_marginal(rows,anchor(mean,lam)),delta=2e-11)

    def test_covariant_rotation_of_residual_and_prior(self):
        rows=[row(1,25,predicted=10),row(2,40,predicted=-10)]
        score=anchored_marginal_log_density(rows,[anchor(28,3)])
        for delta in (-720,-90,0,12.5,360,720):
            transformed=[row(1,25+delta,predicted=10),
                         row(2,40+delta,predicted=-10)]
            self.assertAlmostEqual(
                anchored_marginal_log_density(transformed,[anchor(28+delta,3)]),
                score,delta=1e-12)

    def test_predictive_difference_no_refit(self):
        fit=[row(1,12,kappa=1),row(2,18,kappa=2)]
        future=[row(3,30,kappa=1),row(4,350,kappa=3)]
        aa=[anchor(10,2)]
        self.assertAlmostEqual(anchored_predictive_log_density(fit,future,aa),
                               anchored_marginal_log_density(fit+future,aa) -
                               anchored_marginal_log_density(fit,aa),delta=1e-12)
        self.assertAlmostEqual(anchored_predictive_log_density(fit,future,[anchor(0,0)]),
                               predictive_log_density(fit,future),delta=1e-12)

    def test_new_lineage_in_holdout_requires_prior(self):
        fit=[row(1,0,group="a")]
        future=[row(2,0,group="b")]
        result=anchored_predictive_log_density(fit,future,
                                                 [anchor(0,0,"a"),anchor(20,0,"b")])
        self.assertAlmostEqual(result,-LOG_TAU,delta=1e-12)
        with self.assertRaises(ValueError):
            anchored_predictive_log_density(fit,future,[anchor(0,0,"a")])

    def test_reject_duplicate_missing_unknown_and_bad_anchors(self):
        data=[row(1,0)]
        bad=[
            [anchor(),anchor()],
            [],
            [anchor(group="wrong")],
            [anchor(strength=-1)],
            [anchor(strength=float("nan"))],
            [anchor(strength=float("inf"))],
            [anchor(mean=float("inf"))],
            [OffsetAnchor("catalog",0,0,"","synthetic")],
            [OffsetAnchor("catalog",0,0,"synthetic","")],
            [OffsetAnchor("catalog",0,0,"synthetic",None)],
            [OffsetAnchor("catalog",0,0,"synthetic","synthetic"),"not-an-anchor"],
        ]
        for anchors in bad:
            with self.subTest(anchors=str(anchors)), self.assertRaises(ValueError):
                anchored_marginal_log_density(data,anchors)

    def test_reject_duplicate_norad_epoch(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            anchored_marginal_log_density([row(1,0),row(1,10)],[anchor(0,2)])

    def test_cumulative_bridge_pending_not_an_empirical_prior(self):
        import json
        path = ROOT / "research/constraints/raan_offset_anchor_candidate_C241.json"
        bridge = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(bridge["status"], "CONNECTED_PENDING_EXTERNAL_ANCHOR_AND_CALIBRATION")
        self.assertIsNone(bridge["external_independent_anchor"])
        self.assertIsNone(bridge["historical_posterior"])
        self.assertFalse(bridge["active_constraint"])
        self.assertEqual(bridge["feasible_domain_delta"], "NOT_EVALUABLE")
        self.assertEqual(set(bridge["source_occurrences"]),
                         {"C25#1","C179#1","C180#1","C181#1","C241-L3"})
        self.assertEqual(bridge["original_haar_recovered_at"]["lambda_g"], 0)

    def test_large_concentrations_finite_and_extreme_rejected(self):
        for lam in (50,500,1000,1e6):
            result=anchored_marginal_log_density([row(1,0,kappa=lam)],
                                                  [anchor(0,lam)])
            self.assertTrue(math.isfinite(result))
        with self.assertRaises(ValueError):
            anchored_marginal_log_density([row(1,0,kappa=1e308),
                                            row(2,0,kappa=1e308)],[anchor(0,1e308)])


if __name__ == "__main__":
    unittest.main()
