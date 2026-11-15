#!/usr/bin/env python3
"""R69: append frozen R54 NORAD 528 scenarios to the audited R68 day-error table.

A NASA date label is not a measured terminal instant. This is retrospective,
conditional sensitivity, never a calibrated distribution or a geographical test.
"""
from __future__ import annotations

import argparse
import csv
from datetime import timedelta
import json
from pathlib import Path

from c241_decay_day_error_r68 import (
    FIELDS, HEIGHTS, METHODS, SHA, build as build_r68, error_interval,
    make_row, utc,
)

NASA = "https://ntrs.nasa.gov/citations/19640003479"
CUTOFF = "1963-10-28T00:00:00+00:00"
SSR_DAY = "1963-11-08"
SCHEMA = "conde.c241-decay-day-error-528-r69/v1"


def envelope(rows: list[dict]) -> dict:
    estimable = [r for r in rows if r["prediction_utc"] is not None]
    if not estimable:
        raise ValueError("no estimable comparison in controls")
    lo = min(r["error_days_lower_open_if_UTC"] for r in estimable)
    hi = max(r["error_days_upper_closed_if_UTC"] for r in estimable)
    if not lo < hi:
        raise ValueError("empty proxy error envelope")
    return {
        "lower_open_days_if_UTC": lo,
        "upper_closed_days_if_UTC": hi,
        "width_days": round(hi - lo, 6),
        "scenarios": len(estimable),
        "status": "RETROSPECTIVE_PROXY_ENVELOPE_NOT_CONFIDENCE_OR_SIGMA",
    }


