"""Adversarial tests for the derived source-family reverse lookup."""
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('source_lookup', ROOT / 'tools/export_ssg_source_lookup.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class SourceLookupTest(unittest.TestCase):
    def source_copy(self, folder):
        for path in (module.CITATIONS, module.LINEAGE, module.EVIDENCE, module.MATRIX):
            dest = Path(folder) / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / path).read_bytes())

    def reseal_manifest_source(self, folder, changed):
        path = Path(folder) / module.EVIDENCE
        manifest = json.loads(path.read_bytes())
        for item in manifest['source_files']:
            if item['path'] == str(changed):
                item['sha256'] = module.digest((Path(folder) / changed).read_bytes())
        path.write_bytes(module.encode(manifest))

    def test_determinism_and_complete_reverse_coverage(self):
        artifacts = module.build()
        self.assertEqual(artifacts, module.build())
        module.sync(artifacts, check=True)
        pointer = json.loads(artifacts[module.POINTER])
        raw = artifacts[Path(pointer['source_index']['path'])]
        doc = json.loads(raw)
        self.assertLessEqual(len(raw), 20_000)
        self.assertEqual(len(doc['sources']), 15)
        self.assertEqual(len(doc['families']), 9)
        self.assertEqual(sum(len(x['references']) for x in doc['sources']), 29)
        self.assertEqual(len({r['occurrence'] for s in doc['sources']
                              for r in s['references']}), 28)
        self.assertEqual(len(doc['post_matrix_only']), 1)
        self.assertIsNone(doc['post_matrix_only'][0]['matrix_line'])
        self.assertIsNone(doc['independent_physical_observation_count'])
        self.assertFalse(doc['absence_of_declared_edge_proves_independence'])
        self.assertEqual(module.digest(raw), pointer['source_index']['sha256'])

    def test_lineage_must_be_bijective(self):
        with TemporaryDirectory() as folder:
            self.source_copy(folder)
            path = Path(folder) / module.LINEAGE
            obj = json.loads(path.read_bytes())
            obj['citation_lineages'].pop()
            path.write_bytes(module.encode(obj))
            self.reseal_manifest_source(folder, module.LINEAGE)
            with self.assertRaisesRegex(ValueError, 'Non-bijective'):
                module.build(Path(folder))

    def test_row_hash_cannot_be_rewritten_in_lineage(self):
        with TemporaryDirectory() as folder:
            self.source_copy(folder)
            path = Path(folder) / module.LINEAGE
            obj = json.loads(path.read_bytes())
            obj['citation_lineages'][0]['row_sha256'] = '0' * 64
            path.write_bytes(module.encode(obj))
            self.reseal_manifest_source(folder, module.LINEAGE)
            with self.assertRaisesRegex(ValueError, 'Lineage citation'):
                module.build(Path(folder))

    def test_resealed_crossfeed_cannot_move_source_to_another_occurrence(self):
        # Alter both canonical JSON inputs consistently, including the lineage key,
        # so row digest and source bijection still pass. Only the matrix owns IDs.
        with TemporaryDirectory() as folder:
            self.source_copy(folder)
            citations_path = Path(folder) / module.CITATIONS
            lineage_path = Path(folder) / module.LINEAGE
            citations = json.loads(citations_path.read_bytes())
            lineage = json.loads(lineage_path.read_bytes())
            old = citations['records'][0]['snapshot_ref']
            replacement = 'C238#1'
            new = old.rsplit(':', 1)[0] + ':' + replacement
            citations['records'][0]['occurrence'] = replacement
            citations['records'][0]['snapshot_ref'] = new
            target = next(row for row in lineage['citation_lineages']
                          if row['snapshot_ref'] == old)
            target['snapshot_ref'] = new
            citations_path.write_bytes(module.encode(citations))
            lineage_path.write_bytes(module.encode(lineage))
            self.reseal_manifest_source(folder, module.CITATIONS)
            self.reseal_manifest_source(folder, module.LINEAGE)
            with self.assertRaisesRegex(ValueError, 'occurrence identity'):
                module.build(Path(folder))

    def test_snapshot_ref_must_match_occurrence_even_if_row_hash_matches(self):
        with TemporaryDirectory() as folder:
            self.source_copy(folder)
            citations_path = Path(folder) / module.CITATIONS
            lineage_path = Path(folder) / module.LINEAGE
            citations = json.loads(citations_path.read_bytes())
            lineage = json.loads(lineage_path.read_bytes())
            old = citations['records'][0]['snapshot_ref']
            new = 'matrix:' + '0' * 40 + ':' + citations['records'][0]['occurrence']
            citations['records'][0]['snapshot_ref'] = new
            next(row for row in lineage['citation_lineages']
                 if row['snapshot_ref'] == old)['snapshot_ref'] = new
            citations_path.write_bytes(module.encode(citations))
            lineage_path.write_bytes(module.encode(lineage))
            self.reseal_manifest_source(folder, module.CITATIONS)
            self.reseal_manifest_source(folder, module.LINEAGE)
            with self.assertRaisesRegex(ValueError, 'occurrence identity'):
                module.build(Path(folder))

    def test_physical_independence_cannot_be_forged(self):
        with TemporaryDirectory() as folder:
            self.source_copy(folder)
            path = Path(folder) / module.LINEAGE
            obj = json.loads(path.read_bytes())
            obj['citation_lineages'][0]['independent_physical_observation_count'] = 1
            path.write_bytes(module.encode(obj))
            self.reseal_manifest_source(folder, module.LINEAGE)
            with self.assertRaisesRegex(ValueError, 'Attempted promotion'):
                module.build(Path(folder))

    def test_post_matrix_constraint_cannot_be_forged(self):
        with TemporaryDirectory() as folder:
            self.source_copy(folder)
            path = Path(folder) / module.CITATIONS
            obj = json.loads(path.read_bytes())
            obj['post_matrix_occurrences'][0]['physical_constraint'] = {'impact': True}
            path.write_bytes(module.encode(obj))
            self.reseal_manifest_source(folder, module.CITATIONS)
            with self.assertRaisesRegex(ValueError, 'cannot be promoted'):
                module.build(Path(folder))

    def test_pointer_is_read_only_under_check(self):
        with TemporaryDirectory() as folder:
            self.source_copy(folder)
            expected = module.build(Path(folder))
            module.sync(expected, Path(folder))
            module.sync(expected, Path(folder), check=True)
            p = Path(folder) / module.POINTER
            p.write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, 'Stale/missing'):
                module.sync(expected, Path(folder), check=True)

    def test_historical_immutable_shard_is_never_overwritten(self):
        with TemporaryDirectory() as folder:
            self.source_copy(folder)
            expected = module.build(Path(folder))
            module.sync(expected, Path(folder))
            blob = next(p for p in expected if p != module.POINTER)
            (Path(folder) / blob).write_bytes(b'corrupted')
            with self.assertRaisesRegex(ValueError, 'Refusing to overwrite'):
                module.sync(expected, Path(folder))


if __name__ == '__main__':
    unittest.main()
