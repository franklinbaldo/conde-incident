"""G50: physically typed TEME/ITRS/GCRS state, Jacobian and provenance tests."""
import copy
import json
import math
import os
from pathlib import Path
import sys
import unittest

import erfa
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from iers_1963_frame import EOP, TIME
from iers_1963_intraday import interpolate_at
from iers_1963_teme import (
    frame_operator, jacobian_6d, matrices_at, transform_covariance,
    transform_state,
)


class G50TEMEFrame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("IERS_1963_SOURCE")
        if not source:
            raise RuntimeError("IERS_1963_SOURCE required: do not replace original with a fixture")
        cls.source = Path(source).read_bytes()
        cls.eop = json.loads((ROOT / EOP).read_text())
        cls.times = json.loads((ROOT / TIME).read_text())

    def test_independent_vallado_gstime_polynomial(self):
        # Vallado's published gstime polynomial; independent of erfa.gmst82.
        for utc in ("1963-11-07T06:00:00Z", "1963-11-08T12:00:00Z",
                    "1963-11-08T18:00:00Z"):
            rec = interpolate_at(utc, self.eop, self.times)
            jdut1 = 2400000.5 + rec["mjd_utc"] + rec["ut1_minus_utc_s"] / 86400.
            t = (jdut1 - 2451545.) / 36525.
            sec = (-6.2e-6*t*t*t + 0.093104*t*t +
                   (876600*3600 + 8640184.812866)*t + 67310.54841)
            reference = (sec * math.pi / (180*240)) % (2*math.pi)
            actual = matrices_at(utc, self.eop, self.times)["gmst82_rad"]
            angular_distance = math.remainder(actual-reference, 2*math.pi)
            self.assertLess(abs(angular_distance), 2e-7)

    def test_proper_rotations_and_composition_for_every_interior_anchor(self):
        for utc in ("1963-11-07T06:00:00Z", "1963-11-07T12:00:00Z",
                    "1963-11-07T18:00:00Z", "1963-11-08T00:00:00Z",
                    "1963-11-08T06:00:00Z", "1963-11-08T12:00:00Z",
                    "1963-11-08T18:00:00Z"):
            with self.subTest(utc=utc):
                m = matrices_at(utc, self.eop, self.times)
                for key in ("teme_to_itrs", "teme_to_gcrs"):
                    r = m[key]
                    self.assertLess(np.max(abs(r.T @ r - np.eye(3))), 1e-12)
                    self.assertAlmostEqual(float(np.linalg.det(r)), 1., delta=1e-12)
                self.assertLess(np.max(abs(
                    m["gcrs_to_itrs"] @ m["teme_to_gcrs"] - m["teme_to_itrs"]
                )), 1e-12)

    def test_nonrotating_teme_point_has_nonzero_terrestrial_speed(self):
        # Omit Rdot and a fixed TEME point would appear stationary in ITRS.
        utc = "1963-11-08T12:00:00Z"
        r, dr = frame_operator(utc, self.eop, self.times)
        pos = np.array([7000., 0., 0.])
        v = dr @ pos
        self.assertGreater(float(np.linalg.norm(v)), 0.50)
        self.assertLess(float(np.linalg.norm(v)), 0.52)
        self.assertLess(abs(float(np.dot(r @ pos, v))), 1e-5)

    def test_velocity_matches_direct_position_difference(self):
        utc = "1963-11-08T12:00:00Z"
        pos = np.array([7000., 250., 120.])
        vel = np.array([-0.5, 7.4, 1.])
        from datetime import datetime, timedelta, timezone
        time = datetime(1963, 11, 8, 12, tzinfo=timezone.utc)
        def at(seconds):
            iso = (time + timedelta(seconds=seconds)).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ")
            r = matrices_at(iso, self.eop, self.times)["teme_to_itrs"]
            return r @ (pos + seconds * vel)
        finite_difference = (at(1)-at(-1))/2
        result = transform_state(self.source, self.eop, self.times, utc,
                                 pos, vel)
        self.assertLess(np.linalg.norm(finite_difference -
                        result["velocity_km_s"]), 5e-8)
        naive = matrices_at(utc, self.eop, self.times)["teme_to_itrs"] @ vel
        self.assertGreater(np.linalg.norm(naive - result["velocity_km_s"]), 0.5)

    def test_gcrs_is_not_itrs_and_includes_own_derivative(self):
        utc = "1963-11-08T12:00:00Z"
        f = transform_state(self.source, self.eop, self.times, utc,
                            [7000, 0, 0], [0, 7.5, 0], target="GCRS")
        e = transform_state(self.source, self.eop, self.times, utc,
                            [7000, 0, 0], [0, 7.5, 0], target="ITRS")
        self.assertLess(math.dist(f["position_km"], [7000, 0, 0]), 3000)
        self.assertGreater(math.dist(e["position_km"], [7000, 0, 0]), 1000)
        self.assertNotEqual(f["velocity_km_s"], e["velocity_km_s"])
        self.assertTrue(f["source_sha256_authenticated"])
        self.assertIsNone(f["impact"])
        self.assertEqual(f["historical_holdout_527_529"], "NOT_RUN")

    def test_covariance_cross_blocks_and_roundtrip(self):
        utc = "1963-11-08T12:00:00Z"
        r, dr = frame_operator(utc, self.eop, self.times)
        jac = jacobian_6d(r, dr)
        c = np.diag([0.04, 0.09, 0.16, 1e-6, 2e-6, 3e-6])
        transformed = np.array(transform_covariance(c.tolist(), jac.tolist()))
        self.assertGreater(float(np.linalg.norm(transformed[:3,3:])), 1e-6)
        self.assertLess(np.max(abs(transformed-transformed.T)), 1e-12)
        restored = np.linalg.inv(jac) @ transformed @ np.linalg.inv(jac).T
        self.assertLess(np.max(abs(restored-c)), 1e-12)

    def test_rejects_unauthenticated_bytes_and_tampered_polar_motion(self):
        utc = "1963-11-08T12:00:00Z"
        with self.assertRaises(ValueError):
            transform_state(self.source[:-1]+b"x", self.eop, self.times,
                            utc, [7000,0,0], [0,7,0])
        altered = copy.deepcopy(self.eop)
        altered["sample"][1]["x_arcsec"] += 0.003
        with self.assertRaises(ValueError):
            transform_state(self.source, altered, self.times,
                            utc, [7000,0,0], [0,7,0])

    def test_rejects_bad_states_times_and_frames(self):
        for utc in ("1963-11-07T00:00:00Z", "1963-11-09T00:00:00Z",
                    "1963-11-09T00:00:01Z", "1963-11-08T12:00:00-04:00"):
            with self.subTest(utc=utc), self.assertRaises(ValueError):
                frame_operator(utc, self.eop, self.times)
        for pos, vel in (([float("nan"),0,0], [0,7,0]),
                         ([7000,0,0], [0,float("inf"),0]),
                         ([7000,0], [0,7,0])):
            with self.assertRaises(ValueError):
                transform_state(self.source, self.eop, self.times,
                                "1963-11-08T12:00:00Z", pos, vel)
        for target in ("ECI", "TEME", "ITRF"):
            with self.assertRaises(ValueError):
                frame_operator("1963-11-08T12:00:00Z", self.eop, self.times, target)
        for step in (float("nan"), -1, 0, 11):
            with self.assertRaises(ValueError):
                frame_operator("1963-11-08T12:00:00Z",
                               self.eop, self.times, step_seconds=step)

    def test_rejects_unphysical_covariances(self):
        eye = np.eye(6)
        for cov in (np.ones((6,3)), [[float("nan")]*6]*6,
                    np.diag([-1,1,1,1,1,1])):
            with self.assertRaises(ValueError):
                transform_covariance(cov, eye)
        skew = eye.copy()
        skew[0,1] = 0.2
        with self.assertRaises(ValueError):
            transform_covariance(skew, eye)


if __name__ == "__main__":
    unittest.main()

