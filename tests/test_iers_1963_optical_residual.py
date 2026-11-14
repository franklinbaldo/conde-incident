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
from iers_1963_optical_residual import compare_geometric_gcrs, EXTRACTION_SCHEMA
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
        cls.IERS_SOURCE = source
        cls.EOP_RECORD = eop
        cls.TIME_RECORD = times
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

    def compare(self, predicted, observed, source_bytes, state_bytes,
                extraction_bytes=None):
        if extraction_bytes is None:
            extraction_bytes = json.dumps({
                "schema": EXTRACTION_SCHEMA, "evidence_class": "SYNTHETIC_SCENARIO",
                "observation": observed,
            }, sort_keys=True).encode()
        return compare_geometric_gcrs(predicted, observed, source_bytes,
                                      state_bytes, extraction_bytes,
                                      self.IERS_SOURCE, self.EOP_RECORD, self.TIME_RECORD)

    def test_g57_extraction_custody_rejects_post_transcription_changes(self):
        d = self.datum()
        extraction = json.dumps({
            "schema": EXTRACTION_SCHEMA, "evidence_class": "SYNTHETIC_SCENARIO",
            "observation": d,
        }, sort_keys=True).encode()
        got = self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE, extraction)
        self.assertEqual(got["extraction_sha256_verified"], hashlib.sha256(extraction).hexdigest())
        self.assertEqual(got["extraction_evidence_class"], "SYNTHETIC_SCENARIO")
        self.assertEqual(got["historical_holdout"], "NOT_RUN")
        for key, value in (("right_ascension_deg", (d["right_ascension_deg"]+0.001)%360),
                           ("declination_deg", d["declination_deg"]+0.001),
                           ("instrument_covariance_arcsec2", [[16., 0.], [0., 9.]]),
                           ("station_id", "DIFFERENT_STATION")):
            changed = copy.deepcopy(d)
            changed[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "differs from original extraction"):
                self.compare(self.prediction, changed, DOCUMENT, self.STATE_SOURCE, extraction)
        bad = extraction.replace(b'"SYNTHETIC_SCENARIO"', b'"PRIMARY_INSTRUMENT"')
        with self.assertRaisesRegex(ValueError, "evidence class"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE, bad)
        duplicate = extraction[:-1] + b',"schema":"GCRS_OPTICAL_EXTRACTION_V1"}'
        with self.assertRaisesRegex(ValueError, "Duplicate optical extraction"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE, duplicate)
        with self.assertRaisesRegex(ValueError, "extraction bytes required"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE, b"")
        with self.assertRaisesRegex(ValueError, "original extraction"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE,
                         extraction.replace(b'"right_ascension_deg"', b'"other_ra"'))

    def test_exact_zero_and_never_historical_holdout(self):
        got = self.compare(self.prediction, self.datum(), DOCUMENT, self.STATE_SOURCE)
        self.assertAlmostEqual(got["squared_mahalanobis_2d"], 0., places=15)
        self.assertEqual(got["historical_holdout"], "NOT_RUN")
        self.assertEqual(got["comparison_status"], "CONDITIONAL_GEOMETRIC_ONLY")
        self.assertEqual(got["impact_inference"], "NOT_SUPPORTED")
        self.assertEqual(got["document_sha256_verified"], hashlib.sha256(DOCUMENT).hexdigest())

    def test_ra_wrap_and_tangent_units_one_arcsecond(self):
        d = self.datum()
        self.assertGreater(d["right_ascension_deg"], 359.9)
        d["right_ascension_deg"] = (d["right_ascension_deg"] + 1./3600) % 360
        got = self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        self.assertAlmostEqual(got["residual_east_north_arcsec"][0], 1, places=6)
        self.assertAlmostEqual(got["residual_east_north_arcsec"][1], 0, places=7)
        self.assertAlmostEqual(got["squared_mahalanobis_2d"], .25, places=5)

    def test_position_only_cannot_smuggle_state_covariance(self):
        d = self.datum()
        p = copy.deepcopy(self.prediction)
        conv = (180 * 3600 / math.pi) ** 2
        p["state_only_angular_covariance_rad2"] = [[1e12 / conv, 0], [0, 1e12 / conv]]
        d["right_ascension_deg"] = (d["right_ascension_deg"] + 1. / 3600) % 360
        with self.assertRaisesRegex(ValueError, "Unbound state covariance"):
            self.compare(p, d, DOCUMENT, self.STATE_SOURCE)
        # Only source-declared instrument covariance contributes.
        got = self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        self.assertAlmostEqual(got["squared_mahalanobis_2d"], .25, places=5)
        self.assertIn("POSITION_ONLY", got["uncertainty_contract"])
        d["instrument_covariance_arcsec2"] = [[4, 5], [5, 4]]
        with self.assertRaisesRegex(ValueError, "positive definite"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)

    def test_g58_predicted_angles_must_match_replayed_state_and_iers(self):
        d = self.datum()
        got = self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        self.assertEqual(got["prediction_binding"],
                         "REPLAYED_FROM_ORIGINAL_TEME_AND_IERS_BYTES")
        for name, shift in (("right_ascension_deg", 1 / 3600),
                            ("declination_deg", 1 / 3600)):
            changed = copy.deepcopy(self.prediction)
            changed[name] += shift
            with self.subTest(name=name), self.assertRaisesRegex(
                    ValueError, "differ from original IERS/state replay"):
                self.compare(changed, d, DOCUMENT, self.STATE_SOURCE)

    def test_g58_original_iers_and_derived_time_records_are_checked(self):
        d = self.datum()
        with self.assertRaises(ValueError):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE,
                json.dumps({"schema": EXTRACTION_SCHEMA,
                            "evidence_class": "SYNTHETIC_SCENARIO",
                            "observation": d}, sort_keys=True).encode(),
                self.IERS_SOURCE+b"X", self.EOP_RECORD, self.TIME_RECORD)
        shifted = copy.deepcopy(self.TIME_RECORD)
        # Prevent a different EOP/time record from changing a prediction without
        # authenticating the same full historical source.
        changed_key = next(iter(shifted))
        shifted[changed_key] = {"tampered": True}
        with self.assertRaises(ValueError):
            compare_geometric_gcrs(self.prediction, d, DOCUMENT, self.STATE_SOURCE,
                json.dumps({"schema": EXTRACTION_SCHEMA,
                            "evidence_class": "SYNTHETIC_SCENARIO",
                            "observation": d}, sort_keys=True).encode(),
                self.IERS_SOURCE, self.EOP_RECORD, shifted)

    def test_historical_catalogues_and_clock_bias_fail_closed(self):
        d = self.datum()
        for frame, angle in [("FK4_B1950", d["angle_type"]), ("GCRS", "APPARENT"),
                             ("ICRS", d["angle_type"]), ("TEME", d["angle_type"])]:
            bad = copy.deepcopy(d)
            bad["frame"], bad["angle_type"] = frame, angle
            with self.subTest(frame=frame, angle=angle), self.assertRaisesRegex(ValueError, "explicit conversion"):
                self.compare(self.prediction, bad, DOCUMENT, self.STATE_SOURCE)
        d["epoch_utc"] = "1963-11-08T12:00:01Z"
        with self.assertRaisesRegex(ValueError, "clock bias"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)

    def test_instrument_error_basis_cannot_be_assumed(self):
        d = self.datum()
        del d["instrument_covariance_basis"]
        with self.assertRaisesRegex(ValueError, "basis"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d["instrument_covariance_basis"] = "RAW_RA_DEC"
        with self.assertRaisesRegex(ValueError, "basis"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)

    def test_document_digest_station_and_source_required(self):
        d = self.datum()
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.compare(self.prediction, d, DOCUMENT+b"X", self.STATE_SOURCE)
        with self.assertRaisesRegex(ValueError, "source bytes"):
            self.compare(self.prediction, d, b"", self.STATE_SOURCE)
        d["station_wgs84_geodetic"]["longitude_deg"] = .001
        with self.assertRaisesRegex(ValueError, "station differs"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d = self.datum()
        d["station_id"] = ""
        with self.assertRaisesRegex(ValueError, "provenance"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)

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
                self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d = self.datum()
        d["right_ascension_deg"] = (d["right_ascension_deg"]+6) % 360
        with self.assertRaisesRegex(ValueError, "exceeds 5 degrees"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d = self.datum()
        d["right_ascension_deg"] = 360.
        with self.assertRaisesRegex(ValueError, "normalized domain"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        # The G52 scale-trap: a huge marginal must not mask a negative
        # one of another physical scale or a malformed off-diagonal.
        d = self.datum()
        d["instrument_covariance_arcsec2"] = [[1e12, 0], [0, -1e-7]]
        with self.assertRaisesRegex(ValueError, "positive semidefinite"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        d["instrument_covariance_arcsec2"] = [[1e12, 1e-9], [0., 1e-12]]
        with self.assertRaisesRegex(ValueError, "symmetric"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)
        p = copy.deepcopy(self.prediction)
        p["state_only_angular_covariance_rad2"] = [[1e-10, 0], [0, -1e-10]]
        with self.assertRaisesRegex(ValueError, "Unbound state covariance"):
            self.compare(p, self.datum(), DOCUMENT, self.STATE_SOURCE)


    def test_g56_cross_object_mislabelling_is_rejected(self):
        d = self.datum()
        d["object_id"] = "529_INSTEAD_OF_SYNTHETIC"
        with self.assertRaisesRegex(ValueError, "object identities differ"):
            self.compare(self.prediction, d, DOCUMENT, self.STATE_SOURCE)

    def test_g56_unbound_prediction_cannot_claim_target(self):
        p = copy.deepcopy(self.prediction)
        del p["state_source_binding"]
        with self.assertRaisesRegex(ValueError, "source-bound TEME"):
            self.compare(p, self.datum(), DOCUMENT, self.STATE_SOURCE)

    def test_g56_original_orbit_bytes_cannot_be_substituted(self):
        with self.assertRaisesRegex(ValueError, "source digest mismatch"):
            self.compare(self.prediction, self.datum(), DOCUMENT,
                                   self.STATE_SOURCE + b" ")
        with self.assertRaisesRegex(ValueError, "source bytes required"):
            self.compare(self.prediction, self.datum(), DOCUMENT, b"")

    def test_g56_input_epoch_and_cartesian_position_cannot_be_relabelled(self):
        p = copy.deepcopy(self.prediction)
        p["epoch_utc"] = "1963-11-08T12:00:01Z"
        with self.assertRaisesRegex(ValueError, "input and predicted UTC"):
            self.compare(p, self.datum(), DOCUMENT, self.STATE_SOURCE)
        p = copy.deepcopy(self.prediction)
        p["input_teme_position_km"][0] += 1.0
        with self.assertRaisesRegex(ValueError, "coordinates differ"):
            self.compare(p, self.datum(), DOCUMENT, self.STATE_SOURCE)

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
        got = self.compare(self.prediction, self.datum(), DOCUMENT,
                                     self.STATE_SOURCE)
        self.assertEqual(got["state_source_class"], "SYNTHETIC_SCENARIO")
        self.assertEqual(got["historical_holdout"], "NOT_RUN")
        self.assertEqual(got["object_binding"],
                         "ORIGINAL_TEME_STATE_BYTES_AND_ID_MATCHED_NOT_HISTORICALLY_VERIFIED")


if __name__ == "__main__":
    unittest.main()
