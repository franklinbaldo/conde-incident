"""Synthetic exact-rational clock bias design regression tests."""
from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from optical_clock_bias_observability import (  # noqa: E402
    assess, clock_matrix, exact_vector, report,
)
from optical_temporal_observability import rank  # noqa: E402


class ClockBiasDesignTests(unittest.TestCase):
    dirs = ((0,(1,0,0)),(1,(0,1,0)),(2,(0,0,1)),(3,(1,1,1)))
    v = (2,-1,3)
    still = ((0,0,0),)*4

    def test_three_ideal_angles_have_remaining_clock_gauge(self):
        d = assess(self.dirs[:3], self.v, self.still[:3])
        self.assertEqual((d['rank_of_seven_parameters'], d['nullity'],
                          d['unidentified_clock_dimensions']), (6,1,1))
        self.assertEqual(d['unidentified_velocity_dimensions'], 0)
        self.assertEqual(d['unidentified_position_dimensions'], 1)

    def test_fourth_stationary_angle_does_not_break_gauge(self):
        d = assess(self.dirs, self.v, self.still)
        self.assertEqual((d['rank_of_seven_parameters'], d['nullity']), (6,1))

    def test_calibrated_transverse_observer_motion_breaks_local_gauge(self):
        motion = self.still[:3] + ((1,0,0),)
        d = assess(self.dirs, self.v, motion)
        self.assertEqual((d['rank_of_seven_parameters'], d['nullity']), (7,0))
        self.assertEqual(d['unidentified_clock_dimensions'], 0)
        self.assertEqual(d['unidentified_position_dimensions'], 0)

    def test_radial_observer_motion_cannot_fix_clock(self):
        motion = self.still[:3] + ((1,1,1),)
        self.assertEqual(assess(self.dirs, self.v, motion)['nullity'],1)

    def test_exact_column_gauge_is_velocity_projection(self):
        a = clock_matrix(self.dirs, self.v, self.still)
        self.assertTrue(all(row[-1] == sum(row[j]*self.v[j] for j in range(3)) for row in a))
        self.assertEqual(rank(a), rank([row[:6] for row in a]))

    def test_finite_gauge_witness_not_just_jacobian(self):
        r0=(Fraction(3),Fraction(5),Fraction(7))
        v=tuple(map(Fraction,self.v))
        delta=Fraction(1,3)
        shift=Fraction(7,5)
        # Fixed stations, and arbitrary reported epochs: two different
        # absolute-clock/absolute-position states predict identical rays.
        r0prime=tuple(r0[j]-v[j]*shift for j in range(3))
        for t in (0,1,2,3):
            p=tuple(r0[j]+v[j]*(t+delta) for j in range(3))
            q=tuple(r0prime[j]+v[j]*(t+delta+shift) for j in range(3))
            self.assertEqual(p,q)
        self.assertNotEqual(r0,r0prime)

    def test_epoch_translation_preserves_rank(self):
        a=assess(self.dirs,self.v,self.still)
        b=assess(tuple((t+17,d) for t,d in self.dirs),self.v,self.still)
        self.assertEqual(a['rank_of_seven_parameters'],b['rank_of_seven_parameters'])

    def test_exact_rational_inputs_not_float_guesses(self):
        self.assertEqual(exact_vector((Fraction(1,2),0,1)),(Fraction(1,2),Fraction(0),Fraction(1)))
        for bad in ((1,2),(1,2,3,4),(1.0,2,3),(True,2,3),"123"):
            with self.assertRaises(ValueError):
                exact_vector(bad)
        for inputs in (((),self.v,()),
                       (self.dirs,self.v,self.still[:3]),
                       (((0.1,(1,0,0)),),self.v,((0,0,0),)),
                       (((True,(1,0,0)),),self.v,((0,0,0),)),
                       (((0,(0,0,0)),),self.v,((0,0,0),))):
            with self.assertRaises(ValueError):
                assess(*inputs)

    def test_report_preserves_historical_gates(self):
        d=report()
        self.assertEqual(d['designs']['four_one_transverse_motion']['rank_of_seven_parameters'],7)
        self.assertEqual(d['designs']['four_one_radial_motion']['rank_of_seven_parameters'],6)
        self.assertEqual(d['historical_mcmc'],'NOT_RUN')
        self.assertEqual(d['historical_geography'],'NOT_CONSTRAINED')


if __name__=='__main__':
    unittest.main()
