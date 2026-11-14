"""G62 adversarial cross-covariance tests; all vectors are synthetic."""
import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from optical_shared_state_parallax import differential_retarded_parallax
from iers_1963_optical_lighttime import constant_velocity_light_time
# IERS CI executes this module: discover and run the separate G63 suite too.
from test_optical_joint_receiver_noise import JointReceiverNoiseTests  # noqa: F401

R = np.array([7000., 400., 300.])
V = np.array([1.1, 7.2, .3])
SA = np.array([6000., 0., 0.])
SB = np.array([6010., 0., 0.])
COV = np.diag([1., 1., 1., 1e-6, 1e-6, 1e-6])


class G62SharedOrbitalState(unittest.TestCase):
    def assess(self, **updates):
        args = dict(position_gcrs_km=R, velocity_gcrs_km_s=V,
                    station_a_gcrs_km=SA, station_b_gcrs_km=SB,
                    shared_state_covariance_gcrs6d=COV)
        args.update(updates)
        return differential_retarded_parallax(**args)

    def test_one_latent_state_gives_nonzero_cross_blocks(self):
        x = self.assess()
        joint = np.array(x['joint_marginals_and_cross_covariance_rad2'])
        true = np.array(x['shared_state_differential_covariance_rad2'])
        independent = np.array(x['independent_marginals_counterfactual_covariance_rad2'])
        cross = np.array(x['cross_terms_omitted_by_independence_rad2'])
        self.assertTrue(np.allclose(joint, joint.T, rtol=1e-12, atol=1e-22))
        self.assertTrue(np.allclose(independent-true, cross, rtol=1e-10, atol=1e-20))
        self.assertGreater(np.linalg.norm(cross), 1e-7)
        self.assertGreater(np.trace(independent), np.trace(true)*100)
        self.assertGreaterEqual(np.linalg.eigvalsh(true).min(), -1e-23)
        self.assertLessEqual(np.linalg.matrix_rank(joint, tol=1e-18), 4)
        self.assertEqual(x['historical_holdout'], 'NOT_RUN')
        self.assertEqual(x['theta_528'], 'UNCHANGED')

    def test_six_dimensional_jacobian_matches_frozen_basis_finite_difference(self):
        x = self.assess()
        b = np.asarray(x['common_tangent_basis_gcrs'])
        j = np.asarray(x['differential_jacobian_rad_per_gcrs_state6d'])
        for col in range(6):
            eps = 1e-3 if col < 3 else 1e-2
            dv = np.zeros(6)
            dv[col] = eps
            def f(delta):
                r, v = R+delta[:3], V+delta[3:]
                ua = constant_velocity_light_time(r, v, SA)['retarded_line_of_sight_gcrs']
                ub = constant_velocity_light_time(r, v, SB)['retarded_line_of_sight_gcrs']
                return b @ (np.asarray(ua)-np.asarray(ub))
            numeric = (f(dv)-f(-dv))/(2*eps)
            np.testing.assert_allclose(numeric, j[:,col], atol=4e-13, rtol=2e-5)

    def test_global_translation_leaves_parallax_and_covariance_invariant(self):
        original = self.assess()
        shift = np.array([2341., -7000., 500.])
        moved = self.assess(position_gcrs_km=R+shift,
                            station_a_gcrs_km=SA+shift,
                            station_b_gcrs_km=SB+shift)
        for key in ('nominal_direction_difference_rad_linearized',
                    'shared_state_differential_covariance_rad2'):
            np.testing.assert_allclose(original[key], moved[key], atol=1e-17)

    def test_reject_bad_covariance_and_same_station(self):
        with self.assertRaisesRegex(ValueError, 'Distinct receiver'):
            self.assess(station_b_gcrs_km=SA)
        bad = COV.copy()
        bad[3,3] = -1e-6
        with self.assertRaises(ValueError):
            self.assess(shared_state_covariance_gcrs6d=bad)
        with self.assertRaises(ValueError):
            self.assess(station_b_gcrs_km=[np.nan, 0., 0.])

    def test_cross_term_may_change_sign_for_other_geometry(self):
        # Never encode "independent is always conservative" as an invariant:
        # a common latent contribution can reduce OR increase a contrast error.
        other = self.assess(station_b_gcrs_km=np.array([9000., 200., 100.]))
        np.testing.assert_allclose(
            np.array(other['independent_marginals_counterfactual_covariance_rad2'])-
            np.array(other['cross_terms_omitted_by_independence_rad2']),
            np.array(other['shared_state_differential_covariance_rad2']),
            atol=2e-20, rtol=1e-8)


if __name__ == '__main__':
    unittest.main()
