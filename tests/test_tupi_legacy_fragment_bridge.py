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
        cls.locator = (ROOT / bridge.LOCATOR).read_bytes()
        cls.verified = (ROOT / bridge.VERIFIED).read_bytes()

    def build_with(self, parent=None, lineage=None, editorial=None, locator=None, verified=None):
        return bridge.build(parent if parent is not None else self.parent,
                            lineage if lineage is not None else self.lineage,
                            editorial if editorial is not None else self.editorial, 'testsha',
                            locator if locator is not None else self.locator,
                            verified if verified is not None else self.verified)

    def test_three_occurrences_single_transmission_family(self):
        self.assertEqual([x['occurrence_ref'].rsplit(':', 1)[-1] for x in self.record['documentary_occurrences']],
                         ['C01#1', 'C02#1', 'C03#1'])
        self.assertEqual({x['source_id'] for x in self.record['documentary_occurrences']}, {bridge.FBIS})
        self.assertTrue(all(not x['physical_observation'] for x in self.record['documentary_occurrences']))

    def test_other_newspaper_is_reported_not_a_new_eyewitness(self):
        x = self.record['comparison']
        self.assertEqual(x['other_original_pdf_sha256'], bridge.PDF_SHA256)
        self.assertTrue(x['other_verified_digital_page8_inspected'])
        self.assertEqual(x['other_pdf_get_status_verified'], 200)
        self.assertEqual(x['other_pdf_bytes_verified'], 4337426)
        self.assertEqual(x['other_pdf_page_count_verified'], 8)
        self.assertEqual(x['other_original_facsimile_node'], bridge.PDF_NODE)
        self.assertIsNone(x['other_matrix_occurrence_ref'])
        self.assertIsNone(x['direct_textual_dependency'])
        self.assertIsNone(x['independent_witness_count'])
        self.assertIsNone(x['tupi_broadcast_epoch_utc'])

    def test_docreader_corrected_edition_without_page_promotion(self):
        c = self.record['comparison']
        self.assertEqual(c['other_document_locator_id'], 'DOC-UH-PE-1963-00471-LOCATOR')
        self.assertEqual(c['other_source_url'], 'https://memoria.bn.gov.br/DocReader/765147/5339')
        self.assertEqual(c['other_page8_candidate_url'], 'https://memoria.bn.gov.br/DocReader/765147/5346')
        self.assertEqual(c['earlier_wrong_docreader_edition'], '00507')
        self.assertEqual(c['other_pdf_head_status'], 403)
        self.assertFalse(c['other_page8_raster_retrieved'])
        self.assertFalse(c['other_printed_page8_inspected'])
        self.assertEqual(self.record['delta_links'], 7)
        self.assertIn({'from': c['other_document_locator_id'],
                       'to': bridge.PDF_NODE,
                       'kind': 'EDITION_LOCATOR_LINKED_TO_VERIFIED_ORIGINAL_PDF'},
                      self.record['graph_edges'])
        self.assertIn({'from': bridge.PDF_NODE, 'to': bridge.UH,
                       'kind': 'PAGE8_PRINTED_CLAIM_VERIFIED'}, self.record['graph_edges'])
        self.assertNotIn('recapture_00471_page_8_original_facsimile_and_digest',
                         self.record['candidate']['missing_conditions'])

    def test_wrong_edition_or_false_facsimile_promotion_rejected(self):
        for key, val in (('docreader_selected_edition', '00507'),
                         ('docreader_requested_page8_candidate_id', 5756),
                         ('page_8_inspected', True),
                         ('four_metre_hole_verified', True),
                         ('docreader_page8_raster_retrieved', True)):
            with self.subTest(field=key):
                locator = json.loads(self.locator)
                locator[key] = val
                with self.assertRaisesRegex(ValueError, 'locator bytes changed'):
                    self.build_with(locator=bridge.encoded(locator))

    def test_mutated_primary_ledger_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'verification ledger changed'):
            self.build_with(verified=self.verified.replace(b'4.337.426', b'4.337.427'))

    def test_no_false_dependency_or_printed_page_promotion(self):
        c = self.record['comparison']
        self.assertFalse(c['other_printed_page8_inspected'])
        self.assertFalse(c['other_page8_raster_retrieved'])
        self.assertIsNone(c['direct_textual_dependency'])
        self.assertIsNone(c['tupi_broadcast_epoch_utc'])
        self.assertEqual(c['other_previous_403_status'],
                         'HISTORICAL_ACCESS_FAILURE_NOT_CURRENT_CUSTODY')

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
