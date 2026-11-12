#!/usr/bin/env python3
"""Leave-one-prior-epoch-out falsification of the post-hoc 529 selector.

This is a sensitivity analysis on ONE secondary catalog lineage. Each deletion
re-runs the entire inner chronological model-selection procedure. It is not a
bootstrap, an uncertainty distribution, a physical orbit, or a forecast.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from texugo_holdout_529 import (
    CUTOFFS, EXPECTED_SHA256, EXPECTED_URL, SATELLITES,
    Observation, evaluate, load_audited, utc,
)
from texugo_nested_529 import evaluate_nested

EPS = 1e-10


def direction(delta: float) -> str:
    """Positive means the donor model is worse than quadratic 529."""
    return "WORSE" if delta > EPS else "BETTER" if delta < -EPS else "TIE"


def deltas(control: dict) -> dict[str, float]:
    errors = control["holdout_rmse_rev_day"]
    baseline = errors["quadratic_529_only"]
    return {
        "joint_minus_quadratic_rev_day": errors["shared_curvature_527_528_to_529"] - baseline,
        "donor528_minus_quadratic_rev_day": errors["transfer_528_only"] - baseline,
    }


def evaluate_influence(rows: list[Observation], cutoff_day: str) -> dict:
    cutoff = utc(cutoff_day + "T23:59:59Z")  # a cutoff, NOT an observed event time
    original_nested = evaluate_nested(rows, cutoff_day)
    original_control = evaluate(rows, cutoff_day)
    result = {
        "cutoff_utc_end_of_day": cutoff_day,
        "status": "NOT_RUN",
        "kind": "POST_HOC_FULL_PIPELINE_LEAVE_ONE_PRIOR_EPOCH_OUT",
        "source_independence": "ONE secondary catalog lineage, NO independent sensors",
    }
    if original_nested["status"] != "EVALUATED_RETROSPECTIVE" or original_control["status"] == "NOT_RUN":
        result["reason"] = "baseline nested or donor comparison NOT_RUN; insufficient epochs"
        return result
    initial = deltas(original_control)
    chosen = original_nested["selected_model_without_outer_holdout"]
    result["reference"] = {
        "selected_model_without_outer_holdout": chosen,
        "selected_minus_quadratic_rmse_rev_day": original_nested["selected_minus_quadratic_rmse_rev_day"],
        **initial,
    }
    rows_by_sat = {
        sat: sorted((o for o in rows if o.sat == sat and o.epoch <= cutoff),
                    key=lambda o: o.epoch)
        for sat in SATELLITES
    }
    trials = []
    counts = {}
    for sat in SATELLITES:
        successful = []
        for removed in rows_by_sat[sat]:
            # Remove only a training record; NEVER change the held-out future.
            subset = [o for o in rows if o != removed]
            nested = evaluate_nested(subset, cutoff_day)
            control = evaluate(subset, cutoff_day)
            trial = {
                "removed_sat": sat,
                "removed_epoch_utc": removed.epoch.isoformat(),
                "status": "NOT_RUN",
            }
            if nested["status"] != "EVALUATED_RETROSPECTIVE" or control["status"] == "NOT_RUN":
                trial["reason"] = nested.get("reason") or control.get("reason") or "insufficient fit"
            else:
                trial.update({
                    "status": "EVALUATED_RETROSPECTIVE",
                    "selected_model_without_outer_holdout": nested["selected_model_without_outer_holdout"],
                    "selected_minus_quadratic_rmse_rev_day": nested["selected_minus_quadratic_rmse_rev_day"],
                    **deltas(control),
                })
                successful.append(trial)
            trials.append(trial)
        counts[str(sat)] = {
            "prior_epochs": len(rows_by_sat[sat]),
            "evaluable_deletions": len(successful),
            "not_run_deletions": len(rows_by_sat[sat]) - len(successful),
            "selection_changed": sum(t["selected_model_without_outer_holdout"] != chosen
                                     for t in successful),
            "joint_advantage_direction_changed": sum(
                direction(t["joint_minus_quadratic_rev_day"]) !=
                direction(initial["joint_minus_quadratic_rev_day"]) for t in successful),
            "donor528_advantage_direction_changed": sum(
                direction(t["donor528_minus_quadratic_rev_day"]) !=
                direction(initial["donor528_minus_quadratic_rev_day"]) for t in successful),
            "range_selected_minus_quadratic_rev_day": (
                [min(t["selected_minus_quadratic_rmse_rev_day"] for t in successful),
                 max(t["selected_minus_quadratic_rmse_rev_day"] for t in successful)]
                if successful else None),
            "range_528_minus_quadratic_rev_day": (
                [min(t["donor528_minus_quadratic_rev_day"] for t in successful),
                 max(t["donor528_minus_quadratic_rev_day"] for t in successful)]
                if successful else None),
        }
    result.update({"status": "EVALUATED_POST_HOC", "by_deleted_sat": counts,
                   "trials": trials,
                   "interpretation": "descriptive single-epoch influence; counts are NOT probabilities, trials and outer windows are dependent"})
    return result


def run(rows: list[Observation]) -> dict:
    return {
        "status": "SECONDARY_MIRROR_POST_HOC_INFLUENCE_NOT_ORBITAL_VALIDATION",
        "source_url": EXPECTED_URL, "source_sha256": EXPECTED_SHA256,
        "no_probability": True, "no_geolocation": True,
        "results": [evaluate_influence(rows, cutoff) for cutoff in CUTOFFS],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--parquet", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = run(load_audited(args.csv, args.audit, args.parquet))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    # Keep a short, legible CI log while archiving EVERY deletion in the JSON.
    print(json.dumps({"source_sha256": EXPECTED_SHA256,
                      "summaries": [{"cutoff": r["cutoff_utc_end_of_day"], "status": r["status"],
                                     "reference": r.get("reference"), "by_deleted_sat": r.get("by_deleted_sat"),
                                     "reason": r.get("reason")} for r in report["results"]]}, ensure_ascii=False))
    if all(r["status"] == "NOT_RUN" for r in report["results"]):
        raise SystemExit("No evaluable influence test; see archived JSON")


if __name__ == "__main__":
    main()
