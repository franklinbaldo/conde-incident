"""Adversarial checks against corrupting NOAA ISD daily surface provenance."""
import copy
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_isd_caravelas_1963 import check, load_snapshot, parse, window_from_gz

class CaravelasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_snapshot()

    def mutate(self, offset, replacement):
        data = bytearray(self.raw)
        data[offset:offset+len(replacement)] = replacement
        return bytes(data)

    def test_full_offline_check(self):
        report = check()
        self.assertEqual([24, 24, 24], [r["rows"] for r in report["daily"].values()])
        self.assertEqual(72, report["source"]["excerpt_rows"])
        self.assertIsNone(report["interpretation"]["numeric_constraint_on_conde"])

    def test_wrong_station_is_not_an_observation(self):
        with self.assertRaisesRegex(ValueError, "station"):
            parse(self.mutate(4, b"829000"))

    def test_quality_flags_are_not_optional(self):
        with self.assertRaisesRegex(ValueError, "quality"):
            parse(self.mutate(69, b"9"))

    def test_missing_sentinel_is_not_numeric(self):
        with self.assertRaisesRegex(ValueError, "missing sentinel"):
            parse(self.mutate(99, b"99999"))

    def test_missing_hour_rejected(self):
        with self.assertRaisesRegex(ValueError, "complete nominal days"):
            parse(b"".join(self.raw.splitlines(keepends=True)[:-1]))

    def test_duplicate_timestamp_rejected(self):
        rows = self.raw.splitlines(keepends=True)
        rows[-1] = rows[0]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            parse(b"".join(rows))

    def test_outside_window_rejected(self):
        with self.assertRaisesRegex(ValueError, "timestamp"):
            parse(self.mutate(15, b"19631110"))

    def test_full_gzip_changed_rejected(self):
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            window_from_gz(b"not a valid NOAA 1963 archive")

    def test_snapshot_missing_hours_not_interpolated(self):
        report = parse(self.raw)
        self.assertAlmostEqual(report["daily"]["1963-11-09"]["surface"]["sea_level_pressure_hPa"]["mean"], 1008.4)
        self.assertIsNone(report["quality"]["measurement_uncertainty"])
        self.assertIsNone(report["quality"]["instrument_identity_1963"])

if __name__ == "__main__":
    unittest.main()
