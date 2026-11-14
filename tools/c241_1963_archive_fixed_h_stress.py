#!/usr/bin/env python3
"""R60: secondary calendar-day fixed-H stress, NOT reentry calibration."""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from c241_1963_terminal_control_screen import CASES, collect_pinned, screen, unique_epochs
from c241_king_hele_fixed_h_falsifier import required_h_for_one_origin, common_h_under_day_shift
from c241_fixed_h_day_shift_G71 import day_shift_certificate

OFFSETS_DAYS = (14, 10, 6, 3)
METHODS = ("last_two", "median_three")
CANDIDATES = (292, 308, 565, 668)


def evaluate(rows: list[dict], day: str, method: str) -> dict:
    """Deduplicate identical source epochs before testing multiple origins."""
    if method not in METHODS:
        raise ValueError("unknown method")
    midnight = datetime.fromisoformat(day).replace(tzinfo=timezone.utc)
    attempts, unique = [], {}
    for offset in OFFSETS_DAYS:
        cutoff = (midnight - timedelta(days=offset)).isoformat()
        rec = required_h_for_one_origin(rows, cutoff, day, method)
        origin = rec["origin_utc"]
        attempts.append({"offset_days": offset, "cutoff_utc": cutoff,
                         "origin_utc": origin, "status": rec["status"]})
        key = origin if origin is not None else "missing_" + str(offset)
        if key in unique:
            for field in ("required_H_km_UTC_DAY_COUNTERFACTUAL",
                          "decay_magnitude_km_day_LOCAL_PROXY", "status"):
                if rec.get(field) != unique[key].get(field):
                    raise ValueError("conflicting same-origin results")
        else:
            unique[key] = rec
    origins = list(unique.values())
    if len(origins) < 2:
        common = {"status": "NOT_ESTIMABLE_FEWER_DISTINCT_ORIGINS",
                  "calibrated_timezone": False}
        independent = {"status": "NOT_ESTIMABLE_FEWER_DISTINCT_ORIGINS",
                       "active_constraint": False}
    else:
        common = common_h_under_day_shift(origins, -24.0, 24.0)
        independent = day_shift_certificate(origins, 1.0)
    return {"attempts": attempts, "distinct_catalogue_origins": len(origins),
            "duplicate_cutoffs_coalesced": len(attempts)-len(origins),
            "origins": origins, "common_clock_24h": common,
            "independent_1day": independent}


def report(groups: dict[int, list[dict]], *, pinned: bool) -> dict:
    archive = screen(groups, pin_counts=pinned)
    cases = {}
    for sid in CANDIDATES:
        day, url, grade, role = CASES[sid]
        if role != "CANDIDATE" or grade != "SECONDARY_DECAY_DAY_LEAD":
            raise ValueError("secondary day incorrectly promoted")
        rows = unique_epochs(groups[sid], sid)
        cases[str(sid)] = {
            "secondary_terminal_day": day, "url": url,
            "date_utc_convention_verified": False,
            "unique_catalogue_epochs": len(rows),
            "methods": {m: evaluate(rows, day, m) for m in METHODS},
            "terminal_holdout_ready": False}
    if any(c["terminal_holdout_ready"] for c in archive["cases"]):
        raise ValueError("R59 provenance contract drift")
    return {
        "schema": "conde.c241-1963-archive-fixed-h-stress/v1",
        "source": archive["source"],
        "design": {
            "selection": "POST_INSPECTION_RETROSPECTIVE",
            "clock": "SECONDARY_DAY_AS_HYPOTHETICAL_UTC_NOT_VERIFIED",
            "offsets_days_before_day": list(OFFSETS_DAYS),
            "clock_shift_common_hours": [-24, 24],
            "day_shift_independent_days": 1,
            "repeated_catalogue_origins_are_not_new_tests": True,
            "physical_atmosphere_test": False,
        },
        "cases": cases,
        "inference": {
            "active_constraint_528": False,
            "historical_mcmc": "NOT_RUN",
            "calibrated_terminal_holdouts": 0,
            "terminal_time_sigma_hours": None,
            "mass_528_posterior": None,
            "impact_probability": None,
            "impact_geography": None,
            "physical_atmosphere_falsified": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = report(collect_pinned(args.parquet), pinned=args.check)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False)
                           + "\n", encoding="utf-8")
    for sid, rec in payload["cases"].items():
        print(sid, {m: v["common_clock_24h"]["status"]
                    for m, v in rec["methods"].items()})
    print("R60 proxy stress; independent terminal observations 0; MCMC NOT_RUN")


if __name__ == "__main__":
    main()
