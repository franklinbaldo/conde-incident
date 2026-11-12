"""Falsification tests for historical C151 Recife sounding, no network."""
import hashlib
import base64
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import audit_igra_recife_winds as m


class RecifeWindAuditTests(unittest.TestCase):
    def test_original_bytes_pinned_full_source_recorded(self):
        data=base64.b64decode(m.FIXTURE.read_bytes())
        self.assertEqual(hashlib.sha256(data).hexdigest(),m.EXPECTED_FIXTURE_SHA256)
        d=m.build()
        self.assertEqual(d["source"]["full_station_zip_sha256"],m.ARCHIVE_SHA256)
        self.assertEqual(d["source"]["full_station_zip_bytes"],7834492)
        self.assertEqual(d["source"]["verbatim_1963_profile_sha256"],m.EXPECTED_FIXTURE_SHA256)
        self.assertEqual(d["sounding"]["source_level_count"],26)
        self.assertEqual(d["sounding"]["levels_with_reported_wind"],15)
        self.assertEqual(len(d["missing_wind_levels"]),11)
        self.assertEqual(d["sounding"]["max_reported_wind_height_m_asl"],26693)

    def test_published_json_reproduced_offline(self):
        self.assertEqual(json.loads(m.OUTPUT.read_text()),m.build())

    def test_c151_pressure_level_values_and_heights(self):
        d=m.build()
        by_p={r["pressure_hpa"]:r for r in d["wind_observables_at_recife"]}
        expected={850:(1560,100,4),700:(3197,236,4),500:(5917,159,6),
                  300:(9745,129,15),250:(11007,102,17)}
        for pressure,(height,direction,speed) in expected.items():
            with self.subTest(pressure=pressure):
                row=by_p[pressure]
                self.assertEqual((row["geopotential_height_m_asl"],row["wind_from_deg"],
                                  row["wind_speed_m_s"]),(height,direction,speed))

    def test_meteorological_from_direction_vector(self):
        for row in m.build()["wind_observables_at_recife"]:
            deg=math.radians(row["wind_from_deg"])
            sp=row["wind_speed_m_s"]
            self.assertAlmostEqual(row["eastward_u_m_s"],-sp*math.sin(deg),places=5)
            self.assertAlmostEqual(row["northward_v_m_s"],-sp*math.cos(deg),places=5)
        r=next(x for x in m.build()["wind_observables_at_recife"] if x["pressure_hpa"]==250)
        self.assertLess(r["eastward_u_m_s"],-16.0)

    def test_no_unobserved_epoch_or_conde_position(self):
        r=m.build()
        self.assertIsNone(r["sounding"]["release_time_hhmm"])
        self.assertEqual(r["sounding"]["release_time_raw_missing_code"],9999)
        self.assertEqual(r["station"]["archive_latitude_deg"],-8.05)
        self.assertEqual(r["station"]["archive_longitude_deg_east"],-34.9167)
        self.assertIn("NOT VERIFIED",r["station"]["coordinates_historical_reconstruction"])
        self.assertIn("CONDITIONAL_ONLY",r["physical_links"]["balloon_fragment_drift"])
        self.assertIn("NOT_A_THERMOSPHERIC",r["physical_links"]["density_drag_satellite"])
        self.assertIn("UNKNOWN",r["source"]["instrumental_measurement_error"])

    def test_reject_wrong_nominal_hour_and_invented_release_time(self):
        raw=base64.b64decode(m.FIXTURE.read_bytes())
        for a,b in [(b"1963 11 08 12 9999",b"1963 11 08 00 9999"),
                    (b"1963 11 08 12 9999",b"1963 11 08 12 1159"),
                    (b"BRM00082900",b"BRM00082901"),
                    (b"ncdc6301",b"ncdc6309")]:
            with self.subTest(change=b):
                self.assertIn(a,raw)
                with self.assertRaises(ValueError):m.read_profile(raw.replace(a,b,1))

    def test_reject_invalid_missingness_and_truncated_file(self):
        raw=base64.b64decode(m.FIXTURE.read_bytes())
        with self.assertRaises(ValueError):m.read_profile(raw.rsplit(b"\n",2)[0]+b"\n")
        lines=raw.decode().splitlines(keepends=True)
        target=next(i for i,ln in enumerate(lines) if ln.startswith("10 -9999  85000"))
        ln=lines[target]
        lines[target]=ln[:46]+"-9999"+ln[51:]
        with self.assertRaises(ValueError):m.read_profile("".join(lines).encode())


if __name__=="__main__":unittest.main()
