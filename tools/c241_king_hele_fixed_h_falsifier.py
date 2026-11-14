#!/usr/bin/env python3
"""Test fixed effective scale height across frozen historical cutoffs.

This is a *conditional falsifier* of a local linearized King-Hele proxy.
Neither historical H nor the timezone/semantics of NASA's day is measured.
No likelihood, calibrated terminal error, or geographic inference is produced.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import json
import math
from pathlib import Path

from c241_637_regime_holdout import SOURCE_SHA256, SOURCE_URL, extract_pinned
from c241_king_hele_day_holdout import (
    CUTOFFS_637, CUTOFF_528, NASA_DAY_637, NASA_DAY_528,
    rate_last_two, rate_median_three, secular_dadt_km_day, strict_training,
)

H_STRESS_KM = (40.0, 50.0)
VARIANTS = ("last_two", "median_three")


def civil_day_utc_counterfactual(label: str) -> tuple[datetime, datetime]:
    """Return [start,end); no assertion NASA actually meant UTC."""
    if len(label) != 10 or label[4] != "-" or label[7] != "-":
        raise ValueError("day label must be YYYY-MM-DD, with no hour or timezone")
    try:
        day = date.fromisoformat(label)
    except ValueError as err:
        raise ValueError("invalid civil-day label") from err
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def required_h_for_one_origin(rows: list[dict], cutoff: str, label: str,
                              variant: str) -> dict:
    if variant not in VARIANTS:
        raise ValueError("unsupported slope definition")
    cutoff_dt = datetime.fromisoformat(cutoff)
    selected = strict_training(rows, cutoff_dt)
    slope_fn = rate_last_two if variant == "last_two" else rate_median_three
    slope = slope_fn(selected)
    record = {
        "cutoff_exclusive_utc": cutoff,
        "variant": variant,
        "epochs_before_cutoff": len(selected),
        "last_source_row": selected[-1]["source_row"] if selected else None,
        "origin_utc": selected[-1]["epoch"].isoformat() if selected else None,
        "status": "NOT_ESTIMABLE",
        "required_H_km_UTC_DAY_COUNTERFACTUAL": None,
    }
    if slope is None:
        record["status"] = "NOT_ESTIMABLE_FEWER_PRIOR_EPOCHS"
        return record
    if not math.isfinite(slope) or slope <= 0:
        record["status"] = "NOT_ESTIMABLE_NON_DECAYING_SECANT"
        return record
    decay_km_day = -secular_dadt_km_day(selected[-1]["mean_motion"], slope)
    if not math.isfinite(decay_km_day) or decay_km_day <= 0:
        record["status"] = "NOT_ESTIMABLE_BAD_DYNAMICS"
        return record
    start, end = civil_day_utc_counterfactual(label)
    origin = selected[-1]["epoch"]
    if origin >= end:
        record["status"] = "NOT_ESTIMABLE_ORIGIN_NOT_BEFORE_DAY_END"
        return record
    day_gap_lower = (start - origin).total_seconds() / 86400
    day_gap_upper = (end - origin).total_seconds() / 86400
    lower = max(0.0, decay_km_day * day_gap_lower)
    upper = decay_km_day * day_gap_upper
    if upper <= lower:
        record["status"] = "NOT_ESTIMABLE_NO_POSITIVE_H"
        return record
    record["status"] = "COUNTERFACTUAL_INTERVAL_ONLY"
    record["positive_mean_motion_secant_rev_day2"] = slope
    record["decay_magnitude_km_day_LOCAL_PROXY"] = decay_km_day
    record["required_H_km_UTC_DAY_COUNTERFACTUAL"] = [lower, upper]
    return record


def intersection(records: list[dict], stress_range: tuple[float, float]) -> dict:
    """Do not discard unestimable origins to manufacture apparent agreement."""
    lo, hi = stress_range
    if not (0 < lo < hi and math.isfinite(lo) and math.isfinite(hi)):
        raise ValueError("invalid prespecified positive H stress interval")
    if not records:
        raise ValueError("no frozen cutoffs")
    ok = [r for r in records if r["status"] == "COUNTERFACTUAL_INTERVAL_ONLY"]
    result = {
        "cutoffs_expected": len(records),
        "cutoffs_estimable": len(ok),
        "intersection_all_cutoffs_km": None,
        "intersection_with_H_stress_km": None,
        "status": "NOT_ESTIMABLE_ALL_CUTOFFS",
    }
    if len(ok) != len(records):
        return result
    left = max(r["required_H_km_UTC_DAY_COUNTERFACTUAL"][0] for r in ok)
    right = min(r["required_H_km_UTC_DAY_COUNTERFACTUAL"][1] for r in ok)
    if not left < right:
        result["status"] = "EMPTY_INTERSECTION_CONDITIONAL_FIXED_H"
        return result
    result["intersection_all_cutoffs_km"] = [left, right]
    stress_left, stress_right = max(left, lo), min(right, hi)
    if stress_left < stress_right:
        result["intersection_with_H_stress_km"] = [stress_left, stress_right]
        result["status"] = "CONSISTENT_H_ONLY_IN_ASSUMED_UTC_DAY_MODEL"
    else:
        result["status"] = "NO_H_IN_STRESS_RANGE_CONDITIONAL_FIXED_H"
    return result



def common_h_under_day_shift(records: list[dict], shift_min_hours: float,
                             shift_max_hours: float) -> dict:
    """Solve H>0 and all half-open date windows under ONE common clock shift.

    A shift is a stress variable (UTC start relative to printed civil midnight),
    not an estimated historical timezone. Each interval moves by v*shift/24.
    All inequalities are strict because terminal day windows are half-open.
    The pairwise linear inequalities are solved algebraically, not by grid scan.
    """
    if not (math.isfinite(shift_min_hours) and math.isfinite(shift_max_hours)
            and shift_min_hours <= shift_max_hours):
        raise ValueError("invalid finite, ordered clock-shift stress bounds")
    result = {
        "assumed_common_utc_start_shift_hours": [shift_min_hours, shift_max_hours],
        "status": "NOT_ESTIMABLE_ALL_CUTOFFS",
        "feasible_shift_hours": None,
        "feasible_shift_endpoints_inclusive": None,
        "incompatible_pair_witness": None,
        "calibrated_timezone": False,
    }
    if not records or any(r["status"] != "COUNTERFACTUAL_INTERVAL_ONLY"
                          for r in records):
        return result
    intervals = []
    for record in records:
        limits = record["required_H_km_UTC_DAY_COUNTERFACTUAL"]
        v = record["decay_magnitude_km_day_LOCAL_PROXY"]
        if (limits is None or len(limits) != 2
                or not all(math.isfinite(x) for x in (*limits, v))
                or not (0 <= limits[0] < limits[1] and v > 0)):
            raise ValueError("invalid positive-decay source record")
        intervals.append((limits[0], limits[1], v))

    # A + B*delta > 0, with delta measured in hours, for every constraint:
    # (1) each upper bound must be positive, (2) every lower_i < upper_j.
    # The latter, together with (1), is equivalent to a common positive H.
    constraints = [(hi, v / 24, None) for lo, hi, v in intervals]
    for i, (lo_i, _, v_i) in enumerate(intervals):
        for j, (_, hi_j, v_j) in enumerate(intervals):
            constraints.append((hi_j - lo_i, (v_j - v_i) / 24, (i, j)))

    lower, upper = shift_min_hours, shift_max_hours
    lower_inclusive, upper_inclusive = True, True
    impossible = False
    for intercept, slope, _ in constraints:
        if slope == 0:
            if intercept <= 0:
                impossible = True
                break
            continue
        boundary = -intercept / slope
        if slope > 0:
            if boundary > lower:
                lower, lower_inclusive = boundary, False
            elif boundary == lower:
                lower_inclusive = False
        else:
            if boundary < upper:
                upper, upper_inclusive = boundary, False
            elif boundary == upper:
                upper_inclusive = False
    feasible = not impossible and (
        lower < upper or
        (lower == upper and lower_inclusive and upper_inclusive))
    if feasible:
        result["status"] = "FEASIBLE_ONLY_IN_ASSUMED_SHIFT_MODEL"
        result["feasible_shift_hours"] = [lower, upper]
        result["feasible_shift_endpoints_inclusive"] = [
            lower_inclusive, upper_inclusive]
        return result

    result["status"] = "NO_COMMON_H_FOR_ANY_SHIFT_IN_STRESS_WINDOW"
    # Strongest simple negative certificate, when available: a pair of
    # cutoffs whose two intervals never overlap anywhere in the whole window.
    witnesses = []
    for intercept, slope, pair in constraints:
        if pair is None:
            continue
        maximum_slack_km = max(intercept + slope * shift_min_hours,
                               intercept + slope * shift_max_hours)
        if maximum_slack_km <= 0:
            witnesses.append((maximum_slack_km, pair))
    if witnesses:
        slack, (i, j) = min(witnesses, key=lambda item: (item[0], item[1]))
        result["incompatible_pair_witness"] = {
            "lower_cutoff_index": i,
            "upper_cutoff_index": j,
            "max_upper_minus_lower_km_over_shift_range": slack,
            "conclusion": "upper_j <= lower_i for every shift in bounds",
        }
    return result


def report(groups: dict[int, list[dict]]) -> dict:
    if 528 not in groups or 637 not in groups:
        raise ValueError("required objects 528 and 637 missing")
    objects = {}
    for norad, cutoffs, label in (
        (637, CUTOFFS_637, NASA_DAY_637),
        (528, (CUTOFF_528,), NASA_DAY_528),
    ):
        variants = {}
        for variant in VARIANTS:
            records = [required_h_for_one_origin(groups[norad], cutoff, label, variant)
                       for cutoff in cutoffs]
            variants[variant] = {
                "origins": records, "fixed_H_test": intersection(records, H_STRESS_KM),
                "day_boundary_shift_stress": {
                    "plus_minus_14h": common_h_under_day_shift(records, -14, 14),
                    "plus_minus_24h": common_h_under_day_shift(records, -24, 24),
                }
            }
        objects[str(norad)] = {
            "NASA_calendar_day_timezone_UNVERIFIED": label,
            "source_cutoffs_frozen": list(cutoffs), "variants": variants,
        }
    return {
        "schema": "c241-fixed-h-day-window-conditional-falsifier/v1",
        "source": {
            "url": SOURCE_URL, "sha256_verified_by_reader": SOURCE_SHA256,
            "lineage": "ONE_SECONDARY_CATALOGUE", "Nasa_day_is_timed": False,
        },
        "assumptions": {
            "NASA_day_interpreted_as_UTC_FOR_COUNTERFACTUAL_ONLY": True,
            "all_origins_share_one_H_WITHIN_EACH_OBJECT_FOR_TEST": True,
            "source_labels_preinspected": True,
            "H_stress_range_km_not_calibrated": list(H_STRESS_KM),
            "model": "constant local semimajor-axis decay, positive dn/dt",
            "label_is_not_independent_terminal_instant": True,
            "different_objects_not_forced_to_share_H": True,
        },
        "objects": objects,
        "inference": {
            "active_constraint": False, "historical_mcmc": "NOT_RUN",
            "terminal_time_sigma_hours": None, "impact_geography": None,
            "H_empirically_calibrated": False, "physical_model_falsified": False,
            "reason": "only conditional compatibility of frozen approximate proxy and UTC date semantics",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = report(extract_pinned(args.parquet))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
                           + "\n", encoding="utf-8")
    for norad, obj in payload["objects"].items():
        for variant, values in obj["variants"].items():
            r = values["fixed_H_test"]
            print(norad, variant, r["cutoffs_estimable"], "/",
                  r["cutoffs_expected"], r["status"])
    print("Historical MCMC NOT_RUN; no sigma, mass or impact posterior")


if __name__ == "__main__":
    main()
