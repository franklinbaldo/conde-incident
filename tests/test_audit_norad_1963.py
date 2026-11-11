"""Contraprovas sintéticas do auditor, sem alegar observações NORAD."""
import sys
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_norad_1963 import (check_numeric, digest, epoch_utc, extract_rows, verified_bytes,
    tle_checksum, validate_raw_tle, tle_epoch_utc, angular_distance_deg,
    compare_secondary_528, legacy_raan_epoch_audit, TLE_EPOCH_QUANTUM_US,
    TLE_EPOCH_HALF_QUANTUM_US, write_outputs)


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

    def test_528_secondary_epoch_decimal_exact(self):
        pair = Path(__file__).resolve().parents[1] / "research/tle_custody/mirror_528_1963-10-27.tle"
        first = pair.read_text(encoding="ascii").splitlines()[0]
        self.assertEqual(tle_epoch_utc(first).isoformat(), "1963-10-27T14:40:16.132512+00:00")
        self.assertEqual(angular_distance_deg(359.99, 0.01), 0.01999999999998181)
        with self.assertRaisesRegex(ValueError, "calendário"):
            tle_epoch_utc(first[:20] + "366.00000000" + first[32:])

    def test_secondary_vs_numeric_same_epoch_independent(self):
        pair = Path(__file__).resolve().parents[1] / "research/tle_custody/mirror_528_1963-10-27.tle"
        dt = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=timezone.utc)
        good = record(dt=dt, raan=198.52610778808594)
        good["source_row"] = 42
        good["epoch"] = epoch_utc(good["epoch"])
        comparison = compare_secondary_528([good], pair)
        self.assertEqual(comparison["status"], "MATCH_WITHIN_ROUNDING")
        self.assertEqual(comparison["matched_records"][0]["source_row"], 42)
        self.assertFalse(comparison["primary_1963_tle_provenance"] == "PASS")
        bad = dict(good, raan=284.152)
        self.assertEqual(compare_secondary_528([bad], pair)["status"], "FIELD_DIVERGENCE")
        self.assertEqual(compare_secondary_528([], pair)["status"], "NO_MATCHING_EPOCH")
        self.assertEqual(compare_secondary_528([good, bad], pair)["status"], "AMBIGUOUS_DUPLICATE_EPOCH")

    def test_epoch_match_uses_half_quantum_not_one_second(self):
        # 8 dígitos de fração de dia = 864us de resolução: 500us já é outra época.
        pair = Path(__file__).resolve().parents[1] / "research/tle_custody/mirror_528_1963-10-27.tle"
        epoch = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=timezone.utc)
        self.assertEqual((TLE_EPOCH_QUANTUM_US, TLE_EPOCH_HALF_QUANTUM_US), (864, 432))
        def shifted(us):
            row = record(dt=epoch + timedelta(microseconds=us))
            row["source_row"] = 99
            row["epoch"] = epoch_utc(row["epoch"])
            return row
        within = compare_secondary_528([shifted(432)], pair)
        self.assertEqual(within["status"], "MATCH_WITHIN_ROUNDING")
        self.assertEqual(within["matched_records"][0]["epoch_delta_microseconds"], 432)
        outside = compare_secondary_528([shifted(433)], pair)
        self.assertEqual(outside["status"], "NEAR_EPOCH_NOT_EQUAL")
        self.assertEqual(outside["matched_records"], [])
        self.assertEqual(outside["nearby_but_distinct_epoch"][0]["epoch_delta_microseconds"], 433)
        self.assertEqual(compare_secondary_528([shifted(1_000_001)], pair)["status"], "NO_MATCHING_EPOCH")

    def test_legacy_raan_value_search_does_not_move_old_epoch(self):
        # Construído, não é a série de 1963: mesmo ângulo em agosto não
        # demonstra que 284.1520 em 27/out veio de agosto.
        date = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=timezone.utc)
        rows = [
            dict(record(528, raan=198.5261, dt=date), source_row=3017),
            dict(record(528, raan=284.152, dt=date-timedelta(days=75)), source_row=2000),
            dict(record(529, raan=284.152, dt=date), source_row=3000),
        ]
        for item in rows:
            item["epoch"] = epoch_utc(item["epoch"])
        res = legacy_raan_epoch_audit(rows, date)
        self.assertEqual(res["status"], "VALUE_SEARCH_ONLY_NOT_PROVENANCE")
        self.assertEqual(res["observed_528_epoch_count_in_mirror"], 2)
        self.assertEqual(res["at_mirror_epoch"][0]["raan_deg"], 198.5261)
        self.assertEqual(res["nearest_raan_regardless_of_epoch"][0]["source_row"], 2000)
        self.assertEqual(res["nearest_raan_regardless_of_epoch"][0]["offset_from_literal_mirror_epoch_days"], -75)
        self.assertTrue(all(x["source_row"] != 3000 for x in res["nearest_raan_regardless_of_epoch"]))

    def test_legacy_raan_audit_has_explicit_empty_result(self):
        date = datetime(1963, 10, 27, tzinfo=timezone.utc)
        res = legacy_raan_epoch_audit([], date)
        self.assertEqual(res["observed_528_epoch_count_in_mirror"], 0)
        self.assertEqual(res["nearest_raan_regardless_of_epoch"], [])
        self.assertEqual(res["at_mirror_epoch"], [])

    def test_same_epoch_distinct_state_is_reported_not_deduplicated(self):
        rows, meta = extract_rows(DummyTable([record(527), record(528), record(528, raan=284.152), record(529)]))
        self.assertEqual(len(rows), 4)
        self.assertEqual(meta["duplicate_epochs"]["528"], 1)
        self.assertEqual(len(meta["duplicate_epoch_conflicts"]), 1)
        self.assertEqual(meta["duplicate_epoch_conflicts"][0]["source_rows"], [1, 2])

    def test_csv_528_ledger_has_own_reproducible_sha256(self):
        rows, meta = extract_rows(DummyTable([record(527), record(528), record(529)]))
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            write_outputs(rows, meta, out, {"sha1": "synthetic", "sha256": "synthetic"})
            csv_data = (out / "norad_528_epochs_1963.csv").read_bytes()
            self.assertEqual(csv_data.count(bytes([10])), 2)
            self.assertNotIn(bytes([92, 110]), csv_data)
            report = json.loads((out / "audit.json").read_text())
            self.assertEqual(report["derived_file_hashes"]["norad_528_epochs_1963.csv"], digest(csv_data))



if __name__ == "__main__":
    unittest.main()
