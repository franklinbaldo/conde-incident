#!/usr/bin/env python3
"""Post-hoc nested chronological selector for 529 mean motion, NOT orbit prediction.

The inner validation interval precedes each original outer cutoff; the outer
future is never used to choose a donor or a model. This retrospective analysis
does not make model choice prospective or authenticate an instrument.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from texugo_holdout_529 import (
    CUTOFFS, EXPECTED_SHA256, EXPECTED_URL, SATELLITES, Observation,
    fixed_curvature_fit, load_audited, polynomial_fit, project, rmse, utc, x_at,
)

MODELS = (
    "quadratic_529_only",
    "shared_curvature_527_528_to_529",
    "transfer_527_only",
    "transfer_528_only",
    "linear_529_only",
)


def fit_before(rows: list[Observation], boundary) -> tuple[dict[str, tuple[float, ...]], dict[str, int]]:
    """Fit exclusively at/before boundary, with a separate target intercept."""
    train = {
        sat: [(x_at(o.epoch, boundary), o.mean_motion)
              for o in rows if o.sat == sat and o.epoch <= boundary]
        for sat in SATELLITES
    }
    counts = {str(sat): len(train[sat]) for sat in SATELLITES}
    if any(counts[str(sat)] < 3 for sat in SATELLITES):
        raise ValueError("menos de três épocas de algum objeto na janela de treino")
    c527 = polynomial_fit(train[527], 2)[2]
    c528 = polynomial_fit(train[528], 2)[2]
    estimates = {
        "quadratic_529_only": polynomial_fit(train[529], 2),
        "shared_curvature_527_528_to_529": fixed_curvature_fit(train[529], (c527 + c528) / 2),
        "transfer_527_only": fixed_curvature_fit(train[529], c527),
        "transfer_528_only": fixed_curvature_fit(train[529], c528),
        "linear_529_only": polynomial_fit(train[529], 1),
    }
    return estimates, counts


def scores(estimates, target: list[Observation], origin) -> dict[str, float]:
    xs = [x_at(o.epoch, origin) for o in target]
    ys = [o.mean_motion for o in target]
    return {name: rmse(ys, [project(coeff, x) for x in xs])
            for name, coeff in estimates.items()}


def evaluate_nested(rows: list[Observation], cutoff_day: str) -> dict:
    outer = utc(cutoff_day + "T23:59:59Z")
    target_past = sorted((o for o in rows if o.sat == 529 and o.epoch <= outer),
                         key=lambda o: o.epoch)
    target_future = sorted((o for o in rows if o.sat == 529 and o.epoch > outer),
                           key=lambda o: o.epoch)
    result = {
        "cutoff_utc_end_of_day": cutoff_day,
        "target_529_before_cutoff": len(target_past),
        "target_529_outer_holdout": len(target_future),
        "status": "NOT_RUN",
    }
    if len(target_past) < 8 or not target_future:
        result["reason"] = "menos de oito épocas 529 antes do corte ou sem futuro 529"
        return result
    # An inner chronological last-quarter validation block. Fixed before scoring.
    nval = max(2, len(target_past) // 4)
    first_validation = len(target_past) - nval
    inner = target_past[first_validation - 1].epoch
    validation = target_past[first_validation:]
    if any(o.epoch <= inner or o.epoch > outer for o in validation):
        raise ValueError("janela interna inválida")
    try:
        # The inner 529 validation samples are hidden from ALL inner fits.
        # Donor data between inner and outer are likewise excluded here.
        inner_fits, inner_counts = fit_before(rows, inner)
        inner_rmse = scores(inner_fits, validation, inner)
        # Choosing by inner RMSE is permitted; outer 529 never participates.
        choice = min(MODELS, key=lambda name: inner_rmse[name])
        outer_fits, outer_counts = fit_before(rows, outer)
        outer_rmse = scores(outer_fits, target_future, outer)
    except ValueError as exc:
        result["reason"] = str(exc)
        return result
    hindsight = min(MODELS, key=lambda name: outer_rmse[name])
    result.update({
        "status": "EVALUATED_RETROSPECTIVE",
        "inner_boundary_utc": inner.isoformat(),
        "inner_train_counts": inner_counts,
        "outer_train_counts": outer_counts,
        "inner_validation_529_count": len(validation),
        "inner_validation_rmse_rev_day": inner_rmse,
        "selected_model_without_outer_holdout": choice,
        "outer_holdout_rmse_rev_day": outer_rmse,
        "selected_outer_rmse_rev_day": outer_rmse[choice],
        "selected_minus_quadratic_rmse_rev_day":
            outer_rmse[choice] - outer_rmse["quadratic_529_only"],
        "hindsight_oracle_only_not_admissible_model_selection": {
            "name": hindsight,
            "outer_rmse_rev_day": outer_rmse[hindsight],
            "selector_regret_rev_day": max(0.0, outer_rmse[choice] - outer_rmse[hindsight]),
        },
        "selection_rule": "inner 529 last quarter, chronological; deterministic first minimum tie",
        "interpretation": "POST_HOC nested retrospective control; overlap across outer cutoffs; not independent, not prospective",
    })
    return result


def run(rows: list[Observation]) -> dict:
    return {
        "status": "SECONDARY_MIRROR_POST_HOC_NOT_ORBITAL_VALIDATION",
        "source_url": EXPECTED_URL,
        "source_sha256": EXPECTED_SHA256,
        "no_probability": True,
        "no_geolocation": True,
        "source_independence": "ONE secondary catalog lineage for 527/528/529",
        "results": [evaluate_nested(rows, cutoff) for cutoff in CUTOFFS],
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
    print(json.dumps({"source_sha256": EXPECTED_SHA256, "results": report["results"]}, ensure_ascii=False))
    if all(r["status"] == "NOT_RUN" for r in report["results"]):
        raise SystemExit("No evaluable nested cutoffs: see JSON")


if __name__ == "__main__":
    main()
