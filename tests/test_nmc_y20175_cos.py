import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "audit_nmc_y20175_cos.py"
SPEC = importlib.util.spec_from_file_location("nmc_cos", MODULE)
nmc_cos = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(nmc_cos)
MANIFEST = ROOT / "research" / "meteorology" / "nmc_y20175_cos_structure_2026-11-12.json"


def mock_cos():
    """One synthetic 512-word COS sector: BCW, EOR, EOF, EOD, zero padding."""
    data = bytearray(4096)
    for word_index, word in [
        (0, 2),              # BCW block 0, FWI=2 -> word 3
        (3, (8 << 60) | 3),  # EOR, FWI=3 -> word 7
        (7, (14 << 60) | 1), # EOF, FWI=1 -> word 9
        (9, 15 << 60),       # EOD, FWI=0
    ]:
        data[word_index * 8:word_index * 8 + 8] = word.to_bytes(8, "big")
    return data


class TestNmcCosStructure(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.file = Path(self.tmp.name) / "mock.cos"

    def tearDown(self):
        self.tmp.cleanup()

    def test_good_synthetic_chain(self):
        self.file.write_bytes(mock_cos())
        report = nmc_cos.inspect(self.file)
        self.assertEqual(report["controls"], {"BCW": 1, "EOR": 1, "EOF": 1, "EOD": 1})
        self.assertEqual(report["eor_first_five_byte_offsets"], [24])
        self.assertEqual(report["eod_byte_offset"], 72)
        self.assertEqual(report["station_day_matches"], None)
        self.assertEqual(report["on20_station_record_decoding"], "NOT_RUN")

    def test_rejects_corrupted_block_number(self):
        data = mock_cos()
        data[0:8] = (2 | (1 << 9)).to_bytes(8, "big")
        self.file.write_bytes(data)
        with self.assertRaisesRegex(nmc_cos.BlockingError, "block number"):
            nmc_cos.inspect(self.file)

    def test_rejects_unrecognized_control_type(self):
        data = mock_cos()
        data[24:32] = ((9 << 60) | 3).to_bytes(8, "big")
        self.file.write_bytes(data)
        with self.assertRaisesRegex(nmc_cos.BlockingError, "unrecognized RCW"):
            nmc_cos.inspect(self.file)

    def test_rejects_skipped_or_missing_bcw(self):
        data = mock_cos()
        data[0:8] = (511).to_bytes(8, "big")
        self.file.write_bytes(data)
        with self.assertRaisesRegex(nmc_cos.BlockingError, "missing next control"):
            nmc_cos.inspect(self.file)

    def test_rejects_nonzero_eod_padding(self):
        data = mock_cos()
        data[-1] = 1
        self.file.write_bytes(data)
        with self.assertRaisesRegex(nmc_cos.BlockingError, "padding"):
            nmc_cos.inspect(self.file)

    def test_rejects_wrong_custody_sha(self):
        self.file.write_bytes(mock_cos())
        with self.assertRaisesRegex(nmc_cos.BlockingError, "SHA-256 mismatch"):
            nmc_cos.inspect(self.file, expected_sha256="0" * 64)

    def test_manifest_matches_source_and_does_not_claim_station_matches(self):
        report = json.loads(MANIFEST.read_text(encoding="utf8"))
        self.assertEqual(report["archive_bytes"], 117264384)
        self.assertEqual(report["archive_sha256"], "afec7c443e0c912f8a742738bb82384197baecc7c743cfb00a2a8bda207b5de4")
        self.assertEqual(report["controls"]["BCW"], 28629)
        self.assertEqual(report["controls"]["EOR"], 14889)
        self.assertEqual(report["controls"]["EOF"], 2)
        self.assertEqual(report["controls"]["EOD"], 1)
        self.assertEqual(report["eod_byte_offset"], 117264368)
        self.assertEqual(report["on20_station_record_decoding"], "NOT_RUN")
        self.assertIsNone(report["station_day_matches"])
        self.assertIsNone(report["station_day_absences"])
        self.assertEqual(report["physical_orbital_constraint"], "NOT_ACTIVATED")


if __name__ == "__main__":
    unittest.main()
