"""C241-T6: adversarial decimal/IEEE754 tests with explicitly synthetic rows."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tle_numeric_precision_audit import (
    EXPECTED_TYPES, NOT_IN_NUMERIC_MIRROR, TLE_FIELDS, audit_numeric_table,
    candidate_token, cast_stored, verify_schema,
)


class FakeField:
    def __init__(self, name, kind):
        self.name = name
        self.type = kind


class FakeTable:
    def __init__(self, rows, schema=None):
        self.rows = rows
        self.schema = [FakeField(k, v) for k, v in
                       (schema or EXPECTED_TYPES).items()]

    def select(self, columns):
        return self

    def to_pylist(self):
        return self.rows


def synthetic(n, epoch, raan=198.5261):
    return {
        "norad_id": n, "epoch": epoch,
        "inclination": cast_stored(81.8615, "float"),
        "raan": cast_stored(raan, "float"),
        "eccentricity": cast_stored(0.0017147, "float"),
        "arg_perigee": cast_stored(104.7477, "float"),
        "mean_anomaly": cast_stored(255.4423, "float"),
        "mean_motion": 15.74901460,
        "mean_motion_dot": 0.00686563, "bstar": 0.0,
        "intl_designator": "63003 B",
        "altitude_km": cast_stored(351.0, "float"),
    }


class PrecisionAuditTests(unittest.TestCase):
    def test_real_schema_mean_motion_is_double_not_float(self):
        self.assertEqual(EXPECTED_TYPES["raan"], "float")
        self.assertEqual(EXPECTED_TYPES["mean_motion"], "double")
        self.assertTrue(verify_schema(dict(EXPECTED_TYPES)))
        wrong = dict(EXPECTED_TYPES, mean_motion="float")
        with self.assertRaisesRegex(ValueError, "schema Parquet mudou"):
            verify_schema(wrong)
        with self.assertRaisesRegex(ValueError, "schema Parquet mudou"):
            verify_schema({"norad_id": "int32"})

    def test_angular_float32_four_decimals_roundtrip_unique(self):
        for field, value in (("raan", 198.5261), ("inclination", 81.8615),
                             ("arg_perigee", 104.7477), ("mean_anomaly", 255.4423),
                             ("raan", 359.9999), ("raan", 0.0001)):
            dtype, places, _ = TLE_FIELDS[field]
            data = candidate_token(cast_stored(value, dtype), dtype, places)
            with self.subTest(field=field, value=value):
                self.assertTrue(data["grid_roundtrip"])
                self.assertFalse(data["adjacent_grid_collision"])
                self.assertEqual(data["nearest_grid_value"], f"{value:.4f}")

    def test_eccentricity_float32_seven_digits_roundtrip_unique(self):
        result = candidate_token(cast_stored(0.0017147, "float"), "float", 7)
        self.assertEqual(result["nearest_grid_value"], "0.0017147")
        self.assertTrue(result["grid_roundtrip"])
        self.assertFalse(result["adjacent_grid_collision"])

    def test_mean_motion_double_eight_digits_not_fake_float32(self):
        result = candidate_token(15.74901460, "double", 8)
        self.assertEqual(result["nearest_grid_value"], "15.74901460")
        self.assertTrue(result["grid_roundtrip"])
        self.assertFalse(result["adjacent_grid_collision"])
        rounded_binary32 = cast_stored(15.74901460, "float")
        self.assertNotEqual(rounded_binary32, 15.74901460)
        with self.assertRaisesRegex(ValueError, "dtype efetivo"):
            candidate_token(15.74901460, "float", 8)

    def test_off_grid_values_are_reported_not_forged(self):
        value = cast_stored(198.52615, "float")
        status = candidate_token(value, "float", 4)
        self.assertFalse(status["grid_roundtrip"])

    def test_schema_fields_missing_for_original_tle(self):
        self.assertIn("line1_literal", NOT_IN_NUMERIC_MIRROR)
        self.assertIn("line2_checksum_digit", NOT_IN_NUMERIC_MIRROR)
        self.assertIn("revolution_number_at_epoch", NOT_IN_NUMERIC_MIRROR)
        self.assertIn("historical_sensor_ID", NOT_IN_NUMERIC_MIRROR)

    def test_three_objects_and_source_indices_preserved(self):
        dt = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=timezone.utc)
        data = audit_numeric_table(FakeTable([
            synthetic(527, dt), synthetic(528, dt), synthetic(529, dt)
        ]), "synthetic-sha-not-real")
        self.assertEqual(data["rows"], 3)
        self.assertEqual(data["counts"], {"527": 1, "528": 1, "529": 1})
        self.assertEqual(data["per_row"][1]["source_row"], 1)
        self.assertEqual(data["field_counts"]["mean_motion"]["unique_near_grid"], 3)
        self.assertEqual(data["inconsistent_or_ambiguous_fields"], [])
        self.assertEqual(data["original_line1_line2_checksums"], "NOT_AVAILABLE")
        self.assertEqual(data["legacy_RAAN_284_1520_vs_198_5261"], "UNRESOLVED")

    def test_mixed_off_grid_is_not_hidden(self):
        dt = datetime(1963, 10, 27, tzinfo=timezone.utc)
        rows = [synthetic(n, dt) for n in (527, 528, 529)]
        rows[1]["raan"] = cast_stored(198.52615, "float")
        report = audit_numeric_table(FakeTable(rows), "synthetic-sha-not-real")
        self.assertEqual(len(report["inconsistent_or_ambiguous_fields"]), 1)
        self.assertEqual(report["inconsistent_or_ambiguous_fields"][0]["norad_id"], 528)
        self.assertEqual(report["inconsistent_or_ambiguous_fields"][0]["field"], "raan")

    def test_missing_object_fails_closed(self):
        dt = datetime(1963, 10, 27, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, "sem registros"):
            audit_numeric_table(FakeTable([synthetic(528, dt)]), "synthetic")

    def test_nonfinite_and_dtype_mismatch_fail(self):
        for value in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                candidate_token(value, "float", 4)
        with self.assertRaisesRegex(ValueError, "dtype efetivo"):
            candidate_token(198.5261, "float", 4)


if __name__ == "__main__":
    unittest.main()
