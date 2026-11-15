#!/usr/bin/env python3
"""Adversarial synthetic fixtures for R69 transfer; no synthetic historical claims."""
import copy
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c241_528_censored_transfer_r69 import build, SHA, NULL_INFERENCE
from c241_decay_day_error_r68 import error_interval


def fixture():
    pred = "1963-11-08T13:12:43+00:00"
    r54 = {
        "schema": "conde.c241-king-hele-uncalibrated-day-sensitivity/v1",
        "source": {"sha256_verified_at_ingest": SHA},
        "inference": {"historical_mcmc": "NOT_RUN",
                      "terminal_time_sigma_hours": None, "active_constraint": False},
        "comparisons": [{
            "norad": 528, "cutoff_utc_exclusive": "1963-10-28T00:00:00+00:00",
            "origin_catalogue_epoch_utc": "1963-10-27T14:40:16+00:00",
            "NASA_reported_calendar_day_timezone_UNVERIFIED": "1963-11-08",
            "independent_terminal_time_validation": False,
            "last_two": {"status": "HEURISTIC_ONLY", "scenarios": []},
            "median_three_prior_secants": {"status": "HEURISTIC_ONLY", "scenarios": []}
        }]
    }
    for key in ("last_two", "median_three_prior_secants"):
        for h in (40, 50):
            p = datetime.fromisoformat(pred) + timedelta(days=(h-40)*0.3)
            r54["comparisons"][0][key]["scenarios"].append({
                "H_eff_km_ASSUMED": h,
                "hypothetical_terminal_utc": p.isoformat(),
                "error_days_if_NASA_label_means_UTC_civil_day": error_interval(p, "1963-11-08")
            })
    r68 = {
        "schema": "conde.c241-decay-day-error-unified-r68/v1",
        "source_sha256": SHA,
        "selection": "RETROSPECTIVE_NOT_BLIND",
        "day_clock_assumption": "COUNTERFACTUAL_UTC_CIVIL_DAY_NOT_VERIFIED",
        "inference": copy.deepcopy(NULL_INFERENCE),
        "rows": []
    }
    labels = {637: "1963-11-07", 292: "1963-11-26",
              565: "1963-11-24", 308: "1963-10-30"}
    for sid, label in labels.items():
        start = datetime.fromisoformat(label).replace(tzinfo=timezone.utc)
        seen = set()
        for i in range(4):
            # Two R68 cutoffs for 565 share one origin, not two readings.
            idx = 2 if sid == 565 and i == 3 else i
            origin = start - timedelta(days=14-idx*3)
            cutoff = start - timedelta(days=13-i*3)
            for method in ("last_two", "median_three"):
                for h in (40, 50):
                    p = start + timedelta(days=(sid % 10) - 2 + i + (h-40)*.25)
                    pair = (sid, method, h, origin)
                    new = pair not in seen
                    seen.add(pair)
                    lo, hi = error_interval(p, label)
                    r68["rows"].append({
                        "norad": sid, "method": method,
                        "H_eff_km_assumed": h,
                        "cutoff_utc_exclusive": cutoff.isoformat(),
                        "origin_utc": origin.isoformat(),
                        "published_day": label,
                        "source_grade": ("NASA_SSR_DATE_ONLY_TZ_UNVERIFIED"
                                         if sid == 637 else "SECONDARY_NOT_INDEPENDENT"),
                        "prediction_utc": p.isoformat(),
                        "error_days_lower_open_if_UTC": lo,
                        "error_days_upper_closed_if_UTC": hi,
                        "new_distinct_origin": new,
                        "identity_308_conditional": sid == 308,
                        "status": ("UTC_DAY_COUNTERFACTUAL" if sid == 637
                                   else ("CONDITIONAL_308_OMEGA_ALIAS_UNRESOLVED"
                                         if sid == 308 else "SECONDARY_UTC_DAY_COUNTERFACTUAL"))
                    })
    return r54, r68


class TransferContract(unittest.TestCase):
    def test_scenario_only_and_censor_algebra(self):
        a, b = fixture()
        r = build(a,b)
        self.assertEqual(len(r["results"]),12)
        self.assertEqual(r["inference"],NULL_INFERENCE)
        self.assertEqual(r["independent_control_sensors"],0)
        for row in r["results"]:
            self.assertEqual(row["control_distinct_origins_method_H"],
                             {"ALL_FOUR_CONDITIONAL":15,"OMIT_UNRESOLVED_308":11,
                              "NASA_637_ONLY":4}[row["stratum"]])
            self.assertFalse(row["historical_bound_or_coverage_claim"])
            low = datetime.fromisoformat(row["transferred_terminal_scenario_hull_if_exchangeable"]["lower_closed_utc"])
            high = datetime.fromisoformat(row["transferred_terminal_scenario_hull_if_exchangeable"]["upper_open_utc"])
            pred = datetime.fromisoformat(row["forecast_528_prediction_utc"])
            errors = row["retrospective_control_error_hull_days"]
            self.assertAlmostEqual((pred-low).total_seconds()/86400, errors["upper_closed"],places=5)
            self.assertAlmostEqual((pred-high).total_seconds()/86400, errors["lower_open"],places=5)

    def test_two_estimators_are_not_independent(self):
        r = build(*fixture())
        self.assertTrue(r["method_predictions_are_not_independent"])

    def reject(self, edit):
        a,b = fixture()
        edit(a,b)
        with self.assertRaises(ValueError):
            build(a,b)

    def test_wrong_source_sha(self):
        self.reject(lambda a,b: b.update(source_sha256="bogus"))

    def test_fake_sigma(self):
        self.reject(lambda a,b: b["inference"].update(terminal_time_sigma_hours=10))

    def test_mcmc_promotion(self):
        self.reject(lambda a,b: a["inference"].update(historical_mcmc="DONE"))

    def test_source_grade_misrepresented(self):
        self.reject(lambda a,b: b["rows"][0].update(source_grade="SECONDARY_NOT_INDEPENDENT"))

    def test_308_identity_promotion(self):
        self.reject(lambda a,b: next(r for r in b["rows"] if r["norad"]==308).update(identity_308_conditional=False))

    def test_censoring_reversed(self):
        self.reject(lambda a,b: b["rows"][0].update(error_days_lower_open_if_UTC=100))

    def test_postcutoff_leakage(self):
        self.reject(lambda a,b: b["rows"][0].update(origin_utc="1963-11-30T00:00:00+00:00"))

    def test_non_utc_origin(self):
        self.reject(lambda a,b: b["rows"][0].update(origin_utc="1963-10-20T00:00:00-03:00"))

    def test_missing_control(self):
        self.reject(lambda a,b: b["rows"].pop())

    def test_duplicate_not_marked(self):
        self.reject(lambda a,b: next(r for r in b["rows"] if not r["new_distinct_origin"]).update(new_distinct_origin=True))

    def test_528_terminal_time_promotion(self):
        self.reject(lambda a,b: a["comparisons"][0].update(independent_terminal_time_validation=True))

    def test_528_origin_future(self):
        self.reject(lambda a,b: a["comparisons"][0].update(origin_catalogue_epoch_utc="1963-10-29T00:00:00+00:00"))

    def test_528_predicted_day_tamper(self):
        self.reject(lambda a,b: a["comparisons"][0]["last_two"]["scenarios"][0].update(
            hypothetical_terminal_utc="1963-11-09T13:12:43+00:00"))


if __name__ == "__main__":
    unittest.main()
