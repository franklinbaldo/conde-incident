"""Source-locked IERS 1963 earth-orientation input, no fabricated orbital fit."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from iers_1963_eop import DAYS, SHA256, parse_archive, receipt  # noqa: E402

# Verbatim data rows from official IERS 05 C04 yearly 1963 archive (2011 ed.).
ROWS = [
    '1963  11   7  38340  -0.095115  -0.012515  -0.0364491   0.0020420   0.000000   0.000000   0.030000   0.030000  0.0020000  0.0014000    0.004774    0.002000',
    '1963  11   8  38341  -0.098515  -0.011315  -0.0373852   0.0020760   0.000000   0.000000   0.030000   0.030000  0.0020000  0.0014000    0.004774    0.002000',
    '1963  11   9  38342  -0.101915  -0.010015  -0.0383712   0.0021380   0.000000   0.000000   0.030000   0.030000  0.0020000  0.0014000    0.004774    0.002000',
]


def fragment(rows=ROWS):
    return ('\n'.join(rows) + '\n').encode('ascii')


class IersEop1963Tests(unittest.TestCase):
    def test_three_real_utc_epochs_and_units(self):
        rows = parse_archive(fragment(), expected_days=3)
        self.assertEqual(tuple(sorted(rows)), DAYS)
        self.assertEqual([rows[d]['mjd'] for d in DAYS], [38340, 38341, 38342])
        self.assertEqual(rows['1963-11-08']['ut1_minus_utc_s'], -0.0373852)
        self.assertEqual(rows['1963-11-08']['x_arcsec'], -0.098515)
        self.assertEqual(rows['1963-11-08']['y_arcsec'], -0.011315)
        self.assertEqual(rows['1963-11-08']['sigma_ut1_minus_utc_s'], 0.002)

    def test_frozen_receipt_exact_values_and_epistemic_fences(self):
        report = json.loads((ROOT / 'research/constraints/iers_eop_1963_11_07_09.json').read_text())
        self.assertEqual(report['source']['sha256'], SHA256)
        self.assertEqual(report['source']['original_rows'], 365)
        rows = parse_archive(fragment(), expected_days=3)
        for entry, key in zip(report['sample'], DAYS, strict=True):
            self.assertEqual(entry['utc'], key + 'T00:00:00Z')
            self.assertEqual(entry['mjd'], rows[key]['mjd'])
            for field in ('x_arcsec', 'y_arcsec', 'ut1_minus_utc_s', 'lod_s',
                          'sigma_x_arcsec', 'sigma_y_arcsec',
                          'sigma_ut1_minus_utc_s', 'sigma_lod_s'):
                self.assertEqual(entry[field], rows[key][field])
            self.assertIsNone(entry['dX_arcsec'])
            self.assertIsNone(entry['dY_arcsec'])
            self.assertEqual(entry['celestial_pole_offsets_status'],
                             'UNAVAILABLE_NOT_ZERO_MEASUREMENT')
        limitations = report['limitations']
        self.assertFalse(limitations['can_constrain_historical_reentry'])
        self.assertEqual(limitations['independent_norad_527_529_instrumental_holdout'], 'NOT_RUN')
        self.assertIsNone(limitations['impact_location_or_probability'])
        self.assertEqual(limitations['teme_to_itrf_or_gcrs_operator'], 'NOT_IMPLEMENTED')

    def test_rejects_wrong_mjd(self):
        with self.assertRaisesRegex(ValueError, 'MJD'):
            parse_archive(fragment([ROWS[0], ROWS[1].replace('38341', '38343'), ROWS[2]]), expected_days=3)

    def test_rejects_duplicate_utc(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            parse_archive(fragment([ROWS[0], ROWS[1], ROWS[1]]), expected_days=3)

    def test_rejects_gap(self):
        with self.assertRaisesRegex(ValueError, 'Missing daily'):
            parse_archive(fragment([ROWS[0], ROWS[2]]), expected_days=2)

    def test_rejects_truncated_year(self):
        with self.assertRaisesRegex(ValueError, 'expected 365'):
            parse_archive(fragment())

    def test_rejects_nonfinite_measurement(self):
        with self.assertRaisesRegex(ValueError, 'Non-finite'):
            parse_archive(fragment([ROWS[0], ROWS[1].replace('-0.0373852', 'NaN'), ROWS[2]]), expected_days=3)

    def test_rejects_negative_formal_error(self):
        with self.assertRaisesRegex(ValueError, 'Negative formal'):
            parse_archive(fragment([ROWS[0], ROWS[1].replace('0.030000', '-0.030000', 1), ROWS[2]]), expected_days=3)

    def test_rejects_bad_date(self):
        with self.assertRaisesRegex(ValueError, 'Invalid IERS'):
            parse_archive(fragment([ROWS[0], ROWS[1].replace('11   8', ' 2  30'), ROWS[2]]), expected_days=3)

    def test_rejects_malformed_column_count(self):
        with self.assertRaisesRegex(ValueError, '16 columns'):
            parse_archive(fragment([ROWS[0], ROWS[1] + ' 999', ROWS[2]]), expected_days=3)

    def test_source_bytes_cannot_be_substituted(self):
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            receipt(fragment())

    def test_rejects_non_ascii(self):
        with self.assertRaisesRegex(ValueError, 'not ASCII'):
            parse_archive(fragment() + b'\xff', expected_days=3)


if __name__ == '__main__':
    unittest.main()
