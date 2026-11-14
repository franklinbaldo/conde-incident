#!/usr/bin/env python3
"""C241 R62: calendar-label information limits, NOT calibrated reentry error.

Compare the secondary 308 day with NASA's two-day printed range. Conversions
to UTC are hypothetical only. No original sensor or posterior is inferred.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
from pathlib import Path

SCHEMA = "conde.c241-terminal-calendar-minimax-conditional/v1"
BASE_SCHEMA = "conde.c241-1963-archive-fixed-h-stress/v1"
NTRS_ID = "19640003479"
SOURCE_SHA = "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f"


def _day(value: str) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError("invalid calendar day")
    try:
        day = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("invalid calendar day") from error
    if day.isoformat() != value:
        raise ValueError("noncanonical calendar day")
    return day


def _conditional_window(start: date, last: date, label: str) -> dict:
    """Exact minimax radius of a point estimator on an ASSUMED day interval."""
    if last < start:
        raise ValueError("reversed calendar interval")
    end = last + timedelta(days=1)
    days = (end - start).days
    if days > 3:
        raise ValueError("unbounded printed interval")
    return {
        "label": label,
        "begin_utc_IF_UTC_DAY_HYPOTHESIS": start.isoformat() + "T00:00:00Z",
        "end_utc_exclusive_IF_UTC_DAY_HYPOTHESIS": end.isoformat() + "T00:00:00Z",
        "hypothetical_width_hours": 24 * days,
        "best_possible_worst_case_point_error_hours_IF_UTC": 12 * days,
        "historical_utc_bound": False,
        "instrumentally_observed_interval": False,
    }


def report(baseline: dict, ssr: dict) -> dict:
    """Never promote a publication calendar date to measured UTC reentry time."""
    if baseline.get("schema") != BASE_SCHEMA:
        raise ValueError("R60 schema mismatch")
    if baseline.get("design", {}).get("clock") != (
        "SECONDARY_DAY_AS_HYPOTHETICAL_UTC_NOT_VERIFIED"
    ):
        raise ValueError("historical UTC clock unverified")
    if baseline.get("inference", {}).get("historical_mcmc") != "NOT_RUN":
        raise ValueError("historical posterior unverified")
    if baseline["inference"].get("active_constraint_528") is not False:
        raise ValueError("528 must remain unconstrained")
    case = baseline.get("cases", {}).get("308", {})
    if case.get("secondary_terminal_day") != "1963-10-30":
        raise ValueError("secondary 308 day changed")
    if case.get("terminal_holdout_ready") is not False:
        raise ValueError("308 is not calibrated holdout")
    if ssr.get("id") != "C241-L64":
        raise ValueError("NASA source identity changed")
    source, row, identity = ssr["source"], ssr["original_row"], ssr["identity"]
    if (source.get("ntrs_id") != NTRS_ID or source.get("pdf_sha256") != SOURCE_SHA
            or source.get("individual_instrumental_observation") is not False):
        raise ValueError("NASA source custody/lineage unverified")
    if (row.get("decay_printed") != "29-30 OCT 63"
            or row.get("interpretation") != "PUBLISHED_CALENDAR_RANGE_NOT_UTC_EVENT"
            or any(row.get(k) is not None for k in (
                "printed_norad_id", "terminal_utc", "utc_interval",
                "sensor", "station", "sigma_seconds"))):
        raise ValueError("NASA calendar labels are not terminal observations")
    if (identity.get("secondary_norad_id") != 308
            or identity.get("nasa_explicitly_prints_308") is not False):
        raise ValueError("308 crosswalk is secondary")
    first = _day(row.get("calendar_range_start"))
    last = _day(row.get("calendar_range_end"))
    if first.isoformat() != "1963-10-29" or last != first + timedelta(days=1):
        raise ValueError("printed range drift")
    secondary = _day(case["secondary_terminal_day"])
    if secondary != last:
        raise ValueError("secondary catalogue day diverged")
    windows = {
        "nasa_2day_print": _conditional_window(first, last, "NASA_PRIMARY_PUBLICATION"),
        "secondary_1day_lead": _conditional_window(secondary, secondary, "SECONDARY_CATALOGUE"),
    }
    return {
        "schema": SCHEMA,
        "subject": "NORAD_308_BY_SECONDARY_CROSSWALK_ONLY",
        "source": {"id": "C241-L64", "ntrs_id": NTRS_ID, "pdf_sha256": SOURCE_SHA},
        "design": {
            "comparison": "RETROSPECTIVE_NOT_BLIND",
            "assume_each_printed_day_is_FULL_UTC_DAY": True,
            "actual_terminal_utc_semantics_known": False,
            "minimax_is_set_identification_NOT_sigma": True,
            "source_independent_instrument_count": 0,
        },
        "conditional_windows": windows,
        "inference": {
            "calibrated_terminal_holdouts": 0,
            "terminal_sigma_hours": None,
            "historical_mcmc": "NOT_RUN",
            "mass_528_posterior": None,
            "active_constraint_528": False,
            "impact_probability": None,
            "geography_restricted": False,
        },
        "next_discriminant": "ORIGINAL_308_ID_AND_INSTRUMENTED_TERMINAL_UTC_WITH_ERRORS",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r60", type=Path, required=True)
    parser.add_argument("--ssr", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = report(json.loads(args.r60.read_text(encoding="utf-8")),
                  json.loads(args.ssr.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print("R62: 48h/24h conditional printed windows; calibration NOT_RUN")


if __name__ == "__main__":
    main()