def build(r54: dict, r60: dict, r68: dict) -> dict:
    """Do not silently replace, reorder, or relax any previously audited R68 row."""
    expected = build_r68(r54, r60)
    if r68 != expected:
        raise ValueError("R68 cached table differs from frozen replay")
    if r54["source"]["sha256_verified_at_ingest"] != SHA:
        raise ValueError("528 Parquet lineage mismatch")
    if (r54["inference"]["active_constraint"] is not False
            or r54["inference"]["terminal_time_sigma_hours"] is not None
            or r54["inference"]["historical_mcmc"] != "NOT_RUN"
            or r54["method"]["NASA_date_timezone_known"] is not False
            or r54["method"]["H_eff_km_exploratory"] != list(HEIGHTS)):
        raise ValueError("R54 model, date or inference silently promoted")

    cases = [c for c in r54["comparisons"] if c["norad"] == 528]
    if len(cases) != 1:
        raise ValueError("expected one frozen 528 origin, no extra cutoffs")
    c = cases[0]
    origin = c["origin_catalogue_epoch_utc"]
    if (c["cutoff_utc_exclusive"] != CUTOFF
            or c["NASA_reported_calendar_day_timezone_UNVERIFIED"] != SSR_DAY
            or not c["prior_catalogue_epochs"] >= 4
            or c["independent_terminal_time_validation"] is not False
            or not utc(origin) < utc(CUTOFF)
            or utc(origin).date().isoformat() != "1963-10-27"):
        raise ValueError("528 origin, cutoff, UTC date or nonindependence changed")

    appended = []
    for method, source_key in (
        ("last_two", "last_two"),
        ("median_three", "median_three_prior_secants"),
    ):
        payload = c[source_key]
        status = payload["status"]
        scenarios = payload["scenarios"]
        if status == "HEURISTIC_ONLY":
            if (len(scenarios) != 2
                    or {s["H_eff_km_ASSUMED"] for s in scenarios} != set(HEIGHTS)):
                raise ValueError("528 scenario heights must be 40 and 50 once each")
            by_height = {s["H_eff_km_ASSUMED"]: s for s in scenarios}
        elif status.startswith("NOT_ESTIMABLE"):
            if scenarios:
                raise ValueError("unestimable 528 scenario has prediction")
            by_height = {}
        else:
            raise ValueError("unexpected 528 scenario status")
        for h in HEIGHTS:
            sample = by_height.get(h)
            pred = utc(sample["hypothetical_terminal_utc"]) if sample else None
            if sample:
                cached = sample["error_days_if_NASA_label_means_UTC_civil_day"]
                if (not isinstance(cached, list) or len(cached) != 2
                        or max(abs(a-b) for a, b in zip(
                            error_interval(pred, SSR_DAY), cached)) > 2e-5
                        or sample["life_remaining_days_HEURISTIC"] <= 0
                        or pred <= utc(origin)):
                    raise ValueError("528 cached prediction/error disagrees with frozen model")
            row = make_row(
                528, method, CUTOFF, origin, h, SSR_DAY, NASA,
                "NASA_SSR_DATE_ONLY_TZ_UNVERIFIED_NOT_TERMINAL_HOLDOUT",
                pred, True,
                "528_RETROSPECTIVE_UTC_DAY_COUNTERFACTUAL"
                if sample else "528_NOT_ESTIMABLE",
            )
            if sample:
                row["error_days_lower_open_if_UTC"] = cached[0]
                row["error_days_upper_closed_if_UTC"] = cached[1]
            appended.append(row)
    if len(appended) != 4 or {r["method"] for r in appended} != set(METHODS):
        raise ValueError("528 frozen scenarios incomplete")

    controls = [r for r in expected["rows"] if r["norad"] in (637, 292, 565)]
    controls_all = expected["rows"]
    env = envelope(controls)
    env_with_conditional_308 = envelope(controls_all)
    if env["width_days"] <= 1:
        raise ValueError("unexpected sub-day control envelope: review before concluding")
    combined = expected["rows"] + appended
    if len(combined) != 68 or len(expected["rows"]) != 64:
        raise ValueError("incorrect cohort cardinality")
    return {
        "schema": SCHEMA,
        "source_sha256": SHA,
        "input_analyses": ["C241-R54/PR841", "C241-R60/PR924",
                           "C241-R68/PR1013", "G81/PR1017"],
        "selection": "RETROSPECTIVE_NOT_BLIND",
        "day_clock_assumption": "COUNTERFACTUAL_UTC_CIVIL_DAY_NOT_VERIFIED",
        "error_sign": "predicted_minus_actual",
        "interval": "(lower_open,upper_closed] days",
        "rows": combined,
        "added_528_rows": 4,
        "controls_proxy_error_envelope_excluding_unresolved_308": env,
        "controls_proxy_error_envelope_including_conditional_308":
            env_with_conditional_308,
        "conclusion": {
            "question": "Does the 27 October 528 dynamics refine the SSR 8 NOV date?",
            "answer": "NO_ONLY_CONDITIONALLY_COMPATIBLE",
            "reason": "The 528 scenarios depend on assumed H and an unverified UTC "
                      "interpretation of a NASA date-only label; retrospective controls "
                      "span multiple days and are neither independent terminal-time "
                      "holdouts nor a calibrated prediction-error distribution.",
            "terminal_observation_528": None,
            "all_528_scenarios_are_retrospective": True,
            "controls_envelope_wider_than_one_day": True,
        },
        "inference": dict(expected["inference"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("r54", "r60", "r68", "json", "tsv"):
        parser.add_argument("--" + flag, type=Path, required=True)
    args = parser.parse_args()
    data = build(*(json.loads(getattr(args, key).read_text(encoding="utf-8"))
                   for key in ("r54", "r60", "r68")))
    for path in (args.json, args.tsv):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(data, indent=2, sort_keys=True,
                                   allow_nan=False) + "\n", encoding="utf-8")
    with args.tsv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(data["rows"])
    print("R69: 68 rows (64 preserved + 4 frozen NORAD 528); "
          "only conditional compatibility, no terminal sigma or MCMC")
    for row in data["rows"][-4:]:
        print(row["method"], row["H_eff_km_assumed"], row["prediction_utc"],
              row["error_days_lower_open_if_UTC"],
              row["error_days_upper_closed_if_UTC"])


if __name__ == "__main__":
    main()
