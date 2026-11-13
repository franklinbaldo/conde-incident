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


    def test_un_and_soviet_edges_join_existing_graph_without_promotion(self):
        edges = self.data['pending_documentary_edges']
        un = [e for e in edges if e['source_occurrence'] == 'C241-L33']
        sov = [e for e in edges if e['source_occurrence'] == 'C241-L37']
        self.assertEqual((len(un), len(sov)), (2, 11))
        self.assertEqual({e['matrix_context'] for e in un}, {'C197#1'})
        self.assertTrue(all(e['matrix_context'] is None for e in sov))
        self.assertTrue(all(not e['independence_certified'] for e in edges))
        self.assertEqual({e['to'] for e in un},
                         {'latent_1963_528_state_epoch', 'latent_528_true_terminal_time'})
        self.assertEqual({e['to'] for e in sov if e['to'].startswith('NORAD_')},
                         {f'NORAD_{n}_latent_track' for n in (527, 528, 529)})
        self.assertEqual({e['to'] for e in sov if e['from'] == 'C241-L37'},
                         {'SOVIET_METHODS_SERIAL', 'SOVIET_RAW_RESULTS_SERIAL',
                          'C241-L29', 'C241-L31', 'C241-L34', 'C241-L35'})
        self.assertEqual(len({(e['from'], e['to'], e['relation']) for e in edges}), 13)
        self.assertTrue(all(e['activation'] is False
                            and e['observed_value'] is None
                            and e['status'] == 'CONNECTED_PENDING_CALIBRATION'
                            for e in edges))
        for path, digest in self.data['pending_source_sha256'].items():
            self.assertEqual(links.hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)
        self.assertEqual(len(self.data['edges']), 2)
        self.assertEqual(len(self.data['external_source_edges']), 1)
        self.assertEqual(self.data['epistemic_limits']['activated_constraints'], 0)

    def test_december_529_erratum_c227_and_same_work_c228_are_connected(self):
        edges = self.data["pending_december_compilation_edges"]
        self.assertEqual(len(edges), 3)
        self.assertEqual([e["matrix_occurrence"].rsplit(":", 1)[-1]
                          for e in edges], ["C227#1", "C227#1", "C228#1"])
        self.assertEqual([e["printed_period_min_not_instrument_observation"]
                          for e in edges], ["89.2", "94.6", None])
        self.assertTrue(all(not e["activation"] and not e["independent_sensor"]
                            and e["instrument_epoch_utc"] is None
                            and e["instrument_covariance"] is None
                            for e in edges))
        self.assertEqual(self.data["epistemic_limits"]["activated_constraints"], 0)

    def test_un_administrative_cutoff_cannot_become_instrument_epoch(self):
        un = json.loads((ROOT / 'public/data/conde-un-1963-status-bridge.json').read_text())
        sov = json.loads((ROOT / 'public/data/conde-soviet-raw-route-bridge.json').read_text())
        for key, value in [('actual_terminal_time_utc', '1963-11-08T13:00:00Z'),
                           ('sensor_epoch_utc', '1963-11-15T00:00:00Z'),
                           ('sensor_covariance', [[1]])]:
            bad = copy.deepcopy(un)
            bad['documentary_status_528'][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'UN cutoff'):
                links.pending_documentary_routes(bad, sov)
        bad = copy.deepcopy(un)
        bad['source_documents'][1]['publication_day'] = '1963-11-15'
        with self.assertRaisesRegex(ValueError, 'publication/cutoff'):
            links.pending_documentary_routes(bad, sov)

    def test_soviet_catalogue_not_measured_528_or_november_record(self):
        un = json.loads((ROOT / 'public/data/conde-un-1963-status-bridge.json').read_text())
        sov = json.loads((ROOT / 'public/data/conde-soviet-raw-route-bridge.json').read_text())
        for key, value in [('sigma', 0.1), ('time_utc', '1963-11-08T04:00:00Z'),
                           ('source_identity_confirmed', True), ('value', 0.2)]:
            bad = copy.deepcopy(sov)
            bad['simulator_latent_parameters'][1][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'target parameters'):
                links.pending_documentary_routes(un, bad)
        bad = copy.deepcopy(sov)
        bad['catalogue_leads'][0]['described_observation_month'] = 'November 1963'
        with self.assertRaisesRegex(ValueError, 'Soviet catalogue'):
            links.pending_documentary_routes(un, bad)
        bad = copy.deepcopy(sov)
        bad['source_dependency_graph'][1] = copy.deepcopy(bad['source_dependency_graph'][0])
        with self.assertRaisesRegex(ValueError, 'routes lost'):
            links.pending_documentary_routes(un, bad)

    def test_parent_replay_is_required_before_publishing_aggregate(self):
        with mock.patch.object(links.soviet, 'render', return_value=b'not canonical'):
            with self.assertRaisesRegex(ValueError, 'stale pending source bridge'):
                links.build()
        with mock.patch.object(links.un1963, 'render', return_value=b'not canonical'):
            with self.assertRaisesRegex(ValueError, 'stale pending source bridge'):
                links.build()

if __name__ == '__main__':
    unittest.main()
