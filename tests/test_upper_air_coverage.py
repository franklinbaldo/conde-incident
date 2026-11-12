"""Regression using pinned *real* GDEX API response bytes, not invented soundings."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_upper_air_coverage import parse_uadb_header, validate  # noqa: E402

SNAPSHOT = ROOT / "research/meteorology/gdex_1963_api_snapshot_2026-11-12.json"
MANIFEST = ROOT / "research/meteorology/gdex_uadb_1963_coverage_2026-11-12.json"


class UpperAirCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(SNAPSHOT.read_text())
        cls.manifest = json.loads(MANIFEST.read_text())

    def test_pinned_real_api_bytes_are_verified_and_conservative(self):
        out = validate(self.snapshot, self.manifest)
        self.assertEqual(out["fab_public_files"], 0)
        self.assertEqual(out["verified_uadb_station_files"], 3)
        self.assertEqual(out["1963_station_headers_in_checked_uadb_files"], 0)
        self.assertEqual(out["physical_constraint_status"], "NOT_ACTIVATED")

    def test_date_is_not_a_landing_time_or_verified_launch_clock(self):
        for station, item in self.manifest["uadb_wind_station_files"].items():
            first = parse_uadb_header(item["first_header"], station)
            self.assertEqual(first.isoformat(), item["first_day"])
            self.assertGreater(first.year, 1963)
        # Original archived field 1165 is not HHMM. Only day is trustworthy.
        sample = self.manifest["uadb_wind_station_files"]["83229"]["last_header"]
        self.assertIn(" 1165 ", sample)
        self.assertEqual(parse_uadb_header(sample, "83229").isoformat(), "2018-10-24")

    def test_raw_http_hash_is_required(self):
        forged = copy.deepcopy(self.snapshot)
        forged["responses"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "response hash"):
            validate(forged, self.manifest)

    def test_archive_empty_not_rebranded_as_no_balloon(self):
        forged = copy.deepcopy(self.manifest)
        forged["physical_constraint_status"] = "EXCLUDES_CONDE_BALLOON"
        with self.assertRaisesRegex(ValueError, "archive gap"):
            validate(self.snapshot, forged)

    def test_archive_metadata_cannot_be_promoted_to_independent_wind_observation(self):
        forged = copy.deepcopy(self.manifest)
        forged["new_evidence_occurrences"][0]["instrument_measurement"] = True
        with self.assertRaisesRegex(ValueError, "archive metadata"):
            validate(self.snapshot, forged)

    def test_alternative_file_is_not_an_observed_1963_stations_day(self):
        forged = copy.deepcopy(self.manifest)
        forged["alternative_1963_annual_file"]["station_day_verified"] = True
        with self.assertRaisesRegex(ValueError, "1963 alternative"):
            validate(self.snapshot, forged)


if __name__ == "__main__":
    unittest.main()
