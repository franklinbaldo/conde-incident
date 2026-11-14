"""Independent exact-geometry tests for conditional WGS84 ray entry."""
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from optical_wgs84_ray_range import WGS84_RADII_KM, first_earth_entry_km

R = WGS84_RADII_KM[0]


class OpticalRayRange(unittest.TestCase):
    def test_outward_and_tangent_are_unbounded(self):
        self.assertIsNone(first_earth_entry_km((R,0,0),(1,0,0)))
        self.assertIsNone(first_earth_entry_km((R,0,0),(0,1,0)))
        self.assertIsNone(first_earth_entry_km((R+2,0,0),(1,0,0)))

    def test_surface_inward_cutoff_zero_even_if_endpoint_outside(self):
        self.assertEqual(first_earth_entry_km((R,0,0),(-1,0,0)),0)
        self.assertEqual(first_earth_entry_km((R,0,0),(-5,0,0)),0)
        # A far-side endpoint x=-R has the same high altitude as the station;
        # its ray nevertheless crosses the centre of Earth.
        self.assertGreater(abs(-R), 6000)

    def test_elevated_site_negative_elevation_and_cutoff(self):
        site=(R+2,0,0)
        at=lambda dep: (-math.sin(math.radians(dep)),math.cos(math.radians(dep)),0)
        self.assertIsNone(first_earth_entry_km(site,at(.1)))
        self.assertIsNone(first_earth_entry_km(site,at(1.0)))
        entry=first_earth_entry_km(site,at(2.0))
        self.assertIsNotNone(entry)
        self.assertAlmostEqual(entry,67.542593239,places=5)
        self.assertAlmostEqual(first_earth_entry_km(site,at(5.0)),23.4377725988,places=5)

    def test_bounded_segment_and_cutoff_agree(self):
        site=(R+2,0,0)
        direction=(-math.sin(math.radians(2)),math.cos(math.radians(2)),0)
        cutoff=first_earth_entry_km(site,direction)
        self.assertIsNotNone(cutoff)
        # Independent exact 1-D convex quadratic minimum on a finite segment.
        def blocked(length):
            end=tuple(s+length*d for s,d in zip(site,direction))
            sn=[s/r for s,r in zip(site,WGS84_RADII_KM)]
            dn=[(e-s)/r for s,e,r in zip(site,end,WGS84_RADII_KM)]
            t=max(0,min(1,-sum(x*y for x,y in zip(sn,dn))/sum(x*x for x in dn)))
            return sum((x+t*y)**2 for x,y in zip(sn,dn)) < 1-1e-12
        self.assertFalse(blocked(cutoff-1))
        self.assertTrue(blocked(cutoff+1))
        self.assertTrue(blocked(10000))  # Target emerged beyond Earth.

    def test_fail_closed_bad_rays(self):
        for args in [((0,0,0),(1,0,0)), ((R,0,0),(0,0,0)),
                     ((R,0,0),(float('nan'),0,0)), ((R,0),(1,0,0)),
                     ((R,0,0),(1,0,0),(R,-R,R))]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                first_earth_entry_km(*args)


if __name__ == '__main__':
    unittest.main()
