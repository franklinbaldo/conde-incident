"""Adversarial checks for the literary-source hypothesis bridge."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import export_tupi_legacy_fragment_bridge as bridge


class TupiLegacyFragmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = bridge.from_repo()
        cls.parent = json.loads((ROOT / bridge.PARENT).read_text())
        cls.lineage = json.loads((ROOT / bridge.LINEAGES).read_text())
        cls.editorial = (ROOT / bridge.EDITORIAL).read_bytes()

    def build_with(self, parent=None, lineage=None, editorial=None):
        return bridge.build(parent if parent is not None else self.parent,
                            lineage if lineage is not None else self.lineage,
                            editorial if editorial is not None else self.editorial, 'testsha')

    def test_three_occurrences_single_transmission_family(self):
        self.assertEqual([x['occurrence_ref'].rsplit(':', 1)[-1] for x in self.record['documentary_occurrences']],
                         ['C01#1', 'C02#1', 'C03#1'])
        self.assertEqual({x['source_id'] for x in self.record['documentary_occurrences']}, {bridge.FBIS})
        self.assertTrue(all(not x['physical_observation'] for x in self.record['documentary_occurrences']))

    def test_other_newspaper_is_reported_not_a_new_eyewitness(self):
        x = self.record['comparison']
        self.assertIsNone(x['other_original_pdf_sha256'])
        self.assertIsNone(x['other_matrix_occurrence_ref'])
        self.assertIsNone(x['direct_textual_dependency'])
        self.assertIsNone(x['independent_witness_count'])
        self.assertIsNone(x['tupi_broadcast_epoch_utc'])

    def test_hypotheses_and_simulator_stay_pending(self):
        self.assertEqual(len(self.record['hypotheses']), 4)
        self.assertEqual({h['id'].split('_', 1)[0] for h in self.record['hypotheses']},
                         {'H0', 'H1', 'H2', 'H3'})
        c = self.record['candidate']
        self.assertFalse(c['activation'])
        self.assertIsNone(c['simulator_value'])
        self.assertEqual(c['physical_domain_effect'], 'THETA_UNCHANGED')
        self.assertIsNone(self.record['independent_528_physical_observation_count'])

    def test_site_bytes_exactly_match(self):
        self.assertEqual((ROOT / bridge.OUTPUT).read_bytes(), bridge.encoded(self.record))
        self.assertLessEqual(len(bridge.encoded(self.record)), 20_000)

    def test_mutated_occurrence_hash_rejected(self):
        p = copy.deepcopy(self.parent)
        x = next(x for x in p['citation_lineages'] if x['snapshot_ref'].endswith('C02#1'))
        x['row_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'matrix row identity'):
            self.build_with(parent=p)

    def test_mutated_source_family_rejected(self):
        p = copy.deepcopy(self.parent)
        x = next(x for x in p['citation_lineages'] if x['snapshot_ref'].endswith('C02#1'))
        x['family_id'] = 'INDEPENDENT_EYEWITNESS'
        with self.assertRaisesRegex(ValueError, 'source identity'):
            self.build_with(parent=p)

    def test_deleted_tupi_dependency_rejected(self):
        p = copy.deepcopy(self.parent)
        x = next(x for x in p['citation_lineages'] if x['snapshot_ref'].endswith('C01#1'))
        x['declared_upstream_paths'] = []
        with self.assertRaisesRegex(ValueError, 'transcription lineage'):
            self.build_with(parent=p)

    def test_false_audio_recovery_rejected(self):
        p = copy.deepcopy(self.lineage)
        next(x for x in p['sources'] if x['id'] == bridge.TUPI)['status'] = 'AUDIO_AUTHENTICATED'
        with self.assertRaisesRegex(ValueError, 'origin/broadcast status'):
            self.build_with(lineage=p)

    def test_unreviewed_editorial_change_rejected(self):
        with self.assertRaisesRegex(ValueError, 'editorial snapshot'):
            self.build_with(editorial=self.editorial + b'\nclaim became physical observation')


if __name__ == '__main__':
    unittest.main()
