#!/usr/bin/env python3
"""G71: falsify a shared H even after allowing independent date-label offsets.

The offsets are a sensitivity assumption, NOT NASA clock uncertainty.
The source, model and civil-day interpretation are inherited from G57.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from c241_637_regime_holdout import extract_pinned
from c241_king_hele_fixed_h_falsifier import report as baseline_report

STRESS_SHIFT_DAYS = 1.0


def day_shift_certificate(origins: list[dict], allowance_days: float = STRESS_SHIFT_DAYS) -> dict:
    """Each UTC day window may shift independently by +/- allowance_days.

    A one-day H interval [L,U) translates by v*delta, v=U-L km/day.
    Thus [L-v*b,U+v*b) is its union over all allowed shifts. If the
    unions have empty intersection, even independent shifts cannot
    rescue a common H. A nonempty intersection is only inconclusive.
    """
    if type(allowance_days) not in (int, float) or not math.isfinite(allowance_days) or allowance_days < 0:
        raise ValueError("finite nonnegative day-shift allowance required")
    if len(origins) < 2:
        return {"status": "NOT_ESTIMABLE_SINGLE_CUTOFF", "cutoffs": len(origins),
                "active_constraint": False}
    if any(r.get("status") != "COUNTERFACTUAL_INTERVAL_ONLY" for r in origins):
        return {"status": "NOT_ESTIMABLE_ALL_CUTOFFS", "cutoffs": len(origins),
                "active_constraint": False}
    bounds = []
    for r in origins:
        value = r.get("required_H_km_UTC_DAY_COUNTERFACTUAL")
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ValueError("H interval must have two endpoints")
        low, high = value
        if (type(low) not in (int, float) or type(high) not in (int, float)
                or not all(map(math.isfinite, (low, high)))
                or low < 0 or not low < high):
            raise ValueError("nonfinite, negative or empty half-open H interval")
        bounds.append((float(low), float(high), float(high-low)))
    expanded = [(lo - v*allowance_days, hi + v*allowance_days)
                for lo, hi, v in bounds]
    max_left = max(x[0] for x in expanded)
    min_right = min(x[1] for x in expanded)
    # Since all offsets are independent, pairwise interval separation
    # gives the exact infimum of the required max |offset| in days.
    witnesses = [((bounds[i][0]-bounds[j][1])/(bounds[i][2]+bounds[j][2]), i, j)
                 for i in range(len(bounds)) for j in range(len(bounds)) if i != j]
    radius, low_index, high_index = max(witnesses)
    return {
        "status": ("CERTIFIED_INCOMPATIBLE_WITH_INDEPENDENT_DATE_SHIFTS"
                   if max_left >= min_right else "INCONCLUSIVE_UNDER_DATE_SHIFTS"),
        "cutoffs": len(origins), "independent_offset_bound_days": float(allowance_days),
        "expanded_max_lower_H_km": max_left, "expanded_min_upper_H_km": min_right,
        "separation_after_expansion_km": max_left-min_right,
        "infimum_offset_days_before_common_H_possible": max(0.0, radius),
        "strongest_conflicting_pair_indices": [low_index, high_index],
        "half_open_upper_endpoint": True,
        "active_constraint": False,
    }


def report(groups: dict[int, list[dict]], allowance_days: float = STRESS_SHIFT_DAYS) -> dict:
    source = baseline_report(groups)
    objects = {}
    for obj_id, obj in source["objects"].items():
        objects[obj_id] = {
            "source_cutoffs_frozen": obj["source_cutoffs_frozen"],
            "variants": {
                name: day_shift_certificate(value["origins"], allowance_days)
                for name, value in obj["variants"].items()
            }
        }
    return {
        "schema": "c241-fixed-h-independent-day-shift-stress/v1",
        "source": source["source"],
        "assumptions": {
            "NASA_civil_day_timezone_verified": False,
            "offsets_independent_even_within_one_object": True,
            "offset_allowance_is_stress_not_observed_sigma": True,
            "date_labels_known_before_model_selection": True,
            "one_day_window_converts_to_H_width_km": True,
            "physical_atmosphere_falsified": False,
        },
        "objects": objects,
        "inference": {
            "active_constraint": False, "historical_mcmc": "NOT_RUN",
            "calibrated_terminal_uncertainty": None, "impact_geography": None,
            "reason": "G57 local fixed-H approximation, single secondary catalogue, conditional date interpretation",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report(extract_pinned(args.parquet))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)
                           + "\n", encoding="utf-8")
    for obj, record in result["objects"].items():
        for method, case in record["variants"].items():
            print(obj, method, case["status"],
                  case.get("infimum_offset_days_before_common_H_possible"))
    print("G71 sensitivity only; independent instrumental time NOT_RUN")


if __name__ == "__main__":
    main()
