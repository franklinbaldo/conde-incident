"""Adversarial rational witnesses of autonomous clock/epoch gauge."""
import unittest
import json
from pathlib import Path
from fractions import Fraction as F
from tools import autonomous_time_gauge as gauge


class FlowGaugeTests(unittest.TestCase):
    def setUp(self):
        self.state = ((4, -5, 7), (2, 1, -3))
        self.accel = (3, -2, 1)
        self.station = ((5, 0, -9), (2, 5, 1), (7, -1, 4))
        self.delta, self.epsilon, self.h = F(1, 3), F(2, 7), F(4, 5)
        self.shifted, self.nd, self.ne = gauge.shifted_configuration(
            self.state, self.accel, self.delta, self.epsilon, self.h)

    def line(self, state, epoch, delta, epsilon, station=None):
        return gauge.sightline(state, self.accel, station or self.station,
                               epoch, delta, epsilon)

    def test_flow_group_property_nonzero_acceleration(self):
        for t in (F(-3), F(0), F(1, 2), F(4)):
            self.assertEqual(gauge.flow(gauge.flow(self.state, self.accel, -self.h),
                                         self.accel, t+self.h),
                             gauge.flow(self.state, self.accel, t))

    def test_all_sightlines_identical_with_nonlinear_station(self):
        self.assertNotEqual(self.shifted, self.state)
        for t in (F(-3), F(0), F(1, 2), F(4)):
            self.assertEqual(self.line(self.state, t, self.delta, self.epsilon),
                             self.line(self.shifted, t, self.nd, self.ne))

    def test_arbitrary_new_station_ephemeris_still_invariant(self):
        for t in (F(0), F(3)):
            coeffs = ((17, 11, 9), (3, 2, -2), (5, 6, 7))
            self.assertEqual(self.line(self.state, t, self.delta, self.epsilon, coeffs),
                             self.line(self.shifted, t, self.nd, self.ne, coeffs))

    def test_anchor_station_epoch_breaks_this_specific_gauge(self):
        self.assertNotEqual(self.line(self.state, F(0), self.delta, self.epsilon),
                            self.line(self.shifted, F(0), self.nd, self.epsilon))

    def test_shift_delta_without_compensating_initial_state_fails(self):
        self.assertNotEqual(self.line(self.state, F(2), self.delta, self.epsilon),
                            self.line(self.state, F(2), self.nd, self.ne))

    def test_zero_shift_is_identity(self):
        self.assertEqual(gauge.shifted_configuration(self.state, self.accel,
                                                      self.delta, self.epsilon, 0),
                         (gauge.flow(self.state, self.accel, 0), self.delta, self.epsilon))

    def test_dated_forcing_breaks_three_epoch_shift(self):
        for x, v in ((0, 0), (8, -4), (F(1, 3), F(-2, 7))):
            self.assertEqual(gauge.forced_second_difference(self.h, F(3),
                                                             new_x0=x, new_v0=v),
                             F(3)*self.h)
            self.assertNotEqual(gauge.forced_second_difference(self.h, F(3),
                                                               new_x0=x, new_v0=v), 0)

    def test_dated_forcing_no_counterexample_for_zero_input(self):
        self.assertEqual(gauge.forced_second_difference(0, 3), 0)
        self.assertEqual(gauge.forced_second_difference(self.h, 0), 0)

    def test_frozen_replay_and_inactive_dependency_graph(self):
        root = Path(__file__).resolve().parents[1]
        snap = json.loads((root / "research/statistics/autonomous_time_gauge_C241.json").read_text())
        graph = json.loads((root / "research/constraints/autonomous_time_gauge_candidate_C241.json").read_text())
        self.assertEqual(snap, gauge.report())
        self.assertEqual(graph["id"], snap["id"])
        self.assertEqual(graph["source_occurrences"], [])
        self.assertFalse(graph["historic_constraint_active"])
        self.assertEqual(graph["historical_mcmc"], "NOT_RUN")
        self.assertGreaterEqual(len(graph["dependency_edges"]), 6)

    def test_not_reported_as_historical_inference(self):
        r = gauge.report()
        self.assertEqual(r["classification"], "EXACT_CONDITIONAL_STRUCTURAL_ONLY")
        self.assertFalse(r["active_historical_constraint"])
        self.assertEqual(r["historical_mcmc"], "NOT_RUN")
        self.assertTrue(all(r["witness"]["sightlines_identical_exactly"]))


if __name__ == "__main__":
    unittest.main()
