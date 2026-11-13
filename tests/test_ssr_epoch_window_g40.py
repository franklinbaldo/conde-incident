"""Data-driven G40 source-age sensitivity and negative admissibility tests."""
import copy
import datetime as dt
import hashlib
import os
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import ssr_epoch_window_g40 as g40

CSV = Path(os.environ.get("CASTOR_G40_CSV", "/workspace/.jatoba/tmp/polvo10/source/norad_527_528_529_numeric_1963.csv"))


class EpochWindowG40(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(g40.g39.NASA.read_text())
        cls.snapshot = json.loads(g40.g39.SNAP.read_text())

    def test_real_pinned_corpus_and_december_529_window(self):
        if not CSV.is_file():
            self.skipTest("full SHA-pinned CSV supplied only in CI/local replay")
        raw = CSV.read_bytes()
        result = g40.evaluate(self.ledger, self.snapshot, raw)
        self.assertEqual(len(result["results"]), 7)
        dec = next(r for r in result["results"] if r["norad_id"] == "529"
                   and r["publication_date_NOT_observation_epoch"] == "1963-12-31")
        w2, w7, w14, w30 = dec["windows"]
        self.assertEqual([w["distinct_secondary_epochs"] for w in dec["windows"]], [2, 3, 5, 8])
        # The 7-day discrepancy is large in every eligible mirror row;
        # the 30-day range crosses zero, falsifying robustness to age choice.
        self.assertGreater(w7["printed_height_minus_mirror_kepler_proxy_km_range"][0], 45)
        self.assertGreater(w14["printed_height_minus_mirror_kepler_proxy_km_range"][0], 6)
        self.assertLess(w30["printed_height_minus_mirror_kepler_proxy_km_range"][0], 0)
        self.assertGreater(w30["printed_height_minus_mirror_kepler_proxy_km_range"][1], 80)
        self.assertLess(w2["printed_minus_mirror_period_seconds_range"][1], -14)
        self.assertEqual(g40.OUT.read_text(), g40.render(self.ledger, self.snapshot, raw))
        self.assertFalse(result["physical_constraint_activated"])
        self.assertEqual(result["norad_527_529_historical_holdouts"], "NOT_RUN")

    def test_bad_csv_and_tampered_report_rejected(self):
        if not CSV.is_file():
            self.skipTest("full SHA-pinned CSV supplied only in CI/local replay")
        raw = CSV.read_bytes()
        with self.assertRaises(ValueError):
            g40.evaluate(self.ledger, self.snapshot, raw + b"\n")
        altered = copy.deepcopy(self.ledger)
        altered["sources"][-1]["rows"][-1]["apogee_km"] = 400
        with self.assertRaises(ValueError):
            g40.evaluate(altered, self.snapshot, raw)

    def test_future_mirror_epoch_is_excluded_even_when_closer(self):
        t = dt.datetime(1963, 12, 31, 12, tzinfo=dt.timezone.utc)
        rows = [
            dict(row=1, norad="529", epoch=t-dt.timedelta(days=1), n=16),
            dict(row=2, norad="529", epoch=t+dt.timedelta(seconds=1), n=200),
            dict(row=3, norad="527", epoch=t-dt.timedelta(days=1), n=1),
        ]
        r = g40.window_stats(rows, "529", t, 89.2, 334, 2)
        self.assertEqual(r["distinct_secondary_epochs"], 1)
        self.assertGreater(r["printed_minus_mirror_period_seconds_range"][0], -60)

    def test_empty_window_is_not_zero_discrepancy(self):
        t = dt.datetime(1963, 12, 31, 12, tzinfo=dt.timezone.utc)
        r = g40.window_stats([], "529", t, 89.2, 334, 2)
        self.assertIsNone(r["printed_minus_mirror_period_seconds_range"])
        self.assertIsNone(r["printed_height_minus_mirror_kepler_proxy_km_range"])

    def test_epoch_duplicates_do_not_add_independence(self):
        t = dt.datetime(1963, 12, 31, 12, tzinfo=dt.timezone.utc)
        rows = [dict(row=1, norad="529", epoch=t, n=16),
                dict(row=2, norad="529", epoch=t, n=16)]
        self.assertEqual(g40.window_stats(rows,"529",t,89.2,334,2)["distinct_secondary_epochs"],1)
        rows[1]["n"] = 15
        with self.assertRaises(ValueError):
            g40.window_stats(rows, "529", t, 89.2, 334, 2)

    def test_strict_pinning_and_nonfinite_rejection(self):
        raw = ("source_row,norad_id,epoch,mean_motion\n"
               "1,529,1963-12-30T00:00:00Z,16.0\n").encode()
        with self.assertRaises(ValueError):
            g40.parse_verified_csv(raw)
        with patch.object(g40.g39, "EXPECTED_CSV_SHA256", hashlib.sha256(raw).hexdigest()):
            self.assertEqual(len(g40.parse_verified_csv(raw)), 1)
            with self.assertRaises(ValueError):
                g40.parse_verified_csv(raw.replace(b"16.0", b"NaN"))

    def test_nonphysical_width_rejected(self):
        t = dt.datetime(1963,12,31,tzinfo=dt.timezone.utc)
        for width in (0,-1):
            with self.assertRaises(ValueError):
                g40.window_stats([],"529",t,89.2,334,width)


if __name__ == "__main__":
    unittest.main()
