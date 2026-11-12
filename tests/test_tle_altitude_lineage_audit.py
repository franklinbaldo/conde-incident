"""C241-L9: adversarial synthetic examples ONLY; never 1963 observations."""
import csv
import math
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tle_altitude_lineage_audit import (
    CSV_SHA, RADIUS_CANDIDATES_KM, audit, proxy_semimajor_km, summarize,
)
from tle_mean_motion_secant_audit import read_rows

EPOCH = datetime(1963, 1, 1, tzinfo=timezone.utc)


def sample(idx=1, day=0, sat=528, e="0.001", n="15",
           radius=6378.137, kind="mean"):
    a = proxy_semimajor_km(n)
    es = float(e)
    altitude = (a - radius if kind == "mean"
                else a * (1 - es) - radius if kind == "perigee"
                else a * (1 + es) - radius)
    designator = {527: "1963-003A", 528: "1963-003B",
                  529: "1963-003C"}.get(sat, "1963-003D")
    return {
        "source_row": str(idx), "norad_id": str(sat),
        "epoch": (EPOCH + timedelta(days=day)).isoformat(
            timespec="microseconds").replace("+00:00", "Z"),
        "intl_designator": designator,
        "inclination": "81", "raan": "198.5261",
        "eccentricity": str(e), "arg_perigee": "100",
        "mean_anomaly": "200", "mean_motion": str(n),
        "mean_motion_dot": "0.01", "bstar": "0",
        "altitude_km": str(altitude),
    }


