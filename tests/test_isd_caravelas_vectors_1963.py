"""Test meteorological direction and the limits of derived Caravelas wind vectors."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_isd_caravelas_1963 import load_snapshot
from audit_isd_caravelas_vectors_1963 import calc, check, to_uv


class VectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_snapshot()

    def test_published_manifest_and_graph(self):
        result = check()
        self.assertIsNone(result['interpretation']['numeric_constraint_on_conde_or_trajectory'])
        self.assertFalse(result['interpretation']['transfer_to_conde_calibrated'])
        self.assertIsNone(result['interpretation']['uncertainty_of_hourly_u_v'])

    def test_east_and_north_convention(self):
        u, v = to_uv(5, 90)
        self.assertAlmostEqual(u, -5)
        self.assertAlmostEqual(v, 0, places=10)
        u, v = to_uv(5, 0)
        self.assertAlmostEqual(u, 0)
        self.assertAlmostEqual(v, -5)

    def test_three_days_and_scalar_means(self):
        days = calc(self.raw)['days']
        self.assertEqual([v['rows'] for v in days.values()], [24, 24, 24])
        self.assertEqual([v['scalar_speed_mean_m_s'] for v in days.values()], [3.367, 3.367, 3.775])
        self.assertEqual([v['calm_rows'] for v in days.values()], [0, 3, 1])

    def test_calm_direction_changes_do_not_create_wind(self):
        rows = self.raw.splitlines(keepends=True)
        i = next(i for i, row in enumerate(rows) if int(row[65:69]) == 0)
        rows[i] = rows[i][:60] + b'090' + rows[i][63:]
        self.assertEqual(calc(b''.join(rows)), calc(self.raw))

    def test_reject_bad_bearing(self):
        rows = self.raw.splitlines(keepends=True)
        rows[0] = rows[0][:60] + b'999' + rows[0][63:]
        with self.assertRaisesRegex(ValueError, 'invalid wind direction'):
            calc(b''.join(rows))

    def test_reject_bad_wind_quality(self):
        rows = self.raw.splitlines(keepends=True)
        rows[0] = rows[0][:69] + b'9' + rows[0][70:]
        with self.assertRaisesRegex(ValueError, 'quality'):
            calc(b''.join(rows))

    def test_reject_bad_day_identity(self):
        rows = self.raw.splitlines(keepends=True)
        rows[0] = rows[0][:15] + b'19631110' + rows[0][23:]
        with self.assertRaisesRegex(ValueError, 'timestamp'):
            calc(b''.join(rows))

    def test_vector_magnitude_cannot_exceed_scalar_mean(self):
        for day in calc(self.raw)['days'].values():
            self.assertLessEqual(day['mean_vector_magnitude_m_s'], day['scalar_speed_mean_m_s'] + 0.001)
            self.assertGreaterEqual(day['vector_resultant_fraction_of_scalar_speed'], 0)
            self.assertLessEqual(day['vector_resultant_fraction_of_scalar_speed'], 1)


if __name__ == '__main__':
    unittest.main()
