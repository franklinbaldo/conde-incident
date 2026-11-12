"""C241-T6: contraprovas de perda de precisao; nenhum vetor sintetico vira NORAD."""
import csv
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tle_float32_alias_audit import (
    SOURCE_CSV_SHA256, aliases_binary32, audit, binary32_bits, bits_to_float,
    read_csv, tle_mean_motion_token,
)

PAIR = ROOT / "research/tle_custody/mirror_528_1963-10-27.tle"
REAL_EPOCH = "1963-10-27T14:40:16.132512Z"


def binary32(value):
    return bits_to_float(binary32_bits(value))


def csv_sample(path, records=None):
    rows = records or [
        {"source_row": 7, "norad_id": 527, "epoch": "1963-10-01T00:00:00.000000Z",
         "mean_motion": binary32(15.8)},
        {"source_row": 3017, "norad_id": 528, "epoch": REAL_EPOCH,
         "mean_motion": binary32(15.74901460)},
        {"source_row": 10, "norad_id": 529, "epoch": "1963-10-03T00:00:00.000000Z",
         "mean_motion": binary32(15.9)},
    ]
    with path.open("w", encoding="utf-8", newline="") as fd:
        w = csv.DictWriter(fd, fieldnames=("source_row", "norad_id", "epoch", "mean_motion"),
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


class Float32TLECustody(unittest.TestCase):
    def test_literal_motion_has_96_distinct_eight_decimal_aliases(self):
        aliases = aliases_binary32(binary32(15.74901460))
        self.assertEqual(aliases["count"], 96)
        self.assertEqual(aliases["binary32_bits_hex"], "417bfbf7")
        self.assertEqual(aliases["minimum_token"], "15.74901438")
        self.assertEqual(aliases["maximum_token"], "15.74901533")
        self.assertIn(1574901460, aliases["aliases_int"])

    def test_distinct_printable_tle_numbers_have_same_binary32(self):
        a, b = 1574901438, 1574901533
        self.assertNotEqual(tle_mean_motion_token(a), tle_mean_motion_token(b))
        self.assertEqual(binary32_bits(a / 1e8), binary32_bits(b / 1e8))
        self.assertNotEqual(a, b)

    def test_no_false_inversion_of_non_binary32_double(self):
        with self.assertRaisesRegex(ValueError, "nao contem valor binary32 exato"):
            aliases_binary32(15.74901460)

    def test_invalid_fields_fail_not_invent_tle(self):
        for val in (float("nan"), float("inf"), 0, -1, 100, 1e100):
            with self.subTest(val=val), self.assertRaises(ValueError):
                aliases_binary32(val)
        with self.assertRaises(ValueError):
            tle_mean_motion_token(0)
        with self.assertRaises(ValueError):
            tle_mean_motion_token(10_000_000_000)

    def test_synthetic_three_ids_and_real_literal_528_but_not_real_history(self):
        with tempfile.TemporaryDirectory() as td:
            csv_path = Path(td) / "synthetic.csv"
            csv_sample(csv_path)
            rows, digest = read_csv(csv_path, enforce_sha=False)
            report = audit(rows, digest, PAIR)
            self.assertEqual(report["counts"], {"527": 1, "528": 1, "529": 1})
            self.assertEqual(report["literal_528"]["possible_tokens_after_float32"], 96)
            self.assertEqual(report["literal_528"]["source_row"], 3017)
            self.assertEqual(report["literal_528"]["verbatim_mean_motion_token"], "15.74901460")
            self.assertEqual(report["ambiguous_mean_motion_rows"], {"527": 1, "528": 1, "529": 1})
            self.assertEqual(report["source"]["instrumental_origin"], "NOT_VERIFIED")
            self.assertNotIn("PASS_PRIMARY", json.dumps(report))
            self.assertEqual(report["source"]["csv_sha256"], digest)
            self.assertEqual(report["classification"],
                             "DIGITAL_NON_INJECTIVITY_NOT_PRIMARY_TLE_OBSERVATION")

    def test_pinned_csv_hash_required_in_production(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "synthetic.csv"
            csv_sample(path)
            self.assertNotEqual(hashlib.sha256(path.read_bytes()).hexdigest(), SOURCE_CSV_SHA256)
            with self.assertRaisesRegex(ValueError, "SHA256 fixado"):
                read_csv(path)

    def test_duplicate_source_row_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "synthetic.csv"
            records = [
                {"source_row": 1, "norad_id": n, "epoch": REAL_EPOCH,
                 "mean_motion": binary32(15.7490146)} for n in (527, 528, 529)
            ]
            csv_sample(path, records)
            with self.assertRaisesRegex(ValueError, "source_row duplicados"):
                read_csv(path, enforce_sha=False)

    def test_no_incorrect_time_or_catalog(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "synthetic.csv"
            for norad, epoch in ((530, REAL_EPOCH), (528, "1963-10-27T14:40:00"),
                                 (528, "1964-10-27T14:40:00Z"),
                                 (528, "1963-10-27T15:40:00+01:00")):
                rec = [{"source_row": 1, "norad_id": norad, "epoch": epoch,
                        "mean_motion": binary32(15.75)}]
                csv_sample(path, rec)
                with self.subTest(norad=norad, epoch=epoch), self.assertRaises(ValueError):
                    read_csv(path, enforce_sha=False)

    def test_missing_epoch_of_literal_528_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "synthetic.csv"
            csv_sample(path)
            rows, digest = read_csv(path, enforce_sha=False)
            for r in rows:
                if r["norad_id"] == 528:
                    r["epoch_utc"] = "1963-10-26T14:40:16.132512Z"
            with self.assertRaisesRegex(ValueError, "nao corresponde univocamente"):
                audit(rows, digest, PAIR)

    def test_tampered_literal_pair_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "synthetic.csv"
            pair = Path(td) / "forged.tle"
            pair.write_bytes(PAIR.read_bytes() + b"\n")
            csv_sample(path)
            rows, digest = read_csv(path, enforce_sha=False)
            with self.assertRaisesRegex(ValueError, "par literal 528 alterado"):
                audit(rows, digest, pair)

    def test_deterministic_result(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "synthetic.csv"
            csv_sample(path)
            rows, digest = read_csv(path, enforce_sha=False)
            self.assertEqual(
                json.dumps(audit(rows, digest, PAIR), sort_keys=True),
                json.dumps(audit(rows, digest, PAIR), sort_keys=True))


if __name__ == "__main__":
    unittest.main()
