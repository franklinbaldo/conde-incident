#!/usr/bin/env python3
"""R61: SSR two-day printed interval, not a calibrated UTC terminal time."""
from __future__ import annotations

import argparse
from datetime import date
import json
import math
from pathlib import Path

from c241_king_hele_fixed_h_falsifier import common_h_under_day_shift

SCHEMA = "conde.c241-308-ssr-calendar-range-conditional/v1"
SSR_ID = "C241-L64"
SOURCE_SHA = "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f"


def _civil_day(s: str) -> date:
    if not isinstance(s, str) or len(s) != 10 or s[4] != "-" or s[7] != "-":
        raise ValueError("invalid YYYY-MM-DD calendar label")
    try:
        parsed = date.fromisoformat(s)
    except (TypeError, ValueError) as err:
        raise ValueError("invalid calendar date") from err
    if parsed.isoformat() != s:
        raise ValueError("noncanonical date")
    return parsed


def _validate_source(ssr: dict, baseline: dict) -> int:
    """Fail closed on lineage, identity and printed interval."""
    if baseline.get("schema") != "conde.c241-1963-archive-fixed-h-stress/v1":
        raise ValueError("R60 schema mismatch")
    if baseline.get("design", {}).get("clock") != "SECONDARY_DAY_AS_HYPOTHETICAL_UTC_NOT_VERIFIED":
        raise ValueError("R60 clock may not be verified")
    if baseline.get("inference", {}).get("historical_mcmc") != "NOT_RUN":
        raise ValueError("historical posterior must remain NOT_RUN")
    if baseline["inference"].get("active_constraint_528") is not False:
        raise ValueError("528 must remain unconstrained")
    if ssr.get("id") != SSR_ID or ssr.get("source", {}).get("pdf_sha256") != SOURCE_SHA:
        raise ValueError("different primary facsimile")
    source = ssr["source"]
    if source.get("individual_instrumental_observation") is not False:
        raise ValueError("printed catalogue is not an instrument")
    row, crosswalk = ssr["original_row"], ssr["identity"]
    if (row.get("decay_printed") != "29-30 OCT 63"
            or row.get("printed_norad_id") is not None
            or row.get("terminal_utc") is not None
            or row.get("utc_interval") is not None
            or row.get("sensor") is not None
            or row.get("sigma_seconds") is not None
            or row.get("interpretation") != "PUBLISHED_CALENDAR_RANGE_NOT_UTC_EVENT"):
        raise ValueError("printed interval is not timestamp or sensor")
    if (crosswalk.get("secondary_norad_id") != 308
            or crosswalk.get("nasa_explicitly_prints_308") is not False
            or crosswalk.get("identity_status") != "SECONDARY_CROSSWALK_PENDING_PRIMARY_NORAD_ID"):
        raise ValueError("308 crosswalk must remain secondary")
    start, end = _civil_day(row["calendar_range_start"]), _civil_day(row["calendar_range_end"])
    if start.isoformat() != "1963-10-29" or end.isoformat() != "1963-10-30":
        raise ValueError("range no longer matches facsimile")
    if baseline["cases"]["308"]["secondary_terminal_day"] != end.isoformat():
        raise ValueError("original R60 anchor drift")
    if baseline["cases"]["308"]["terminal_holdout_ready"] is not False:
        raise ValueError("secondary day incorrectly promoted")
    return (end - start).days


def _expand_origin(record: dict, extra_earlier_days: int) -> dict:
    """[L,U) for 30 Oct becomes [max(0,L-v*days),U) for 29–30 Oct."""
    if record.get("status") != "COUNTERFACTUAL_INTERVAL_ONLY":
        return dict(record)
    bounds = record.get("required_H_km_UTC_DAY_COUNTERFACTUAL")
    v = record.get("decay_magnitude_km_day_LOCAL_PROXY")
    if (not isinstance(bounds, list) or len(bounds) != 2
            or not all(type(x) in (int, float) and math.isfinite(x) for x in (*bounds, v))
            or bounds[0] < 0 or not bounds[0] < bounds[1] or v <= 0):
        raise ValueError("invalid proxy interval")
    # With origins before 29 Oct, one calendar day is exactly v km in this
    # *local* proxy; prevent silently applying this to truncated day windows.
    if not math.isclose(bounds[1] - bounds[0], v, rel_tol=1e-8, abs_tol=1e-7):
        raise ValueError("origin too close to day boundary or bad window")
    copy = dict(record)
    copy["required_H_km_UTC_DAY_COUNTERFACTUAL"] = [
        max(0.0, bounds[0] - extra_earlier_days * v), bounds[1]]
    return copy


