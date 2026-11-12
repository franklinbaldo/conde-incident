"""Offline negative controls for historical IGRA vertical shear interpretation."""
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_igra_recife_shear as s
import audit_igra_recife_window as w


class HistoricalShearTests(unittest.TestCase):
    def test_pinned_archival_bytes_and_shear_reproduction(self):
        result = s.build()
        self.assertEqual(json.loads(s.OUTPUT.read_text()), result)
        self.assertEqual([p["adjacent_observed_pairs"] for p in result["observables"]], [14, 14, 14])
        for day, profile in zip(w.DAYS, result["observables"]):
            self.assertEqual(profile["original_excerpt_sha256"], w.DAYS[day][0])
            self.assertEqual(profile["actual_release_utc"], None)

    def test_positive_heights_decreasing_pressure_and_finite_difference(self):
        for d in s.build()["observables"]:
            for l in d["vertical_layers"]:
                self.assertGreater(l["geopotential_height_top_m_asl"], l["geopotential_height_bottom_m_asl"])
                self.assertGreater(l["pressure_bottom_hpa"], l["pressure_top_hpa"])
                dz = l["geopotential_height_top_m_asl"]-l["geopotential_height_bottom_m_asl"]
                expect = 1000*math.hypot(l["delta_u_east_m_s"], l["delta_v_north_m_s"])/dz
                self.assertAlmostEqual(expect, l["finite_difference_m_s_per_geopotential_km"], places=5)

    def test_no_invented_error_hour_or_regional_observation(self):
        data = s.build()["methodology"]
        for key in ("instrumental_uncertainty_m_s", "vertical_transfer_uncertainty_m_s", "regional_transfer_uncertainty_m_s"):
            self.assertIsNone(data[key])
        self.assertFalse(data["wind_transfer_to_conde_calibrated"])
        self.assertFalse(data["thermospheric_drag_constraint"])
        self.assertFalse(data["vertical_profile_between_levels_observed"])
        self.assertEqual(data["independent_confirmation_count_for_conde_winds"], 0)
        self.assertEqual(data["physical_constraint_status"], "CONNECTED_PENDING_SPATIOTEMPORAL_TRANSFER")

    def test_calm_not_directional_nov09_50hpa(self):
        row = next(x for x in s.read_winds("09") if x["pressure_hpa"] == 50)
        self.assertEqual(row["speed_m_s"], 0)
        self.assertEqual(row["wind_from_recorded_deg"], 0)
        self.assertFalse(row["wind_direction_defined"])
        self.assertEqual(row["u_east_m_s"], 0)
        self.assertEqual(row["v_north_m_s"], 0)
        self.assertTrue(any(l["calm_endpoint_present"] for l in s.build()["observables"][2]["vertical_layers"]))

    def test_no_filling_11_missing_winds_per_profile(self):
        import base64
        from audit_igra_recife_winds import number
        for day in w.DAYS:
            lines=w.load_original(day).decode("ascii").splitlines()[1:]
            self.assertEqual(sum(number(line,40,45) is None for line in lines),w.DAYS[day][1]-15)
            self.assertEqual(len(s.read_winds(day)),15)

    def test_wrong_epoch_and_truncated_raw_refused(self):
        import unittest.mock as mock
        day="08"
        original=w.load_original(day)
        for altered in (original.replace(b"1963 11 08",b"1963 11 09",1),
                        original.replace(b"12 9999",b"12 1200",1),
                        original.rsplit(b"\n",2)[0]+b"\n"):
            with self.subTest(altered=altered[:50]), mock.patch.object(s,"load_original",return_value=altered):
                with self.assertRaises(ValueError):
                    s.read_winds(day)

    def test_wrong_height_direction_pressure_refused(self):
        import unittest.mock as mock
        original=w.load_original("08")
        # parse_day independently validates only selected levels; all-level
        # range/order checks must reject a modified nonstandard wind level.
        lines=original.decode("ascii").splitlines(keepends=True)
        idx=next(i for i,ln in enumerate(lines) if ln[9:15]==" 40000")
        for replacement in ("00000","-0100"):
            data=lines.copy()
            data[idx]=data[idx][:16]+replacement+data[idx][21:]
            with mock.patch.object(s,"load_original",return_value="".join(data).encode()):
                with self.assertRaises(ValueError):
                    s.read_winds("08")


if __name__=="__main__":
    unittest.main()
