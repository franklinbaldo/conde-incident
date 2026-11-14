"""Synthetic adversarial tests of the gate and forecast, not 1963 evidence."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c241_637_regime_holdout as m


def sample(day, n, raan=275.0, sat=637):
    return {'norad':sat,'source_row':day, 'intl_designator':'63035  A',
            'epoch':datetime(1963,10,1,tzinfo=timezone.utc)+timedelta(days=day),
            'mean_motion':n,'raan':raan,'inclination':81.86,
            'eccentricity':.001,'mean_motion_dot':0.0}


class TestLowPerigeeControl(unittest.TestCase):
    def test_source_integrity_guard(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'false.parquet'
            path.write_bytes(b'PAR1fakePAR1')
            with self.assertRaisesRegex(ValueError,'SHA mismatch'):
                m.extract_pinned(path)

    def test_kepler_proxy_must_not_be_an_observed_altitude(self):
        origin={**sample(0,16.27407972), 'eccentricity':0.0000115}
        self.assertGreater(m.perigee_proxy_km(origin),195)
        self.assertLess(m.perigee_proxy_km(origin),205)
        self.assertLess(m.rate_j2_deg_day(origin),0)

    def test_no_future_leakage(self):
        prev,origin,target=sample(0,16),sample(2,16.1),sample(5,16.21)
        original=m.choose_pairs([prev,origin,target],m.WINDOWS['short'])
        tampered={**target,'mean_motion':17.21,'raan':5.0}
        updated=m.choose_pairs([prev,origin,tampered],m.WINDOWS['short'])
        self.assertEqual(len(original),1)
        self.assertAlmostEqual(updated[0]['signed_errors']['n_last_secant_rev_day']-
                               original[0]['signed_errors']['n_last_secant_rev_day'],1.0)
        self.assertAlmostEqual(m.wrap(updated[0]['signed_errors']['raan_j2_deg']-
                                      original[0]['signed_errors']['raan_j2_deg']),90.0)

    def test_predicted_epoch_must_really_be_in_future_window(self):
        rows=[sample(0,16),sample(2,16.1),sample(10,16.2)]
        self.assertEqual(m.choose_pairs(rows,m.WINDOWS['short']),[])
        self.assertEqual(m.summary([])['unique_future_epochs'],0)

    def test_duplicate_or_disorder_rejected(self):
        rows=[sample(0,16),sample(2,16.1),sample(2,16.1)]
        with self.assertRaisesRegex(ValueError,'unordered/duplicate'):
            m.choose_pairs(rows,m.WINDOWS['short'])

    def test_nearest_horizon_uses_time_not_future_values(self):
        rows=[sample(0,16),sample(2,16.1),sample(12,16.3),sample(15,16.4)]
        result=m.choose_pairs(rows,m.WINDOWS['twelve_day'])
        self.assertEqual(len(result),1)
        self.assertTrue(result[0]['target_utc'].startswith('1963-10-16'))

    def test_invalid_horizon_and_silent_independence(self):
        with self.assertRaises(ValueError):
            m.choose_pairs([],(-1,5,3))
        self.assertEqual(m.wrap(359),-1)
        self.assertEqual(m.wrap(-359),1)
        self.assertEqual(m.summary([])['pairs_not_independent'],0)


if __name__=='__main__':unittest.main()
