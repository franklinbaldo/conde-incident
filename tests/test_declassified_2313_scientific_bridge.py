"""Fail-closed documentary crosswalk: NSA/NRO L51 cannot manufacture 528 telemetry."""
import copy
import hashlib
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import export_declassified_2313_scientific_bridge as b


class TestDeclassified2313Bridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = b.sources()

    def mutate(self, source, mutation):
        candidate = copy.deepcopy(self.inputs)
        mutation(candidate[source])
        with self.assertRaises(ValueError):
            b.build(candidate)

    def test_rebuild_from_pinned_sources_and_parent(self):
        data = json.loads(b.render())
        self.assertEqual(b.render(), b.OUT.read_bytes())
        self.assertEqual(data['id'], 'ABELHA-C241-L51-01')
        self.assertEqual(data['parent_bridge']['sha256'], b.PINS[b.PARENT])
        self.assertEqual(data['related_matrix_occurrence'], 'C197#1')
        self.assertEqual(len(data['dependency_graph']), 17)
        self.assertEqual(len(data['facsimiles']), 2)
        self.assertEqual({(x['physical_pdf_page'], x['printed_page']) for x in data['facsimiles']},
                         {(132, 5), (123, 90)})
        self.assertEqual(data['physical_domain_effect'], 'THETA_UNCHANGED')
        self.assertEqual(data['new_528_instrumental_observations'], 0)
        self.assertFalse(data['activation'])
        self.assertIsNone(data['instrumental_epoch_utc'])
        self.assertIsNone(data['instrumental_frame'])
        self.assertIsNone(data['instrumental_station'])
        self.assertIsNone(data['instrumental_covariance'])
        self.assertTrue(all(not e['activation'] and not e['independent_instrumental_observation']
                            for e in data['dependency_graph']))
        self.assertTrue(all(p['value'] is None and not p['activation']
                            for p in data['simulator_latent_parameters']))

    def test_pages_are_not_interchangeable_with_printed_page(self):
        self.mutate(b.SOURCE, lambda x: x['documents'][0].update(pdf_page_1_based=5))
        self.mutate(b.SOURCE, lambda x: x['documents'][1].update(printed_page=123))

    def test_1975_year_and_2017_release_cannot_become_sensor_epoch(self):
        self.mutate(b.SOURCE, lambda x: x['documents'][0].update(authored_year=1963))
        self.mutate(b.SOURCE, lambda x: x['documents'][0].update(release_date='1963-11-08'))
        self.mutate(b.SOURCE, lambda x: x['norad528'].update(observation_utc='1963-11-08T00:00Z'))
        self.mutate(b.SOURCE, lambda x: x['norad528'].update(decay_hour='1963-11-08T00:00Z'))
        self.mutate(b.SOURCE, lambda x: x['norad528'].update(station='SAO-1'))

    def test_false_piece_identity_or_hardware_resolution_rejected(self):
        self.mutate(b.SOURCE, lambda x: x['norad528'].update(hardware_identity='Agena D'))
        self.mutate(b.SOURCE, lambda x: x['conflict'].update(result='RESOLVED_AGENA_D'))
        self.mutate(b.SOURCE, lambda x: x['documents'][1]['readout'].update(
            launch_vehicle_wording='Thor-Agena D'))
        self.mutate(b.SOURCE, lambda x: x['conflict'].update(same_observation_family_claim=True))

    def test_battery_failure_is_not_decay_evidence(self):
        self.mutate(b.SOURCE, lambda x: x['documents'][1]['readout'].update(
            mission_duration_wording='two days until orbital reentry'))
        self.mutate(b.SOURCE, lambda x: x.update(physical_constraint_active=True))
        self.mutate(b.SOURCE, lambda x: x.update(orbital_parameters='THETA_REDUCED'))

    def test_parent_scope_and_inactive_latents_are_required(self):
        self.mutate(b.PARENT, lambda x: x['independence'].update(nro_pdf_verified=True))
        self.mutate(b.PARENT, lambda x: x['simulator_latent_parameters'][0].update(value='D'))
        self.mutate(b.PARENT, lambda x: x.update(activation=True))
        self.mutate(b.PARENT, lambda x: x.update(new_528_instrumental_observations=1))

    def test_original_pdf_sha_is_not_the_manifest_sha(self):
        data = b.build(copy.deepcopy(self.inputs))
        for x in data['facsimiles']:
            self.assertEqual(len(x['pdf_sha256']), 64)
            self.assertNotEqual(x['pdf_sha256'], b.PINS[b.SOURCE])
        self.mutate(b.SOURCE, lambda x: x['documents'][0].update(sha256='0' * 64))
        self.mutate(b.SOURCE, lambda x: x['documents'][1].update(bytes=0))

    def test_source_bytes_fail_closed_even_if_equivalent_json(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            for rel in list(b.PINS) + list(b.previous.PINS):
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dest)
            self.assertEqual(b.render(root), b.render())
            with (root / b.SOURCE).open('ab') as fd:
                fd.write(b'\n')
            with self.assertRaisesRegex(ValueError, 'source hash drift'):
                b.render(root)

    def test_duplicate_keys_cannot_override_activation(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            json.loads('{"activation":false,"activation":true}', object_pairs_hook=b.no_duplicate_keys)


if __name__ == '__main__':
    unittest.main()
