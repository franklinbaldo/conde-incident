"""R69 adversarial unit tests. All times are SYNTHETIC, never historical inputs."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
from c241_decay_day_error_r68 import build as build_r68, error_interval
from c241_528_day_interval_r69 import build, SSR_DAY
from test_c241_decay_day_error_r68 import fixture as old_fixture

UTC = timezone.utc


def fixture():
    r54, r60 = old_fixture()
    r54["method"] = {
        "NASA_date_timezone_known": False,
        "H_eff_km_exploratory": [40, 50],
    }
    r54["inference"]["active_constraint"] = False
    origin = datetime(1963, 10, 27, 10, tzinfo=UTC)
    def scenarios():
        result = []
        for h, n in ((40, 12), (50, 15)):
            pred = origin + timedelta(days=n)
            result.append({
                "H_eff_km_ASSUMED": h,
                "hypothetical_terminal_utc": pred.isoformat(timespec="seconds"),
                "life_remaining_days_HEURISTIC": n,
                "error_days_if_NASA_label_means_UTC_civil_day":
                    list(error_interval(pred, SSR_DAY)),
            })
        return result
    r54["comparisons"].append({
        "norad": 528,
        "cutoff_utc_exclusive": "1963-10-28T00:00:00+00:00",
        "NASA_reported_calendar_day_timezone_UNVERIFIED": SSR_DAY,
        "prior_catalogue_epochs": 45,
        "origin_catalogue_epoch_utc": origin.isoformat(),
        "independent_terminal_time_validation": False,
        "last_two": {"status": "HEURISTIC_ONLY", "scenarios": scenarios()},
        "median_three_prior_secants":
            {"status": "HEURISTIC_ONLY", "scenarios": scenarios()},
    })
    return r54, r60, build_r68(r54, r60)


class Frozen528Tests(unittest.TestCase):
    def test_preserves_original_rows_and_appends_four(self):
        a, b, c = fixture()
        x = build(a, b, c)
        self.assertEqual(len(x["rows"]), 68)
        self.assertEqual(x["rows"][:64], c["rows"])
        self.assertEqual(len([r for r in x["rows"] if r["norad"] == 528]), 4)
        self.assertEqual({(r["method"], r["H_eff_km_assumed"])
                          for r in x["rows"][64:]},
                         {("last_two", 40), ("last_two", 50),
                          ("median_three", 40), ("median_three", 50)})

    def test_conclusion_cannot_be_promoted(self):
        x = build(*fixture())
        self.assertEqual(x["conclusion"]["answer"], "NO_ONLY_CONDITIONALLY_COMPATIBLE")
        self.assertGreater(x["controls_proxy_error_envelope_excluding_unresolved_308"]
                           ["width_days"], 1)
        self.assertFalse(x["inference"]["active_constraint_528"])
        self.assertIsNone(x["inference"]["terminal_time_sigma_hours"])
        self.assertEqual(x["inference"]["historical_mcmc"], "NOT_RUN")
        self.assertIsNone(x["inference"]["impact_geography"])

    def test_cached_r68_mutation_rejected(self):
        a, b, c = fixture()
        c["rows"][0]["prediction_utc"] = "1963-11-01T00:00:00+00:00"
        with self.assertRaisesRegex(ValueError, "frozen replay"):
            build(a, b, c)

    def test_duplicate_528_H_rejected(self):
        a, b, c = fixture()
        a["comparisons"][-1]["last_two"]["scenarios"][1]["H_eff_km_ASSUMED"] = 40
        with self.assertRaisesRegex(ValueError, "40 and 50"):
            build(a, b, c)

    def test_extra_cutoff_rejected(self):
        a, b, c = fixture()
        a["comparisons"].append(deepcopy(a["comparisons"][-1]))
        with self.assertRaisesRegex(ValueError, "one frozen"):
            build(a, b, c)

    def test_wrong_origin_cutoff_rejected(self):
        a, b, c = fixture()
        a["comparisons"][-1]["origin_catalogue_epoch_utc"] = (
            "1963-10-29T00:00:00+00:00")
        with self.assertRaisesRegex(ValueError, "origin"):
            build(a, b, c)

    def test_wrong_ssr_calendar_day_rejected(self):
        a, b, c = fixture()
        a["comparisons"][-1]["NASA_reported_calendar_day_timezone_UNVERIFIED"] = (
            "1963-11-09")
        with self.assertRaisesRegex(ValueError, "origin"):
            build(a, b, c)

    def test_fabricated_utc_certification_rejected(self):
        a, b, c = fixture()
        a["method"]["NASA_date_timezone_known"] = True
        with self.assertRaisesRegex(ValueError, "promoted"):
            build(a, b, c)

    def test_fabricated_independent_holdout_rejected(self):
        a, b, c = fixture()
        a["comparisons"][-1]["independent_terminal_time_validation"] = True
        with self.assertRaisesRegex(ValueError, "nonindependence"):
            build(a, b, c)

    def test_tampered_528_prediction_rejected(self):
        a, b, c = fixture()
        a["comparisons"][-1]["last_two"]["scenarios"][0][
            "hypothetical_terminal_utc"] = "1963-11-22T00:00:00+00:00"
        with self.assertRaisesRegex(ValueError, "cached"):
            build(a, b, c)

    def test_uncalibrated_source_sham_rejected(self):
        a, b, c = fixture()
        a["source"]["sha256_verified_at_ingest"] = "0"*64
        with self.assertRaisesRegex(ValueError, "SHA|lineage"):
            build(a, b, c)

    def test_no_future_data_after_cutoff(self):
        a, b, c = fixture()
        a["comparisons"][-1]["cutoff_utc_exclusive"] = (
            "1963-10-27T00:00:00+00:00")
        with self.assertRaisesRegex(ValueError, "origin"):
            build(a, b, c)


if __name__ == "__main__":
    unittest.main()
