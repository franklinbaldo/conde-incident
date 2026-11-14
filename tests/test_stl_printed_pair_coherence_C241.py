"""Reject inference from rounded orbital table fields and unsupported promotions."""
import copy
import json
import unittest

from tools.stl_printed_pair_coherence_C241 import SOURCE, inspect, report


class STLPairCoherence(unittest.TestCase):
    def setUp(self):
        self.raw = SOURCE.read_bytes()
        self.data = json.loads(self.raw)

    def test_exact_printed_pair(self):
        r = inspect(self.data, self.raw)
        self.assertEqual(r['printed_altitude_sum'], [620, 620])
        self.assertEqual(r['printed_mean_altitude_in_printed_miles'], ['310', '310'])
        self.assertEqual(r['period_nominal_difference_first_minus_second_seconds'], '6')
        self.assertEqual(r['conditional_rounding_model']['intervals_touch_at_minutes'], '94.65')
        self.assertEqual(r['observational_design']['new_528_tracking_observations'], 0)
        self.assertFalse(r['observational_design']['active_constraint'])
        self.assertEqual(r, report())

    def invalid(self, branch, key, new):
        changed = copy.deepcopy(self.data)
        changed[branch][key] = new
        with self.assertRaises(ValueError):
            inspect(changed, self.raw)

    def test_reject_altitude_transcription_drift(self):
        self.invalid('printed_row', 'perigee_altitudes_in_printed_order', [298, 287])

    def test_reject_altitude_only_without_compensation(self):
        self.invalid('printed_row', 'apogee_altitudes_in_printed_order', [322, 333])

    def test_reject_period_change(self):
        self.invalid('printed_row', 'period_minutes_in_printed_order', [94.7, 94.7])

    def test_reject_unverified_unit(self):
        self.invalid('printed_row', 'perigee_apogee_unit_on_b12', 'km')

    def test_reject_invented_statute_mile_subtype(self):
        self.invalid('printed_row', 'mile_variant_as_printed', 'statute')

    def test_reject_sensor_promotion(self):
        changed = copy.deepcopy(self.data)
        changed['scientific_interpretation']['independent_instrumental_sensors_added'] = 1
        with self.assertRaises(ValueError):
            inspect(changed, self.raw)

    def test_reject_original_issue_promotion(self):
        changed = copy.deepcopy(self.data)
        changed['stl_original_issue_retrieved'] = True
        with self.assertRaises(ValueError):
            inspect(changed, self.raw)


if __name__ == '__main__':
    unittest.main()

