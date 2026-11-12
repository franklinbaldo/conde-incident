"""Adversarial offline tests: angular geometry is not the RAAN text difference."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from gaviao_ch12_plane_geometry import (
    LEGACY_BLOB, MIRROR_SHA256, angular_distance, audit, check_checksum,
    git_blob_sha1, parse_elements, parse_epoch, plane_separation,
    proxy_node_rate,
)

# Literal extracts only, copied from explicitly pinned GitHub sources.
# NOT a measurement, synthetic truth, independent witness or new ephemeris.
LEGACY = (
    "1 00528U 63003B   63300.61111111  .00000000  00000-0  00000-0 0  9992",
    "2 00528  81.8615 284.1520 0084200 142.3150 218.4210 15.74900000 45124",
)
MIRROR = (
    "1 00528U 63003  B 63300.61129783  .00686563 +00000-0 +00000-0 0  9990",
    "2 00528 081.8615 198.5261 0017147 104.7477 255.4423 15.74901460043614",
)


class PlaneAuditTests(unittest.TestCase):
    def test_both_checksum_pairs_are_formally_valid(self):
        for line in LEGACY + MIRROR:
            check_checksum(line)

    def test_checksum_mutation_rejected(self):
        bad = MIRROR[1][:68] + str((int(MIRROR[1][68]) + 1) % 10)
        with self.assertRaisesRegex(ValueError, "checksum"):
            check_checksum(bad)

    def test_cannot_turn_syntax_into_authentication(self):
        r = audit(LEGACY, MIRROR)
        self.assertEqual(r["legacy_instrumental_provenance"], "NOT_VERIFIED")
        self.assertEqual(r["secondary_independent_tracking"], "NOT_ESTABLISHED")

    def test_exact_decimal_epochs(self):
        self.assertEqual(parse_epoch(LEGACY[0]).isoformat(), "1963-10-27T14:39:59.999904+00:00")
        self.assertEqual(parse_epoch(MIRROR[0]).isoformat(), "1963-10-27T14:40:16.132512+00:00")

    def test_offset_in_microsecond_precision(self):
        self.assertAlmostEqual(audit(LEGACY, MIRROR)["epoch_difference_seconds"], 16.132608, places=6)

    def test_raan_difference_is_not_plane_angle(self):
        r = audit(LEGACY, MIRROR)
        self.assertAlmostEqual(r["raan_difference_deg"], 85.6259, places=4)
        self.assertAlmostEqual(r["conditional_normal_plane_separation_deg"], 84.56129210269033, places=7)
        self.assertTrue(r["raan_is_not_plane_angle"])

    def test_equatorial_plane_has_no_geometric_raan_separation(self):
        self.assertAlmostEqual(plane_separation(0, 10, 0, 100), 0, places=8)

    def test_polar_orbit_with_equal_inclinations_matches_raan(self):
        self.assertAlmostEqual(plane_separation(90, 10, 90, 95), 85, places=8)

    def test_angular_wrapping(self):
        self.assertAlmostEqual(angular_distance(359, 1), 2.0)

    def test_independent_j2_rate_and_drift(self):
        r = audit(LEGACY, MIRROR)
        self.assertAlmostEqual(r["j2_rates_deg_per_day"][0], -1.17328099195, delta=1e-7)
        self.assertAlmostEqual(r["j2_rates_deg_per_day"][1], -1.17312407103, delta=1e-7)
        self.assertAlmostEqual(r["j2_max_proxy_drift_deg"], 0.0002191, delta=1e-7)
        self.assertGreater(r["minimum_required_rate_deg_per_day"], 458000)

    def test_exclusion_only_conditional_not_impact(self):
        r = audit(LEGACY, MIRROR)
        self.assertEqual(r["offset_only_j2"], "EXCLUDED_CONDITIONALLY")
        self.assertEqual(r["common_reference_frame"], "ASSUMED_ONLY_FOR_GEOMETRIC_CONDITIONAL")
        self.assertEqual(r["lean_physical_constraint"], "NOT_ESTABLISHED")
        self.assertEqual(r["terminal_simulation_with_holdout"], "NOT_RUN")
        self.assertEqual(r["site_of_impact"], "INDETERMINATE")

    def test_zero_offset_fails(self):
        with self.assertRaisesRegex(ValueError, "zero epoch"):
            audit(LEGACY, (LEGACY[0], MIRROR[1]))

    def test_bad_satellite_id_fails(self):
        bad = ("2 00529" + MIRROR[1][7:],)
        with self.assertRaises(ValueError):
            parse_elements(bad[0])

    def test_parsing_impossible_kepler_orbit_fails(self):
        elements = {"inclination": 81.8, "eccentricity": 0.999,
                    "mean_motion": 15.75}
        with self.assertRaisesRegex(ValueError, "pericenter"):
            proxy_node_rate(elements)

    def test_pinning_digest_catches_modified_bytes(self):
        blob = b"source bytes"
        changed = blob + b" "
        self.assertNotEqual(git_blob_sha1(blob), git_blob_sha1(changed))
        self.assertEqual(len(LEGACY_BLOB), 40)
        self.assertEqual(len(MIRROR_SHA256), 64)


if __name__ == "__main__":
    unittest.main()
