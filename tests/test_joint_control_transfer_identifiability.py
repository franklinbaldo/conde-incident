"""Counterexamples to unsupported transfer from sibling satellite controls."""
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from joint_control_transfer_identifiability import (  # noqa: E402
    build, basis, dot, estimable, observations, row,
)


class JointControlsTests(unittest.TestCase):
    def test_baseline_unidentified_target(self):
        obj = build()
        x = obj['scenarios']['baseline']
        self.assertEqual((x['training_rows'], x['rank'], x['unknown_columns']), (8, 8, 10))
        self.assertFalse(x['terminal_528_row_estimable'])

    def test_arbitrarily_more_control_rows_do_not_identify_missing_body(self):
        base = observations()
        other_rows = [row(obj, Fraction(k, 7)) for obj in (527, 529)
                      for k in range(3, 80)]
        self.assertFalse(estimable(base + other_rows, row(528, Fraction(3))))

    def test_missing_body_witness_constructive(self):
        v = tuple(Fraction(-1, 2) if i == 4 else Fraction(1) if i == 5
                  else Fraction(0) for i in range(10))
        self.assertTrue(all(dot(x, v) == 0 for x in observations()))
        self.assertEqual(dot(row(528, Fraction(3)), v), 3)

    def test_shared_gauge_survives_hypothetical_third_528(self):
        v = tuple(Fraction(-1) if i in (2, 5, 8) else
                  Fraction(1) if i == 9 else Fraction(0) for i in range(10))
        for obj in (527, 528, 529):
            for t in range(8):
                self.assertEqual(dot(row(obj, Fraction(t)), v), 0)

    def test_additional_528_epoch_changes_what_is_estimable(self):
        self.assertTrue(estimable(observations() + [row(528, Fraction(2))],
                                  row(528, Fraction(3))))
        self.assertFalse(build()['scenarios']['additional_control_after_missing_body']
                         ['terminal_528_row_estimable'])

    def test_calibrating_only_control_curvature_not_enough(self):
        self.assertFalse(estimable(observations() + [basis(2)], row(528, Fraction(3))))
        self.assertTrue(estimable(observations() + [basis(9), basis(5)],
                                  row(528, Fraction(3))))

    def test_reject_invalid_object_time_and_vector(self):
        for obj in (526, 530, '528', True):
            with self.assertRaises(ValueError):
                row(obj, Fraction(1))
        for t in (1, 1.0, -1, Fraction(-1, 2)):
            with self.assertRaises(ValueError):
                row(528, t)
        with self.assertRaises(ValueError):
            dot((Fraction(0),), basis(0))
        with self.assertRaises(ValueError):
            estimable([], basis(0))

    def test_no_mcmc_or_historical_probability(self):
        data = build()
        self.assertEqual(data['source_context']['historical_observations_loaded'], 0)
        self.assertEqual(data['decision']['historical_mcmc'], 'NOT_RUN')
        self.assertFalse(data['decision']['active_constraint'])
        self.assertEqual(data['decision']['geographic_exclusion'], 'NOT_AUTHORIZED')

    def test_replay(self):
        actual = (json.dumps(build(), sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()
        expected = (ROOT/'research/statistics/joint_control_transfer_identifiability_C241.json').read_bytes()
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
