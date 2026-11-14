"""G63: correlated receiver errors are mandatory when total error is claimed.

Only synthetic geometry / covariance. No historical sigma or station calibration.
"""
import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from optical_shared_state_parallax import differential_retarded_parallax

STATE = np.diag([1.0, 1.0, 1.0, 1e-6, 1e-6, 1e-6])
ARGS = dict(
    position_gcrs_km=[7000., 400., 300.],
    velocity_gcrs_km_s=[1.1, 7.2, .3],
    station_a_gcrs_km=[6000., 0., 0.],
    station_b_gcrs_km=[6010., 0., 0.],
    shared_state_covariance_gcrs6d=STATE,
)


def joint(rho: float, scale: float = 2e-10) -> np.ndarray:
    eye = np.eye(2) * scale
    return np.block([[eye, rho * eye], [rho * eye, eye]])


class JointReceiverNoiseTests(unittest.TestCase):
    def run_model(self, cov=None, assume_independent=False):
        return differential_retarded_parallax(
            **ARGS,
            receiver_noise_covariance_common_tangent_4d_rad2=cov,
            assume_receiver_state_independent=assume_independent)

    def test_missing_measurements_are_unknown_not_noiseless(self):
        x = self.run_model()
        self.assertIsNone(x['total_differential_covariance_rad2'])
        self.assertIsNone(x['receiver_noise_differential_covariance_rad2'])
        self.assertIsNone(x['receiver_noise_covariance_common_tangent_4d_rad2'])
        self.assertEqual(x['receiver_noise_status'], 'UNSPECIFIED_NOT_ZERO')
        self.assertEqual(x['theta_528'], 'UNCHANGED')

    def test_known_receiver_noise_still_has_unknown_total_if_cross_unknown(self):
        x = self.run_model(joint(0))
        self.assertIsNone(x['total_differential_covariance_rad2'])
        self.assertIsNotNone(x['receiver_noise_differential_covariance_rad2'])
        self.assertEqual(x['receiver_state_cross_covariance_status'],
                         'UNKNOWN_NOT_ZERO')

    def test_cannot_assert_independence_without_receiver_covariance(self):
        with self.assertRaisesRegex(ValueError, 'Cannot assume zero'):
            self.run_model(assume_independent=True)
        with self.assertRaisesRegex(ValueError, 'explicit bool'):
            self.run_model(joint(0), assume_independent='yes')

    def test_independent_receivers_are_an_explicit_assumption(self):
        x = self.run_model(joint(0), assume_independent=True)
        expected = 4e-10 * np.eye(2)
        np.testing.assert_allclose(x['receiver_noise_differential_covariance_rad2'],
                                   expected, rtol=1e-13, atol=1e-24)
        np.testing.assert_allclose(
            x['total_differential_covariance_rad2'],
            np.asarray(x['shared_state_differential_covariance_rad2']) + expected,
            rtol=1e-12, atol=1e-24)

    def test_common_mode_receiver_error_cancels(self):
        x = self.run_model(joint(1), assume_independent=True)
        np.testing.assert_allclose(x['receiver_noise_differential_covariance_rad2'],
                                   np.zeros((2, 2)), atol=1e-24)
        np.testing.assert_allclose(x['total_differential_covariance_rad2'],
                                   x['shared_state_differential_covariance_rad2'],
                                   atol=1e-24)

    def test_anti_correlated_receiver_error_doubles_independent_std(self):
        x = self.run_model(joint(-1), assume_independent=True)
        np.testing.assert_allclose(x['receiver_noise_differential_covariance_rad2'],
                                   8e-10 * np.eye(2), atol=1e-24)
        self.assertEqual(x['historical_holdout'], 'NOT_RUN')

    def test_asymmetric_valid_cross_block_and_psd(self):
        a = np.array([[1., 0.], [.1, 1.]])
        b = np.array([[.5, 0.], [0., 2.]])
        m = np.vstack([a, b])
        cov = 1e-10 * m @ m.T
        x = self.run_model(cov, assume_independent=True)
        D = np.hstack([np.eye(2), -np.eye(2)])
        want = D @ cov @ D.T
        np.testing.assert_allclose(x['receiver_noise_differential_covariance_rad2'],
                                   want, atol=1e-24)
        self.assertGreaterEqual(np.linalg.eigvalsh(want).min(), -1e-23)

    def test_reject_forged_nonpsd_correlations(self):
        for bad in (joint(1.01), joint(-1.01),
                    np.diag([1., -1., 1., 1.])):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, 'positive semidefinite'):
                    self.run_model(bad)

    def test_reject_nonfinite_nonsymmetric_wrong_shape(self):
        for bad in (np.eye(3), np.full((4, 4), np.nan),
                    np.diag([1., 1., 1., 1.]) + np.eye(4, k=1)):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, '4x4|symmetric'):
                    self.run_model(bad)


if __name__ == '__main__':
    unittest.main()