class AltitudeLineageControls(unittest.TestCase):
    def test_mean_altitude_numerical_dependence_not_primary_claim(self):
        r = audit([sample()], "SYNTHETIC")
        row = r["per_distinct_epoch"][0]
        self.assertLess(abs(row["reported_minus_proxy_km"][
            "mean_a_minus_radius"]), 1e-6)
        self.assertAlmostEqual(
            row["implied_radius_if_altitude_equals_a_minus_radius_km"],
            6378.137, places=6)
        self.assertEqual(r["source"]["independent_altitude_measurement"],
                         "NOT_ESTABLISHED")
        self.assertEqual(r["lean_4_35_physical_restriction"], "NOT_PROMOTED")

    def test_perigee_altitude_not_confused_with_mean(self):
        row = audit([sample(e="0.02", kind="perigee")],
                    "SYNTHETIC")["per_distinct_epoch"][0]
        self.assertEqual(row["closest_arithmetic_proxy_not_field_identification"],
                         "perigee_a_times_1_minus_e_minus_radius")
        self.assertGreater(abs(row["reported_minus_proxy_km"][
            "mean_a_minus_radius"]), 10)

    def test_apogee_altitude_is_distinct_diagnostic(self):
        row = audit([sample(e="0.03", kind="apogee")],
                    "SYNTHETIC")["per_distinct_epoch"][0]
        self.assertEqual(row["closest_arithmetic_proxy_not_field_identification"],
                         "apogee_a_times_1_plus_e_minus_radius")

    def test_circular_orbit_is_ambiguous_not_proven(self):
        r = audit([sample(e="0")], "SYNTHETIC")
        row = r["per_distinct_epoch"][0]
        # Three proxies at the SAME WGS84 radius coincide for e=0.
        # The separately tested 6371-km candidate must remain distinct.
        wgs84 = {k: v for k, v in row["proxies_km"].items()
                 if k != "perigee_using_mean_earth_radius_6371"}
        self.assertEqual(len(set(wgs84.values())), 1)
        self.assertEqual(len(set(row["proxies_km"].values())), 2)
        self.assertFalse(r["algorithm"]["independent_height_or_observation_claim"])

    def test_changed_reference_radius_gives_constant_but_wrong_radius(self):
        r = audit([sample(1, 0, radius=6371), sample(2, 1, radius=6371)],
                  "SYNTHETIC")
        self.assertEqual(r["overall"]["constant_radius_2km_spread_diagnostic"],
                         "NUMERICALLY_COMPATIBLE_NOT_PROVEN_DERIVED")
        self.assertAlmostEqual(r["overall"]["implied_radius_range_km"][0],
                               6371, places=6)
        self.assertNotEqual(RADIUS_CANDIDATES_KM["mean_earth"],
                            RADIUS_CANDIDATES_KM["WGS84_equatorial"])

    def test_perigee_6371_formula_can_match_without_etl_custody(self):
        r = audit([sample(1, 0, kind="perigee", radius=6371),
                   sample(2, 1, kind="perigee", radius=6371)],
                  "SYNTHETIC")
        self.assertEqual(r["overall"][
            "perigee_6371_numerical_match_at_0_1km_not_ETL_proof"], 2)
        self.assertLess(r["overall"]["perigee_implied_radius_spread_km"],
                        1e-6)
        self.assertAlmostEqual(
            r["overall"]["perigee_implied_radius_range_km"][0],
            6371, places=6)
        self.assertTrue(r["algorithm"][
            "perigee_6371_is_only_a_candidate_formula"])
        self.assertEqual(r["source"]["ETL_formula_for_altitude_km"],
                         "NOT_VERIFIED")
        self.assertEqual(r["constraint_link"]["state"], "CONNECTED_PENDING_CALIBRATION")
        self.assertIsNone(r["constraint_link"]["sensor_error_sigma_km"])
        self.assertIsNone(r["constraint_link"]["physical_frame"])
        self.assertEqual(r["constraint_link"]["lean_4_35_0_physical_predicate"], "NOT_PROMOTED")

    def test_nonconstant_radius_is_reported_not_hidden(self):
        r = audit([sample(1, 0), sample(2, 1, radius=6350)],
                  "SYNTHETIC")
        self.assertEqual(r["overall"]["constant_radius_2km_spread_diagnostic"],
                         "NOT_COMPATIBLE_AT_THIS_DIAGNOSTIC_THRESHOLD")

    def test_same_epoch_duplicates_preserve_indices_but_not_independence(self):
        r = audit([sample(1), sample(2), sample(3, day=1)], "SYNTHETIC")
        self.assertEqual(r["source_rows_total"], 3)
        self.assertEqual(r["distinct_catalog_epochs"], 2)
        self.assertEqual(r["per_distinct_epoch"][0]["source_rows"], [1, 2])
        self.assertIn("528:1963-01-01", next(iter(r[
            "duplicate_rows_not_independent"].keys())))

    def test_duplicate_same_epoch_changed_altitude_rejected(self):
        a, b = sample(1), sample(2)
        b["altitude_km"] = "0"
        with self.assertRaisesRegex(ValueError, "contradictory altitude_km"):
            audit([a, b], "SYNTHETIC")

    def test_conflicting_state_duplicate_rejected_upstream(self):
        a, b = sample(1), sample(2)
        b["raan"] = "201"
        with self.assertRaisesRegex(ValueError, "contradictory"):
            audit([a, b], "SYNTHETIC")

    def test_missing_nonfinite_altitude_and_invalid_elements_rejected(self):
        for badval in (None, "NaN", "Infinity", "-Infinity", "oops"):
            with self.subTest(value=badval):
                s = sample()
                s["altitude_km"] = badval
                with self.assertRaisesRegex(ValueError,
                                            "altitude_km"):
                    audit([s], "SYNTHETIC")
        for field, value in (("eccentricity", "-0.1"),
                             ("eccentricity", "1"),
                             ("inclination", "200")):
            s = sample()
            s[field] = value
            with self.assertRaisesRegex(ValueError,
                                        "inclination/eccentricity"):
                audit([s], "SYNTHETIC")

    def test_rows_out_of_scope_and_epoch_mutation_rejected(self):
        with self.assertRaisesRegex(ValueError, "catalog"):
            audit([sample(sat=530)], "SYNTHETIC")
        s = sample()
        s["epoch"] = "1963-01-01T00:00:00.000001Z"
        with self.assertRaisesRegex(ValueError, "grid"):
            audit([s], "SYNTHETIC")

    def test_pinned_counts_distinct_and_sha_gate(self):
        with self.assertRaisesRegex(ValueError, "row counts"):
            audit([sample()], "SYNTHETIC", counts={528: 45})
        with self.assertRaisesRegex(ValueError, "distinct"):
            audit([sample()], "SYNTHETIC", distinct={528: 45})
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "synthetic.csv"
            with path.open("w", newline="", encoding="utf-8") as fd:
                w = csv.DictWriter(fd, fieldnames=list(sample().keys()),
                                   lineterminator="\n")
                w.writeheader()
                w.writerow(sample())
            with self.assertRaisesRegex(ValueError, "SHA256"):
                read_rows(path)
            rows, sha = read_rows(path, enforce_sha=False)
            self.assertNotEqual(sha, CSV_SHA)
            self.assertEqual(len(rows), 1)

    def test_three_catalogs_kept_separate_and_physical_limit(self):
        r = audit([sample(1, sat=527), sample(2, sat=528),
                   sample(3, sat=529)], "SYNTHETIC")
        self.assertEqual(r["distinct_catalog_epochs"], 3)
        self.assertEqual(set(r["by_norad"]), {"527", "528", "529"})
        self.assertEqual(r["by_norad"]["528"]["distinct_epochs"], 1)
        self.assertEqual(r["source"]["ETL_formula_for_altitude_km"],
                         "NOT_VERIFIED")
        self.assertEqual(r["raan_198_5261_vs_284_1520"],
                         "UNRESOLVED_PRIMARY_ORIGIN")
        self.assertEqual(r["conde_impact"], "INDETERMINATE")
        self.assertEqual(summarize([], 0)["distinct_epochs"], 0)


if __name__ == "__main__":
    unittest.main()
