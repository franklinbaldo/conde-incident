"""Synthetic exact-rational adversarial tests; no orbit or instrument asserted."""
from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from optical_temporal_observability import (  # noqa: E402
    assess, bearing_matrix, projector, rank, report, witness,
)


class OpticalTemporalTests(unittest.TestCase):
    X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)

    def test_one_bearing(self):
        self.assertEqual(assess(((0, self.X),))["rank_of_six_state_columns"], 2)

    def test_simultaneous_stereo_identifies_position_not_velocity(self):
        r = assess(((0, self.X), (0, self.Y)))
        self.assertEqual((r["rank_of_six_state_columns"],
                          r["unidentified_initial_position_dimensions"],
                          r["unidentified_velocity_dimensions"]), (3, 0, 3))

    def test_two_asynchronous_stereo_is_not_triangulation(self):
        r = assess(((0, self.X), (1, self.Y)))
        self.assertEqual((r["rank_of_six_state_columns"], r["nullity"],
                          r["unidentified_initial_position_dimensions"],
                          r["unidentified_velocity_dimensions"]), (4, 2, 1, 2))

    def test_explicit_range_ambiguity_witness(self):
        a, b = witness(100, 100), witness(200, 300)
        self.assertNotEqual(a["initial_position"], b["initial_position"])
        for w in (a, b):
            r0 = w["initial_position"]
            v = w["constant_velocity_per_time_unit"]
            p0 = tuple(r0[i]-w["first_station"][i] for i in range(3))
            p1 = tuple(r0[i]+v[i]-w["second_station"][i] for i in range(3))
            self.assertEqual(p0, tuple(w["ranges"][0]*x for x in w["first_line_of_sight"]))
            self.assertEqual(p1, tuple(w["ranges"][1]*x for x in w["second_line_of_sight"]))

    def test_three_orthogonal_epochs_full_rank_only_conditional(self):
        r = assess(((0, self.X), (1, self.Y), (2, self.Z)))
        self.assertEqual((r["rank_of_six_state_columns"], r["nullity"]), (6, 0))

    def test_three_collinear_epochs_keep_two_directions_unobserved(self):
        r = assess(((0, self.X), (1, self.X), (2, self.X)))
        self.assertEqual((r["rank_of_six_state_columns"], r["nullity"]), (4, 2))

    def test_one_stereo_epoch_plus_later_is_rank_five(self):
        r = assess(((0, self.X), (0, self.Y), (1, self.Z)))
        self.assertEqual((r["rank_of_six_state_columns"],
                          r["unidentified_velocity_dimensions"]), (5, 1))

    def test_two_stereo_epochs_are_rank_six(self):
        r = assess(((0, self.X), (0, self.Y), (1, self.Y), (1, self.Z)))
        self.assertEqual(r["nullity"], 0)

    def test_nonunit_rational_directions_do_not_change_rank(self):
        self.assertEqual(projector((3, 0, 0)), projector(self.X))
        self.assertEqual(projector((2, 2, 0)), projector((1, 1, 0)))
        a = ((0, self.X), (Fraction(1, 2), self.Y), (2, self.Z))
        b = ((0, (9, 0, 0)), (Fraction(1, 2), (0, 8, 0)), (2, (0, 0, 7)))
        self.assertEqual(bearing_matrix(a), bearing_matrix(b))

    def test_time_origin_shift_preserves_six_state_rank(self):
        a = ((0, self.X), (1, self.Y), (2, self.Z))
        b = tuple((t+17, direction) for t, direction in a)
        self.assertEqual(rank(bearing_matrix(a)), rank(bearing_matrix(b)))

    def test_invalid_observations_are_rejected(self):
        for observations in ((), ((0, (0, 0, 0)),), ((0.2, self.X),),
                             ((True, self.X),), ((0, (1.0, 0, 0)),),
                             ((0, (True, 0, 0)),)):
            with self.assertRaises(ValueError):
                assess(observations)
        for a, b in ((0, 2), (1, -2), (1.2, 2), (True, 2)):
            with self.assertRaises(ValueError):
                witness(a, b)

    def test_report_keeps_epistemic_gates(self):
        r = report()
        self.assertEqual(r["historical_mcmc"], "NOT_RUN")
        self.assertEqual(r["constraint_status"], "CONNECTED_PENDING_CALIBRATION")
        self.assertEqual(r["impact_inference"], "NOT_SUPPORTED")
        self.assertEqual(r["designs"]["two_asynchronous_nonparallel"]["nullity"], 2)


if __name__ == "__main__":
    unittest.main()
