"""R68 adversarial tests; synthetic fixtures are not historical observations."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c241_decay_day_error_r68 import SHA, build, error_interval, utc

UTC = timezone.utc


def fixture():
    r54 = {
        "schema": "conde.c241-king-hele-uncalibrated-day-sensitivity/v1",
        "source": {"sha256_verified_at_ingest": SHA},
        "inference": {"terminal_time_sigma_hours": None, "historical_mcmc": "NOT_RUN"},
        "comparisons": []
    }
    for n in range(4):
        cut = datetime(1963, 10, 18 + n, tzinfo=UTC)
        origin = cut - timedelta(days=1)
        entries = []
        for h in (40, 50):
            pred = datetime(1963, 11, 8 + n, tzinfo=UTC) + timedelta(hours=h)
            entries.append({
                "H_eff_km_ASSUMED": h, "hypothetical_terminal_utc": pred.isoformat(),
                "error_days_if_NASA_label_means_UTC_civil_day":
                    list(error_interval(pred, "1963-11-07"))
            })
        r54["comparisons"].append({
            "norad": 637, "cutoff_utc_exclusive": cut.isoformat(),
            "origin_catalogue_epoch_utc": origin.isoformat(),
            "NASA_reported_calendar_day_timezone_UNVERIFIED": "1963-11-07",
            "last_two": {"status": "HEURISTIC_ONLY", "scenarios": deepcopy(entries)},
            "median_three_prior_secants": {
                "status": "HEURISTIC_ONLY", "scenarios": deepcopy(entries)}
        })
    r60 = {
        "schema": "conde.c241-1963-archive-fixed-h-stress/v1",
        "source": {"sha256": SHA},
        "design": {"selection": "POST_INSPECTION_RETROSPECTIVE"},
        "inference": {"terminal_time_sigma_hours": None, "calibrated_terminal_holdouts": 0},
        "cases": {}
    }
    for sid, day in ((292, "1963-11-26"), (565, "1963-11-24"),
                     (308, "1963-10-30"), (668, "1963-10-12")):
        methods = {}
        for method in ("last_two", "median_three"):
            origins, attempts = [], []
            base = datetime.fromisoformat(day).replace(tzinfo=UTC)
            for n in range(4):
                origin = base - timedelta(days=15 - n * 3)
                if sid == 565 and n == 1:
                    origin = base - timedelta(days=15)
                cutoff = base - timedelta(days=14 - n * 3)
                record = {
                    "origin_utc": origin.isoformat(),
                    "status": "COUNTERFACTUAL_INTERVAL_ONLY",
                    "decay_magnitude_km_day_LOCAL_PROXY": 2.0 + n / 10}
                if sid == 565 and n == 1:
                    record["decay_magnitude_km_day_LOCAL_PROXY"] = 2.0
                if not any(x["origin_utc"] == record["origin_utc"] for x in origins):
                    origins.append(record)
                attempts.append({
                    "origin_utc": record["origin_utc"], "cutoff_utc": cutoff.isoformat(),
                    "status": record["status"]})
            methods[method] = {"origins": origins, "attempts": attempts}
        r60["cases"][str(sid)] = {
            "secondary_terminal_day": day, "url": f"https://example.invalid/{sid}",
            "date_utc_convention_verified": False,
            "terminal_holdout_ready": False, "methods": methods}
    return r54, r60


class DayErrorTests(unittest.TestCase):
    def test_censor_half_open_actual_becomes_open_lower(self):
        pred = datetime(1963, 11, 9, tzinfo=UTC)
        self.assertEqual(error_interval(pred, "1963-11-07"), (1.0, 2.0))
        self.assertEqual(error_interval(pred, "1963-11-07", 2), (0.0, 2.0))

    def test_utc_not_local_time(self):
        with self.assertRaisesRegex(ValueError, "UTC"):
            utc("1963-11-07T00:00:00-04:00")

    def test_invalid_censor_width(self):
        with self.assertRaises(ValueError):
            error_interval(datetime(1963, 11, 7, tzinfo=UTC), "1963-11-07", 3)

    def test_four_controls_and_duplicate_origin_coalescing(self):
        x = build(*fixture())
        self.assertEqual(len(x["rows"]), 64)
        self.assertEqual(sum(r["new_distinct_origin"] for r in x["rows"]), 60)
        self.assertEqual({r["norad"] for r in x["rows"]}, {637, 292, 308, 565})
        self.assertTrue(all(r["norad"] != 528 for r in x["rows"]))

    def test_308_alias_never_confirmed(self):
        x = build(*fixture())
        self.assertTrue(all(r["identity_308_conditional"] for r in x["rows"]
                            if r["norad"] == 308))
        self.assertEqual(x["nasa_308_omega1_two_day_alternative"]["days_inclusive"],
                         ["1963-10-29", "1963-10-30"])

    def test_calibration_disabled(self):
        x = build(*fixture())
        self.assertIsNone(x["inference"]["terminal_time_sigma_hours"])
        self.assertFalse(x["inference"]["active_constraint_528"])
        self.assertEqual(x["inference"]["historical_mcmc"], "NOT_RUN")

    def test_sha_mutation_fails_closed(self):
        a, b = fixture()
        b["source"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA"):
            build(a, b)

    def test_posterior_promotion_rejected(self):
        a, b = fixture()
        a["inference"]["terminal_time_sigma_hours"] = 12
        with self.assertRaisesRegex(ValueError, "calibration"):
            build(a, b)

    def test_undocumented_timezone_rejected(self):
        a, b = fixture()
        b["cases"]["292"]["date_utc_convention_verified"] = True
        with self.assertRaisesRegex(ValueError, "promoted"):
            build(a, b)

    def test_postcutoff_leakage_rejected(self):
        a, b = fixture()
        b["cases"]["292"]["methods"]["last_two"]["attempts"][0]["cutoff_utc"] = (
            datetime(1963, 11, 1, tzinfo=UTC).isoformat())
        with self.assertRaisesRegex(ValueError, "post-cutoff"):
            build(a, b)

    def test_mismatched_cached_error_rejected(self):
        a, b = fixture()
        a["comparisons"][0]["last_two"]["scenarios"][0][
            "error_days_if_NASA_label_means_UTC_civil_day"] = [100, 101]
        with self.assertRaisesRegex(ValueError, "contradicts"):
            build(a, b)

    def test_conflicting_duplicate_origin_rejected(self):
        a, b = fixture()
        b["cases"]["565"]["methods"]["last_two"]["attempts"][1]["status"] = "NOT_ESTIMABLE"
        with self.assertRaisesRegex(ValueError, "origin/cutoff"):
            build(a, b)

    def test_nonpositive_rate_rejected(self):
        a, b = fixture()
        b["cases"]["292"]["methods"]["last_two"]["origins"][0][
            "decay_magnitude_km_day_LOCAL_PROXY"] = -1
        with self.assertRaisesRegex(ValueError, "positive|proxy"):
            build(a, b)


if __name__ == "__main__":
    unittest.main()
