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

    def test_caravelas_external_occurrence_is_connected_but_not_activated(self):
        self.assertEqual(len(self.data['external_source_edges']), 1)
        ext = self.data['external_source_edges'][0]
        self.assertEqual(ext['source_id'], 'MET-ISD-19631107-09-CARAVELAS-01')
        self.assertIsNone(ext['matrix_occurrence'])
        self.assertEqual(ext['digitized_station_hour_rows'], 72)
        self.assertEqual(ext['source_family'], 'NOAA_NCEI_ISD_DIGITIZED_SURFACE_OBSERVATIONS')
        self.assertEqual(ext['graph_edges'][1], {
            'from': 'Caravelas_surface_wind_at_hour_t',
            'to': 'Conde_surface_wind_at_hour_t',
            'type': 'PENDING_SPATIAL_TRANSFER'})
        self.assertEqual(ext['recife_context']['source_id'], 'NOAA_IGRA_RECIFE_1963')
        self.assertTrue(ext['recife_context']['matrix_occurrence'].endswith(':C151#1'))
        self.assertFalse(ext['recife_context']['independence_certified'])
        self.assertFalse(ext['activation'])
        self.assertEqual(len(ext['activation_requirements']), 4)
        self.assertEqual(ext['physical_domain_effect'], 'THETA_UNCHANGED')
        for name in ('station_position_1963', 'instrument_covariance',
                     'spatial_transfer_operator', 'terminal_epoch_528', 'simulator_value'):
            self.assertIsNone(ext[name], name)

    def test_caravelas_spatial_transfer_and_error_require_real_evidence(self):
        paths = ('research/meteorology/isd_caravelas_19631107_09.json',
                 'research/constraints/isd_caravelas_surface_1963.json')
        report, graph = (json.loads((ROOT / x).read_text()) for x in paths)
        context = next(x for x in self.data['edges']
                       if x['source_id'] == 'NOAA_IGRA_RECIFE_1963')
        def audit(r, g, c):
            return links.build_caravelas_external(r, g, c, {})
        assert audit(report, graph, context)['activation'] is False
        mutated = copy.deepcopy(graph)
        mutated['edges'][1]['type'] = 'OBSERVED_AT_CONDE'
        with self.assertRaisesRegex(ValueError, 'Caravelas edges'):
            audit(report, mutated, context)
        mutated = copy.deepcopy(graph)
        mutated['active_conde_constraint'] = True
        with self.assertRaisesRegex(ValueError, 'activated'):
            audit(report, mutated, context)
        mutated = copy.deepcopy(report)
        mutated['quality']['measurement_uncertainty'] = 0.05
        with self.assertRaisesRegex(ValueError, 'custody'):
            audit(mutated, graph, context)
        mutated = copy.deepcopy(context)
        mutated['matrix_occurrence'] = mutated['matrix_occurrence'].replace('C151#1', 'C179#1')
        with self.assertRaisesRegex(ValueError, 'Recife context'):
            audit(report, graph, mutated)

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
