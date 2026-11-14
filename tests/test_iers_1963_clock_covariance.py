"""Adversarial G64 paired clock controls: scenarios, not observations."""
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from iers_1963_clock_covariance import paired_clock_covariance  # noqa: E402


class G64ClockCovariance(unittest.TestCase):
    def cov(self, a, b, c):
        return paired_clock_covariance(a, b, c)

    def test_missing_sigma_is_unknown_not_zero(self):
        o = self.cov([.004, 0], [.004, 0], None)
        self.assertIsNone(o["clock_only_joint_covariance_rad2"])
        self.assertIsNone(o["clock_only_difference_covariance_rad2"])
        self.assertEqual(o["historical_holdout"], "NOT_RUN")

    def test_independent_clocks_add_variance(self):
        v = .01**2
        o = self.cov([.004, 0], [.004, 0], [[v, 0], [0, v]])
        d = np.asarray(o["clock_only_difference_covariance_rad2"])
        self.assertAlmostEqual(d[0, 0], 2*.004**2*v, delta=1e-22)
        self.assertAlmostEqual(np.sqrt(d[0, 0])*206264.806, 11.67, delta=.05)

    def test_shared_clock_equal_rates_cancel(self):
        v = .01**2
        o = self.cov([.004, 0], [.004, 0], [[v, v], [v, v]])
        d = np.asarray(o["clock_only_difference_covariance_rad2"])
        self.assertLess(abs(d[0, 0]), 1e-23)
        self.assertEqual(o["clock_correlation"], 1.)
        self.assertIsNone(o["combined_state_instrument_clock_covariance_rad2"])

    def test_shared_clock_opposite_rates_amplify(self):
        v = .01**2
        o = self.cov([.004, 0], [-.004, 0], [[v, v], [v, v]])
        self.assertAlmostEqual(o["clock_only_difference_covariance_rad2"][0][0],
                               4*.004**2*v, delta=1e-22)

    def test_anticorrelated_clock_amplifies_equal_rates(self):
        v = .01**2
        o = self.cov([.004, 0], [.004, 0], [[v, -v], [-v, v]])
        self.assertAlmostEqual(o["clock_only_difference_covariance_rad2"][0][0],
                               4*.004**2*v, delta=1e-22)
        self.assertEqual(o["clock_correlation"], -1.)

    def test_cross_terms_in_joint_and_difference(self):
        a = np.array([.002, -.003])
        b = np.array([.005, .001])
        c = np.array([[.01**2, .00003], [.00003, .02**2]])
        o = self.cov(a, b, c)
        j = np.asarray(o["clock_only_joint_covariance_rad2"])
        d = np.asarray(o["clock_only_difference_covariance_rad2"])
        self.assertAlmostEqual(j[0, 2], a[0]*b[0]*c[0, 1], delta=1e-24)
        expected = (c[0, 0]*np.outer(a, a) + c[1, 1]*np.outer(b, b)
                    - c[0, 1]*(np.outer(a, b)+np.outer(b, a)))
        self.assertTrue(np.allclose(d, expected, atol=1e-24, rtol=1e-13))

    def test_zero_rate_does_not_certify_historical_clock(self):
        o = self.cov([0, 0], [0, 0], [[1, 0], [0, 1]])
        self.assertEqual(o["clock_only_difference_covariance_rad2"],
                         [[0., 0.], [0., 0.]])
        self.assertEqual(o["historical_holdout"], "NOT_RUN")

    def test_reject_non_psd_asymmetric_nonfinite_wrong_shape(self):
        v = 1e-4
        for c in (
            [[-1e-30, 0], [0, v]], [[v, 2*v], [2*v, v]],
            [[v, 1e-10], [0, v]], [[0, 1e-12], [1e-12, v]],
            [[float("nan"), 0], [0, v]], [[v, float("inf")], [0, v]],
            [[v, 0, 0], [0, v, 0]], "uncalibrated", [[True, False], [False, True]],
        ):
            with self.subTest(clock=c), self.assertRaises(ValueError):
                self.cov([.004, 0], [0, .004], c)
        for a in ([1], [0, 0, 0], [float("inf"), 0], "0.001", [True, False]):
            with self.subTest(rate=a), self.assertRaises(ValueError):
                self.cov(a, [0, 1], [[1, 0], [0, 1]])

    def test_finite_difference_rate_in_fixed_tangent_plane(self):
        dt = 0.0001
        def theta(t):
            return np.array([.004*t + .00005*t*t, -.002*t])
        rate = (theta(dt)-theta(-dt))/(2*dt)
        o = self.cov(rate, [0, 0], [[.01**2, 0], [0, 0]])
        self.assertAlmostEqual(o["clock_only_difference_covariance_rad2"][0][0],
                               (.004*.01)**2, delta=1e-22)


if __name__ == "__main__":
    unittest.main()
