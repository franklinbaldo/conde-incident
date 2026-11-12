"""Traceable quantitative regression for two preserved 1963 evidence entries."""
from __future__ import annotations

from pathlib import Path
from fractions import Fraction
import math
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal" / "scripts"))
from source_observables import (  # noqa: E402
    MATRIX_BLOB_SHA1, pinned_rows, entry_orbit, winds,
    illustrative_descent, crosswalk,
)

MATRIX = ROOT / "research/evidence_matrix_C001-C238_2026-11-11.md"


class PinnedObservablesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = pinned_rows(MATRIX)
        cls.result = crosswalk(MATRIX, 50)

    def test_orbit_fields_come_from_single_secondary_mirror(self):
        x = entry_orbit(self.rows["C179"])
        self.assertAlmostEqual(x["raan_deg_printed"], 198.5261)
        self.assertAlmostEqual(x["inclination_deg"], 81.8615)
        self.assertAlmostEqual(x["eccentricity"], .0017147)
        self.assertAlmostEqual(x["mean_motion_rev_day"], 15.74901460)
        self.assertEqual(x["source_id"], "C179#1")
        self.assertEqual(x["source_type"], "AFSPC_SECONDARY_MIRROR")
        self.assertAlmostEqual(x["derived_mean_motion_rad_s"],
                               15.74901460 * 2 * math.pi / 86400)
        semimajor = x["derived_semimajor_axis_km_kepler_proxy"]
        self.assertAlmostEqual(
            x["derived_mean_motion_rad_s"] ** 2 * semimajor ** 3,
            398600.4418, delta=.000001)
        self.assertTrue(6700 < semimajor < 6750)
        self.assertTrue(300 < x["derived_perigee_altitude_km_kepler_proxy"] < 350)
        self.assertAlmostEqual(x["derived_j2_raan_rate_deg_day_first_order"],
                               -1.173124071, places=7)

    def test_wind_was_measured_at_recife_not_at_conde(self):
        observed = winds(self.rows["C151"])
        self.assertEqual([w["pressure_hpa"] for w in observed],
                         [850, 700, 500, 300, 250])
        self.assertEqual([w["direction_from_deg"] for w in observed],
                         [100, 236, 159, 129, 102])
        self.assertEqual([w["speed_m_s"] for w in observed],
                         [4, 4, 6, 15, 17])
        self.assertEqual([w["pressure_pa"] for w in observed],
                         [85000, 70000, 50000, 30000, 25000])
        self.assertTrue(all(w["source_id"] == "C151#1" for w in observed))
        self.assertAlmostEqual(observed[0]["derived_east_m_s"],
                               -4 * math.sin(math.radians(100)))
        self.assertAlmostEqual(observed[0]["derived_north_m_s"],
                               -4 * math.cos(math.radians(100)))
        self.assertEqual(
            self.result["recife_nominal_1963_11_08_12UTC"]["actual_balloon_release_time"],
            "NOT_RECORDED")

    def test_downward_speed_sensitivity_is_kinematic_only(self):
        observed = winds(self.rows["C151"])
        result50 = illustrative_descent(observed, 50)
        result100 = illustrative_descent(observed, 100)
        self.assertAlmostEqual(result50["derived_time_s"], 188.8)
        self.assertAlmostEqual(result100["derived_time_s"], 94.4)
        self.assertAlmostEqual(result50["derived_east_m"], 2 * result100["derived_east_m"])
        self.assertAlmostEqual(result50["derived_north_m"], 2 * result100["derived_north_m"])
        self.assertAlmostEqual(result50["derived_magnitude_m"], 2 * result100["derived_magnitude_m"])
        self.assertGreater(result50["derived_east_m"], -1500)
        self.assertLess(result50["derived_east_m"], 0)
        self.assertGreater(result50["derived_north_m"], 0)
        self.assertIn("NOT_CONDE", result50["status"])

    def test_zero_negative_infinite_and_nan_speeds_rejected(self):
        for v in [0, -1, float("inf"), float("-inf"), float("nan")]:
            with self.subTest(v=v), self.assertRaises(ValueError):
                illustrative_descent(winds(self.rows["C151"]), v)

    def test_snapshot_mutation_fails_closed(self):
        source = MATRIX.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "research.md"
            candidate.write_bytes(source.replace(b"850 hPa 100", b"850 hPa 101", 1))
            with self.assertRaisesRegex(ValueError, "matrix changed"):
                pinned_rows(candidate)
        self.assertEqual(self.result["matrix_git_blob_sha1"], MATRIX_BLOB_SHA1)
        self.assertIn("no NORAD 528 domain reduction",
                      self.result["interpretation"])
        self.assertEqual(set(self.result),
                         {"schema", "matrix_git_blob_sha1", "orbital",
                          "recife_nominal_1963_11_08_12UTC", "illustrative_only",
                          "interpretation"})


if __name__ == "__main__":
    unittest.main()
