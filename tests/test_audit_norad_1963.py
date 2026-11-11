"""Contraprovas sintéticas do auditor, sem alegar observações NORAD."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_norad_1963 import check_numeric, digest, epoch_utc, extract_rows, verified_bytes, tle_checksum, validate_raw_tle


class DummyTable:
    column_names = ["norad_id", "epoch", "inclination", "raan", "eccentricity",
                    "arg_perigee", "mean_anomaly", "mean_motion", "mean_motion_dot",
                    "bstar", "intl_designator", "altitude_km"]
    def __init__(self, records):
        self.records = records
    def select(self, cols):
        return self
    def to_pylist(self):
        return self.records


def record(norad=528, *, raan=198.5261, dt=None):
    return {"norad_id": norad,
            "epoch": dt or datetime(1963, 10, 27, 14, 40, 16, tzinfo=timezone.utc),
            "inclination": 81.8615, "raan": raan, "eccentricity": 0.0017147,
            "arg_perigee": 104.7477, "mean_anomaly": 255.4423,
            "mean_motion": 15.7490146, "mean_motion_dot": 0.00686563,
            "bstar": 0., "intl_designator": "63003 B", "altitude_km": 340.}


class Custody(unittest.TestCase):
    def test_utc_requires_timezone(self):
        with self.assertRaises(ValueError):
            epoch_utc(datetime(1963, 10, 27))

    def test_physical_bounds(self):
        self.assertEqual(check_numeric(record()), [])
        self.assertIn("raan fora de intervalo", check_numeric(record(raan=361)))
        x = record()
        x["eccentricity"] = -0.01
        self.assertIn("eccentricity fora de intervalo", check_numeric(x))

    def test_duplicates_are_retained_and_identified(self):
        rows, meta = extract_rows(DummyTable([record(527), record(528), record(528), record(529)]))
        self.assertEqual(len(rows), 4)
        self.assertEqual(meta["counts"]["528"], 2)
        self.assertEqual(meta["duplicate_epochs"]["528"], 1)
        self.assertTrue(meta["original_tle_line_checksums"].startswith("NOT_RUN"))

    def test_conflicting_raan_never_coalesced(self):
        rows, meta = extract_rows(DummyTable([record(527), record(528), record(528, raan=284.152), record(529)]))
        self.assertEqual([r["raan_deg"] for r in meta["norad_528_oct27_rows"]], [198.5261, 284.152])
        self.assertEqual(meta["reported_difference_deg"], 85.6259)

    def test_column_missing_fails_closed(self):
        class Missing(DummyTable):
            column_names = [x for x in DummyTable.column_names if x != "raan"]
        with self.assertRaisesRegex(ValueError, "colunas ausentes"):
            extract_rows(Missing([]))

    def test_bad_sha_fails_closed(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "fake.parquet"
            file.write_bytes(b"PAR1totally fabricatedPAR1")
            with self.assertRaisesRegex(ValueError, "SHA256 divergente"):
                verified_bytes(file)

    def test_synthetic_tle_pair_checksum_only(self):
        # Apenas strings SINTÉTICAS para verificar o algoritmo; não provêm de rastreio.
        a = "1 00528U 63003B   63300.61129630  .01373126  00000-0  00000-0 0  000"
        b = "2 00528  81.8615 198.5261 0017147 104.7477 255.4423 15.74901460  000"
        self.assertEqual(len(a), 68)
        self.assertEqual(len(b), 68)
        a += str(sum(int(c) if c.isdigit() else (c == "-") for c in a) % 10)
        b += str(sum(int(c) if c.isdigit() else (c == "-") for c in b) % 10)
        self.assertEqual(tle_checksum(a), int(a[-1]))
        self.assertEqual(validate_raw_tle(a, b, 528)["raan_deg"], 198.5261)
        corrupt = b[:-1] + str((int(b[-1])+1) % 10)
        with self.assertRaisesRegex(ValueError, "checksum"):
            validate_raw_tle(a, corrupt, 528)

    def test_digest_reproducible(self):
        self.assertEqual(digest(b"abc")["sha256"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")


if __name__ == "__main__":
    unittest.main()
