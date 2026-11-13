"""CGEO-22 metadata integrity, real-file replay optional, and parser negative tests."""
from __future__ import annotations

import copy
import json
import unittest

from tools.cgeo22_jpeg_lineage import (
    APP1_SIZES, CONTRACT, IMAGE_DIMENSIONS, SCAN_SHA, SOURCES,
    compare, parse_jpeg, validate_contract,
)


def marker(code: int, payload: bytes) -> bytes:
    return bytes([255, code]) + (len(payload) + 2).to_bytes(2, "big") + payload


def test_only_jpeg(exif_extra: bytes = b"", entropy: bytes = b"\x52\x42\x10") -> bytes:
    """Small manufactured marker stream for parser MUTATION tests, not an evidence fixture."""
    exif = b"Exif\x00\x00" + (
        b"II\x2a\x00\x08\x00\x00\x00"
        b"\x00\x00"      # IFD0: 0 entries
        b"\x00\x00\x00\x00"
    ) + exif_extra
    sof = b"\x08\x00\x01\x00\x01\x01\x01\x11\x00"
    return (b"\xff\xd8" + marker(0xE0, b"JFIF\x00")
            + marker(0xE1, exif) + marker(0xDB, b"\x00\x01")
            + marker(0xC0, sof) + marker(0xC4, b"\x00\x01")
            + marker(0xDA, b"\x01\x01\x00\x00\x3f\x00")
            + entropy + b"\xff\xd9")


class Cgeo22Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text(encoding="utf8"))

    def test_known_real_source_hashes_and_scan(self):
        validate_contract(self.data)
        self.assertEqual(self.data["result"]["scan_sha256"], SCAN_SHA)
        self.assertEqual(self.data["result"]["exif_payload_bytes"], list(APP1_SIZES))
        for name, (size, sha) in SOURCES.items():
            self.assertEqual((self.data["sources"][name]["byte_size"],
                              self.data["sources"][name]["sha256"]), (size, sha))
        self.assertEqual(self.data["result"]["dimensions_px"], list(IMAGE_DIMENSIONS))

    def test_changed_exif_does_not_erase_scan_identity(self):
        a = test_only_jpeg()
        b = test_only_jpeg(exif_extra=b"extra")
        result = compare(a, b)
        self.assertTrue(result["same_encoded_image"])
        self.assertFalse(result["same_complete_file"])

    def test_changed_scan_bytes_not_same_image(self):
        with self.assertRaisesRegex(ValueError, "scan_sha256"):
            compare(test_only_jpeg(), test_only_jpeg(exif_extra=b"x", entropy=b"\x52\x42\x11"))

    def test_changed_quantization_header_not_same_image(self):
        a = test_only_jpeg()
        b = test_only_jpeg(exif_extra=b"x").replace(b"\xff\xdb\x00\x04\x00\x01",
                                                   b"\xff\xdb\x00\x04\x00\x02")
        with self.assertRaisesRegex(ValueError, "non_app1_header_sha256"):
            compare(a, b)

    def test_corrupt_jpeg_rejected(self):
        source = test_only_jpeg()
        cases = (
            source[2:],
            source[:-2],
            source + b"junk",
            source.replace(b"\xff\xda", b"\xff\xd9", 1),
            source.replace(b"\x52\x42\x10", b"\x52\xff\xda\x10", 1),
        )
        for changed in cases:
            with self.subTest(length=len(changed)):
                with self.assertRaises(ValueError):
                    parse_jpeg(changed)

    def test_invalid_promotion_of_historical_claims_rejected(self):
        for group, field, bad in (
            ("result", "direction_of_copying_proven", True),
            ("result", "original_capture_date_proven", True),
            ("result", "two_independent_photo_captures", True),
            ("result", "whole_files_identical", True),
            ("result", "other_two_2012_2014_photo_pairs_compared", True),
            ("result", "scan_sha256", "0" * 64),
            ("result", "dimensions_px", [160, 116]),
            ("geospatial", "can_constrain_orbital_reentry", True),
            ("geospatial", "historic_center_1963", [-11.8, -37.6]),
            ("geospatial", "point_of_impact", [-11.8, -37.6]),
        ):
            changed = copy.deepcopy(self.data)
            changed[group][field] = bad
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_contract(changed)

    def test_source_hash_tampering_rejected(self):
        for name in SOURCES:
            changed = copy.deepcopy(self.data)
            changed["sources"][name]["sha256"] = "f" * 64
            with self.assertRaises(ValueError):
                validate_contract(changed)


if __name__ == "__main__":
    unittest.main()
