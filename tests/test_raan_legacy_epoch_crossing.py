"""Adversarial controls for catalog epoch interpolation, not tracking accuracy."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from raan_legacy_epoch_crossing import arc, pair_crossing, audit, secondary_interpolation_control
from cross_object_epoch_support import FIELDS


def row(n, angle, seconds, src):
    state=['0']*len(FIELDS)
    state[FIELDS.index('raan')]=str(angle)
    return {'epoch':datetime(1963,8,12,tzinfo=timezone.utc)+timedelta(seconds=seconds),
            'state':state,'source_rows':[src]}


class EpochCrossingControls(unittest.TestCase):
    def test_crossing_interpolation_requires_both_epochs(self):
        x=pair_crossing(row(528,290,0,1),row(528,280,86400,2))
        self.assertAlmostEqual(x['fraction'],0.5848,places=4)
        self.assertEqual(x['start_source_rows'],[1])
        self.assertEqual(x['end_source_rows'],[2])

    def test_no_crossing_outside_arc(self):
        self.assertIsNone(pair_crossing(row(528,300,0,1),row(528,290,86400,2)))
        self.assertIsNone(pair_crossing(row(528,260,0,1),row(528,240,86400,2)))

    def test_circular_wraparound(self):
        self.assertAlmostEqual(arc(350,10),20)
        self.assertIsNotNone(pair_crossing(row(528,350,0,1),row(528,10,86400,2),0))
        self.assertIsNone(pair_crossing(row(528,350,0,1),row(528,10,86400,2),200))

    def test_ambiguity_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'half-circle'):
            pair_crossing(row(528,0,0,1),row(528,180,86400,2),90)
        with self.assertRaisesRegex(ValueError,'non-increasing'):
            pair_crossing(row(528,290,86400,1),row(528,280,0,2))
        with self.assertRaisesRegex(ValueError,'nonfinite'):
            pair_crossing(row(528,float('nan'),0,1),row(528,280,86400,2))

    def test_two_sided_control_measures_error_not_sensor_sigma(self):
        rows=[row(528,290,0,1),row(528,285,43200,2),row(528,280,86400,3)]
        x=secondary_interpolation_control(rows)
        self.assertEqual(x['n'],1)
        self.assertAlmostEqual(x['interpolation_mae_deg'],0.)
        self.assertAlmostEqual(x['nearest_catalogue_mae_deg'],5.)
        self.assertIn('NOT_FORWARD',x['method'])

    def test_excessive_interpolation_gap_not_scored(self):
        rows=[row(528,290,0,1),row(528,285,86400*20,2),row(528,280,86400*40,3)]
        x=secondary_interpolation_control(rows)
        self.assertEqual(x['n'],0)
        self.assertEqual(x['interpolation_mae_deg'],'NOT_EVALUABLE')

    def test_duplicate_source_is_not_epoch(self):
        with self.assertRaisesRegex(ValueError,'incorrect unique'):
            audit({527:[row(527,300,0,1)],528:[row(528,290,0,2)],529:[row(529,280,0,3)]})

if __name__=='__main__': unittest.main()
