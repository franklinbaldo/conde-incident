"""Contraprovas de representacao TLE em linhas LITERAIS; nao autentica sensor NORAD."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tle_literal_layout import MIRROR_SHA256, audit_pair, audit_literal_file, _checksum

PAIR = ROOT / "research/tle_custody/mirror_528_1963-10-27.tle"


def checksummed(line):
    part = line[:68]
    value = sum((ord(c) - 48 if "0" <= c <= "9" else 1 if c == "-" else 0)
                for c in part) % 10
    return part + str(value)


def mutate(line, start, value):
    return checksummed(line[:start] + value + line[start + len(value):])


class TLEFieldLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first, cls.second = PAIR.read_text(encoding="ascii").splitlines()

    def test_original_bytes_are_pinned_and_not_called_primary(self):
        report = audit_literal_file(PAIR)
        self.assertEqual(hashlib.sha256(PAIR.read_bytes()).hexdigest(), MIRROR_SHA256)
        self.assertEqual(report["catalog"], 528)
        self.assertEqual(report["representation_status"], "SYNTACTICALLY_VALID")
        self.assertEqual(report["epoch_raw"], "63300.61129783")
        self.assertEqual(report["epoch_utc"], "1963-10-27T14:40:16.132512Z")
        self.assertEqual(report["values"]["raan"]["decimal"], "198.5261")
        self.assertEqual(report["values"]["mean_motion"]["unit"], "rev/day")
        self.assertEqual(report["values"]["eccentricity"]["unit"], "dimensionless")
        self.assertEqual(report["line1_other_fields"]["bstar"], "+00000-0")
        self.assertEqual(report["checksums"]["line1"]["printed"], 0)
        self.assertEqual(report["checksums"]["line2"]["printed"], 4)
        self.assertEqual(report["primary_norad_1963_provenance"], "NOT_VERIFIED")
        self.assertFalse(report["other_45_original_pairs_checksummed"])
        self.assertEqual(report["legacy_raan_provenance_conflict"], "UNRESOLVED")

    def test_hash_and_literal_bytes_preserved_in_report(self):
        r = audit_literal_file(PAIR)
        self.assertEqual(r["source"]["sha256"], MIRROR_SHA256)
        self.assertEqual(r["sha256_per_line_no_newline"],
                         [hashlib.sha256(s.encode("ascii")).hexdigest()
                          for s in (self.first, self.second)])

    def test_corrupted_checksum_and_nonascii_fail(self):
        for first, second in (
            (self.first[:-1] + "1", self.second),
            (self.first, self.second[:-1] + "5"),
            (self.first, self.second[:11] + "０" + self.second[12:]),
            (self.first, self.second[:11] + "\t" + self.second[12:]),
        ):
            with self.subTest(first=first[:20], second=second[:20]):
                with self.assertRaises(ValueError):
                    audit_pair(first, second)

    def test_wrong_catalog_and_line_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "catalog"):
            audit_pair(self.first, mutate(self.second, 2, "00529"))
        with self.assertRaisesRegex(ValueError, "prefix"):
            audit_pair(self.first, mutate(self.second, 0, "1"))
        with self.assertRaisesRegex(ValueError, "catalog"):
            audit_pair(self.first, self.second, 527)

    def test_invalid_calendar_with_recomputed_checksum_rejected(self):
        for field in ("000.61129783", "366.61129783", "300.6112978A"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    audit_pair(mutate(self.first, 20, field), self.second)

    def test_fields_not_just_checksum_of_line1(self):
        for index, bad in ((33, " x00686563"), (44, " +00000a0"),
                           (53, " +00000-9"), (62, "X")):
            # BSTAR exponent 9 is syntactically valid; choose invalid letter.
            if index == 53:
                bad = " +00000-x"
            if index == 44:
                bad = " +00000x0"
            if index == 33:
                bad = " x00686563"
            self.assertEqual(len(bad), {33: 10, 44: 8, 53: 8, 62: 1}[index])
            with self.subTest(column=index):
                with self.assertRaisesRegex(ValueError, "field invalid"):
                    audit_pair(mutate(self.first, index, bad), self.second)

    def test_fields_not_just_checksum_of_line2(self):
        for index, bad in ((8, "181.0000"), (17, "360.0000"),
                           (26, "12X4567"), (34, "361.0000"),
                           (43, "361.0000"), (52, "00.00000000")):
            with self.subTest(column=index, value=bad):
                with self.assertRaises(ValueError):
                    audit_pair(self.first, mutate(self.second, index, bad))

    def test_good_checksum_does_not_certify_origin(self):
        # A RAAN arbitrária 284.1520 é um exemplo SINTÉTICO com checksum válido.
        artificial = mutate(self.second, 17, "284.1520")
        r = audit_pair(self.first, artificial)
        self.assertEqual(r["values"]["raan"]["decimal"], "284.1520")
        self.assertEqual(r["primary_norad_1963_provenance"], "NOT_VERIFIED")

    def test_pinned_file_rejects_even_checksummed_replacement(self):
        modified = (self.first + "\n" + mutate(self.second, 17, "284.1520") + "\n")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mirror.tle"
            path.write_text(modified, encoding="ascii")
            with self.assertRaisesRegex(ValueError, "SHA256"):
                audit_literal_file(path)

    def test_schema_json_ascii_text_serializable(self):
        report = audit_literal_file(PAIR)
        data = json.loads(json.dumps(report, sort_keys=True))
        self.assertEqual(data["values"]["inclination"]["unit"], "deg")


if __name__ == "__main__":
    unittest.main()