def _independent_offset_stress(records: list[dict], radius_days: float = 1) -> dict:
    """Exact union-of-window bounds for independent hypothetical shifts."""
    if not records or any(x.get("status") != "COUNTERFACTUAL_INTERVAL_ONLY" for x in records):
        return {"status": "NOT_ESTIMABLE_ALL_CUTOFFS", "intersection_H_km": None}
    limits = []
    for r in records:
        lo, hi = r["required_H_km_UTC_DAY_COUNTERFACTUAL"]
        v = r["decay_magnitude_km_day_LOCAL_PROXY"]
        limits.append((max(0.0, lo - v * radius_days), hi + v * radius_days))
    lo, hi = max(x[0] for x in limits), min(x[1] for x in limits)
    return {"status": ("INCONCLUSIVE_UNDER_INDEPENDENT_SHIFTS" if lo < hi
                       else "INCOMPATIBLE_UNDER_INDEPENDENT_SHIFTS"),
            "intersection_H_km": [lo, hi] if lo < hi else None,
            "separation_km": max(0.0, lo - hi),
            "bound_days_each_origin": radius_days,
            "same_offset_not_required": True}


def report(baseline: dict, ssr: dict) -> dict:
    extra_earlier = _validate_source(ssr, baseline)
    result = {}
    for method in ("last_two", "median_three"):
        source = baseline["cases"]["308"]["methods"][method]
        records = source["origins"]
        if source["distinct_catalogue_origins"] != len(records):
            raise ValueError("duplicated origin masquerading as independent")
        widened = [_expand_origin(x, extra_earlier) for x in records]
        result[method] = {
            "distinct_origins": len(records),
            "r60_secondary_day_common_clock_status": source["common_clock_24h"]["status"],
            "ssr_two_day_common_clock_24h": common_h_under_day_shift(widened, -24, 24),
            "ssr_two_day_independent_shift_1d": _independent_offset_stress(widened),
            "original_origin_utc": [x["origin_utc"] for x in records],
            "new_interval_H_km_conditional": [
                x.get("required_H_km_UTC_DAY_COUNTERFACTUAL") for x in widened],
        }
    return {
        "schema": SCHEMA,
        "evidence_id": SSR_ID,
        "pdf_sha256": SOURCE_SHA,
        "secondary_crosswalk_norad": 308,
        "printed_calendar_days_inclusive": ["1963-10-29", "1963-10-30"],
        "assumptions": {
            "original_cutoffs_and_catalogue_origins_frozen": True,
            "civil_days_as_UTC_is_counterfactual": True,
            "actual_UTC_interval_known": False,
            "common_H_is_unvalidated_proxy": True,
            "selection_post_inspection": True,
            "new_sensor_or_terminal_observation": False,
        },
        "methods": result,
        "inference": {
            "calibrated_terminal_holdouts": 0,
            "historical_mcmc": "NOT_RUN",
            "active_constraint_528": False,
            "sigma_terminal_hours": None,
            "mass_528_posterior": None,
            "impact_probability": None,
            "conde_geography": None,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--r60", required=True, type=Path)
    p.add_argument("--ssr", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    payload = report(json.loads(args.r60.read_text(encoding="utf-8")),
                     json.loads(args.ssr.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True,
                                      allow_nan=False) + "\n", encoding="utf-8")
    for method, value in payload["methods"].items():
        print(method, value["ssr_two_day_common_clock_24h"]["status"],
              value["ssr_two_day_independent_shift_1d"]["status"])
    print("R61 conditional calendar sensitivity; MCMC NOT_RUN; Conde unchanged")


if __name__ == "__main__":
    main()
