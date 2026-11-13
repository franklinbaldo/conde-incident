"""Adversarial checks on compiled NASA SSR period contrasts, not physical tracks."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ssr_post528_print_contrasts import build, read_sources, reports  # noqa: E402


class SourceLockedSsrTests(unittest.TestCase):
    def test_all_seven_issues_and_last_three_do_not_list_528(self):
        obj = build()
        self.assertEqual(len(obj["sources"]), 7)
        self.assertEqual(obj["not_listed_528"],
                         ["1963-11-15", "1963-11-30", "1963-12-31"])
        self.assertFalse(obj["not_listed_is_nondetection"])

    def test_post_october_529_declines_strictly_in_printed_rounding_bands(self):
        results = build()["post_october_adjacent_contrasts"]
        self.assertEqual([x["printed_earlier_minus_later"]["interval_centiminutes"]
                          for x in results["1963-003C"]],
                         [[60, 80], [30, 50], [290, 310]])
        self.assertTrue(all(x["printed_earlier_minus_later"]
                            ["strictly_positive_under_rounding"]
                            for x in results["1963-003C"]))
        self.assertFalse(any(x["printed_earlier_minus_later"]
                             ["strictly_positive_under_rounding"]
                             for x in results["1963-003A"]))

    def test_printed_october_december_difference_of_differences(self):
        obj = build()
        self.assertEqual(obj["C_minus_A_october_december"],
                         {"center_centiminutes": 410,
                          "interval_centiminutes": [390, 430],
                          "strictly_positive_under_rounding": True})
        # Adjacent intervals are not added as if the shared November values were independent.
        self.assertEqual([x["C_minus_A_printed_change_contrast"]
                          ["center_centiminutes"]
                          for x in obj["C_minus_A_difference_in_differences"]],
                         [70, 40, 300])

    def test_no_instrument_epoch_or_historical_posterior(self):
        obj = build()
        self.assertIsNone(obj["limits"]["instrumental_epoch"])
        self.assertIsNone(obj["limits"]["sensor_and_covariance"])
        self.assertEqual(obj["limits"]["mcmc_historical"], "NOT_RUN")
        self.assertFalse(obj["limits"]["active_physical_constraint"])
        self.assertEqual(obj["limits"]["holdout"],
                         "RETROSPECTIVE_NOT_BLIND_NO_PHYSICAL_FORWARD_OPERATOR")

    def test_fail_closed_on_report_metadata_date_mutation(self):
        d = read_sources()
        d["nov"]["documents"][0]["date"] = "1963-11-08"
        with self.assertRaisesRegex(ValueError, "metadata drift"):
            reports(d)

    def test_fail_closed_on_nasa_pdf_sha_drift(self):
        d = read_sources()
        d["nov"]["documents"][0]["sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "source sha256 drift"):
            reports(d)

    def test_fail_closed_on_invented_november_528_row(self):
        d = read_sources()
        row = copy.deepcopy(d["nov"]["documents"][0]["rows"][0])
        row["designator"] = "1963-003B"
        d["nov"]["documents"][0]["rows"].append(row)
        with self.assertRaisesRegex(ValueError, "membership drift"):
            reports(d)

    def test_fail_closed_on_duplicate_same_report(self):
        d = read_sources()
        d["jul_dec"]["sources"][0]["rows"].append(
            copy.deepcopy(d["jul_dec"]["sources"][0]["rows"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            reports(d)

    def test_fail_closed_on_period_rounding_drift(self):
        d = read_sources()
        d["aug"]["rows"][0]["nodal_period_min"] = "94.62"
        with self.assertRaisesRegex(ValueError, "one decimal"):
            reports(d)

    def test_fail_closed_on_superseded_december_transcription(self):
        d = read_sources()
        d["jul_dec"]["sources"][2]["rows"][1]["period_min"] = "89.6"
        with self.assertRaisesRegex(ValueError, "transcription reverted"):
            reports(d)

    def test_replay_frozen_source_only(self):
        expected = (ROOT / "research/statistics/ssr_post528_print_contrasts_C241.json")
        actual = (json.dumps(build(), ensure_ascii=False,
                             sort_keys=True, indent=2)+"\n").encode()
        self.assertEqual(expected.read_bytes(), actual)


if __name__ == "__main__":
    unittest.main()
