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


class RecifeAdjacentDateAuditTests(unittest.TestCase):
    """The existing IGRA CI workflow also exercises the three-day audit."""

    def test_original_neighboring_profiles_pinned_and_all_5_levels(self):
        import audit_igra_recife_window as w
        result = w.build()
        self.assertEqual([x["source_levels"] for x in result["soundings"]], [29, 26, 26])
        self.assertEqual([x["complete_wind_levels"] for x in result["soundings"]], [15, 15, 15])
        self.assertEqual([x["release_time_utc"] for x in result["soundings"]], [None] * 3)
        for day in ("07", "08", "09"):
            raw = w.load_original(day)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), w.DAYS[day][0])
            self.assertEqual(
                len(w.parse_day(raw, day)["standard_pressure_levels"]), 5
            )
        self.assertEqual(
            json.loads(w.OUTPUT.read_text()), result
        )

    def test_real_nominal_date_contrasts_not_zero_or_independent(self):
        import audit_igra_recife_window as w
        result = w.build()
        by_p = {c["pressure_hpa"]: c for c in result["inter_day_at_recife_nominal_date_contrasts"]}
        self.assertAlmostEqual(by_p[850]["day_09_minus_08"]["vector_difference_m_s"], 5.883598)
        self.assertAlmostEqual(by_p[250]["day_07_minus_08"]["vector_difference_m_s"], 8.931830)
        meta = result["methodology"]
        self.assertTrue(meta["comparisons_are_not_calibrated_uncertainty_bounds"])
        self.assertTrue(meta["real_release_times_all_unknown"])
        self.assertTrue(meta["sampling_is_not_spatially_transferable_to_conde"])
        self.assertFalse(meta["balloon_drift_or_impact_location_estimated"])
        self.assertFalse(meta["satellite_thermospheric_density_estimated"])
        self.assertIsNone(result["source"]["recife_to_conde_transfer_error_m_s"])
        self.assertIsNone(result["source"]["instrument_error_m_s"])

    def test_reject_shifted_date_upstream_and_claimed_release_time(self):
        import audit_igra_recife_window as w
        original = w.load_original("07")
        for old, new in (
            (b"1963 11 07", b"1963 11 09"),
            (b"12 9999", b"12 1159"),
            (b"ncdc6301", b"ncdc6302"),
            (b"BRM00082900", b"BRM00082999"),
        ):
            with self.subTest(old=old, new=new):
                self.assertIn(old, original)
                with self.assertRaises(ValueError):
                    w.parse_day(original.replace(old, new, 1), "07")

    def test_reject_partial_wind_and_truncated_record(self):
        import audit_igra_recife_window as w
        raw = w.load_original("09")
        with self.assertRaises(ValueError):
            w.parse_day(raw.rsplit(b"\n", 2)[0] + b"\n", "09")
        lines = raw.decode().splitlines(keepends=True)
        index = next(i for i, ln in enumerate(lines) if ln[9:15] == " 85000")
        line = lines[index]
        self.assertNotEqual(line[46:51], "-9999")
        lines[index] = line[:46] + "-9999" + line[51:]
        with self.assertRaises(ValueError):
            w.parse_day("".join(lines).encode(), "09")
