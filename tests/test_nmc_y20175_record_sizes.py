import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location("nmc_length", TOOLS / "audit_nmc_y20175_record_sizes.py")
lengths = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lengths)
MANIFEST = ROOT / "research/meteorology/nmc_y20175_cos_payload_sizes_2026-11-12.json"


def mock_two_records():
    sector = bytearray(4096)
    markers = (
        (0, 2),              # BCW -> word 3, with 16 payload bytes.
        (3, (8 << 60) | 2),  # EOR 1 -> word 6, with 16 payload bytes.
        (6, (8 << 60)),      # EOR 2 -> word 7.
        (7, (14 << 60)),     # EOF -> word 8.
        (8, (14 << 60)),     # EOF -> word 9.
        (9, (15 << 60)),     # EOD; all rest zero.
    )
    sector[8:24] = b"abcdefghijklmnop"
    sector[32:48] = b"ABCDEFGHIJKLMNOP"
    for index, value in markers:
        sector[index * 8:index * 8 + 8] = value.to_bytes(8, "big")
    return bytes(sector)


class TestCosSizes(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "synthetic.cos"
        self.bytes = mock_two_records()
        self.path.write_bytes(self.bytes)
        self.custody = {
            "archive_bytes": len(self.bytes),
            "archive_sha256": hashlib.sha256(self.bytes).hexdigest(),
        }

    def tearDown(self):
        self.dir.cleanup()

    def test_replay_two_physical_payloads_not_station_observations(self):
        result = lengths.audit(self.path, self.custody)
        self.assertEqual(result["eor_delimited_payloads"], 2)
        self.assertEqual(result["total_payload_bytes"], 32)
        self.assertEqual(result["length_histogram"], {"16": 2})
        self.assertEqual(result["payload_stream_sha256"], hashlib.sha256(b"abcdefghijklmnopABCDEFGHIJKLMNOP").hexdigest())
        self.assertEqual(result["first_five_eor"][0]["eor_byte_offset"], 24)
        self.assertEqual(result["last_eor"]["byte_offset"], 48)
        self.assertEqual([x["byte_offset"] for x in result["eof_markers"]], [56, 64])
        self.assertIsNone(result["station_day_matches"])
        self.assertIsNone(result["station_day_absences"])
        self.assertEqual(result["on20_station_record_decoding"], "NOT_RUN")

    def test_custody_size_mismatch_fails_closed(self):
        wrong = dict(self.custody, archive_bytes=9999)
        with self.assertRaisesRegex(lengths.BlockingError, "byte count mismatch"):
            lengths.audit(self.path, wrong)

    def test_custody_hash_mismatch_fails_closed(self):
        wrong = dict(self.custody, archive_sha256="0"*64)
        with self.assertRaisesRegex(lengths.BlockingError, "SHA-256 mismatch"):
            lengths.audit(self.path, wrong)

    def test_corrupted_control_chain_fails_closed(self):
        damaged = bytearray(self.bytes)
        damaged[0:8] = (1 << 9 | 2).to_bytes(8, "big")
        self.path.write_bytes(damaged)
        bad = dict(self.custody, archive_sha256=hashlib.sha256(damaged).hexdigest())
        with self.assertRaisesRegex(lengths.BlockingError, "BCW block number mismatch"):
            lengths.audit(self.path, bad)

    def test_disallowed_trailing_unassigned_payload(self):
        damaged = bytearray(self.bytes)
        damaged[64:72] = ((14 << 60) | 1).to_bytes(8, "big")
        damaged[72:80] = b"JUNKJUNK"
        damaged[80:88] = (15 << 60).to_bytes(8, "big")
        self.path.write_bytes(damaged)
        bad = dict(self.custody, archive_sha256=hashlib.sha256(damaged).hexdigest())
        with self.assertRaisesRegex(lengths.BlockingError, "payload after last EOR"):
            lengths.audit(self.path, bad)

    def test_median_floor_index(self):
        self.assertEqual(lengths.percentile([1, 10, 20, 30], 50), 10)
        self.assertEqual(lengths.percentile([1, 10, 20, 30], 100), 30)

    def test_manifest_is_bounded_and_exposes_no_weather_claim(self):
        m = json.loads(MANIFEST.read_text(encoding="utf8"))
        self.assertEqual(m["archive_sha256"], "afec7c443e0c912f8a742738bb82384197baecc7c743cfb00a2a8bda207b5de4")
        self.assertEqual(m["total_payload_bytes"], 116916208)
        self.assertEqual(m["eor_delimited_payloads"], 14889)
        self.assertEqual(sum(int(k)*v for k,v in m["length_histogram"].items()),m["total_payload_bytes"])
        self.assertEqual(sum(m["length_histogram"].values()), 14889)
        self.assertEqual(m["min_payload_bytes"], 1192)
        self.assertEqual(m["max_payload_bytes"], 8000)
        self.assertEqual(m["last_eor"]["byte_offset"], 117264344)
        self.assertEqual(len(m["eof_markers"]), 2)
        self.assertEqual(m["on20_station_record_decoding"], "NOT_RUN")
        self.assertIsNone(m["station_day_matches"])
        self.assertIsNone(m["station_day_absences"])
        self.assertEqual(m["orbital_constraint"], "NOT_ACTIVATED")


if __name__ == "__main__":
    unittest.main()
