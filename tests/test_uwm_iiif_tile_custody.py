"""Offline checks for UWM IIIF full-canvas derivative, never original JP2 proof."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/archives/audit_uwm_iiif_tiles.py"
RECORD = ROOT / "research/geo/uwm_aracaju_se_iiif_tile_custody_2026-11-12.json"
SPEC = importlib.util.spec_from_file_location("uwm_iiif_tile_audit", SCRIPT)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class TileSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_all_native_pixels_covered_exactly_once(self):
        cells = AUDIT.grid()
        self.assertEqual(len(cells), 80)
        self.assertEqual(sum(w * h for _, _, w, h in cells), 9603 * 7783)
        self.assertEqual(cells[0], (0, 0, 1024, 1024))
        self.assertEqual(cells[-1], (9216, 7168, 387, 615))
        self.assertEqual(len({(x, y) for x, y, _, _ in cells}), 80)
        self.assertEqual(AUDIT.validate(self.record), 80)

    def test_first_and_last_source_region_are_reproducible(self):
        self.assertEqual(AUDIT.url_for(AUDIT.grid()[0]),
                         AUDIT.BASE + "0,0,1024,1024/1024,/0/default.jpg")
        self.assertEqual(AUDIT.url_for(AUDIT.grid()[-1]),
                         AUDIT.BASE + "9216,7168,387,615/387,/0/default.jpg")
        self.assertEqual(self.record["tile_hashes_and_lengths_row_major"][0][0],
                         "7586884d6bcce4ea4f98a39821895236d5b58f9b87b651f44f66092c1f7ffc72")
        self.assertEqual(self.record["tile_hashes_and_lengths_row_major"][-1][0],
                         "94fccb886e0c013216ef6822435f66d97296c3a4e7f1f06e7ffb2c72f07ed2ce")

    def test_missing_or_duplicate_tile_rejected(self):
        cut = copy.deepcopy(self.record)
        cut["tile_hashes_and_lengths_row_major"].pop()
        with self.assertRaisesRegex(ValueError, "incomplete"):
            AUDIT.validate(cut)
        dupe = copy.deepcopy(self.record)
        dupe["tile_hashes_and_lengths_row_major"][2] = dupe["tile_hashes_and_lengths_row_major"][1]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            AUDIT.validate(dupe)

    def test_wrong_digest_or_partial_tile_rejected(self):
        tampered = copy.deepcopy(self.record)
        tampered["tile_hashes_and_lengths_row_major"][0][0] = "0"
        with self.assertRaisesRegex(ValueError, "invalid tile digest"):
            AUDIT.validate(tampered)
        tampered = copy.deepcopy(self.record)
        tampered["tile_hashes_and_lengths_row_major"][0][1] = 0
        with self.assertRaisesRegex(ValueError, "missing/truncated"):
            AUDIT.validate(tampered)

    def test_full_jp2_and_1963_polygon_remain_unknown(self):
        self.assertFalse(self.record["original_jp2_full_fixity"])
        self.assertIsNone(self.record["original_jp2_sha256"])
        self.assertIsNone(self.record["legal_boundary_1963"])
        self.assertEqual(self.record["orbital_constraint"], "NOT_ACTIVATED")
        for key, value in [
            ("original_jp2_full_fixity", True),
            ("original_jp2_sha256", "a" * 64),
            ("legal_boundary_1963", [[1, 2]]),
            ("orbital_constraint", "ACTIVATED"),
        ]:
            fake = copy.deepcopy(self.record)
            fake[key] = value
            with self.assertRaises(ValueError):
                AUDIT.validate(fake)

    def test_presentation_and_image_info_different_tile_widths(self):
        self.assertEqual(self.record["presentation_service_tiles_width"], 9603)
        self.assertEqual(self.record["image_info_tiles_width"], 1024)
        fake = copy.deepcopy(self.record)
        fake["presentation_service_tiles_width"] = 1024
        with self.assertRaisesRegex(ValueError, "discrepancy"):
            AUDIT.validate(fake)

    def test_capture_does_not_require_network_during_unit_tests(self):
        with patch.object(AUDIT, "get", side_effect=AssertionError("no network")):
            self.assertEqual(AUDIT.validate(self.record), 80)
            self.assertEqual(len(AUDIT.grid()), 80)

    def test_public_custody_domain_only(self):
        with self.assertRaisesRegex(ValueError, "non-custodial"):
            AUDIT.get("https://example.invalid/test")

    def test_jpeg_sof_parser_and_negative_cases(self):
        # Minimal JPEG SOI + SOF0, only the *header* is validated.
        sof = bytes.fromhex("ffd8ffc0001108") + (615).to_bytes(2, "big") + (387).to_bytes(2, "big") + bytes(12)
        self.assertEqual(AUDIT.jpeg_dimensions(sof), (387, 615))
        with self.assertRaisesRegex(ValueError, "not a JPEG"):
            AUDIT.jpeg_dimensions(b"garbage")
        with self.assertRaisesRegex(ValueError, "invalid JPEG segment"):
            AUDIT.jpeg_dimensions(b"\xff\xd8\xff\xc0\x00\x11")


if __name__ == "__main__":
    unittest.main()
