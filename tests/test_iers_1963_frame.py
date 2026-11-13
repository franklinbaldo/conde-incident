"""Reference and adversarial tests for the G48 IAU2000A daily GCRS/ITRS frame."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest

import erfa

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from iers_1963_frame import EOP, TIME, build, mul, orthogonality_error  # noqa: E402


class G48Iau2000a(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.eop = json.loads((ROOT / EOP).read_text())
        cls.times = json.loads((ROOT / TIME).read_text())

    def test_authoritative_sofa_c2t00a_vector_not_internal_roundtrip(self):
        # SOFA t_sofa_c.c test_c2t00a, independently published expected matrix.
        matrix = erfa.c2t00a(2400000.5, 53736.0, 2400000.5, 53736.0,
                              2.55060238e-7, 1.860359247e-6)
        expected = [[-0.1810332128307182668, 0.9834769806938457836, 0.00006555535638688341725],
                    [-0.9834768134135984552, -0.1810332203649520727, 0.0005749801116141056317],
                    [0.0005773474014081406921, 0.00003961832391770163647, 0.9999998325501692289]]
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(matrix[i][j], expected[i][j], delta=1e-12)

    def test_documented_daily_epochs_and_orthogonality(self):
        report = build(self.eop, self.times)
        self.assertEqual([x['mjd'] for x in report['daily_00_utc_only']], [38340,38341,38342])
        for row in report['daily_00_utc_only']:
            matrix = row['gcrs_to_itrs']
            self.assertLess(orthogonality_error(matrix), 1e-12)
            self.assertEqual(matrix[0], row['itrs_x_axis_in_gcrs'])
            self.assertEqual(matrix[2], row['itrs_pole_axis_in_gcrs'])
            cartesian = [6300.0, -1200.0, 1500.0]
            transformed = mul(matrix, cartesian)
            recovered = [sum(matrix[k][i]*transformed[k] for k in range(3)) for i in range(3)]
            self.assertLess(math.dist(cartesian, recovered), 1e-8)
        self.assertEqual(report['limitations']['holdout_527_529'], 'NOT_RUN')
        self.assertIsNone(report['limitations']['impact_location_or_probability'])

    def test_utc_and_tt_must_be_distinct(self):
        from iers_1963_frame import matrix_at_epoch
        a, b = self.eop['sample'][1], self.times['rows_at_00_utc'][1]
        true_m = matrix_at_epoch(a, b)
        wrong = dict(b, tt_minus_utc_s=0.0)
        wrong_m = matrix_at_epoch(a, wrong)
        self.assertGreater(abs(true_m[0][2] - wrong_m[0][2]), 1e-11)

    def test_wrong_earth_rotation_clock_changes_orientation(self):
        from iers_1963_frame import matrix_at_epoch
        a, b = self.eop['sample'][1], self.times['rows_at_00_utc'][1]
        m = matrix_at_epoch(a, b)
        bad_eop = dict(a, ut1_minus_utc_s=a['ut1_minus_utc_s'] + 1.0)
        wrong = matrix_at_epoch(bad_eop, b)
        self.assertGreater(math.dist(mul(m, [6378.137, 0, 0]),
                                     mul(wrong, [6378.137, 0, 0])), 0.4)

    def test_wrong_polar_motion_is_detectable(self):
        from iers_1963_frame import matrix_at_epoch
        a, b = self.eop['sample'][1], self.times['rows_at_00_utc'][1]
        m = matrix_at_epoch(a, b)
        missing = matrix_at_epoch(dict(a, x_arcsec=0, y_arcsec=0), b)
        self.assertGreater(math.dist(mul(m, [0,0,6378.137]),
                                     mul(missing, [0,0,6378.137])), 0.001)

    def test_rejects_g46_g47_incompatible_or_forged_sources(self):
        for key, value in [('ut1_minus_utc_s', 1.0), ('dX_arcsec', 0.0), ('mjd', 1)]:
            tampered = copy.deepcopy(self.eop)
            tampered['sample'][1][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                build(tampered, self.times)
        tampered = copy.deepcopy(self.times)
        tampered['rows_at_00_utc'][1]['tai_minus_utc_s'] = 37.0
        with self.assertRaises(ValueError):
            build(self.eop, tampered)
        tampered = copy.deepcopy(self.eop)
        tampered['source']['sha256'] = '0'*64
        with self.assertRaises(ValueError):
            build(tampered, self.times)

    def test_output_never_claims_teme_or_norad_measurements(self):
        report = build(self.eop, self.times)
        self.assertEqual(report['classification'], 'RETROSPECTIVE_GCRS_TO_ITRS_FRAME_NOT_NORAD_TRACKING')
        self.assertEqual(report['limitations']['TEME_to_GCRS_or_ITRS'], 'NOT_IMPLEMENTED')
        self.assertEqual(report['limitations']['dX_dY'], 'UNAVAILABLE_NOT_ASSUMED_MEASURED_ZERO')


if __name__ == '__main__':
    unittest.main()
