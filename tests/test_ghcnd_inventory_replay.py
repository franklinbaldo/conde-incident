"""Negative controls for full-file Wayback -> byte-exact NOAA recovery."""
import base64
import gzip
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
S = importlib.util.spec_from_file_location('inventory_replay', ROOT / 'tools/reconstruct_ghcnd_inventory.py')
replay = importlib.util.module_from_spec(S)
S.loader.exec_module(replay)


class InventoryReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get('GHCND_WAYBACK_INVENTORY'):
            raise unittest.SkipTest('Dedicated workflow supplies full Wayback source')
        cls.archive = Path(os.environ['GHCND_WAYBACK_INVENTORY'])

    def test_reconstruct_exact_full_source_and_11_consumed_rows(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'recovered.txt'
            replay.recover(self.archive, out)
            self.assertEqual(replay.sha256(out), replay.PINNED_SHA)
            report = json.loads((ROOT / 'research/meteorology/ghcnd_conde_precip_19631107_09.json').read_text())
            station_ids = {s['id']: s['catalogue_prcp_year_bounds'] for s in report['stations']}
            found = {}
            with out.open(encoding='ascii') as fh:
                for line in fh:
                    if line[:11] in station_ids and line[31:35] == 'PRCP':
                        self.assertNotIn(line[:11], found)
                        found[line[:11]] = [int(line[36:40]), int(line[41:45])]
            self.assertEqual(found, station_ids)

    def test_altered_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / 'bad.txt'
            with self.archive.open('rb') as f, src.open('wb') as target:
                target.write(b'X')
                f.read(1)
                for chunk in iter(lambda: f.read(1024*1024), b''):
                    target.write(chunk)
            with self.assertRaisesRegex(ValueError, 'Wayback source SHA-256'):
                replay.recover(src, Path(d) / 'out.txt')

    def test_changed_delta_cannot_reconstruct_approved_original(self):
        delta = json.loads(gzip.decompress(base64.b64decode(replay.DELTA.read_bytes())))
        self.assertTrue(delta['year_2025_to_2026'])
        delta['year_2025_to_2026'].pop()
        with tempfile.TemporaryDirectory() as d:
            altered = Path(d) / 'altered.b64'
            altered.write_bytes(base64.b64encode(gzip.compress(json.dumps(delta).encode())))
            with self.assertRaisesRegex(ValueError, 'reconstructed.*SHA-256'):
                replay.recover(self.archive, Path(d) / 'out.txt', altered)


if __name__ == '__main__':
    unittest.main()
