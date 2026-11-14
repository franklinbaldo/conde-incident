"""G53: independent station geometry / topocentric angular sensitivity tests."""
import copy
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
from iers_1963_optical import forward_optical, station_itrs_km
from iers_1963_teme import matrices_at

UTC = "1963-11-08T12:00:00Z"


class G53StationOptical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src = os.environ.get("IERS_1963_SOURCE")
        if not src:
            raise RuntimeError("Original IERS_1963_SOURCE required; no fake fixtures")
        cls.source = Path(src).read_bytes()
        cls.eop = json.loads((ROOT / EOP).read_text())
        cls.times = json.loads((ROOT / TIME).read_text())
        cls.m = matrices_at(UTC, cls.eop, cls.times)
        cls.site = station_itrs_km(0, 0, 0)
        cls.site_g = cls.m["gcrs_to_itrs"].T @ cls.site

    def call(self, r, lon=0, lat=0, h=0, cov=None):
        return forward_optical(self.source, self.eop, self.times, UTC,
                               r, lon, lat, h, cov)

    def from_gcrs(self, g):
        return self.m["teme_to_gcrs"].T @ np.asarray(g)

    def test_wgs84_independent_equator_pole_and_height(self):
        self.assertAlmostEqual(np.linalg.norm(station_itrs_km(0, 0, 0)), 6378.137, places=9)
        self.assertAlmostEqual(np.linalg.norm(station_itrs_km(0, 90, 0)), 6356.752314245, places=6)
        self.assertAlmostEqual(np.linalg.norm(station_itrs_km(0, 0, 1000)), 6379.137, places=9)
        # No silent lat/lon swapping or degrees/radians confusion.
        self.assertLess(np.linalg.norm(station_itrs_km(90, 0, 0) -
                                       np.array([0, 6378.137, 0])), 1e-8)

    def test_line_of_sight_ra_dec_and_range(self):
        # Earlier synthetic GCRS +X ray passed *through* the Earth. Use
        # the local radial outward direction and verify its celestial angles.
        up = self.site_g / np.linalg.norm(self.site_g)
        target = self.site_g + 1000. * up
        out = self.call(self.from_gcrs(target))
        self.assertAlmostEqual(out["right_ascension_deg"],
                               math.degrees(math.atan2(up[1], up[0])) % 360., places=10)
        self.assertAlmostEqual(out["declination_deg"],
                               math.degrees(math.asin(up[2])), places=10)
        self.assertAlmostEqual(out["range_km"], 1000., places=9)
        self.assertEqual(out["output_frame"], "GCRS")
        self.assertIsNone(out["historical_527_528_529_observation"])
        self.assertEqual(out["historical_holdout"], "NOT_RUN")
        self.assertIsNone(out["wgs84_ray_first_earth_entry_km"])
        self.assertIsNone(out["state_only_angular_covariance_rad2"])
        self.assertIn("FK4_B1950", out["model_omissions"])

    def test_topocentric_parallax_and_overhead_horizon(self):
        up = self.site_g / np.linalg.norm(self.site_g)
        target = self.site_g + 800 * up
        r = self.from_gcrs(target)
        near = self.call(r)
        far = self.call(r, lon=25)
        self.assertAlmostEqual(near["elevation_deg"], 90., places=7)
        self.assertGreater(math.dist(near["unit_line_of_sight_gcrs"],
                                     far["unit_line_of_sight_gcrs"]), .2)
        self.assertLess(far["range_km"], 4000.)

    def test_analytic_angular_jacobian_against_finite_differences(self):
        up = self.site_g / np.linalg.norm(self.site_g)
        r = self.from_gcrs(self.site_g + 1200. * up + [0., 700., 600.])
        out = self.call(r)
        j = np.array(out["angular_jacobian_east_north_rad_per_km_and_km_s"])
        self.assertEqual(j.shape, (2, 6))
        self.assertTrue(np.all(j[:, 3:] == 0.))
        alpha = math.radians(out["right_ascension_deg"])
        delta = math.radians(out["declination_deg"])
        e = np.array([-math.sin(alpha), math.cos(alpha), 0])
        n = np.array([-math.sin(delta)*math.cos(alpha),
                      -math.sin(delta)*math.sin(alpha), math.cos(delta)])
        eps = .0005
        for k in range(3):
            bump = np.eye(3)[k] * eps
            plus = np.array(self.call(r + bump)["unit_line_of_sight_gcrs"])
            minus = np.array(self.call(r - bump)["unit_line_of_sight_gcrs"])
            measured = np.array([e @ (plus-minus), n @ (plus-minus)])/(2*eps)
            self.assertLess(np.max(np.abs(measured-j[:, k])), 3e-12)

    def test_state_covariance_tangent_plane_not_instrument_sigma(self):
        up = self.site_g / np.linalg.norm(self.site_g)
        r = self.from_gcrs(self.site_g + 1000. * up)
        c = np.diag([.01]*3 + [1e-6]*3)
        out = self.call(r, cov=c)
        d = np.array(out["state_only_angular_covariance_rad2"])
        self.assertLess(np.max(np.abs(d-np.eye(2)*1e-8)), 1e-14)
        self.assertLess(abs(float(d[0,1])), 1e-14)
        self.assertEqual(out["historical_holdout"], "NOT_RUN")
        c[3,3] = -1e-6
        with self.assertRaisesRegex(ValueError, "negative marginal"):
            self.call(r, cov=c)

    def from_itrs(self, itrs):
        return self.from_gcrs(self.m["gcrs_to_itrs"].T @ np.asarray(itrs))

    def test_g59_reference_ellipsoid_blocks_solid_earth(self):
        # Same station, satellite on the opposite side of Earth: both
        # endpoints outside the ellipsoid, but the optical ray is occulted.
        with self.assertRaisesRegex(ValueError, "Earth-occluded"):
            self.call(self.from_itrs([-7000., 0., 0.]))
        # A satellite point itself beneath the reference ellipsoid is invalid.
        with self.assertRaisesRegex(ValueError, "Satellite lies inside"):
            self.call(self.from_itrs([6000., 0., 0.]))
        # A 1-degree downward surface ray may emerge from the far side;
        # valid endpoint altitude alone cannot prove visible line of sight.
        a = 6378.137
        downward = np.radians(1.)
        far_side = [a - 2000. * math.sin(downward),
                    2000. * math.cos(downward), 0.]
        with self.assertRaisesRegex(ValueError, "Earth-occluded"):
            self.call(self.from_itrs(far_side))

    def test_g59_tangent_horizon_is_clear_at_sea_level(self):
        a = 6378.137
        got = self.call(self.from_itrs([a, 1000., 0.]))
        self.assertAlmostEqual(got["elevation_deg"], 0., places=8)
        self.assertEqual(got["earth_occultation"],
                         "CLEAR_AGAINST_WGS84_ELLIPSOID_ONLY")
        self.assertEqual(got["historical_holdout"], "NOT_RUN")
        self.assertIn("TERRAIN_AND_OBSERVATION_WEATHER", got["model_omissions"])

    def test_g59_elevated_site_can_see_below_horizontal(self):
        # 2-km-high observer: a -0.1-degree depression does NOT imply
        # solid-Earth occultation. This catches naive elevation < 0 vetoes.
        a = 6378.137
        site = a + 2.
        tilt = math.radians(.1)
        target = [site - 400. * math.sin(tilt),
                  400. * math.cos(tilt), 0.]
        got = self.call(self.from_itrs(target), h=2000)
        self.assertAlmostEqual(got["elevation_deg"], -.1, places=7)
        self.assertEqual(got["earth_occultation"],
                         "CLEAR_AGAINST_WGS84_ELLIPSOID_ONLY")

    def test_polvo_conditional_range_cutoff_not_historical_instrument(self):
        # At 2 km above the equator, -2 degrees crosses the WGS84 ellipsoid
        # after 67.54 km. A 50 km target is visible; farther targets along
        # the SAME ray are occulted, including those beyond the far horizon.
        a = 6378.137
        depression = math.radians(2.)
        near = [a+2.-50.*math.sin(depression), 50.*math.cos(depression), 0.]
        got = self.call(self.from_itrs(near), h=2000)
        self.assertAlmostEqual(got["wgs84_ray_first_earth_entry_km"],
                               67.542593239, places=5)
        self.assertEqual(got["historical_holdout"], "NOT_RUN")
        middle = [a+2.-100.*math.sin(depression), 100.*math.cos(depression), 0.]
        with self.assertRaisesRegex(ValueError, "Satellite lies inside"):
            self.call(self.from_itrs(middle), h=2000)
        # 500 km is past the far exit: the endpoint itself is again outside.
        far = [a+2.-500.*math.sin(depression), 500.*math.cos(depression), 0.]
        with self.assertRaisesRegex(ValueError, "Earth-occluded"):
            self.call(self.from_itrs(far), h=2000)

    def test_g59_source_bound_prediction_rejects_occulted_state(self):
        # A synthetic observed angle can be made to agree exactly with a
        # claimed prediction from the far side; replay must still reject it.
        from iers_1963_optical import forward_source_bound_optical
        state = json.dumps({"schema": "TEME_POSITION_ONLY_V1",
                            "object_id": "SYNTHETIC_OCCULTED_NOT_NORAD",
                            "epoch_utc": UTC, "frame": "TEME",
                            "teme_position_km": self.from_itrs([-7000., 0., 0.]).tolist(),
                            "record_class": "SYNTHETIC_SCENARIO"}).encode()
        with self.assertRaisesRegex(ValueError, "Earth-occluded"):
            forward_source_bound_optical(self.source, self.eop, self.times,
                                         UTC, state, "urn:synthetic:occulted",
                                         0, 0, 0)

    def test_untrusted_source_bad_geometry_and_missing_1963_utc(self):
        up = self.site_g / np.linalg.norm(self.site_g)
        r = self.from_gcrs(self.site_g + 1000. * up)
        with self.assertRaises(ValueError):
            forward_optical(self.source[:-1] + b'X', self.eop, self.times,
                            UTC, r, 0, 0, 0)
        altered = copy.deepcopy(self.eop)
        altered["sample"][1]["x_arcsec"] += .001
        with self.assertRaises(ValueError):
            forward_optical(self.source, altered, self.times, UTC, r, 0, 0, 0)
        with self.assertRaises(ValueError):
            forward_optical(self.source, self.eop, self.times,
                            "1963-11-10T12:00:00Z", r, 0, 0, 0)
        for lon,lat,h in ((180, 0,0), (0, 91,0), (0,0,float('nan')),
                          (0, 0,100000), (0, -91, 0)):
            with self.subTest(lon=lon,lat=lat,h=h), self.assertRaises(ValueError):
                self.call(r,lon,lat,h)
        with self.assertRaisesRegex(ValueError, "Degenerate"):
            self.call(self.from_gcrs(self.site_g))
        with self.assertRaisesRegex(ValueError, "RA undefined"):
            polar_site = self.m["gcrs_to_itrs"].T @ station_itrs_km(0, 80, 0)
            self.call(self.from_gcrs(polar_site + [0.,0.,1000.]), lat=80)


if __name__ == "__main__":
    unittest.main()
