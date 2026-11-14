"""Source-pinned replay tests for one mutable Aracaju archive file."""
import base64
import gzip
import hashlib
from pathlib import Path
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from reconstruct_ghcnd_station import PARTS, ORIGINAL_BYTES, SHA256, recover
from audit_ghcnd_conde_rain_1963 import parse_november


class OriginalStationReplayTests(unittest.TestCase):
    def test_byte_exact_archive_and_1963_precipitation(self):
        with tempfile.TemporaryDirectory() as d:
            p = recover(Path(d) / 'station.dly')
            data = p.read_bytes()
            self.assertEqual(len(data), ORIGINAL_BYTES)
            self.assertEqual(hashlib.sha256(data).hexdigest(), SHA256)
            self.assertEqual(len(parse_november(data, 'BR048158910')), 3)

    def test_modified_source_is_detected_even_with_valid_gzip(self):
        payload = gzip.decompress(base64.b64decode(''.join(p.read_text().strip() for p in PARTS)))
        modified = payload[:258481] + b' ' + payload[258482:]
        self.assertNotEqual(modified, payload)
        with tempfile.TemporaryDirectory() as d:
            enc = base64.b64encode(gzip.compress(modified)).decode()
            p = Path(d) / 'repacked.b64'
            p.write_text(enc)
            with self.assertRaisesRegex(ValueError, 'source SHA-256 mismatch'):
                recover(Path(d) / 'result.dly', [p])

    def test_missing_piece_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises((ValueError, EOFError, OSError)):
                recover(Path(d) / 'result.dly', PARTS[:2])


if __name__ == '__main__':
    unittest.main()
