"""Adversarial geometry checks; no real 1963 instrument data are asserted."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from optical_parallax_identifiability import assess_geometry  # noqa: E402


class OpticalParallaxTests(unittest.TestCase):
    def test_one_station_never_observes_range(self):
        for target in ((0, 1, 0), (1, 1, 100), (0, 0, 9000)):
            self.assertEqual(assess_geometry((0, 0, 0), (10, 0, 0), target)
                             ['one_station_rank'], 2)

    def test_distinct_station_positions_can_still_be_collinear(self):
        for pair in (((-1, 0, 0), (1, 0, 0), (0, 0, 0)),
                     ((0, 0, 0), (0, 0, 10), (0, 0, 100)),
                     ((0, 0, 0), (0, 0, 0), (0, 0, 100))):
            x = assess_geometry(*pair)
            self.assertEqual(x['two_station_structural_rank'], 2)
            self.assertIsNone(x['angular_jacobian_condition'])
            self.assertEqual(x['squared_singular_values_per_km2'][0], 0)

    def test_two_nonparallel_sightlines_recover_three_local_components(self):
        r = assess_geometry((0, 0, 0), (1, 0, 0), (0, 1, 0))
        self.assertEqual(r['two_station_structural_rank'], 3)
        self.assertAlmostEqual(r['parallax_angle_deg'], 45)
        eigen = r['squared_singular_values_per_km2']
        self.assertTrue(0 < eigen[0] <= eigen[1] <= eigen[2])

    def test_exact_right_angle_and_equal_ranges_have_expected_spectrum(self):
        r = assess_geometry((0, 1, 0), (1, 0, 0), (0, 0, 0))
        self.assertEqual(r['two_station_structural_rank'], 3)
        for observed, expected in zip(r['squared_singular_values_per_km2'], (1, 1, 2)):
            self.assertAlmostEqual(observed, expected)
        self.assertAlmostEqual(r['angular_jacobian_condition'], math.sqrt(2))

    def test_near_parallel_geometry_is_weak_without_sigma_claim(self):
        near = assess_geometry((0, 0, 0), (1, 0, 0), (0, 0, 100000))
        far = assess_geometry((0, 0, 0), (1, 0, 0), (0, 0, 1000000))
        self.assertEqual(near['two_station_structural_rank'], 3)
        self.assertGreater(far['angular_jacobian_condition'],
                           near['angular_jacobian_condition'] * 9)
        self.assertIsNone(near['sensor_covariance'])
        self.assertEqual(far['historical_mcmc'], 'NOT_RUN')

    def test_common_translation_does_not_change_design(self):
        points = ((1, 2, 3), (2, 2, 3), (1, 3, 20))
        original = assess_geometry(*points)
        shift = (90, -31, 12)
        shifted = assess_geometry(*(tuple(x+y for x, y in zip(v, shift))
                                    for v in points))
        self.assertAlmostEqual(original['angular_jacobian_condition'],
                               shifted['angular_jacobian_condition'])
        self.assertAlmostEqual(original['parallax_angle_deg'],
                               shifted['parallax_angle_deg'])

    def test_scaling_changes_sensitivity_not_condition(self):
        points = ((0, 0, 0), (1, 0, 0), (0, 0, 10))
        original = assess_geometry(*points)
        scaled = assess_geometry(*(tuple(10*x for x in v) for v in points))
        self.assertAlmostEqual(original['angular_jacobian_condition'],
                               scaled['angular_jacobian_condition'])
        for x, y in zip(original['squared_singular_values_per_km2'],
                        scaled['squared_singular_values_per_km2']):
            self.assertAlmostEqual(x/100, y)

    def test_reject_invalid_vectors_and_coincident_targets(self):
        valid = ((0, 0, 0), (1, 0, 0), (0, 0, 1))
        for v in ((0, 0), ('1', 0, 0), (True, 0, 0),
                  (math.nan, 0, 0), (math.inf, 0, 0)):
            with self.assertRaises(ValueError):
                assess_geometry(v, *valid[1:])
        with self.assertRaises(ValueError):
            assess_geometry((0, 0, 0), (0, 0, 1), (0, 0, 0))

    def test_no_historical_authentication_even_if_rank_three(self):
        r = assess_geometry((0, 0, 0), (1, 0, 0), (0, 0, 2))
        self.assertEqual(r['instrument_authentication'], 'NOT_ASSESSED')
        self.assertEqual(r['impact_inference'], 'NOT_SUPPORTED')
        self.assertIsNone(r['physical_orbit_model'])


if __name__ == '__main__':
    unittest.main()
