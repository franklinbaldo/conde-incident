"""Guard derived observables against mis-cited source and false activation."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import export_observable_dependency_links as links

class ObservableDependencyLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = links.build()

    def test_two_derived_observable_links_are_exactly_c179_and_c151(self):
        rows = self.data['edges']
        self.assertEqual({r['matrix_occurrence'].rsplit(':', 1)[-1] for r in rows},
                         {'C179#1', 'C151#1'})
        self.assertEqual({r['source_id'] for r in rows},
                         {'AFSPC_MIRROR_528', 'NOAA_IGRA_RECIFE_1963'})
        self.assertTrue(all(not r['activation'] and r['simulator_value'] is None
                            and r['lean_status'] == 'CANDIDATE_NOT_PROMOTED'
                            and len(r['required_before_physical_activation']) >= 3
                            for r in rows))

    def test_derived_wind_is_recife_not_conde_or_new_independent_sensor(self):
        x = next(r for r in self.data['edges'] if r['source_id'].startswith('NOAA_'))
        self.assertEqual(x['station'], 'BRM00082900')
        self.assertEqual(x['pressure_levels_hpa'], [850, 700, 500, 300, 250])
        self.assertTrue(self.data['epistemic_limits']['recife_is_not_conde'])
        self.assertIsNone(self.data['epistemic_limits']['independent_physical_observation_count'])

    def test_export_matches_exact_canonical_bytes(self):
        raw = (ROOT / links.OUTPUT).read_bytes()
        self.assertEqual(raw, links.encoded(self.data))
        self.assertLessEqual(len(raw), 20_000)

    def test_mutated_crosswalk_is_rejected(self):
        original = links.documentary.build
        def mutate(root):
            data = copy.deepcopy(original(root))
            row = next(c for c in data['contract_citation_crosswalk']
                       if c['contract_id'] == 'C179_C151_BRIDGE')['occurrences'][0]
            row['cited_source_ids'] = ['NASA_SSR_19631115']
            return data
        # A direct canonical source mutation must fail byte verification.
        with mock.patch.object(links.documentary, 'build', side_effect=mutate):
            with self.assertRaisesRegex(ValueError, 'stale parent'):
                links.build()

    def test_noaa_station_transfer_to_conde_is_rejected(self):
        original = links.physical.recife_winds
        def corrupt(matrix):
            obs = original(matrix)
            return [{**x, 'location': 'Conde, Bahia, Brazil'} for x in obs]
        with mock.patch.object(links.physical, 'recife_winds', side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, 'Recife profile'):
                links.build()

    def test_contract_source_changed_to_false_528_measurement_is_rejected(self):
        original = links.physical.orbital_observables()
        with mock.patch.object(links.physical, 'orbital_observables',
                               return_value={**original, 'source_status': 'PRIMARY_TRACK'}):
            with self.assertRaisesRegex(ValueError, 'TLE custody'):
                links.build()

if __name__ == '__main__':
    unittest.main()
