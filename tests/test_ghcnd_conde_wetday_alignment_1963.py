"""Adversarial controls for fixed-source wet-day label sensitivity."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/audit_ghcnd_conde_wetday_alignment_1963.py"
spec = importlib.util.spec_from_file_location("ghcnd_lag_audit", P)
import sys
sys.path.insert(0, str(P.parent))
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


class WetDayAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if "GHCND_SOURCE_DIR" not in os.environ:
            raise unittest.SkipTest("Only pinned NOAA originals, supplied in CI, are accepted")
        cls.root = Path(os.environ["GHCND_SOURCE_DIR"])
        cls.output = analysis.audit(cls.root)

    def test_reproduce_pinned_manifest(self):
        expected = json.loads(analysis.OUT.read_text())
        self.assertEqual(self.output, expected)

    def test_ten_comparators_and_constant_support_per_lag(self):
        self.assertEqual(len(self.output["comparisons"]), 10)
        for row in self.output["comparisons"]:
            r = row["full_year"]
            self.assertEqual(len(r["lag_results"]), 5)
            self.assertGreater(r["overlap_days_fixed"], 0)
            for lag in r["lag_results"]:
                n = sum(lag[k] for k in ("joint_wet_days", "conde_only_wet",
                                        "peer_only_wet", "joint_dry_days"))
                self.assertEqual(n, r["overlap_days_fixed"])

    def test_lag_nonuniform_and_cannot_fix_station_clock(self):
        chosen = [r["full_year"]["strongest_lag_days"] for r in self.output["comparisons"]]
        self.assertEqual({k: chosen.count(k) for k in (-1, 0, 1)}, {-1: 4, 0: 5, 1: 1})
        self.assertIsNone(self.output["not_proved"]["actual_1963_observation_clock"])
        self.assertIsNone(self.output["not_proved"]["weather_at_incident_hour"])

    def test_november_historical_controls(self):
        x = self.output["november_controls"]
        self.assertEqual(len(x["1963-11-08"]["reported_positive"]), 2)
        self.assertEqual(len(x["1963-11-13"]["reported_positive"]), 8)
        self.assertEqual(len(x["1963-11-14"]["reported_positive"]), 8)
        self.assertEqual(x["1963-11-08"]["present"], 11)

    def test_months_absent_are_not_zero(self):
        cambuis = next(x for x in self.output["comparisons"] if x["station"] == "CAMBUIS")
        self.assertEqual(cambuis["observed_1963_days_after_QC"], 92)
        self.assertLess(cambuis["full_year"]["overlap_days_fixed"], 92)

    def test_spatial_QC_failure_excluded(self):
        timbo = next(x for x in self.output["comparisons"] if x["station"] == "TIMBO (VFFLB)")
        self.assertEqual(timbo["observed_1963_days_after_QC"], 364)
        self.assertEqual(len(timbo["excluded_QC_flagged_days"]), 1)
        self.assertEqual(timbo["excluded_QC_flagged_days"][0]["date"], "1963-08-06")
        self.assertEqual(timbo["excluded_QC_flagged_days"][0]["quality_flag"], "S")

    def test_corrupt_whole_file_fails_sha(self):
        sid = "BR048346820"
        data = (self.root/(sid+".dly")).read_bytes()
        self.assertNotEqual(analysis.original.sha256(data+b"tamper"),
                            analysis.original.SHA[sid+".dly"])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for other in analysis.original.IDS:
                name = other+".dly"
                if other == sid:
                    (root/name).write_bytes(data+b"tamper")
                else:
                    (root/name).symlink_to(self.root/name)
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                analysis.audit(root)

    def test_source_flag_adulteration_rejected(self):
        raw = (self.root/"BR048346820.dly").read_bytes()
        self.assertIn(b"   35  I", raw)
        rows = raw.splitlines()
        for i, row in enumerate(rows):
            if row[11:21] == b"196311PRCP":
                off = 21+7*8
                self.assertEqual(row[off:off+8], b"   35  I")
                rows[i] = row[:off]+b"   35  N"+row[off+8:]
        edited = b"\n".join(rows)
        with self.assertRaisesRegex(ValueError, "unexpected source"):
            analysis.read_year(edited, "BR048346820")

    def test_missing_data_not_invented(self):
        raw = (self.root/"BR048346820.dly").read_bytes()
        rows = raw.splitlines()
        changed = []
        for r in rows:
            if r[11:21] == b"196311PRCP":
                i = 21+7*8
                r = r[:i]+b"-9999  I"+r[i+8:]
            changed.append(r)
        parsed, exceptions = analysis.read_year(b"\n".join(changed), "BR048346820")
        self.assertNotIn(date(1963, 11, 8), parsed)
        self.assertEqual(exceptions, [])

    def test_shift_orientation_positive_control(self):
        conde = {date(1963,1,d): (1 if d in (3,5,7) else 0) for d in range(1,11)}
        peer = {t+timedelta(days=1): v for t,v in conde.items()}
        r = analysis.lag_scan(conde, peer, list(conde))
        self.assertEqual(r["strongest_lag_days"], 1)

    def test_not_physical_reentry_constraint(self):
        self.assertEqual(self.output["status"], "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION")
        for k in ("station_independence", "wind_or_drag", "fall_geography"):
            self.assertIsNone(self.output["not_proved"][k])


if __name__ == "__main__":
    unittest.main()
