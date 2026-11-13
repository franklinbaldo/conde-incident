"""Adversarial checks of 1963-Nov historical UTC rates and IERS LOD relation."""
import json
from pathlib import Path
import sys
import unittest
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from iers_1963_timescales import (  # noqa: E402
    DAYS, OUTPUT, UTC_RATE_S_PER_DAY, tai_minus_utc, earth_rotation_angle_iau2000,
)
from iers_1963_eop import SHA256  # noqa: E402


class TimescalesG47(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((ROOT / OUTPUT).read_text())

    def test_original_eop_source_binding(self):
        self.assertEqual(self.report['sources']['iers_eop']['sha256'], SHA256)
        self.assertEqual(self.report['sources']['iers_eop']['original_rows'], 365)
        self.assertEqual(self.report['sources']['tai_utc_definition']['rate_s_per_day'], 0.0011232)

    def test_1963_nov_8_official_offset(self):
        self.assertEqual(tai_minus_utc(38341), Decimal('2.7051412'))
        self.assertEqual(tai_minus_utc(38340), Decimal('2.7040180'))
        self.assertEqual(tai_minus_utc(38342), Decimal('2.7062644'))

    def test_era_specific_utc_clause_limits(self):
        self.assertEqual(tai_minus_utc(38334), Decimal('2.6972788'))
        for value in (38333, 38395, 0, -1, 20261108, 38341.0, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                tai_minus_utc(value)

    def test_three_real_epochs_and_correct_time_scales(self):
        rows = self.report['rows_at_00_utc']
        self.assertEqual([r['utc'][:10] for r in rows], list(DAYS))
        self.assertEqual([r['mjd'] for r in rows], [38340, 38341, 38342])
        self.assertAlmostEqual(rows[1]['tt_minus_utc_s'], 34.8891412, places=7)
        self.assertAlmostEqual(rows[1]['ut1_minus_tai_s'], -2.7425264, places=7)
        self.assertAlmostEqual(rows[1]['jd_part2_tt'] - 38341, 34.8891412/86400, places=10)
        self.assertAlmostEqual(rows[1]['jd_part2_ut1'] - 38341, -0.0373852/86400, places=10)
        self.assertEqual(rows[1]['jd_part1'], 2400000.5)

    def test_iau2000_era_against_published_sofa_reference(self):
        # Public SOFA era00(2400000.5, 54388.0) example (not derived from G47).
        self.assertAlmostEqual(earth_rotation_angle_iau2000(
            Decimal('2400000.5'), Decimal('54388.0')),
            0.40228372400281165, delta=2e-11)
        for row in self.report['rows_at_00_utc']:
            self.assertGreaterEqual(row['era_iau2000_rad'], 0)
            self.assertLess(row['era_iau2000_rad'], 6.283185307179587)

    def test_era_uses_real_dut1_not_utc_as_ut1(self):
        row = self.report['rows_at_00_utc'][1]
        raw = earth_rotation_angle_iau2000(Decimal('2400000.5'),
                                           Decimal(row['mjd']))
        self.assertGreater(abs(raw - row['era_iau2000_rad']), 1e-6)

    def test_lod_coherence_rejects_false_constant_utc(self):
        a, b = self.report['daily_lod_diagnostics']
        self.assertEqual(a['delta_tai_minus_utc_s'], float(UTC_RATE_S_PER_DAY))
        self.assertEqual(b['delta_tai_minus_utc_s'], float(UTC_RATE_S_PER_DAY))
        self.assertAlmostEqual(a['delta_ut1_minus_tai_s'], -0.0020593, places=10)
        self.assertAlmostEqual(b['delta_ut1_minus_tai_s'], -0.0021092, places=10)
        self.assertAlmostEqual(a['lod_residual_with_utc_rate_us'], -0.3, places=6)
        self.assertAlmostEqual(b['lod_residual_with_utc_rate_us'], -2.2, places=6)
        for entry in (a, b):
            self.assertGreater(abs(entry['lod_residual_without_utc_rate_us']), 1000)
            self.assertLess(abs(entry['lod_residual_with_utc_rate_us']), 3)

    def test_not_promoted_into_orbital_measurement(self):
        limits = self.report['limits']
        self.assertEqual(limits['historical_527_529_holdout'], 'NOT_RUN')
        self.assertEqual(limits['full_iau2000a_celestial_to_terrestrial_rotation'], 'NOT_IMPLEMENTED')
        self.assertIsNone(limits['impact_location_or_probability'])
        self.assertEqual(limits['daily_dut1_interpolation'], 'NOT_IMPLEMENTED')

    def test_original_source_sha_cannot_be_bypassed(self):
        from iers_1963_timescales import build
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            build(b'FORGED IERS 1963 EOP')


if __name__ == '__main__':
    unittest.main()
