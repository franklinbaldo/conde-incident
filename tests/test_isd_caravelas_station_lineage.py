"""Adversarial tests: ISD 1963 row metadata versus retrospective NOAA site catalog."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_isd_caravelas_1963 import load_snapshot
from audit_isd_caravelas_station_lineage import (
    HISTORY_ROW, build_report, check, extract_station_history,
    parse_original_rows, parse_station_row, great_circle_km,
)

class StationLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.window = load_snapshot()
        cls.history = HISTORY_ROW.read_bytes()

    def test_offline_manifest_and_graph(self):
        result = check()
        self.assertEqual(result["comparison"]["horizontal_geodesic_separation_km"], 2.136489)
        self.assertEqual(result["comparison"]["elevation_catalog_minus_record_m"], 7.0)
        self.assertIsNone(result["scientific_status"]["active_location_or_drag_constraint"])
        self.assertIsNone(result["scientific_status"]["instrument_position_in_1963"])

    def test_original_encoded_location(self):
        orig = parse_original_rows(self.window)
        self.assertEqual([orig["lat_deg"], orig["lon_deg"], orig["elevation_m"]],
                         [-17.633, -39.25, 4])
        self.assertEqual((orig["rows"], orig["distinct_dates"]), (72, 3))

    def test_retrospective_catalog_location(self):
        cat = parse_station_row(self.history)
        self.assertEqual([cat["lat_deg"], cat["lon_deg"], cat["elevation_m"]],
                         [-17.652, -39.253, 11.0])

    def test_wrong_original_record_position_rejected(self):
        rows = self.window.splitlines(keepends=True)
        rows[0] = rows[0][:28] + b"-17000" + rows[0][34:]
        with self.assertRaisesRegex(ValueError, "multiple"):
            parse_original_rows(b"".join(rows))

    def test_wrong_record_year_rejected(self):
        rows = self.window.splitlines(keepends=True)
        rows[0] = rows[0][:15] + b"19621107" + rows[0][23:]
        with self.assertRaisesRegex(ValueError, "1963"):
            parse_original_rows(b"".join(rows))

    def test_wrong_station_history_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "station history identity"):
            parse_station_row(self.history.replace(b'"834970"', b'"834971"'))

    def test_wrong_station_history_archive_dates_rejected(self):
        with self.assertRaisesRegex(ValueError, "metadata period"):
            parse_station_row(self.history.replace(b'"19610101"', b'"19620101"'))

    def test_wrong_history_checksum_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            extract_station_history(self.history + b"corrupted")

    def test_unverified_coordinates_not_mistaken_for_error_bound(self):
        result = build_report()
        self.assertFalse(result["comparison"]["difference_is_geolocation_error_bound"])
        self.assertFalse(result["comparison"]["station_relocation_proven"])
        self.assertIsNone(result["retrospective_catalog"]["position_epoch_verified"])
        self.assertAlmostEqual(great_circle_km(
            result["original_records"]["reported_position"],
            result["retrospective_catalog"]["reported_position"]), 2.136489261, 6)

if __name__ == "__main__":
    unittest.main()
