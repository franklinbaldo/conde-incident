"""Adversarial custody and no-promotion checks for R51; work under python -O."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('stl_bridge', ROOT / 'tools/export_stl_r51_dependency_bridge.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class STLBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r51, cls.r49 = bridge.load()

    def test_render_matches_public_artifact(self):
        self.assertEqual(bridge.OUT.read_bytes(), bridge.render())

    def test_two_sources_not_two_instruments(self):
        data = bridge.build(self.r51, self.r49)
        self.assertEqual(0, data['independent_instrumental_observations_added'])
        self.assertEqual(0, data['new_confirmed_norad_528_observations'])
        self.assertFalse(data['activation'])
        self.assertEqual('THETA_UNCHANGED', data['physical_domain_effect'])
        self.assertTrue(all(not e['activation'] and e['documentary_only'] for e in data['graph']))
        self.assertTrue(all(x['value'] is None and not x['activation'] for x in data['latents']))
        self.assertTrue(all(x['value'] is None and not x['activation'] for x in data['simulator_parameters']))
        self.assertEqual([527, 528, 529], [x['norad_id'] for x in data['other_norad_candidates']])

    def test_pair_not_fused_into_november(self):
        data = bridge.build(self.r51, self.r49)
        self.assertEqual([94.7, 94.6], data['printed_values']['period_min'])
        self.assertEqual([82.0, 81.9], data['printed_values']['inclination_deg'])
        self.assertEqual('initial_orbital_data_as_of_1963_01_31', data['source_epoch_context'])
        self.assertEqual('miles', data['altitude_unit_verified'])
        self.assertIsNone(data['altitude_mile_subtype_verified'])
        self.assertEqual('NASA_TM_X59315_B12_FOOTER_PDF_PAGE_105', data['altitude_unit_evidence'])
        self.assertEqual([298, 286], data['printed_values']['perigee_miles_as_printed'])
        self.assertIn('LATENT:mile_subtype', [x['id'] for x in data['latents']])
        self.assertFalse(data['pair_mapping_proven'])

    def reject(self, which, path, value):
        r51, r49 = copy.deepcopy(self.r51), copy.deepcopy(self.r49)
        item = r51 if which == 'r51' else r49
        for name in path[:-1]:
            item = item[name]
        item[path[-1]] = value
        with self.assertRaises(ValueError):
            bridge.build(r51, r49)

    def test_reject_false_km_unit(self):
        self.reject('r51', ['printed_row', 'perigee_apogee_unit_on_b12'], 'km')

    def test_reject_fabricated_statute_mile_subtype(self):
        self.reject('r51', ['printed_row', 'mile_variant_as_printed'], 'statute')

    def test_reject_unverified_stl_genealogy(self):
        self.reject('r51', ['scientific_interpretation', 'candidate_upstream_proven'], True)

    def test_reject_528_sensor_promotion(self):
        self.reject('r51', ['scientific_interpretation', 'independent_instrumental_sensors_added'], 1)

    def test_reject_528_constraint_promotion(self):
        self.reject('r51', ['scientific_interpretation', 'new_physical_constraints_activated'], 1)

    def test_reject_parent_bridge_activation(self):
        self.reject('r49', ['activation'], True)

    def test_reject_parent_object_substitution(self):
        self.reject('r49', ['nasa_print_row'], '1963-003B')

    def test_reject_hash_drift(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)
            (p / bridge.R51_PATH).parent.mkdir(parents=True)
            (p / bridge.R49_PATH).parent.mkdir(parents=True)
            (p / bridge.R51_PATH).write_bytes((ROOT / bridge.R51_PATH).read_bytes() + b' ')
            (p / bridge.R49_PATH).write_bytes((ROOT / bridge.R49_PATH).read_bytes())
            with self.assertRaisesRegex(ValueError, 'source SHA drift'):
                bridge.load(p)


if __name__ == '__main__':
    unittest.main()
