"""Adversarial source/print gates for a nonphysical report-date counterfactual."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ssr_report_date_proxy_falsifier import (  # noqa: E402
    DAYS, affine_report_date_test, build,
)
from ssr_post528_print_contrasts import read_sources  # noqa: E402


class ReportDateProxyTests(unittest.TestCase):
    def test_529_proxy_affine_falsified_exactly_beyond_print_rounding(self):
        result = build()["tests_by_designator"]["1963-003C"]
        self.assertEqual(result["printed_centiminutes"], [9220, 9160, 8920])
        self.assertEqual(result["interpolation_weight_last"],
                         {"numerator": 15, "denominator": 31})
        self.assertEqual(result["midpoint_minus_affine_interpolation_centiminutes"],
                         {"numerator": 2640, "denominator": 31})
        self.assertEqual(result["conditional_residual_interval_centiminutes"],
                         [{"numerator": 2330, "denominator": 31},
                          {"numerator": 2950, "denominator": 31}])
        self.assertFalse(result["affine_publication_date_proxy_feasible_under_rounding"])

    def test_527_control_is_compatible_not_declared_constant_orbit(self):
        result = build()["tests_by_designator"]["1963-003A"]
        self.assertEqual(result["printed_centiminutes"], [9460, 9460, 9460])
        self.assertEqual(result["midpoint_minus_affine_interpolation_centiminutes"],
                         {"numerator": 0, "denominator": 1})
        self.assertTrue(result["affine_publication_date_proxy_feasible_under_rounding"])

    def test_touching_print_interval_is_compatible_not_refuted(self):
        result = affine_report_date_test(("1963-01-01", "1963-01-02", "1963-01-03"),
                                         (1000, 1010, 1000))
        self.assertTrue(result["affine_publication_date_proxy_feasible_under_rounding"])
        self.assertEqual(result["conditional_residual_interval_centiminutes"][0],
                         {"numerator": 0, "denominator": 1})

    def test_nonmidpoint_weights_not_silently_forced_half(self):
        result = affine_report_date_test(DAYS, (1000, 1020, 1040), 0)
        self.assertEqual(result["interpolation_weight_last"],
                         {"numerator": 15, "denominator": 31})
        self.assertEqual(result["midpoint_minus_affine_interpolation_centiminutes"],
                         {"numerator": 20, "denominator": 31})

    def test_bad_dates_centers_and_width_rejected(self):
        invalid = [
            (("1963-12-31", "1963-12-15", "1963-11-30"), (1, 2, 3), 5),
            (("1963-11-30", "1963-11-30", "1963-12-31"), (1, 2, 3), 5),
            (DAYS, (100, 0, 300), 5),
            (DAYS, (100, True, 300), 5),
            (DAYS, (100, 200, 300), -1),
        ]
        for days, centers, width in invalid:
            with self.subTest(days=days, centers=centers, width=width):
                with self.assertRaises(ValueError):
                    affine_report_date_test(days, centers, width)

    def test_source_sha_provenance_and_528_absence(self):
        data = build()
        self.assertEqual([r["report_date_not_observation_epoch"]
                          for r in data["source_rows"]], list(DAYS))
        self.assertEqual({r["source_family"] for r in data["source_rows"]},
                         {"NASA_GODDARD_COMPILED_SHARED_TRACKING"})
        self.assertEqual(set(data["tests_by_designator"]), {"1963-003A", "1963-003C"})
        self.assertIsNone(data["limits"]["instrumental_epoch_utc"])
        self.assertFalse(data["limits"]["active_physical_constraint"])
        self.assertEqual(data["limits"]["historical_mcmc"], "NOT_RUN")

    def test_mutated_nasa_source_sha_is_rejected(self):
        data = read_sources()
        data["dec15"]["source"]["sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "source sha256 drift"):
            build(data)

    def test_invented_528_in_later_report_is_rejected(self):
        data = read_sources()
        altered = copy.deepcopy(data["jul_dec"]["sources"][2]["rows"][0])
        altered["designator"] = "1963-003B"
        data["jul_dec"]["sources"][2]["rows"].append(altered)
        with self.assertRaisesRegex(ValueError, "membership drift"):
            build(data)

    def test_frozen_json_reproducible(self):
        expected = ROOT / "research/statistics/ssr_report_date_proxy_C241.json"
        self.assertEqual(expected.read_bytes(),
                         (json.dumps(build(), indent=2, sort_keys=True,
                                     ensure_ascii=False)+"\n").encode())


if __name__ == "__main__":
    unittest.main()
