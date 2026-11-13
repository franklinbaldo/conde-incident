"""Guard document/secondary matching and reject imaginary independent epochs."""
import copy
import csv
import hashlib
import io
import json
import unittest
from unittest.mock import patch

from tools import ssr_secondary_period_g39 as g39


class PeriodMirrorG39Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nasa = json.loads(g39.NASA.read_text())
        cls.snap = json.loads(g39.SNAP.read_text())

    def test_snapshot_uses_exactly_seven_pinned_rows(self):
        report = g39.evaluate(self.nasa, self.snap)
        self.assertEqual(len(report["comparisons"]), 7)
        self.assertFalse(report["activated_historical_orbital_restriction"])
        self.assertEqual(report["independent_historical_527_529_holdout"], "NOT_RUN")
        self.assertEqual(len(set(x["mirror_source_row"] for x in report["comparisons"])), 7)

    def test_december_mismatch_disproportionate_to_november(self):
        report = g39.evaluate(self.nasa, self.snap)
        dec = next(x for x in report["comparisons"] if x["norad"] == "529" and x["document_publication_NOT_instrument_epoch"] == "1963-12-31")
        nov = next(x for x in report["comparisons"] if x["norad"] == "529" and x["document_publication_NOT_instrument_epoch"] == "1963-11-30")
        a = next(x for x in report["comparisons"] if x["norad"] == "527" and x["document_publication_NOT_instrument_epoch"] == "1963-12-31")
        self.assertEqual(dec["mirror_source_row"], 3071)
        self.assertAlmostEqual(dec["mirror_period_proxy_min_NOT_osculating"], 89.4507, places=3)
        self.assertLess(dec["printed_minus_mirror_period_seconds"], -10)
        self.assertGreater(dec["printed_height_minus_mirror_proxy_km"], 80)
        self.assertLess(abs(nov["printed_height_minus_mirror_proxy_km"]), 5)
        self.assertLess(abs(a["printed_height_minus_mirror_proxy_km"]), 5)
        self.assertEqual(report["december_529_vs_november_529"]["hypothesis_of_lagged_altitudes"], "UNRESOLVED_CANDIDATE_NOT_PROVED")

    def test_check_output_exact_not_just_numerical_summary(self):
        self.assertEqual(g39.OUT.read_text(), g39.render(self.nasa, self.snap))

    def test_reject_change_in_nasa_printed_data(self):
        altered = copy.deepcopy(self.nasa)
        altered["sources"][-1]["rows"][-1]["period_min"] = "90.2"
        with self.assertRaises(ValueError):
            g39.evaluate(altered, self.snap)

    def test_reject_source_checksum_or_stale_identity(self):
        for field in ("source_csv_sha256", "source_parquet_sha256", "id"):
            altered = copy.deepcopy(self.snap)
            altered[field] = "fabricated"
            with self.subTest(field=field), self.assertRaises(ValueError):
                g39.evaluate(self.nasa, altered)

    def test_reject_future_epoch_or_foreign_norad(self):
        for key, val in (("epoch", "1964-01-01T00:00:00Z"), ("norad_id", "528")):
            altered = copy.deepcopy(self.snap)
            altered["selected"][-1][key] = val
            with self.subTest(key=key), self.assertRaises(ValueError):
                g39.evaluate(self.nasa, altered)

    def test_reject_invented_negative_mean_motion_and_duplicate(self):
        for value in ("-1", "NaN", "inf"):
            altered = copy.deepcopy(self.snap)
            altered["selected"][-1]["mean_motion_rev_day"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                g39.evaluate(self.nasa, altered)
        altered = copy.deepcopy(self.snap)
        altered["selected"][-1]["source_row"] = altered["selected"][-2]["source_row"]
        with self.assertRaises(ValueError):
            g39.evaluate(self.nasa, altered)

    def test_secondary_full_csv_hash_checked_before_selection(self):
        fields = ["source_row", "norad_id", "epoch", "mean_motion"]
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        writer.writerow(dict(source_row=1, norad_id=529, epoch="1963-12-30T00:00:00Z", mean_motion=16.0))
        rows = out.getvalue().encode()
        with self.assertRaises(ValueError):
            g39.source_candidates(rows, [("19640005618", "1963-003C", g39.instant("1963-12-31T12:00:00Z"))])
        with patch.object(g39, "EXPECTED_CSV_SHA256", hashlib.sha256(rows).hexdigest()):
            selected = g39.source_candidates(rows, [("19640005618", "1963-003C", g39.instant("1963-12-31T12:00:00Z"))])
            self.assertEqual(selected[0]["source_row"], 1)

    def test_reject_conflicting_nearest_duplicate_and_pick_past(self):
        rows = ("source_row,norad_id,epoch,mean_motion\n"
                "1,529,1963-12-25T00:00:00Z,15.8\n"
                "2,529,1963-12-30T00:00:00Z,16.0\n"
                "3,529,1964-01-03T00:00:00Z,16.9\n")
        query = [("19640005618", "1963-003C", g39.instant("1963-12-31T12:00:00Z"))]
        with patch.object(g39, "EXPECTED_CSV_SHA256", hashlib.sha256(rows.encode()).hexdigest()):
            selected = g39.source_candidates(rows.encode(), query)
            self.assertEqual(selected[0]["source_row"], 2)
            corrupt = rows + "4,529,1963-12-30T00:00:00Z,15.9\n"
            with patch.object(g39, "EXPECTED_CSV_SHA256", hashlib.sha256(corrupt.encode()).hexdigest()):
                with self.assertRaises(ValueError):
                    g39.source_candidates(corrupt.encode(), query)


if __name__ == "__main__":
    unittest.main()
