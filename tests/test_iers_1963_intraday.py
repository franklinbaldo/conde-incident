"""G49: source-bound conditional intra-day Earth-frame regression tests."""
import copy
from decimal import Decimal
import json
import math
import os
from pathlib import Path
import sys
import unittest

import erfa

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from iers_1963_frame import EOP, TIME, matrix_at_epoch, mul, orthogonality_error  # noqa: E402
from iers_1963_intraday import build, fractional_mjd, interpolate_at, checked_source, EPOCHS  # noqa: E402

class G49AuthenticatedIntraday(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        location = os.environ.get("IERS_1963_SOURCE")
        if not location:
            raise RuntimeError("IERS_1963_SOURCE must point to original SHA-pinned 1963 archive; no skips")
        cls.raw = Path(location).read_bytes()
        cls.eop = json.loads((ROOT / EOP).read_text())
        cls.times = json.loads((ROOT / TIME).read_text())
        checked_source(cls.raw, cls.eop, cls.times)

    def test_all_nine_times_source_bound_and_orthogonal(self):
        report = build(self.raw, self.eop, self.times)
        self.assertEqual([v["utc"] for v in report["epochs"]], list(EPOCHS))
        for row in report["epochs"]:
            self.assertLess(orthogonality_error(row["gcrs_to_itrs"]), 1e-12)
            self.assertIsNone(row["sensor_epoch"])
            self.assertIsNone(row["interpolation_sigma"])
            state = [7000, -80, 170]
            rotated = mul(row["gcrs_to_itrs"], state)
            transpose = [[row["gcrs_to_itrs"][j][i] for j in range(3)] for i in range(3)]
            self.assertLess(math.dist(state, mul(transpose, rotated)), 1e-8)
        self.assertEqual(report["limitations"]["historical_holdout_527_529"], "NOT_RUN")
        self.assertIsNone(report["limitations"]["impact_coordinates_time_probability"])

    def test_documented_daily_endpoints_match_g48(self):
        for k, row in enumerate(self.eop["sample"]):
            record = interpolate_at(row["utc"], self.eop, self.times)
            expected = matrix_at_epoch(row, self.times["rows_at_00_utc"][k])
            self.assertLess(max(abs(record["gcrs_to_itrs"][i][j] - expected[i][j])
                                for i in range(3) for j in range(3)), 5e-13)
            self.assertAlmostEqual(record["ut1_minus_utc_s"], row["ut1_minus_utc_s"], delta=1e-12)

    def test_midday_ut1_minus_tai_tracks_lod_not_fake_utc_rate(self):
        row = interpolate_at("1963-11-07T12:00:00Z", self.eop, self.times)
        a, b = self.times["rows_at_00_utc"][:2]
        expected = 0.5 * (a["ut1_minus_tai_s"] + b["ut1_minus_tai_s"])
        self.assertAlmostEqual(row["ut1_minus_tai_s"], expected, delta=1e-12)
        self.assertAlmostEqual(row["tai_minus_utc_s"], 2.7045796, delta=1e-11)
        # The 24h difference of UT1-UTC is not minus LOD: historical UTC drift matters.
        nominal_lod = - (b["ut1_minus_tai_s"] - a["ut1_minus_tai_s"])
        self.assertAlmostEqual(nominal_lod, 0.0020593, delta=2e-10)
        bad_lod = - (b["ut1_minus_utc_s"] - a["ut1_minus_utc_s"])
        self.assertGreater(abs(bad_lod - nominal_lod), 0.001)

    def test_fractional_utc_precision_and_midday_matrix(self):
        a = interpolate_at("1963-11-08T12:00:00Z", self.eop, self.times)
        b = interpolate_at("1963-11-08T12:00:01Z", self.eop, self.times)
        self.assertGreater(math.dist(mul(a["gcrs_to_itrs"], [6378, 0, 0]),
                                     mul(b["gcrs_to_itrs"], [6378, 0, 0])), 0.4)
        self.assertEqual(fractional_mjd("1963-11-08T00:00:00Z"), 38341)
        self.assertEqual(fractional_mjd("1963-11-09T00:00:00Z"), 38342)
        self.assertGreater(fractional_mjd("1963-11-08T00:00:00.000001Z"), 38341)

    def test_subsecond_rotation_against_independent_split_jd_erfa(self):
        # A two-part JD must preserve the fractional day rather than rounding
        # it onto the 38,341-day MJD in a single binary64 number.
        utc = "1963-11-08T12:00:00.123456Z"
        row = interpolate_at(utc, self.eop, self.times)
        mjd = fractional_mjd(utc)
        jd1 = 2400000.5 + int(mjd)
        frac = mjd - Decimal(int(mjd))
        ut1 = float(frac + Decimal(str(row["ut1_minus_utc_s"])) / 86400)
        tt = float(frac + Decimal(str(row["tt_minus_utc_s"])) / 86400)
        from iers_1963_frame import AS2RAD
        reference = erfa.c2t00a(jd1, tt, jd1, ut1,
                                 row["x_arcsec"] * AS2RAD,
                                 row["y_arcsec"] * AS2RAD)
        self.assertLess(max(abs(reference[i][j] - row["gcrs_to_itrs"][i][j])
                            for i in range(3) for j in range(3)), 2e-14)

    def test_source_binding_rejects_mutated_numbers_without_sha_change(self):
        # G48 previously checked only the string SHA lineage, not the payload cells.
        for name, index, field, value in [
            ("polar_x", 1, "x_arcsec", 0.0),
            ("polar_y", 2, "y_arcsec", 0.0),
            ("lod", 0, "lod_s", 0.0),
            ("sigma", 1, "sigma_ut1_minus_utc_s", 0.0),
        ]:
            tampered = copy.deepcopy(self.eop)
            tampered["sample"][index][field] = value
            with self.subTest(name=name), self.assertRaises(ValueError):
                build(self.raw, tampered, self.times)
        # Also catch internal G47 changes not covered by its high-level SHA label.
        tampered = copy.deepcopy(self.times)
        tampered["rows_at_00_utc"][1]["era_iau2000_rad"] += 0.3
        with self.assertRaises(ValueError):
            build(self.raw, self.eop, tampered)

    def test_source_integrity_and_complete_year_are_mandatory(self):
        with self.assertRaises(ValueError):
            build(self.raw[:-1] + b" ", self.eop, self.times)
        with self.assertRaises(ValueError):
            build(b"", self.eop, self.times)

    def test_rejects_unbracketed_epochs_and_ambiguous_clock(self):
        bad = (
            "1963-11-06T23:59:59Z", "1963-11-09T00:00:01Z",
            "1963-11-01T00:00:00Z", "1963-11-08T12:00:00+00:00",
            "1963-11-08T12:00:00-04:00", "1963-11-08T12:00:60Z",
            "1963-11-08T12:00Z", "1963-11-08T12:00:00.1234567Z",
            "1963-11-08T99:00:00Z", "1963-11-08T12:00:00",
        )
        for utc in bad:
            with self.subTest(utc=utc), self.assertRaises(ValueError):
                fractional_mjd(utc)

    def test_rejects_duplicate_unsorted_or_empty_epoch_list(self):
        for epochs in ((), (EPOCHS[0], EPOCHS[0]), (EPOCHS[1], EPOCHS[0])):
            with self.subTest(epochs=epochs), self.assertRaises(ValueError):
                build(self.raw, self.eop, self.times, epochs)

    def test_interpolation_is_not_claimed_as_sensor_data(self):
        out = build(self.raw, self.eop, self.times)
        self.assertTrue(out["sources"]["g46_g47_source_cells_verified"])
        self.assertEqual(out["limitations"]["TEME_to_GCRS"], "NOT_IMPLEMENTED")
        self.assertEqual(out["limitations"]["sensor_observations_527_529"], "MISSING")
        self.assertIsNone(out["limitations"]["interpolation_uncertainty"])

if __name__ == "__main__":
    unittest.main()

