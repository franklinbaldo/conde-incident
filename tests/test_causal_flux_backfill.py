"""Offline adversarial tests for candidate causal flux backfill and status guards."""
import copy
import datetime as dt
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_causal_flux_backfill import (  # noqa: E402
    SOURCE, audit_bytes_causal, causal_window,
)


class CausalFluxBackfillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(SOURCE.read_text())
        cls.rows = audit_bytes_causal(SOURCE.read_bytes())['rows']

    def mutated(self, change):
        doc = copy.deepcopy(self.original)
        change(doc)
        return json.dumps(doc).encode()

    def test_real_extract_missing_dates_are_not_hidden(self):
        for row, day, first, missing, observed in zip(
            self.rows, ('07', '08', '09'), ('18', '19', '20'), (40, 39, 38), (41, 42, 43)
        ):
            self.assertEqual(row['model_evaluation_utc_not_event_time'], f'1963-11-{day}T12:00:00Z')
            self.assertEqual(row['required_window']['first'], f'1963-08-{first}')
            self.assertEqual(row['required_window']['last'], f'1963-11-{int(day)-1:02}')
            self.assertEqual(row['missing_dates_in_pinned_extract'], missing)
            self.assertEqual(row['observed_dates_in_pinned_extract'], observed)
            self.assertEqual(row['missing_first'], f'1963-08-{first}')
            self.assertEqual(row['missing_last'], '1963-09-26')
            self.assertEqual(missing + observed, 81)
            self.assertIsNone(row['candidate_mean_sfu'])
            self.assertFalse(row['complete_candidate_mean_computable'])
            self.assertFalse(row['prospective_driver_eligible'])
            self.assertFalse(row['historical_release_timestamp_audited'])
            self.assertFalse(row['standard_centered_f107a_replaced'])
            self.assertFalse(row['historical_trajectory_constraint_active'])

    def test_epoch_window_excludes_unknown_current_day(self):
        dates = causal_window(dt.datetime(1963, 11, 8, 12, tzinfo=dt.timezone.utc))
        self.assertEqual(len(dates), 81)
        self.assertEqual(len(set(dates)), 81)
        self.assertLess(max(dates), dt.date(1963, 11, 8))
        self.assertNotIn(dt.date(1963, 11, 8), dates)

    def test_non_utc_and_incomplete_intraday_rejected(self):
        for epoch in (dt.datetime(1963, 11, 8, 12, tzinfo=dt.timezone(dt.timedelta(hours=1))),
                      dt.datetime(1963, 11, 8, 11, tzinfo=dt.timezone.utc)):
            with self.assertRaises(ValueError):
                causal_window(epoch)

    def test_backfill_completion_is_not_release_calibration(self):
        # Inject all absent dates from a synthetic source; this never certifies
        # a real source or as-of availability, and changes the snapshot hash.
        def patch(doc):
            data = doc['raw_series']['F107_observed_daily']
            for row in self.rows:
                day = dt.date.fromisoformat(row['missing_first'])
                last = dt.date.fromisoformat(row['missing_last'])
                while day <= last:
                    data[day.isoformat()] = {'observed_sfu': 100.0}
                    day += dt.timedelta(days=1)
        rows = audit_bytes_causal(self.mutated(patch))['rows']
        self.assertTrue(all(x['complete_candidate_mean_computable'] for x in rows))
        self.assertTrue(all(x['candidate_mean_sfu'] is not None for x in rows))
        self.assertTrue(all(not x['prospective_driver_eligible'] for x in rows))

    def test_source_mutation_caught_by_parent_audit(self):
        with self.assertRaisesRegex(ValueError, 'centered F107A mismatch'):
            audit_bytes_causal(self.mutated(lambda d: d['raw_series']['F107_observed_daily']
                ['1963-12-18'].__setitem__('observed_sfu', 999.0)))

    def test_certificate_replay(self):
        run = subprocess.run([sys.executable, 'tools/audit_causal_flux_backfill.py', '--check'],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main()
