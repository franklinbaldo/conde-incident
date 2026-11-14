"""G54: conditional synthetic counterexamples, never historical optical samples."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from iers_1963_frame import EOP, TIME
from iers_1963_optical import forward_optical, station_itrs_km, forward_source_bound_optical
from iers_1963_optical_residual import compare_geometric_gcrs
from iers_1963_teme import matrices_at

UTC = "1963-11-08T12:00:00Z"
DOCUMENT = b"G54 synthetic mathematical source integrity check; NOT a 1963 film."


class G54OpticalResidual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        filename = os.environ.get("IERS_1963_SOURCE")
        if not filename:
            raise RuntimeError("Authentic IERS_1963_SOURCE required, no fake fixtures")
        source = Path(filename).read_bytes()
        eop = json.loads((ROOT / EOP).read_text())
        times = json.loads((ROOT / TIME).read_text())
        m = matrices_at(UTC, eop, times)
        station = m["gcrs_to_itrs"].T @ station_itrs_km(0, 0, 0)
        # Synthetic state: geometric GCRS RA near 360-degree boundary.
        u = np.array([math.cos(math.radians(0.01)), -math.sin(math.radians(0.01)), 0.])
        state = m["teme_to_gcrs"].T @ (station + 1500 * u)
        cls.STATE_SOURCE = json.dumps({
            "schema": "TEME_POSITION_ONLY_V1",
            "object_id": "SYNTHETIC_ONLY_NOT_528", "epoch_utc": UTC,
            "frame": "TEME", "teme_position_km": state.tolist(),
            "record_class": "SYNTHETIC_SCENARIO",
        }, sort_keys=True).encode()
        cls.prediction = forward_source_bound_optical(
            source, eop, times, UTC, cls.STATE_SOURCE,
            "urn:synthetic:g56:teme-state", 0, 0, 0)

    def datum(self):
        p = self.prediction
        return {
            "object_id": "SYNTHETIC_ONLY_NOT_528",
            "station_id": "WGS84_SCENARIO_ONLY",
            "document_uri": "urn:synthetic:g54:mathematical-fixture",
            "document_sha256": hashlib.sha256(DOCUMENT).hexdigest(),
            "frame": "GCRS",
            "angle_type": "INSTANTANEOUS_GEOMETRIC_NOT_APPARENT_FK4",
            "epoch_utc": UTC,
            "station_wgs84_geodetic": copy.deepcopy(p["station_wgs84_geodetic"]),
            "right_ascension_deg": p["right_ascension_deg"],
            "declination_deg": p["declination_deg"],
            "instrument_covariance_basis": "PREDICTED_GCRS_TANGENT_EAST_NORTH",
            "instrument_covariance_arcsec2": [[4., 0.], [0., 9.]],
        }

    def test_exact_zero_and_never_historical_holdout(self):
        got = compare_geometric_gcrs(self.prediction, self.datum(), DOCUMENT, self.STATE_SOURCE)
        self.assertAlmostEqual(got["squared_mahalanobis_2d"], 0., places=15)
        self.assertEqual(got["historical_holdout"], "NOT_RUN")
        self.assertEqual(got["comparison_status"], "CONDITIONAL_GEOMETRIC_ONLY")
        self.assertEqual(got["impact_inference"], "NOT_SUPPORTED")
        self.assertEqual(got["document_sha256_verified"], hashlib.sha256(DOCUMENT).hexdigest())

    def test_ra_wrap_and_tangent_units_one_arcsecond(self):
        d = self.datum()
        self.assertGreater(d["right_ascension_deg"], 359.9)
        d["right_ascension_deg"] = (d["right_ascension_deg"] + 1./3600) % 360
        got = compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        self.assertAlmostEqual(got["residual_east_north_arcsec"][0], 1, places=6)
        self.assertAlmostEqual(got["residual_east_north_arcsec"][1], 0, places=7)
        self.assertAlmostEqual(got["squared_mahalanobis_2d"], .25, places=5)

    def test_covariance_combination_and_correlations(self):
        d = self.datum()
        p = copy.deepcopy(self.prediction)
        conv = (180*3600/math.pi)**2
        p["state_only_angular_covariance_rad2"] = [[1/conv, 0], [0, 1/conv]]
        d["right_ascension_deg"] = (d["right_ascension_deg"] + 1./3600) % 360
        got = compare_geometric_gcrs(p, d, DOCUMENT, self.STATE_SOURCE)
        self.assertAlmostEqual(got["combined_covariance_arcsec2"][0][0], 5, places=10)
        self.assertAlmostEqual(got["combined_covariance_arcsec2"][1][1], 10, places=10)
        self.assertAlmostEqual(got["squared_mahalanobis_2d"], .2, places=5)
        d["instrument_covariance_arcsec2"] = [[4, 5], [5, 4]]
        with self.assertRaisesRegex(ValueError, "positive definite"):
            compare_geometric_gcrs(p, d, DOCUMENT, self.STATE_SOURCE)

    def test_historical_catalogues_and_clock_bias_fail_closed(self):
        d = self.datum()
        for frame, angle in [("FK4_B1950", d["angle_type"]), ("GCRS", "APPARENT"),
                             ("ICRS", d["angle_type"]), ("TEME", d["angle_type"])]:
            bad = copy.deepcopy(d)
            bad["frame"], bad["angle_type"] = frame, angle
            with self.subTest(frame=frame, angle=angle), self.assertRaisesRegex(ValueError, "explicit conversion"):
                compare_geometric_gcrs(self.prediction, bad, DOCUMENT, self.STATE_SOURCE)
        d["epoch_utc"] = "1963-11-08T12:00:01Z"
        with self.assertRaisesRegex(ValueError, "clock bias"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)

    def test_instrument_error_basis_cannot_be_assumed(self):
        d = self.datum()
        del d["instrument_covariance_basis"]
        with self.assertRaisesRegex(ValueError, "basis"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d["instrument_covariance_basis"] = "RAW_RA_DEC"
        with self.assertRaisesRegex(ValueError, "basis"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)

    def test_document_digest_station_and_source_required(self):
        d = self.datum()
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT+b"X", self.STATE_SOURCE)
        with self.assertRaisesRegex(ValueError, "source bytes"):
            compare_geometric_gcrs(self.prediction, d, b"", self.STATE_SOURCE)
        d["station_wgs84_geodetic"]["longitude_deg"] = .001
        with self.assertRaisesRegex(ValueError, "station differs"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d = self.datum()
        d["station_id"] = ""
        with self.assertRaisesRegex(ValueError, "provenance"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)

    def test_bad_angular_covariances_and_large_offsets(self):
        cases = [
            ([[1., 2.], [2., 1.]], "positive definite"),
            ([[1., .1], [.2, 1.]], "symmetric"),
            ([[0., 0.], [0., 0.]], "positive definite"),
            ([[-1., 0.], [0., 4.]], "positive semidefinite"),
            ([[math.nan, 0.], [0., 1.]], "finite"),
        ]
        for matrix, error in cases:
            d = self.datum()
            d["instrument_covariance_arcsec2"] = matrix
            with self.subTest(matrix=matrix), self.assertRaisesRegex(ValueError, error):
                compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d = self.datum()
        d["right_ascension_deg"] = (d["right_ascension_deg"]+6) % 360
        with self.assertRaisesRegex(ValueError, "exceeds 5 degrees"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d = self.datum()
        d["right_ascension_deg"] = 360.
        with self.assertRaisesRegex(ValueError, "normalized domain"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        # The G52 scale-trap: a huge marginal must not mask a negative
        # one of another physical scale or a malformed off-diagonal.
        d = self.datum()
        d["instrument_covariance_arcsec2"] = [[1e12, 0], [0, -1e-7]]
        with self.assertRaisesRegex(ValueError, "positive semidefinite"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d["instrument_covariance_arcsec2"] = [[1e12, 1e-9], [0., 1e-12]]
        with self.assertRaisesRegex(ValueError, "symmetric"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        p = copy.deepcopy(self.prediction)
        p["state_only_angular_covariance_rad2"] = [[1e-10, 0], [0, -1e-10]]
        with self.assertRaisesRegex(ValueError, "positive semidefinite"):
            compare_geometric_gcrs(p, self.datum(), DOCUMENT, self.STATE_SOURCE)


    def test_g56_cross_object_mislabelling_is_rejected(self):
        d = self.datum()
        d["object_id"] = "529_INSTEAD_OF_SYNTHETIC"
        with self.assertRaisesRegex(ValueError, "object identities differ"):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE)

    def test_g56_unbound_prediction_cannot_claim_target(self):
        p = copy.deepcopy(self.prediction)
        del p["state_source_binding"]
        with self.assertRaisesRegex(ValueError, "source-bound TEME"):
            compare_geometric_gcrs(p, self.datum(), DOCUMENT, self.STATE_SOURCE)

    def test_g56_original_orbit_bytes_cannot_be_substituted(self):
        with self.assertRaisesRegex(ValueError, "source digest mismatch"):
            compare_geometric_gcrs(self.prediction, self.datum(), DOCUMENT,
                                   self.STATE_SOURCE + b" ")
        with self.assertRaisesRegex(ValueError, "source bytes required"):
            compare_geometric_gcrs(self.prediction, self.datum(), DOCUMENT, b"")

    def test_g56_input_epoch_and_cartesian_position_cannot_be_relabelled(self):
        p = copy.deepcopy(self.prediction)
        p["epoch_utc"] = "1963-11-08T12:00:01Z"
        with self.assertRaisesRegex(ValueError, "input and predicted UTC"):
            compare_geometric_gcrs(p, self.datum(), DOCUMENT, self.STATE_SOURCE)
        p = copy.deepcopy(self.prediction)
        p["input_teme_position_km"][0] += 1.0
        with self.assertRaisesRegex(ValueError, "coordinates differ"):
            compare_geometric_gcrs(p, self.datum(), DOCUMENT, self.STATE_SOURCE)

    def test_g56_duplicate_source_keys_and_nonfinite_input_rejected(self):
        good = json.loads(self.STATE_SOURCE)
        forged = self.STATE_SOURCE[:-1] + b',"object_id":"NORAD528"}'
        from iers_1963_optical import decode_source_bound_state
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            decode_source_bound_state(forged)
        for value in [True, "1", float("inf")]:
            corrupt = copy.deepcopy(good)
            corrupt["teme_position_km"][0] = value
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                decode_source_bound_state(json.dumps(corrupt).encode())

    def test_g56_source_evidence_tier_does_not_promote_synthetic_to_historical(self):
        got = compare_geometric_gcrs(self.prediction, self.datum(), DOCUMENT,
                                     self.STATE_SOURCE)
        self.assertEqual(got["state_source_class"], "SYNTHETIC_SCENARIO")
        self.assertEqual(got["historical_holdout"], "NOT_RUN")
        self.assertEqual(got["object_binding"],
                         "ORIGINAL_TEME_STATE_BYTES_AND_ID_MATCHED_NOT_HISTORICALLY_VERIFIED")


if __name__ == "__main__":
    unittest.main()
