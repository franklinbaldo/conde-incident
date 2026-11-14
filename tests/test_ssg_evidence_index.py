"""Adversarial custody tests for the documentary SSG index."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('evidence_export', ROOT / 'tools/export_ssg_evidence_index.py')
export = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export)


class EvidenceIndexTest(unittest.TestCase):
    def test_source_custody_and_bounded_shards(self):
        artifacts = export.build()
        manifest = json.loads(artifacts[export.MANIFEST])
        self.assertEqual(manifest['schema'], 'conde.evidence-index/v1')
        matrix_raw = (ROOT / export.MATRIX).read_bytes()
        self.assertEqual(manifest['matrix_source'],
                         {'path': str(export.MATRIX), 'bytes': len(matrix_raw),
                          'sha256': export.digest(matrix_raw)})
        self.assertIsNone(manifest['independent_physical_observation_count'])
        self.assertFalse(manifest['absence_of_declared_dependency_proves_independence'])
        self.assertEqual(len(manifest['post_matrix_ids_not_in_curated_index']), 1)
        gaps = manifest['unmapped_matrix_refs']
        self.assertEqual(len(gaps), manifest['unmapped_matrix_occurrences'])
        self.assertEqual(len(gaps) + manifest['curated_occurrences'],
                         manifest['total_matrix_occurrences'])
        indexed = {r['occurrence'] for r in
                   json.loads((ROOT / export.CITATIONS).read_text())['records']}
        self.assertFalse(indexed.intersection(r['occurrence'] for r in gaps))
        inventory = export.matrix_inventory((ROOT / export.MATRIX).read_bytes().splitlines())
        self.assertEqual({g['occurrence']: g['matrix_line'] for g in gaps},
                         {k: v for k, v in inventory.items() if k not in indexed})
        self.assertEqual(inventory['C44#2'] > inventory['C44#1'], True)
        seen = set()
        for shard in manifest['shards']:
            raw = artifacts[Path(shard['path'])]
            self.assertEqual(export.digest(raw), shard['sha256'])
            self.assertEqual(len(raw), shard['bytes'])
            self.assertLessEqual(len(raw), export.MAX_SHARD_BYTES)
            rows = json.loads(raw)['records']
            self.assertEqual(len(rows), shard['record_count'])
            for row in rows:
                key = (row['snapshot_ref'], row['source_id'])
                self.assertNotIn(key, seen)
                seen.add(key)
                self.assertTrue(row['not_a_verified_conde_physical_event'])
                self.assertIsNone(row['independent_physical_observation_count'])
                self.assertEqual(row['archive_path'], '/conde-incident/evidencias/arquivo/'
                                 + row['occurrence'].lower().replace('#', '-') + '/')
        self.assertEqual(len(seen), manifest['curated_reference_count'])
        published_gaps = []
        for shard in manifest['unmapped_shards']:
            raw = artifacts[Path(shard['path'])]
            self.assertEqual(export.digest(raw), shard['sha256'])
            self.assertEqual(len(raw), shard['bytes'])
            self.assertLessEqual(len(raw), export.MAX_SHARD_BYTES)
            document = json.loads(raw)
            self.assertEqual(document['schema'], 'conde.evidence-gap-shard/v1')
            self.assertEqual(len(document['records']), shard['record_count'])
            published_gaps.extend(document['records'])
        matrix = (ROOT / export.MATRIX).read_bytes().splitlines()
        self.assertEqual([{'occurrence': gap['occurrence'],
                           'matrix_line': gap['matrix_line'],
                           'row_sha256': export.digest(matrix[gap['matrix_line'] - 1]),
                           'claim_text': matrix[gap['matrix_line'] - 1].decode('utf-8').split('|')[2].strip()}
                          for gap in gaps], published_gaps)
        self.assertTrue(all(set(record) == {'occurrence', 'matrix_line',
                                             'row_sha256', 'claim_text'}
                            for record in published_gaps))
        for source in manifest['source_files']:
            self.assertEqual(export.digest((ROOT / source['path']).read_bytes()), source['sha256'])
        self.assertEqual(artifacts, export.build(), 'Mesma fonte deve gerar bytes idênticos')
        export.sync(artifacts, check=True)

    def mutate_inputs(self, alter, edit_matrix=lambda raw: raw):
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            (scratch / 'public/data').mkdir(parents=True)
            (scratch / 'research').mkdir()
            data = {path: json.loads((ROOT / path).read_text())
                    for path in (export.CITATIONS, export.LINEAGE)}
            alter(data)
            for path, document in data.items():
                (scratch / path).write_text(json.dumps(document))
            (scratch / export.MATRIX).write_bytes(
                edit_matrix((ROOT / export.MATRIX).read_bytes()))
            with self.assertRaises(ValueError):
                export.build(scratch)

    def mutate(self, filename, alter):
        self.mutate_inputs(lambda data: alter(data[filename]))

    def test_declaration_cannot_hide_an_unindexed_matrix_row(self):
        def forge(data):
            citation = data[export.CITATIONS]
            citation['total_matrix_occurrences'] -= 1
            citation['unmapped_occurrences'] -= 1
            # Old arithmetic check still held, but the frozen rows did not.
        self.mutate_inputs(forge)

    def test_inventory_keeps_duplicate_matrix_labels_distinct(self):
        lines = (ROOT / export.MATRIX).read_bytes().splitlines()
        inventory = export.matrix_inventory(lines)
        for name in ('C44', 'C45', 'C46'):
            self.assertIn(f'{name}#1', inventory)
            self.assertIn(f'{name}#2', inventory)
            self.assertNotEqual(inventory[f'{name}#1'],inventory[f'{name}#2'])

    def test_both_feeds_cannot_forge_a_row_hash(self):
        def forge(data):
            row = data[export.CITATIONS]['records'][0]
            row['row_sha256'] = '0' * 64
            key = (row['snapshot_ref'], row['source_id'])
            entry = next(e for e in data[export.LINEAGE]['citation_lineages']
                         if (e['snapshot_ref'], e['source_id']) == key)
            entry['row_sha256'] = row['row_sha256']
        self.mutate_inputs(forge)

    def test_both_feeds_cannot_move_a_matrix_line(self):
        def forge(data):
            row = data[export.CITATIONS]['records'][0]
            row['matrix_line'] += 1
            key = (row['snapshot_ref'], row['source_id'])
            entry = next(e for e in data[export.LINEAGE]['citation_lineages']
                         if (e['snapshot_ref'], e['source_id']) == key)
            entry['matrix_line'] = row['matrix_line']
        self.mutate_inputs(forge)

    def test_rewritten_claim_rejected_even_when_matrix_row_hash_is_valid(self):
        def forge(data):
            data[export.CITATIONS]['records'][0]['claim_text'] = 'Impacto físico confirmado em Conde'
        self.mutate_inputs(forge)

    def test_mutated_frozen_matrix_rejected_even_with_same_feeds(self):
        self.mutate_inputs(lambda _: None, lambda raw: raw + b'\n<!-- altered -->\n')

    def test_duplicate_document_link_rejected(self):
        self.mutate(export.CITATIONS, lambda d: d['records'].append(copy.deepcopy(d['records'][0])))

    def test_broken_row_sha_rejected(self):
        self.mutate(export.CITATIONS, lambda d: d['records'][0].update(row_sha256='0' * 64))

    def test_unknown_snapshot_id_rejected(self):
        self.mutate(export.CITATIONS, lambda d: d['records'][0].update(snapshot_ref='matrix:wrong:C01#1'))

    def test_unmatched_genealogy_rejected(self):
        self.mutate(export.LINEAGE, lambda d: d['citation_lineages'][0].update(source_id='MISSING_SOURCE'))

    def test_promotion_to_physical_witness_rejected(self):
        self.mutate(export.CITATIONS, lambda d: d['records'][0].update(not_a_verified_conde_physical_event=False))

    def test_cyclic_dependency_rejected(self):
        def change(data):
            chain = next(x for x in data['citation_lineages'] if x['declared_upstream_paths'])
            path = chain['declared_upstream_paths'][0]
            path['edges'].append({'from': path['upstream_source_id'],
                                  'to': chain['source_id'], 'kind': 'claims'})
            path['upstream_source_id'] = chain['source_id']
        self.mutate(export.LINEAGE, change)

    def test_unvalidated_terminal_claim_in_path_rejected(self):
        def inject(data):
            entry = next(x for x in data['citation_lineages'] if x['declared_upstream_paths'])
            entry['declared_upstream_paths'][0]['norad_528_terminal_epoch_utc'] = '1963-11-08T08:15:00Z'
        self.mutate(export.LINEAGE, inject)

    def test_unvalidated_terminal_claim_in_edge_rejected(self):
        def inject(data):
            entry = next(x for x in data['citation_lineages'] if x['declared_upstream_paths'])
            entry['declared_upstream_paths'][0]['edges'][0]['norad_528_terminal_latitude_deg'] = -11.85
        self.mutate(export.LINEAGE, inject)

    def test_manual_edit_does_not_survive_check(self):
        artifacts = export.build()
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            export.sync(artifacts, scratch)
            export.sync(artifacts, scratch, check=True)
            damaged = scratch / export.MANIFEST
            damaged.write_bytes(damaged.read_bytes() + b' ')
            with self.assertRaises(ValueError):
                export.sync(artifacts, scratch, check=True)

    def test_unindexed_gap_shard_rewrite_cannot_survive_check(self):
        artifacts = export.build()
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            export.sync(artifacts, scratch)
            target = scratch / export.GAPS_DEST / 'part-001.json'
            data = json.loads(target.read_bytes())
            data['records'][0]['claim_text'] = 'Impacto físico confirmado'
            target.write_bytes(export.canonical(data))
            with self.assertRaisesRegex(ValueError, 'Índice não reproduzível'):
                export.sync(artifacts, scratch, check=True)

    def test_orphan_gap_chunk_rejected(self):
        artifacts = export.build()
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            export.sync(artifacts, scratch)
            extra = scratch / export.GAPS_DEST / 'part-999.json'
            extra.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Lista de shards'):
                export.sync(artifacts, scratch, check=True)

    def test_orphan_chunk_rejected(self):
        artifacts = export.build()
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            export.sync(artifacts, scratch)
            extra = scratch / export.DEST / 'part-999.json'
            extra.write_text('{}')
            with self.assertRaises(ValueError):
                export.sync(artifacts, scratch, check=True)


if __name__ == '__main__':
    unittest.main()
