#!/usr/bin/env python3
"""R68: unify previously audited R54/R60 day-error scenarios; NOT reentry calibration."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path

SHA = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
METHODS = ("last_two", "median_three")
HEIGHTS = (40, 50)
DAYS = {292: "1963-11-26", 565: "1963-11-24", 308: "1963-10-30"}
FIELDS = ("norad", "method", "cutoff_utc_exclusive", "origin_utc",
          "H_eff_km_assumed", "published_day", "published_source_url",
          "source_grade", "prediction_utc", "error_days_lower_open_if_UTC",
          "error_days_upper_closed_if_UTC", "new_distinct_origin",
          "identity_308_conditional", "status")


def utc(text: str) -> datetime:
    value = datetime.fromisoformat(text)
    if value.utcoffset() != timedelta(0):
        raise ValueError("UTC timestamp required")
    return value


def error_interval(pred: datetime, label: str, width_days: int = 1) -> tuple[float, float]:
    if len(label) != 10 or datetime.fromisoformat(label).date().isoformat() != label:
        raise ValueError("ISO calendar label required")
    if width_days not in (1, 2):
        raise ValueError("unsupported censor width")
    start = datetime.fromisoformat(label).replace(tzinfo=timezone.utc)
    return (round((pred - start - timedelta(days=width_days)).total_seconds() / 86400, 6),
            round((pred - start).total_seconds() / 86400, 6))


def validate(r54: dict, r60: dict) -> None:
    if r54["schema"] != "conde.c241-king-hele-uncalibrated-day-sensitivity/v1":
        raise ValueError("wrong R54 schema")
    if r60["schema"] != "conde.c241-1963-archive-fixed-h-stress/v1":
        raise ValueError("wrong R60 schema")
    if (r54["source"]["sha256_verified_at_ingest"] != SHA
            or r60["source"]["sha256"] != SHA):
        raise ValueError("input lineage/SHA mismatch")
    if (r54["inference"]["terminal_time_sigma_hours"] is not None
            or r54["inference"]["historical_mcmc"] != "NOT_RUN"
            or r60["inference"]["terminal_time_sigma_hours"] is not None
            or r60["inference"]["calibrated_terminal_holdouts"] != 0
            or r60["design"]["selection"] != "POST_INSPECTION_RETROSPECTIVE"):
        raise ValueError("unverified calibration/promotion")


def make_row(sid: int, method: str, cutoff: str, origin: str, h: int,
             day: str, source: str, grade: str, prediction: datetime | None,
             new_origin: bool, status: str) -> dict:
    if not utc(origin) < utc(cutoff):
        raise ValueError("post-cutoff leakage")
    if h not in HEIGHTS or method not in METHODS:
        raise ValueError("undeclared model scenario")
    low, high = error_interval(prediction, day) if prediction else (None, None)
    values = (sid, method, cutoff, origin, h, day, source, grade,
              prediction.isoformat(timespec="seconds") if prediction else None,
              low, high, new_origin, sid == 308, status)
    return dict(zip(FIELDS, values))


def build(r54: dict, r60: dict) -> dict:
    validate(r54, r60)
    rows = []
    nasa = "https://ntrs.nasa.gov/citations/19640003479"
    source637 = [c for c in r54["comparisons"] if c["norad"] == 637]
    if len(source637) != 4 or len({c["cutoff_utc_exclusive"] for c in source637}) != 4:
        raise ValueError("four unique NASA 637 cutoffs required")
    for c in source637:
        if c["NASA_reported_calendar_day_timezone_UNVERIFIED"] != "1963-11-07":
            raise ValueError("unexpected NASA 637 day")
        for method, key in (("last_two", "last_two"),
                            ("median_three", "median_three_prior_secants")):
            payload = c[key]
            if payload["status"] != "HEURISTIC_ONLY" or len(payload["scenarios"]) != 2:
                raise ValueError("missing 637 scenario")
            if {item["H_eff_km_ASSUMED"] for item in payload["scenarios"]} != set(HEIGHTS):
                raise ValueError("637 scenario heights must include exactly 40 and 50 km")
            for scenario in payload["scenarios"]:
                h = scenario["H_eff_km_ASSUMED"]
                pred = utc(scenario["hypothetical_terminal_utc"])
                old = scenario["error_days_if_NASA_label_means_UTC_civil_day"]
                if max(abs(a-b) for a, b in zip(error_interval(pred, "1963-11-07"), old)) > 2e-5:
                    raise ValueError("637 cached error contradicts date")
                row = make_row(637, method, c["cutoff_utc_exclusive"],
                               c["origin_catalogue_epoch_utc"], h, "1963-11-07",
                               nasa, "NASA_SSR_DATE_ONLY_TZ_UNVERIFIED", pred, True,
                               "UTC_DAY_COUNTERFACTUAL")
                # R54's cached intervals retain higher precision than its seconds-formatted UTC.
                row["error_days_lower_open_if_UTC"], row["error_days_upper_closed_if_UTC"] = old
                rows.append(row)
    if set(r60["cases"]) != {"292", "308", "565", "668"}:
        raise ValueError("R60 cohort drift")
    for sid in (292, 565, 308):
        case = r60["cases"][str(sid)]
        if (case["secondary_terminal_day"] != DAYS[sid]
                or case["date_utc_convention_verified"]
                or case["terminal_holdout_ready"]):
            raise ValueError("archive day promoted or changed")
        for method in METHODS:
            method_data = case["methods"][method]
            attempts = method_data["attempts"]
            origins = method_data["origins"]
            by_origin = {item["origin_utc"]: item for item in origins}
            if (len(attempts) != 4
                    or len({a["cutoff_utc"] for a in attempts}) != 4
                    or len(by_origin) != len(origins)):
                raise ValueError("missing or duplicated cutoffs or conflicting origins")
            seen = set()
            for attempt in attempts:
                origin = attempt["origin_utc"]
                if origin not in by_origin or attempt["status"] != by_origin[origin]["status"]:
                    raise ValueError("invalid origin/cutoff mapping")
                value = by_origin[origin]
                new = origin not in seen
                seen.add(origin)
                rate = value.get("decay_magnitude_km_day_LOCAL_PROXY")
                for h in HEIGHTS:
                    if attempt["status"] == "COUNTERFACTUAL_INTERVAL_ONLY":
                        if not isinstance(rate, (float, int)) or not math.isfinite(rate) or rate <= 0:
                            raise ValueError("missing physical proxy secant")
                        pred = utc(origin) + timedelta(days=h / rate)
                        status = ("CONDITIONAL_308_OMEGA_ALIAS_UNRESOLVED" if sid == 308
                                  else "SECONDARY_UTC_DAY_COUNTERFACTUAL")
                    else:
                        if rate is not None:
                            raise ValueError("unestimable interval with rate")
                        pred, status = None, "NOT_ESTIMABLE"
                    rows.append(make_row(sid, method, attempt["cutoff_utc"],
                                         origin, h, DAYS[sid], case["url"],
                                         "SECONDARY_NOT_INDEPENDENT", pred, new, status))
    if (len(rows) != 64 or sum(bool(r["new_distinct_origin"]) for r in rows) != 60
            or any(r["norad"] == 528 for r in rows)):
        raise ValueError("cohort cardinality/pseudoreplication failure")
    return {
        "schema": "conde.c241-decay-day-error-unified-r68/v1",
        "source_sha256": SHA,
        "input_analyses": ["C241-R54/PR841", "C241-R60/PR924"],
        "selection": "RETROSPECTIVE_NOT_BLIND",
        "day_clock_assumption": "COUNTERFACTUAL_UTC_CIVIL_DAY_NOT_VERIFIED",
        "error_sign": "predicted_minus_actual",
        "interval": "(lower_open,upper_closed] days",
        "nasa_308_omega1_two_day_alternative": {
            "days_inclusive": ["1963-10-29", "1963-10-30"],
            "identity_in_1963_unresolved": True,
            "not_used_as_independent_terminal_measurement": True
        },
        "fixed_H_crosscutoff": "R57/R58/R60 exclude common H in their stated shift scenarios; NOT a calibrated day-error distribution",
        "rows": rows,
        "inference": {
            "calibrated_terminal_holdouts": 0,
            "terminal_time_sigma_hours": None,
            "historical_mcmc": "NOT_RUN",
            "active_constraint_528": False,
            "impact_geography": None
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r54", type=Path, required=True)
    parser.add_argument("--r60", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--tsv", type=Path, required=True)
    args = parser.parse_args()
    result = build(json.loads(args.r54.read_text(encoding="utf-8")),
                   json.loads(args.r60.read_text(encoding="utf-8")))
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.tsv.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
                         encoding="utf-8")
    with args.tsv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, delimiter="\t", fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["rows"])
    print("R68: 64 rows, 60 unique-origin/H/method scenarios, 0 calibrated holdouts; historical MCMC NOT_RUN")


if __name__ == "__main__":
    main()
