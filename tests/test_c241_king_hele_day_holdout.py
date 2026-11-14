"""Adversarial synthetic-only tests for the date-only King-Hele sensitivity."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c241_king_hele_day_holdout import (  # noqa: E402
    CUTOFFS_637, H_KM, NASA_DAY_637, assumed_utc_day_error, evaluate,
    method, rate_last_two, rate_median_three, report, secular_dadt_km_day,
    semimajor_axis_km, strict_training,
)

UTC = timezone.utc


def row(day: int, n: float, source_row: int | None = None, ecc: float = 0.0) -> dict:
    return {'epoch': datetime(1963, 10, 1, tzinfo=UTC) + timedelta(days=day),
            'mean_motion': n, 'source_row': day if source_row is None else source_row,
            'eccentricity': ecc}


class KingHeleTests(unittest.TestCase):
    def setUp(self):
        self.rows = [row(i*3, 15.0 + 0.012*i*3) for i in range(10)]

    def test_conversion_rev_day_to_rad_sec_kepler(self):
        n = 16.0
        a = semimajor_axis_km(n)
        self.assertAlmostEqual(math.sqrt(398600.4418/a**3), 2*math.pi*16/86400, 13)
        self.assertGreater(a, 6378)

    def test_decreasing_a_requires_positive_dn_dt(self):
        self.assertLess(secular_dadt_km_day(16, 0.012), 0)
        self.assertGreater(secular_dadt_km_day(16, -0.012), 0)
        self.assertEqual(secular_dadt_km_day(16, 0), 0)

    def test_negative_or_invalid_n_rejected(self):
        for n in (0, -1, math.nan, math.inf):
            with self.subTest(n=n), self.assertRaises(ValueError):
                semimajor_axis_km(n)

    def test_strict_train_before_cutoff_no_leak(self):
        cutoff = self.rows[4]['epoch']
        self.assertEqual(len(strict_training(self.rows, cutoff)), 4)
        corrupted = self.rows[:4] + [row(12, 100), *self.rows[5:]]
        self.assertEqual(rate_last_two(strict_training(self.rows, cutoff)),
                         rate_last_two(strict_training(corrupted, cutoff)))

    def test_cutoff_later_does_not_change_earlier_report(self):
        cutoff = CUTOFFS_637[0]
        baseline = evaluate(self.rows, cutoff, NASA_DAY_637, 637)
        future = self.rows + [row(40, 1000)]
        self.assertEqual(baseline, evaluate(future, cutoff, NASA_DAY_637, 637))

    def test_missing_previous_epoch_fails_closed(self):
        result = evaluate([self.rows[0]], CUTOFFS_637[0], NASA_DAY_637, 637)
        self.assertEqual(result['last_two']['status'], 'NOT_ESTIMABLE_INSUFFICIENT_PRIOR_EPOCHS')

    def test_no_future_epoch_does_not_retrofit_slope(self):
        cutoff = self.rows[3]['epoch'].isoformat()
        result = evaluate(self.rows, cutoff, NASA_DAY_637, 637)
        self.assertEqual(result['prior_catalogue_epochs'], 3)
        self.assertEqual(result['source_rows_used_for_last_two'], [3, 6])

    def test_duplicates_or_disorder_are_rejected(self):
        with self.assertRaises(ValueError):
            strict_training([self.rows[0], self.rows[0]], self.rows[3]['epoch'])
        with self.assertRaises(ValueError):
            strict_training([self.rows[1], self.rows[0]], self.rows[3]['epoch'])

    def test_nasa_day_is_censored_not_point_hour(self):
        prediction = datetime(1963, 11, 7, 12, tzinfo=UTC)
        self.assertEqual(assumed_utc_day_error(prediction, NASA_DAY_637), [-0.5, 0.5])
        with self.assertRaises(ValueError):
            assumed_utc_day_error(prediction, '1963-11-07T12:00:00')

    def test_two_H_options_are_sensitivity_not_probability(self):
        result = method(self.rows[:4], NASA_DAY_637, 'last_two')
        a, b = result['scenarios']
        self.assertEqual([s['H_eff_km_ASSUMED'] for s in result['scenarios']], list(H_KM))
        self.assertAlmostEqual(b['life_remaining_days_HEURISTIC']/a['life_remaining_days_HEURISTIC'], 1.25, 5)
        self.assertNotIn('probability', result)

    def test_perigee_not_substituted_for_semimajor_axis(self):
        base = method(self.rows[:4], NASA_DAY_637, 'last_two')
        different_eccentricities = [dict(r, eccentricity=0.80) for r in self.rows[:4]]
        self.assertEqual(base, method(different_eccentricities, NASA_DAY_637, 'last_two'))

    def test_negative_secant_does_not_claim_remaining_life(self):
        negative = [row(0, 16), row(3, 15.95)]
        result = method(negative, NASA_DAY_637, 'last_two')
        self.assertEqual(result['scenarios'], [])
        self.assertEqual(result['status'], 'NOT_ESTIMABLE_NON_DECAYING_SECANT')

    def test_median_three_is_purely_pre_cutoff(self):
        rows = [row(0, 16), row(1, 16.01), row(2, 16.02), row(3, 16.8)]
        self.assertAlmostEqual(rate_median_three(rows), 0.01)
        self.assertAlmostEqual(rate_last_two(rows), 0.78)
        self.assertIsNone(rate_median_three(rows[:3]))

    def test_report_cannot_activate_inference(self):
        payload = report({637: self.rows, 528: self.rows})
        self.assertEqual(len(payload['comparisons']), 5)
        self.assertFalse(payload['inference']['active_constraint'])
        self.assertIsNone(payload['inference']['terminal_time_sigma_hours'])
        self.assertIsNone(payload['inference']['impact_geography'])
        self.assertEqual(payload['inference']['historical_mcmc'], 'NOT_RUN')
        self.assertFalse(payload['method']['NASA_date_timezone_known'])
        self.assertTrue(all(not v['independent_terminal_time_validation']
                            for v in payload['comparisons']))

    def test_source_identity_required(self):
        with self.assertRaises(ValueError):
            report({637: self.rows})


if __name__ == '__main__':
    unittest.main()
