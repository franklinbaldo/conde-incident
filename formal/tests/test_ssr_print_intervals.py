"""C241-P8: rounding changes catalogued intervals, never orbital inference."""
import copy
import json
from pathlib import Path
import unittest
from formal.scripts.compile_ssr_print_intervals import intervals, render_lean

ROOT = Path(__file__).resolve().parents[2]
APR = json.loads((ROOT / 'research/tle_custody/nasa_ssr_apr_oct_1963_C241-L16.json').read_text())
OCT = json.loads((ROOT / 'research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json').read_text())


class PeriodIntervalTests(unittest.TestCase):
    def test_disjoint_period_intervals_not_inferred_orbit(self):
        report = intervals(APR, OCT)
        rows = report['objects']
        self.assertEqual([r['conditional_april_minus_october_centiminutes'] for r in rows],
                         [[-10, 10], [160, 180], [90, 110]])
        self.assertEqual([r['printed_period_change_robust_to_nearest_tenth_rounding'] for r in rows],
                         [False, True, True])
        self.assertEqual([r['printed_apogee_delta_oct_minus_apr_km'] for r in rows],
                         [-6, -104, -73])
        self.assertEqual(report['physical_domain_change'], 'NONE_NO_HISTORICAL_EPOCH_OR_INSTRUMENT_SIGMA')
        self.assertTrue(all(r['observed_epoch'] is None and r['measured_decay_rate'] is None
                            for r in rows))
        self.assertIn('omega', render_lean(report))

    def test_all_printed_number_mutations_fail_closed(self):
        for designator_index in range(3):
            apr = copy.deepcopy(APR)
            apr['april_rows'][designator_index]['nodal_period_min'] = '00.0'
            with self.subTest(designator=designator_index), self.assertRaises(ValueError):
                intervals(apr, OCT)
            octo = copy.deepcopy(OCT)
            octo['catalog_rows'][designator_index]['nodal_period_min_printed'] = '00.0'
            with self.subTest(designator=designator_index), self.assertRaises(ValueError):
                intervals(APR, octo)

    def test_no_false_tracking_epoch_or_instrument_sigma(self):
        for key, value in [('date_is_orbital_epoch', True), ('delta_is_time_derivative', True),
                           ('sigma', 0.01), ('terminal_time', '1963-11-08T00:00Z')]:
            apr = copy.deepcopy(APR)
            apr['limits'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                intervals(apr, OCT)


if __name__ == '__main__':
    unittest.main()
