#!/usr/bin/env python3
"""R69: scenario-only transfer of R68 censored day errors to 528, not calibration."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from c241_decay_day_error_r68 import SHA, METHODS, HEIGHTS, error_interval, utc

STRATA = {
    "ALL_FOUR_CONDITIONAL": {637, 292, 565, 308},
    "OMIT_UNRESOLVED_308": {637, 292, 565},
    "NASA_637_ONLY": {637},
}
NULL_INFERENCE = {
    "calibrated_terminal_holdouts": 0,
    "terminal_time_sigma_hours": None,
    "historical_mcmc": "NOT_RUN",
    "active_constraint_528": False,
    "impact_geography": None,
}
LABEL_528 = "1963-11-08"
CUTOFF_528 = "1963-10-28T00:00:00+00:00"


def verify(r54: dict, r68: dict) -> dict:
    if r54.get("schema") != "conde.c241-king-hele-uncalibrated-day-sensitivity/v1":
        raise ValueError("wrong R54 schema")
    if r68.get("schema") != "conde.c241-decay-day-error-unified-r68/v1":
        raise ValueError("wrong R68 schema")
    if (r54["source"]["sha256_verified_at_ingest"] != SHA
            or r68["source_sha256"] != SHA):
        raise ValueError("pinned historical source SHA mismatch")
    if (r54["inference"]["historical_mcmc"] != "NOT_RUN"
            or r54["inference"]["terminal_time_sigma_hours"] is not None
            or r54["inference"]["active_constraint"]
            or r68["inference"] != NULL_INFERENCE
            or r68["selection"] != "RETROSPECTIVE_NOT_BLIND"
            or r68["day_clock_assumption"] != "COUNTERFACTUAL_UTC_CIVIL_DAY_NOT_VERIFIED"):
        raise ValueError("calibration/active constraint not licensed")
    candidates = [x for x in r54["comparisons"] if x["norad"] == 528]
    if len(candidates) != 1:
        raise ValueError("expected exactly one 528 forecast origin")
    target = candidates[0]
    if (target["cutoff_utc_exclusive"] != CUTOFF_528
            or target["NASA_reported_calendar_day_timezone_UNVERIFIED"] != LABEL_528
            or target["independent_terminal_time_validation"]
            or not utc(target["origin_catalogue_epoch_utc"]) < utc(CUTOFF_528)):
        raise ValueError("528 forecast origin leaked after cutoff or terminal label promoted")
    for method, key in (("last_two", "last_two"),
                        ("median_three", "median_three_prior_secants")):
        obj = target[key]
        if obj["status"] != "HEURISTIC_ONLY":
            raise ValueError("528 model is not estimable as declared")
        cases = obj["scenarios"]
        if len(cases) != 2 or {s["H_eff_km_ASSUMED"] for s in cases} != set(HEIGHTS):
            raise ValueError("wrong H scenarios")
        for s in cases:
            pred = utc(s["hypothetical_terminal_utc"])
            old = s["error_days_if_NASA_label_means_UTC_civil_day"]
            if max(abs(a - b) for a, b in zip(error_interval(pred, LABEL_528), old)) > 0.00002:
                raise ValueError("528 declared terminal day error inconsistent")
    return target


def distinct_rows(r68: dict) -> list[dict]:
    rows = r68["rows"]
    if len(rows) != 64 or {r["norad"] for r in rows} != {637, 292, 565, 308}:
        raise ValueError("control cohort or count drift")
    unique = []
    seen = set()
    for row in rows:
        sid, m, h = row["norad"], row["method"], row["H_eff_km_assumed"]
        if m not in METHODS or h not in HEIGHTS:
            raise ValueError("unexpected estimator or H")
        if not utc(row["origin_utc"]) < utc(row["cutoff_utc_exclusive"]):
            raise ValueError("post-cutoff training record")
        if row["identity_308_conditional"] != (sid == 308):
            raise ValueError("OMEGA 308 identity promoted")
        if row["source_grade"] not in {"NASA_SSR_DATE_ONLY_TZ_UNVERIFIED", "SECONDARY_NOT_INDEPENDENT"}:
            raise ValueError("unknown source grade")
        if (sid == 637) != (row["source_grade"] == "NASA_SSR_DATE_ONLY_TZ_UNVERIFIED"):
            raise ValueError("source grade/identity mismatch")
        key = (sid, m, h, row["origin_utc"])
        if row["new_distinct_origin"] != (key not in seen):
            raise ValueError("duplicate origins misclassified")
        seen.add(key)
        if row["status"] == "NOT_ESTIMABLE":
            if row["prediction_utc"] is not None:
                raise ValueError("non-estimable record with prediction")
            continue
        if row["status"] not in {"UTC_DAY_COUNTERFACTUAL",
                                 "SECONDARY_UTC_DAY_COUNTERFACTUAL",
                                 "CONDITIONAL_308_OMEGA_ALIAS_UNRESOLVED"}:
            raise ValueError("control became an observational holdout")
        if (sid == 308) != (row["status"] == "CONDITIONAL_308_OMEGA_ALIAS_UNRESOLVED"):
            raise ValueError("conditional identity not marked")
        pred = utc(row["prediction_utc"])
        low, high = error_interval(pred, row["published_day"])
        if (abs(low - row["error_days_lower_open_if_UTC"]) > 2e-5
                or abs(high - row["error_days_upper_closed_if_UTC"]) > 2e-5):
            raise ValueError("cached censor interval disagrees with forecast/day")
        if key not in {(r["norad"],r["method"],r["H_eff_km_assumed"],r["origin_utc"]) for r in unique}:
            unique.append(row)
    if len(unique) != 60:
        raise ValueError("unexpected independent-origin/H/method count")
    return unique


def build(r54: dict, r68: dict) -> dict:
    target = verify(r54, r68)
    controls = distinct_rows(r68)
    output = []
    for method, key in (("last_two", "last_two"),
                        ("median_three", "median_three_prior_secants")):
        for forecast in target[key]["scenarios"]:
            h = forecast["H_eff_km_ASSUMED"]
            prediction = utc(forecast["hypothetical_terminal_utc"])
            for group, eligible in STRATA.items():
                cohort = [r for r in controls
                          if r["norad"] in eligible and r["method"] == method
                          and r["H_eff_km_assumed"] == h]
                if not cohort or not {r["norad"] for r in cohort} == eligible:
                    raise ValueError("missing control/stratum")
                # If E=(low,high] is prediction - terminal, then
                # terminal=[prediction-high, prediction-low). The hull of a
                # finite union is NOT an observed, guaranteed or confidence bound.
                minimum_error_open = min(r["error_days_lower_open_if_UTC"] for r in cohort)
                maximum_error_closed = max(r["error_days_upper_closed_if_UTC"] for r in cohort)
                lower = prediction - timedelta(days=maximum_error_closed)
                upper = prediction - timedelta(days=minimum_error_open)
                if not lower < upper:
                    raise ValueError("invalid transferred scenario hull")
                date_begin = datetime.fromisoformat(LABEL_528).replace(tzinfo=timezone.utc)
                date_end = date_begin + timedelta(days=1)
                output.append({
                    "stratum": group,
                    "control_norads": sorted(eligible),
                    "control_distinct_origins_method_H": len(cohort),
                    "method": method,
                    "H_eff_km_ASSUMED": h,
                    "forecast_528_origin_utc": target["origin_catalogue_epoch_utc"],
                    "forecast_528_cutoff_utc_exclusive": target["cutoff_utc_exclusive"],
                    "forecast_528_prediction_utc": prediction.isoformat(timespec="seconds"),
                    "retrospective_control_error_hull_days": {
                        "lower_open": minimum_error_open, "upper_closed": maximum_error_closed
                    },
                    "transferred_terminal_scenario_hull_if_exchangeable": {
                        "lower_closed_utc": lower.isoformat(timespec="seconds"),
                        "upper_open_utc": upper.isoformat(timespec="seconds")
                    },
                    "nasa_528_day_label": LABEL_528,
                    "hull_intersects_hypothetical_UTC_NASA_day": lower < date_end and upper > date_begin,
                    "historical_bound_or_coverage_claim": False
                })
    if len(output) != 12:
        raise ValueError("expected twelve scenario-only transfers")
    return {
        "schema": "conde.c241-528-retrospective-day-error-transfer-r69/v1",
        "source_sha256": SHA,
        "inputs": ["C241-R54/PR841", "C241-R68/PR1013"],
        "selection": "POST_INSPECTION_RETROSPECTIVE_NOT_BLIND",
        "day_clock": "IF_NASA_DATES_ARE_UTC_CIVIL_DAYS_ONLY",
        "exchangeability_of_637_292_565_308_with_528": "NOT_ESTABLISHED",
        "interpretation": "HULL_OF_HYPOTHETICAL_TRANSFER_SCENARIOS_NOT_A_CONFIDENCE_INTERVAL_OR_PHYSICAL_BOUND",
        "independent_control_sensors": 0,
        "method_predictions_are_not_independent": True,
        "results": output,
        "inference": NULL_INFERENCE
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r54", type=Path, required=True)
    parser.add_argument("--r68", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = build(json.loads(args.r54.read_text(encoding="utf-8")),
                   json.loads(args.r68.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R69: 12 scenario hulls, zero independently calibrated holdouts, MCMC NOT_RUN")


if __name__ == "__main__":
    main()
