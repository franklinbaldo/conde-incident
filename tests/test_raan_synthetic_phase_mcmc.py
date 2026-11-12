"""Counterfactual synthetic phase MCMC, NOT posterior for Conde 1963."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from raan_circular_likelihood import Datum, OffsetAnchor
from raan_synthetic_phase_mcmc import (
    PhasePrior, SyntheticPhaseModel, circular_moment,
    quadrature_circular_moment, sample_synthetic_phase,
)


def model(*, prior_kappa=0.0, anchor_kappa=0.0, prior_mu=0.0,
          anchor_mu=0.0, data_kappa=6.0, count=2):
    toy = tuple(
        Datum(100 + j, f"synthetic-epoch-{j}", "toy-catalog",
              37.0 + 3.0*j, 0.0, data_kappa,
              "synthetic:fixed H=0 for toy", "synthetic:arbitrary toy kappa")
        for j in range(count)
    )
    anchors = (OffsetAnchor("toy-catalog", anchor_mu, anchor_kappa,
                            "synthetic:anchor prior", "synthetic:no independence proof"),)
    phase_prior = PhasePrior(prior_mu, prior_kappa,
                             "synthetic:phase prior", "synthetic:not empirical")
    return SyntheticPhaseModel(toy, anchors, phase_prior)


class SyntheticCircularPhaseTests(unittest.TestCase):
    def test_gauge_and_haar_uniform_phase(self):
        m = model(anchor_kappa=0.0, prior_kappa=0.0)
        target = m.log_target(0)
        for phi in (0, 35, 180, 299.5, 359.9, 720):
            self.assertAlmostEqual(m.log_target(phi), target, delta=1e-12)
        self.assertLess(abs(quadrature_circular_moment(m)), 1e-12)
        result = sample_synthetic_phase(m, seed=1963, warmup=300, draws_per_chain=640)
        self.assertEqual(len(result.chains_deg), 4)
        self.assertEqual([len(c) for c in result.chains_deg], [640]*4)
        self.assertLess(abs(circular_moment(result.chains_deg)), 0.15)
        self.assertTrue(all(0.0 <= x <= 1.0 for x in result.acceptance_rates))
        self.assertIn("SYNTHETIC", result.interpretation)
        self.assertEqual(result.diagnostic.chain_count, 4)

    def test_anchored_toy_posterior_matches_quadrature_not_history(self):
        m = model(anchor_kappa=8.0, prior_kappa=0.0, anchor_mu=5.0)
        oracle = quadrature_circular_moment(m, nodes=1440)
        self.assertGreater(abs(oracle), 0.4)
        # Toy observation at ~37deg + synthetic anchor at 5deg.
        self.assertGreater(oracle.real, 0.0)
        self.assertGreater(oracle.imag, 0.0)
        chains = sample_synthetic_phase(
            m, seed=4816, warmup=450, draws_per_chain=640,
            proposal_step_deg=42.0, global_jump_probability=0.35
        )
        simulated = circular_moment(chains.chains_deg)
        self.assertLess(abs(simulated - oracle), 0.12)
        self.assertGreater(min(chains.acceptance_rates), 0.15)

    def test_assumed_phase_prior_drives_unidentified_phase(self):
        m = model(anchor_kappa=0.0, prior_kappa=10.0, prior_mu=292.0)
        z = quadrature_circular_moment(m)
        self.assertGreater(abs(z), 0.9)
        self.assertAlmostEqual(math.degrees(math.atan2(z.imag, z.real)) % 360,
                               292.0, delta=0.5)
        m2 = model(anchor_kappa=0.0, prior_kappa=10.0, prior_mu=67.0)
        z2 = quadrature_circular_moment(m2)
        self.assertAlmostEqual(math.degrees(math.atan2(z2.imag, z2.real)) % 360,
                               67.0, delta=0.5)

    def test_360_periodicity_does_not_introduce_seam(self):
        m = model(anchor_kappa=7.0, prior_kappa=3.0, prior_mu=359.0)
        for theta in (0.001, 45.0, 179.0, 359.999):
            self.assertAlmostEqual(m.log_target(theta), m.log_target(theta+360),
                                   delta=2e-12)

    def test_seed_reproducible_and_distinct_streams(self):
        m = model(anchor_kappa=5.0)
        a = sample_synthetic_phase(m, seed=123, warmup=60, draws_per_chain=64)
        b = sample_synthetic_phase(m, seed=123, warmup=60, draws_per_chain=64)
        c = sample_synthetic_phase(m, seed=124, warmup=60, draws_per_chain=64)
        self.assertEqual(a.chains_deg, b.chains_deg)
        self.assertNotEqual(a.chains_deg, c.chains_deg)
        self.assertNotEqual(a.chains_deg[0], a.chains_deg[1])

    def test_bad_mixing_detected_not_certified(self):
        m = model(anchor_kappa=0.0)
        result = sample_synthetic_phase(
            m, seed=45, draws_per_chain=128, warmup=10,
            proposal_step_deg=0.00001, global_jump_probability=0
        )
        self.assertFalse(result.diagnostic.passes_numerical_gate())
        self.assertGreater(result.diagnostic.worst_rhat, 1.1)

    def test_no_historical_inputs_even_with_provenance_string(self):
        m = model()
        row = m.rows[0]
        historical = Datum(row.norad, row.epoch_utc, row.lineage,
                           row.observed_raan_deg, row.predicted_raan_deg,
                           row.kappa, "C241-L3", row.calibration_ref)
        with self.assertRaisesRegex(ValueError, "synthetic"):
            SyntheticPhaseModel((historical,), m.anchors, m.phase_prior)
        anchor = OffsetAnchor("toy-catalog", 0.0, 5.0, "C197",
                              "synthetic:independence unknown")
        with self.assertRaisesRegex(ValueError, "synthetic"):
            SyntheticPhaseModel(m.rows, (anchor,), m.phase_prior)
        prior = PhasePrior(25, 3, "synthetic:prior", "C241-L3")
        with self.assertRaisesRegex(ValueError, "synthetic"):
            SyntheticPhaseModel(m.rows, m.anchors, prior)
        with self.assertRaisesRegex(ValueError, "historical"):
            SyntheticPhaseModel(m.rows, m.anchors, m.phase_prior,
                                purpose="HISTORICAL_1963")

    def test_duplicate_epoch_and_missing_lineage_rejected(self):
        m = model()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            SyntheticPhaseModel(m.rows + m.rows[:1], m.anchors, m.phase_prior)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            SyntheticPhaseModel(m.rows, (), m.phase_prior)

    def test_invalid_configuration_and_quadrature_guards(self):
        m = model()
        bad_values = [
            {"seed": True}, {"draws_per_chain": 5}, {"warmup": -1},
            {"proposal_step_deg": 0}, {"global_jump_probability": -0.1},
            {"global_jump_probability": 1.01},
            {"global_jump_probability": math.nan},
        ]
        for bad in bad_values:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                sample_synthetic_phase(m, **{"seed": 123, **bad})
        for n in (359, 32769, 720.5):
            with self.assertRaises(ValueError):
                quadrature_circular_moment(m, nodes=n)
        with self.assertRaises(ValueError):
            m.log_target(float("nan"))

    def test_zero_error_concentration_no_data_based_phase_information(self):
        m = model(anchor_kappa=11.0, data_kappa=0.0)
        a = m.log_target(20.0)
        self.assertAlmostEqual(m.log_target(199.0), a, places=12)
        self.assertLess(abs(quadrature_circular_moment(m)), 1e-12)


if __name__ == "__main__":
    unittest.main()
