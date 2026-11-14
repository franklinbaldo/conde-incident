"""Adversarial tests of conditional plane geometry, never an impact likelihood."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import math
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c241_conditional_plane_windows as m

REPO=Path(__file__).resolve().parents[1]


def state(raan=198.5, inc=81.86, n=15.749):
    return {'source_row':528, 'epoch':datetime(1963,10,27,14,40,tzinfo=timezone.utc),
            'raan':raan,'inclination':inc,'mean_motion':n,'eccentricity':0.0017}


class TestConditionalPlane(unittest.TestCase):
    def test_polar_raan_180_same_unoriented_plane(self):
        lat,theta,raan=map(math.radians,(30,30,17))
        a=m.signed_normal_projection(lat,theta,raan,math.pi/2)
        b=m.signed_normal_projection(lat,theta,raan+math.pi,math.pi/2)
        self.assertAlmostEqual(a,-b,places=12)

    def test_raan_180_not_alias_nonpolar(self):
        lat,theta,raan=map(math.radians,(20,20,60))
        a=m.signed_normal_projection(lat,theta,raan,math.radians(81.86))
        b=m.signed_normal_projection(lat,theta,raan+math.pi,math.radians(81.86))
        self.assertGreater(abs(abs(a)-abs(b)),0.01)

    def test_latitude_above_inclination_never_crosses_plane(self):
        lat=math.radians(70)
        inc=math.radians(30)
        normal=lambda t:m.signed_normal_projection(lat,
                         m.gmst_radians(t),0,inc)
        self.assertFalse(m.roots_for_day(normal,m.START))
        self.assertGreater(math.sin(lat-inc),0)

    def test_time_utc_required(self):
        with self.assertRaises(ValueError):
            m.gmst_radians(datetime(1963,11,6))
        with self.assertRaises(ValueError):
            m.signed_normal_projection(float('nan'),0,0,0)

    def test_epoch_and_secular_slope(self):
        origin=state()
        for drift in (0,-3.35):
            a=m.raan_at(origin,origin['epoch'],drift)
            self.assertAlmostEqual(a,math.radians(origin['raan']),places=11)
            after=m.raan_at(origin,m.START,drift)
            self.assertTrue(math.isfinite(after))
        rows=[{**origin,'epoch':origin['epoch']-timedelta(days=2),'mean_motion':15.7},origin]
        self.assertLess(m.dadt_last_secant(rows),0)
        with self.assertRaises(ValueError):
            m.dadt_last_secant([origin,{**origin,'epoch':origin['epoch']+timedelta(days=2),
                                          'mean_motion':15.70}])

    def test_thresholds_nested_and_closed(self):
        origin=state()
        fn=lambda t:m.cross_km(t,origin,0,-11.7988,-37.621475)
        roots=m.roots_for_day(fn,m.START)
        self.assertGreaterEqual(len(roots),1)
        root=roots[0]
        self.assertAlmostEqual(fn(root),0,delta=0.01)
        spans=[]
        for threshold in m.DISTANCES_KM:
            begin,end=m.interval_for_root(fn,root,threshold)
            spans.append((end-begin).total_seconds())
            self.assertAlmostEqual(abs(fn(begin)),threshold,delta=.05)
            self.assertAlmostEqual(abs(fn(end)),threshold,delta=.05)
        self.assertLess(spans[0],spans[1])
        self.assertLess(spans[1],spans[2])

    def test_date_readings_do_not_invent_instant(self):
        self.assertEqual(m.cutoff_for(637,'UTC_CIVIL_DAY'),
                         datetime(1963,11,8,tzinfo=timezone.utc))
        self.assertEqual(m.cutoff_for(637,'BAHIA_CIVIL_DAY'),
                         datetime(1963,11,8,3,tzinfo=timezone.utc))
        self.assertEqual(m.cutoff_for(528,'BAHIA_CIVIL_DAY'),
                         datetime(1963,11,9,3,tzinfo=timezone.utc))
        self.assertNotEqual(m.cutoff_for(528,'BAHIA_CIVIL_DAY'),
                            m.cutoff_for(637,'BAHIA_CIVIL_DAY'))

    def test_centro_not_geocoded_vila_camera_is_modern(self):
        lat,lon,name,sha=m.source_point(REPO)
        self.assertAlmostEqual(lat,-11.7988)
        self.assertAlmostEqual(lon,-37.621475)
        self.assertTrue(name.startswith('CGEO15'))
        self.assertEqual(len(sha),64)

    def test_reject_mutated_geographic_role(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for file in (m.CAMERA_FILE,m.GEO_FILE,m.CENTRO_VILA_FILE):
                source=REPO/file
                target=root/file
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(source.read_bytes())
            import json
            path=root/m.CAMERA_FILE
            data=json.loads(path.read_text())
            data['captured_images'][0]['camera_point_from_commons']['srs_usable_for_1963']=True
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                m.source_point(root)

    def test_reject_fake_parquet_before_extract(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'fake.parquet'
            path.write_bytes(b'PAR1changed')
            with self.assertRaisesRegex(ValueError,'SHA mismatch'):
                m.extract_pinned(path)

    def test_curves_empty_after_truncation(self):
        cfg={'lat':-11.7988,'lon':-37.621475,'origin':state(),'dadt':0}
        result=m.sensitivity_one_day(cfg,datetime(1963,11,9,tzinfo=timezone.utc),
                                     528,[0.0]*m.DRAW_COUNT)
        self.assertEqual(result['UTC_CIVIL_DAY_valid_rows'],0)
        self.assertEqual(result['BAHIA_CIVIL_DAY_valid_rows'],60)
        result=m.sensitivity_one_day(cfg,datetime(1963,11,9,tzinfo=timezone.utc),
                                     637,[0.0]*m.DRAW_COUNT)
        self.assertEqual(len(result['matrix_minute_of_day_then_dist50_scales123_dist100_scales123_dist200_scales123']),0)


if __name__=='__main__':
    unittest.main()
