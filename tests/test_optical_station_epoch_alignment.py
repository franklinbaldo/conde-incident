"""Exact rational, synthetic adversarial station-epoch tests."""
from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from optical_station_epoch_alignment import (  # noqa: E402
    alignment_matrix, assess, exact_gauge, report,
)


class StationEpochAlignmentTests(unittest.TestCase):
    observations = ((0,(1,0,0)), (1,(0,1,0)),
                    (2,(0,0,1)), (3,(1,1,1)))
    v = (2,-1,3)
    stationary = ((0,0,0),)*4
    transverse = stationary[:3]+((1,0,0),)

    def test_free_station_epoch_restores_gauge_even_with_transverse_motion(self):
        d = assess(self.observations, self.v, self.transverse)
        self.assertEqual((d["rank_of_eight_parameters"], d["nullity"]), (7,1))
        self.assertEqual(d["unidentified_target_clock_dimensions"], 1)
        self.assertEqual(d["unidentified_station_clock_dimensions"], 1)

    def test_external_epoch_calibration_breaks_gauge_conditionally(self):
        d = assess(self.observations, self.v, self.transverse,
                   station_epoch_calibrated=True)
        self.assertEqual((d["rank_of_eight_parameters"], d["nullity"]), (8,0))
        self.assertEqual(d["unidentified_target_clock_dimensions"], 0)

    def test_fixed_station_and_radial_motion_still_unidentified(self):
        a = assess(self.observations, self.v, self.stationary)
        b = assess(self.observations, self.v, self.stationary,
                   station_epoch_calibrated=True)
        radial = self.stationary[:3]+((1,1,1),)
        c = assess(self.observations, self.v, radial,
                   station_epoch_calibrated=True)
        self.assertEqual((a["rank_of_eight_parameters"], a["nullity"]), (6,2))
        self.assertEqual((b["rank_of_eight_parameters"], b["nullity"]), (7,1))
        self.assertEqual((c["rank_of_eight_parameters"], c["nullity"]), (7,1))

    def test_gauge_is_exact_for_rational_epochs_and_velocities(self):
        vel = (Fraction(1,2), Fraction(-3,5), Fraction(7,4))
        observations = tuple((Fraction(i,7),d) for i,d in self.observations)
        a = alignment_matrix(observations, vel, self.transverse)
        g = exact_gauge(vel)
        self.assertEqual(len(g), 8)
        self.assertTrue(all(sum(x*y for x,y in zip(row,g)) == 0 for row in a))

    def test_finite_nonidentifiability_not_just_linear_rank(self):
        r = (Fraction(3), Fraction(5), Fraction(7))
        v = tuple(map(Fraction, self.v))
        delta, epsilon, shift = Fraction(1,3), Fraction(-1,5), Fraction(7,11)
        rprime = tuple(r[j]-v[j]*shift for j in range(3))
        origins = ((2,4,1), (-2,0,5), (3,-1,4), (6,7,8))
        motions = ((0,0,1), (1,0,0), (0,1,0), (1,-2,0))
        for t,s,w in zip((0,1,2,3), origins, motions):
            a = tuple(r[j]+v[j]*(t+delta)-Fraction(s[j])
                      -Fraction(w[j])*(t+delta+epsilon) for j in range(3))
            b = tuple(rprime[j]+v[j]*(t+delta+shift)-Fraction(s[j])
                      -Fraction(w[j])*(t+delta+shift+epsilon-shift)
                      for j in range(3))
            self.assertEqual(a,b)
        self.assertNotEqual(r,rprime)

    def test_incorrectly_fixing_station_epoch_raises_rank(self):
        free = assess(self.observations, self.v, self.transverse)
        fixed = assess(self.observations, self.v, self.transverse,
                       station_epoch_calibrated=True)
        self.assertEqual(fixed["rank_of_eight_parameters"]
                         -free["rank_of_eight_parameters"], 1)

    def test_input_guards_inherited_from_clock_operator(self):
        with self.assertRaises(ValueError):
            assess(((Fraction(1,2),(0,0,0)),), self.v, ((0,0,0),))
        with self.assertRaises(ValueError):
            assess(self.observations, (2.0,-1,3), self.transverse)
        with self.assertRaises(ValueError):
            assess(self.observations, self.v, self.stationary[:3])

    def test_report_fail_closed_for_history(self):
        d=report()
        self.assertEqual(d["historical_mcmc"], "NOT_RUN")
        self.assertEqual(d["historical_geography"], "NOT_CONSTRAINED")
        self.assertEqual(d["historical_station_time_calibration"], "NOT_AVAILABLE")
        self.assertEqual(d["designs"]["four_transverse_free_epoch"]["nullity"],1)


if __name__ == "__main__":
    unittest.main()
