#!/usr/bin/env python3
"""POST_HOC rotate holdout target 527/528/529; same secondary catalog, NOT orbit fit.

Tests whether a purportedly generic shared-curvature advantage depends on
cherry-picking 529 as target. This is not triangulation, dynamics or a prior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from texugo_holdout_529 import (
    CUTOFFS, EXPECTED_SHA256, EXPECTED_URL, SATELLITES, Observation,
    evaluate, fixed_curvature_fit, load_audited, polynomial_fit, project,
    rmse, utc, x_at,
)


def evaluate_target(rows: list[Observation], day: str, target: int) -> dict:
    if target not in SATELLITES:
        raise ValueError("target must be one of 527/528/529")
    cutoff = utc(day + "T23:59:59Z")
    donors = tuple(sat for sat in SATELLITES if sat != target)
    training = {
        sat: [(x_at(o.epoch, cutoff), o.mean_motion)
              for o in rows if o.sat == sat and o.epoch <= cutoff]
        for sat in SATELLITES
    }
    future = sorted((o for o in rows if o.sat == target and o.epoch > cutoff),
                    key=lambda o: o.epoch)
    result = {
        "cutoff_utc_end_of_day": day,
        "target_norad_id": target,
        "donor_norad_ids": list(donors),
        "prior_counts": {str(s): len(training[s]) for s in SATELLITES},
        "future_target_count": len(future),
        "status": "NOT_RUN",
        "source_independence": "ONE SECONDARY CATALOG, NOT INDEPENDENT SENSORS",
    }
    if any(len(training[s]) < 3 for s in SATELLITES) or not future:
        result["reason"] = "fewer than 3 prior epochs per object or no future target"
        return result
    try:
        baseline = polynomial_fit(training[target], 2)
        donor_curvatures = {s: polynomial_fit(training[s], 2)[2] for s in donors}
        mean_curvature = sum(donor_curvatures.values()) / len(donors)
        fits = {
            "quadratic_target_only": baseline,
            "equal_other_two_curvature": fixed_curvature_fit(training[target], mean_curvature),
            "linear_target_only": polynomial_fit(training[target], 1),
        }
        for sat in donors:
            fits[f"donor_{sat}_only"] = fixed_curvature_fit(training[target], donor_curvatures[sat])
    except ValueError as exc:
        result["reason"] = str(exc)
        return result
    xs = [x_at(o.epoch, cutoff) for o in future]
    truth = [o.mean_motion for o in future]
    errors = {name: rmse(truth, [project(coef, x) for x in xs])
              for name, coef in fits.items()}
    delta = errors["equal_other_two_curvature"] - errors["quadratic_target_only"]
    result.update({
        "status": "EVALUATED_POST_HOC",
        "outer_rmse_rev_day": errors,
        "joint_minus_quadratic_rmse_rev_day": delta,
        "joint_direction": ("JOINT_BETTER" if delta < -1e-10 else
                            "BASELINE_BETTER" if delta > 1e-10 else "TIE"),
        "donor_curvatures": {str(s): donor_curvatures[s] for s in donors},
        "fit_coefficients": {name: list(coef) for name, coef in fits.items()},
        "future_horizon_days": [(o.epoch - cutoff).total_seconds() / 86400 for o in future],
        "interpretation": "POST_HOC target rotation, repeated epochs and overlapping windows; NOT independent physical validation",
    })
    return result


def run(rows: list[Observation]) -> dict:
    results = [evaluate_target(rows, cutoff, target)
               for cutoff in CUTOFFS for target in SATELLITES]
    # Independently recompute the existing 529 benchmark. Disagreement is
    # a regression, never silently promoted to a new empirical finding.
    for day in CUTOFFS:
        rotated = next(r for r in results
                       if r["target_norad_id"] == 529 and r["cutoff_utc_end_of_day"] == day)
        original = evaluate(rows, day)
        if (rotated["status"] == "NOT_RUN") != (original["status"] == "NOT_RUN"):
            raise ValueError("rotated 529 evaluability disagrees with original baseline")
        if rotated["status"] == "NOT_RUN":
            continue
        before = original["holdout_rmse_rev_day"]
        after = rotated["outer_rmse_rev_day"]
        pairs = (
            ("quadratic_529_only", "quadratic_target_only"),
            ("shared_curvature_527_528_to_529", "equal_other_two_curvature"),
            ("transfer_527_only", "donor_527_only"),
            ("transfer_528_only", "donor_528_only"),
            ("linear_529_only", "linear_target_only"),
        )
        if any(abs(before[a] - after[b]) > 1e-8 for a, b in pairs):
            raise ValueError("rotated 529 scores disagree with original benchmark")
    return {
        "status": "SECONDARY_MIRROR_POST_HOC_TARGET_ROTATION_NOT_ORBITAL_VALIDATION",
        "source_url": EXPECTED_URL,
        "source_sha256": EXPECTED_SHA256,
        "no_probability": True,
        "no_geolocation": True,
        "no_new_primary_evidence": True,
        "targets": list(SATELLITES),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("csv", "parquet", "audit", "output"):
        parser.add_argument("--" + field, type=Path, required=True)
    args = parser.parse_args()
    report = run(load_audited(args.csv, args.audit, args.parquet))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_sha256": EXPECTED_SHA256,
        "summaries": [{k: v for k, v in res.items() if k not in ("fit_coefficients", "future_horizon_days")}
                      for res in report["results"]],
    }, ensure_ascii=False))
    if all(r["status"] == "NOT_RUN" for r in report["results"]):
        raise SystemExit("All rotated targets NOT_RUN; see artifact")


if __name__ == "__main__":
    main()
