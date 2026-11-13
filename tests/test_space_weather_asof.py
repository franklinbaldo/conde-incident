"""Adversarial offline tests for historical driver availability, not orbital likelihoods."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_space_weather_asof import SOURCE, audit_bytes  # noqa: E402


class SpaceWeatherAsOfAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(SOURCE.read_text())
        cls.result = audit_bytes(SOURCE.read_bytes())

    def mutate(self, fn):
        d = copy.deepcopy(self.original)
        fn(d)
        return json.dumps(d).encode()

    def test_all_three_are_retrospective_not_prospective(self):
        self.assertEqual(len(self.result['rows']), 3)
        self.assertEqual(self.result['prospective_score'], 'NOT_AUTHORIZED')
        self.assertEqual(self.result['retrospective_driver_status'], 'RETROSPECTIVE_INPUT_ONLY')
        self.assertEqual(self.result['prospective_driver_status'], 'PROSPECTIVE_SCORE_NOT_AUTHORIZED')
        for row in self.result['rows']:
            self.assertFalse(row['eligible_for_prospective_asof_evaluation'])
            self.assertTrue(row['eligible_for_retrospective_driver_reconstruction'])
            self.assertEqual(row['f107a_days_after_asof'], 40)
            self.assertEqual(row['ap_daily_bins_at_or_after_asof'], 4)
            self.assertIsNone(row['f107_previous_day_release_time'])
            self.assertIsNone(row['definitive_ap_kp_release_time'])
            self.assertFalse(row['physical_constraint_active'])

    def test_november_eighth_exact_window(self):
        row = self.result['rows'][1]
        self.assertEqual(row['f107a_centered_window_utc_days'],
                         {'first': '1963-09-29', 'last': '1963-12-18', 'total': 81})
        self.assertEqual(row['ap_current_bin_utc'],
                         {'start': '1963-11-08T12:00:00Z', 'end_exclusive': '1963-11-08T15:00:00Z'})

    def test_no_false_observation_time_from_source(self):
        self.assertTrue(all('model_evaluation_utc_not_event_time' in r for r in self.result['rows']))
        self.assertEqual(self.result['historical_density_and_reentry_posterior'], 'NOT_RUN')

    def test_wrong_centered_flux_rejected(self):
        with self.assertRaisesRegex(ValueError, 'centered F107A mismatch'):
            audit_bytes(self.mutate(lambda x: x['model_inputs'][1].__setitem__(
                'F107A_81day_centered_observed_sfu', 81.0)))

    def test_mutated_future_flux_rejected(self):
        with self.assertRaisesRegex(ValueError, 'centered F107A mismatch'):
            audit_bytes(self.mutate(lambda x: x['raw_series']['F107_observed_daily']['1963-12-18'].__setitem__(
                'observed_sfu', 200.0)))

    def test_mutated_daily_ap_rejected(self):
        with self.assertRaisesRegex(ValueError, 'daily Ap mismatch'):
            audit_bytes(self.mutate(lambda x: x['raw_series']['Ap'].__setitem__(
                '1963-11-08T00:00:00Z', 99)))

    def test_wrong_current_bin_rejected(self):
        with self.assertRaisesRegex(ValueError, 'current 3-hour ap mismatch'):
            audit_bytes(self.mutate(lambda x: x['model_inputs'][1]['ap_history_planetary'].__setitem__(1, 99)))

    def test_observation_epoch_is_noon_only(self):
        with self.assertRaisesRegex(ValueError, 'only has noon'):
            audit_bytes(self.mutate(lambda x: x['model_inputs'][1].__setitem__(
                'epoch_utc', '1963-11-08T09:00:00Z')))

    def test_frozen_certificate_replay(self):
        res = subprocess.run([sys.executable, 'tools/audit_space_weather_asof.py', '--check'],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)


if __name__ == '__main__':
    unittest.main()
