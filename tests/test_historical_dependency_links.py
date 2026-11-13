"""Adversarial controls for Lontra handoffs: source custody != independent observation."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import export_historical_dependency_links as graph


class HistoricalLinksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for source in graph.FILES.values():
            target = self.root / source
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(graph.ROOT / source, target)

    def patch(self, source, update):
        path = self.root / graph.FILES[source]
        record = json.loads(path.read_text())
        update(record)
        path.write_text(json.dumps(record))

    def test_source_locked_handoffs_and_rejected_bridges(self):
        artifact = graph.build(self.root)
        self.assertEqual(len(artifact['handoffs']), 3)
        self.assertEqual(artifact['result']['new_connected_edges'], 12)
        self.assertEqual(artifact['result']['new_activated_physical_predicates'], 0)
        self.assertEqual(artifact['result']['admissible_orbital_domain'],
                         'UNCHANGED_NOT_EVALUATED')
        self.assertIsNone(artifact['result']['historical_impact_location'])
        node_ids = {n['id'] for n in artifact['nodes']}
        connected = {(e['from'], e['to']) for e in artifact['edges']}
        for edge in artifact['edges']:
            self.assertIn(edge['from'], node_ids)
            self.assertIn(edge['to'], node_ids)
        for blocked in artifact['rejected_edges']:
            self.assertNotIn((blocked['from'], blocked['to']), connected)
        self.assertEqual(artifact['provenance']['nara_independent_physical_witnesses_added'], 0)
        self.assertFalse(next(n for n in artifact['nodes'] if n['id'] == 'UWM-AGDM-10814')
                         ['georeferenced_for_1963'])
        self.assertEqual(artifact['candidate_links'][0]['variable'],
                         'config_municipal_1960_retro_proxy')
        self.assertIsNone(artifact['candidate_links'][0]['simulator_filter'])
        self.assertIsNone(artifact['candidate_links'][0]['legal_1963_geometry'])
        self.assertIn(('IBGE-CGEO-10', 'CGEO-10-RETRO-PROXY'), connected)
        self.assertIn(('NARA-302531015', 'C10#1'), connected)
        self.assertNotIn(('NARA-BB-302531012', 'C234#1'), connected)
        self.assertIsNone(artifact['candidate_links'][2]['value'])

    def test_committed_export_matches_source_and_is_under_policy(self):
        built = graph.encode(graph.build())
        self.assertLess(len(built), 20_000)
        self.assertEqual((graph.ROOT / graph.OUTPUT).read_bytes(), built)
        self.assertLess((graph.ROOT / 'tools/export_historical_dependency_links.py').stat().st_size,
                        20_000)

    def test_reject_matrix_occurrence_retcon(self):
        path = self.root / graph.FILES['MATRIX']
        source = path.read_text()
        self.assertIn('Telegrama DOS-UAP-D001', source)
        path.write_text(source.replace('Telegrama DOS-UAP-D001', 'TELEGRAM_RENAMED'))
        with self.assertRaisesRegex(ValueError, 'matrix occurrence'):
            graph.build(self.root)

    def test_reject_ibge_forged_survey_or_boundary(self):
        self.patch('IBGE_CGEO10', lambda x: x['method_and_limits'].update(
            admissible_historical_boundary_1963=True))
        with self.assertRaisesRegex(ValueError, 'historical boundary'):
            graph.build(self.root)

    def test_reject_ibge_zip_hash_drift(self):
        self.patch('IBGE_CGEO10', lambda x: x['source']['binary'].update(
            source_zip_sha256='0' * 64))
        with self.assertRaisesRegex(ValueError, 'source bytes drift'):
            graph.build(self.root)

    def test_reject_uwm_forged_original_jp2_and_boundary(self):
        self.patch('UWM_10814', lambda x: x['object'].update(
            original_jp2_downloaded=True, original_jp2_sha256='1' * 64))
        with self.assertRaisesRegex(ValueError, 'integrity drift'):
            graph.build(self.root)
        shutil.copyfile(graph.ROOT / graph.FILES['UWM_10814'],
                        self.root / graph.FILES['UWM_10814'])
        self.patch('UWM_10814', lambda x: x['epistemic_and_model_links'].update(
            historical_polygon_1963=[[1, 2]]))
        with self.assertRaisesRegex(ValueError, 'promoted to 1963'):
            graph.build(self.root)

    def test_reject_nara_crossed_image_hash(self):
        path = self.root / graph.FILES['NARA_302531012']
        text = path.read_text()
        h1, h2 = graph.NARA_JP2['0809.jp2'][1], graph.NARA_JP2['0810.jp2'][1]
        # Both digests still exist, but no longer belong to the right image.
        path.write_text(text.replace(h1, 'TEMP_HASH').replace(h2, h1)
                        .replace('TEMP_HASH', h2))
        with self.assertRaisesRegex(ValueError, 'table identity/hash mismatch'):
            graph.build(self.root)

    def test_reject_telegram_promoted_to_verified_newspaper(self):
        path = self.root / graph.FILES['NARA_302531012']
        source = path.read_text()
        path.write_text(source.replace('O GLOBO', 'NEWSPAPER_REDACAO'))
        with self.assertRaisesRegex(ValueError, 'newspaper candidate'):
            graph.build(self.root)


if __name__ == '__main__':
    unittest.main()
