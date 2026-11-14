"""CASTOR-G63: independent negative/positive controls for local light-time Taylor error."""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from iers_1963_optical_lighttime import (
    quadratic_central_gravity_light_time, constant_velocity_light_time,
)


class G63CentralAccelerationDiagnostic(unittest.TestCase):
    def setUp(self):
        self.r = np.array([7000., 2000., 0.])
        self.v = np.array([0., 7.5, 0.])
        self.s = np.array([6378.137, 0., 0.])

    def test_zero_gm_recovers_g60_exactly(self):
        got = quadratic_central_gravity_light_time(self.r, self.v, self.s, 0.)
        linear = constant_velocity_light_time(self.r, self.v, self.s)
        self.assertAlmostEqual(got["quadratic_light_time_s"],
                               linear["light_time_s"], delta=1e-14)
        self.assertLess(got["quadratic_vs_linear_angle_arcsec"], 1e-9)
        self.assertEqual(got["second_order_acceleration_displacement_m"], 0.)

    def test_acceleration_changes_oblique_ray_at_microarcsecond_scale(self):
        got = quadratic_central_gravity_light_time(self.r, self.v, self.s)
        self.assertGreater(got["quadratic_vs_linear_angle_arcsec"], 1e-6)
        self.assertLess(got["quadratic_vs_linear_angle_arcsec"], 1e-3)
        self.assertLess(abs(got["quadratic_light_time_equation_residual_km"]),
                        1e-8)
        self.assertGreater(got["second_order_acceleration_displacement_m"], 0.)
        self.assertEqual(got["historical_holdout"], "NOT_RUN")
        self.assertIsNone(got["historical_impact_inference"])

    def test_equation_residual_and_displacement_are_separately_testable(self):
        got = quadratic_central_gravity_light_time(self.r, self.v, self.s)
        tau = got["quadratic_light_time_s"]
        acc = np.asarray(got["reception_central_acceleration_km_s2"])
        line = self.r - self.v*tau + .5*acc*tau*tau - self.s
        self.assertLess(abs(np.linalg.norm(line) - 299792.458*tau), 1e-8)
        self.assertAlmostEqual(got["second_order_acceleration_displacement_m"],
                               500. * np.linalg.norm(acc)*tau*tau, places=13)
        self.assertAlmostEqual(np.linalg.norm(
            got["quadratic_retarded_line_of_sight_gcrs"]), 1., places=13)

    def test_radial_stationary_direction_remains_unchanged(self):
        got = quadratic_central_gravity_light_time(
            [7000., 0., 0.], [0., 0., 0.], [6378.137, 0., 0.])
        self.assertLess(got["quadratic_vs_linear_angle_arcsec"], 1e-9)
        self.assertGreater(got["second_order_acceleration_displacement_m"], 0.)

    def test_invalid_physics_and_long_range_fail_closed(self):
        args = (self.r, self.v, self.s)
        for gm in (-1., float("nan"), float("inf")):
            with self.subTest(gm=gm), self.assertRaises(ValueError):
                quadratic_central_gravity_light_time(*args, gm)
        with self.assertRaisesRegex(ValueError, "Outside-Earth"):
            quadratic_central_gravity_light_time([100., 0., 0.], self.v, self.s)
        with self.assertRaisesRegex(ValueError, "speed"):
            quadratic_central_gravity_light_time(self.r, [25., 0., 0.], self.s)
        with self.assertRaisesRegex(ValueError, "0.2"):
            quadratic_central_gravity_light_time([100000., 0., 0.], self.v, self.s)


if __name__ == "__main__":
    unittest.main()
