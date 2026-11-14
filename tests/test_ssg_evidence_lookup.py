# Deterministic lookup tests.

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('evidence_export', ROOT / 'tools/export_ssg_evidence_index.py')
export = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export)


class LookupTest(unittest.TestCase):
    def test_all_original_occurrences_reachable_without_duplicate_claims(self):
        artifacts = export.build()
        manifest = json.loads(artifacts[export.MANIFEST])
        entries = [entry for meta in manifest['lookup_shards']
                   for entry in json.loads(artifacts[Path(meta['path'])])['records']]
        original = export.matrix_inventory((ROOT / export.MATRIX).read_bytes().splitlines())
        self.assertEqual([r['occurrence'] for r in entries], list(original))
        self.assertEqual(len(entries), 241)
        for item in entries:
            sources = manifest['shards'] if item['kind'] == 'curated' else manifest['unmapped_shards']
            for shard_idx, row_idx in item['positions']:
                shard = json.loads(artifacts[Path(sources[shard_idx]['path'])])
                self.assertEqual(shard['records'][row_idx]['occurrence'], item['occurrence'])
            self.assertEqual(set(item), {'occurrence', 'kind', 'positions'})
        for label in ('C44', 'C45', 'C46'):
            self.assertEqual(len([row for row in entries if row['occurrence'].startswith(label+'#')]), 2)
        for meta in manifest['lookup_shards']:
            contents = artifacts[Path(meta['path'])]
            self.assertLessEqual(len(contents), export.MAX_SHARD_BYTES)
            self.assertEqual(export.digest(contents), meta['sha256'])

    def test_damaged_lookup_detected_by_check(self):
        artifacts = export.build()
        with tempfile.TemporaryDirectory() as folder:
            copy = Path(folder)
            export.sync(artifacts, root=copy)
            location = next(path for path in artifacts if path.parent == export.LOOKUP_DEST)
            (copy / location).write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, 'não reproduzível'):
                export.sync(artifacts, root=copy, check=True)
