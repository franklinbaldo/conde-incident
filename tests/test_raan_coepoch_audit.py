"""Cervo: regression of real secondary 1963 rows plus algorithmic edge cases."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_coepoch_audit import circular_difference_deg, parse_records, match_epochs, report


class CircularRaanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / "research/statistics/raan_527_528_529_1963.json").read_text())
        cls.result = report(cls.source)

    def test_angular_wrap_at_zero(self):
        self.assertAlmostEqual(circular_difference_deg(359.9, 0.1), -0.2)
        self.assertAlmostEqual(circular_difference_deg(0.1, 359.9), 0.2)
        self.assertAlmostEqual(circular_difference_deg(10, 190), -180)
        for a, b in [(math.nan, 4), (3, math.inf)]:
            with self.assertRaises(ValueError):
                circular_difference_deg(a, b)

    def test_raw_counts_and_exact_duplicate_epochs(self):
        self.assertEqual(self.result["raw_rows_per_object"], {"527":21, "528":45, "529":57})
        self.assertEqual(self.result["unique_epochs_per_object"], {"527":20, "528":45, "529":54})
        self.assertEqual(self.result["exact_duplicate_epoch_rows_per_object"], {"527":1,"528":0,"529":3})
        self.assertEqual(self.result["unique_epoch_total"], 119)
        self.assertEqual(self.result["raw_total_rows"], 123)

    def test_real_pair_528_529_first_near_coepoch(self):
        case = next(row for row in self.result["cases"] if (
            row["left"], row["right"], row["window_minutes"]) == (528,529,10))
        self.assertEqual(case["count"], 1)
        p = case["earliest_pair"]
        self.assertEqual(p["left_utc"], "1963-01-17T16:18:12.350304Z")
        self.assertEqual(p["right_utc"], "1963-01-17T16:20:21.950304Z")
        self.assertAlmostEqual(p["delta_t_s"],129.6,places=6)
        self.assertAlmostEqual(p["delta_raan_deg_signed"],0.0014,places=6)

    def test_real_pair_counts_sensitivity(self):
        counts = {
            (r["left"],r["right"],r["window_minutes"]):r["count"]
            for r in self.result["cases"]
        }
        self.assertEqual([counts[(527,528,w)] for w in (10,60,360,1440)],[0,1,2,5])
        self.assertEqual([counts[(528,529,w)] for w in (10,60,360,1440)],[1,3,6,15])
        self.assertEqual([counts[(527,529,w)] for w in (10,60,360,1440)],[0,1,3,7])
        last = next(r for r in self.result["cases"] if (r["left"],r["right"],r["window_minutes"]) == (528,529,1440))["latest_pair"]
        self.assertEqual(last["left_utc"],"1963-10-27T14:40:16.132512Z")
        self.assertEqual(last["right_utc"],"1963-10-28T04:51:52.072992Z")
        self.assertAlmostEqual(last["delta_t_s"],51095.940480)
        self.assertAlmostEqual(last["delta_raan_deg_signed"],-2.8122)

    def test_different_value_same_epoch_is_rejected_not_averaged(self):
        invalid=copy.deepcopy(self.source)
        twin=next(row for row in invalid["records"] if row["norad"]==528)
        invalid["records"].append({**twin,"raan_deg":(twin["raan_deg"]+10)%360})
        with self.assertRaisesRegex(ValueError,"conflicting RAAN"):
            parse_records(invalid)

    def test_unverified_timestamp_or_norad_refused(self):
        for mutation in ({"epoch_utc":"1963-01-17T16:18:12.350304"},
                         {"epoch_utc":"1963-01-17T16:18:12+01:00"},
                         {"raan_deg":360}, {"raan_deg":math.nan}, {"norad": 530}):
            bad=copy.deepcopy(self.source)
            bad["records"][0].update(mutation)
            with self.assertRaises(ValueError):
                parse_records(bad)

    def test_no_reuse_within_pair(self):
        from datetime import datetime,timezone,timedelta
        t=datetime(1963,1,1,tzinfo=timezone.utc)
        l=[(t,1),(t+timedelta(seconds=10),2)]
        r=[(t+timedelta(seconds=5),1)]
        matches=match_epochs(l,r,window_s=3600)
        self.assertEqual(len(matches),1)

    def test_pinned_report_is_generated_exactly(self):
        frozen=json.loads((ROOT / "research/statistics/raan_coepoch_1963_report.json").read_text())
        self.assertEqual(frozen,self.result)
        self.assertEqual(frozen["inference_status"],"DESCRIPTIVE_ONLY_NOT_POSTERIOR")
        self.assertEqual(frozen["physical_domain_reduction"],
                         "NOT_RUN_NO_FRAME_ERROR_OR_EPOCH_PROPAGATION")


if __name__ == "__main__":
    unittest.main()
