#!/usr/bin/env python3
"""Post-hoc UTC calendar-block falsification, NOT an orbit or probability model."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from texugo_holdout_529 import CUTOFFS, EXPECTED_URL, EXPECTED_SHA256, Observation, load_audited, evaluate, utc
from texugo_nested_529 import evaluate_nested
from texugo_influence_529 import deltas, direction

ANCHOR = datetime(1963, 1, 1, tzinfo=timezone.utc)
WIDTHS = (14, 28)


def prior_blocks(rows: list[Observation], cutoff: datetime, width: int):
    if width not in WIDTHS:
        raise ValueError("only predeclared 14/28 day widths")
    groups = {}
    for observation in rows:
        if observation.epoch <= cutoff:
            index = (observation.epoch - ANCHOR).days // width
            groups.setdefault(index, []).append(observation)
    return [(ANCHOR + timedelta(days=k * width), groups[k]) for k in sorted(groups)]


def evaluate_blocks(rows: list[Observation], day: str, width: int) -> dict:
    cutoff = utc(day + "T23:59:59Z")
    original_nested = evaluate_nested(rows, day)
    original_control = evaluate(rows, day)
    out = {"cutoff_utc_end_of_day": day, "block_days": width, "status": "NOT_RUN",
           "kind": "POST_HOC_JOINT_UTC_TRAINING_BLOCK_DELETION",
           "source_independence": "ONE secondary catalog lineage"}
    if original_nested["status"] != "EVALUATED_RETROSPECTIVE" or original_control["status"] == "NOT_RUN":
        out["reason"] = "reference nested/control fit NOT_RUN"
        return out
    reference = deltas(original_control)
    chosen = original_nested["selected_model_without_outer_holdout"]
    out["reference"] = {"selected_model_without_outer_holdout": chosen,
                        "selected_minus_quadratic_rmse_rev_day": original_nested["selected_minus_quadratic_rmse_rev_day"],
                        **reference}
    trials = []
    for start, removed in prior_blocks(rows, cutoff, width):
        removed_keys = {(o.sat, o.epoch) for o in removed}
        subset = [o for o in rows if (o.sat, o.epoch) not in removed_keys]
        nested = evaluate_nested(subset, day)
        control = evaluate(subset, day)
        trial = {"start_utc_inclusive": start.isoformat(),
                 "end_utc_exclusive": (start + timedelta(days=width)).isoformat(),
                 "removed_prior_total": len(removed),
                 "removed_prior_by_sat": {str(s): sum(o.sat == s for o in removed) for s in (527, 528, 529)},
                 "removed_keys": [f"{o.sat}:{o.epoch.isoformat()}" for o in sorted(removed, key=lambda o: (o.sat, o.epoch))],
                 "status": "NOT_RUN"}
        if nested["status"] == "EVALUATED_RETROSPECTIVE" and control["status"] != "NOT_RUN":
            trial.update({"status": "EVALUATED_RETROSPECTIVE",
                          "selected_model_without_outer_holdout": nested["selected_model_without_outer_holdout"],
                          "selected_minus_quadratic_rmse_rev_day": nested["selected_minus_quadratic_rmse_rev_day"],
                          **deltas(control)})
        else:
            trial["reason"] = nested.get("reason") or control.get("reason") or "insufficient history"
        trials.append(trial)
    passed = [t for t in trials if t["status"] == "EVALUATED_RETROSPECTIVE"]
    out.update({"status": "EVALUATED_POST_HOC" if passed else "NOT_RUN",
                "reason": None if passed else "no evaluable block deletion",
                "blocks_total": len(trials), "blocks_evaluable": len(passed),
                "blocks_not_run": len(trials) - len(passed),
                "multi_epoch_blocks": sum(t["removed_prior_total"] > 1 for t in trials),
                "model_selection_changed": sum(t["selected_model_without_outer_holdout"] != chosen for t in passed),
                "joint_sign_changed": sum(direction(t["joint_minus_quadratic_rev_day"]) !=
                                          direction(reference["joint_minus_quadratic_rev_day"]) for t in passed),
                "donor528_sign_changed": sum(direction(t["donor528_minus_quadratic_rev_day"]) !=
                                             direction(reference["donor528_minus_quadratic_rev_day"]) for t in passed),
                "joint_delta_range": [min(t["joint_minus_quadratic_rev_day"] for t in passed),
                                      max(t["joint_minus_quadratic_rev_day"] for t in passed)] if passed else None,
                "donor528_delta_range": [min(t["donor528_minus_quadratic_rev_day"] for t in passed),
                                         max(t["donor528_minus_quadratic_rev_day"] for t in passed)] if passed else None,
                "trials": trials,
                "interpretation": "POST_HOC correlated calendar-block control; counts NOT probabilities/replicates"})
    return out



def translation_placebo(rows: list[Observation], day: str, lag_days: int = 28) -> dict:
    """Synthetic donor-clock perturbation: tests a missing synchrony feature.

    Only the already-eligible pre-cutoff 527/528 epochs are translated backwards.
    Target 529 and every mean-motion value remain unchanged. Donor quadratic
    curvature must be invariant; this is NOT a clock correction or orbit model.
    """
    cutoff = utc(day + "T23:59:59Z")
    reference = evaluate(rows, day)
    result = {"cutoff_utc_end_of_day": day, "lag_days": lag_days,
              "kind": "SYNTHETIC_DONOR_EPOCH_TRANSLATION_NEGATIVE_CONTROL",
              "status": "NOT_RUN", "is_historical_observation": False}
    if reference["status"] == "NOT_RUN":
        result["reason"] = reference.get("reason", "baseline NOT_RUN")
        return result
    altered = [Observation(o.sat, o.epoch - timedelta(days=lag_days), o.mean_motion)
               if o.sat in (527, 528) and o.epoch <= cutoff else o
               for o in rows]
    shifted = evaluate(altered, day)
    if shifted["status"] == "NOT_RUN":
        result["reason"] = shifted.get("reason", "synthetic translation NOT_RUN")
        return result
    names = ("quadratic_529_only", "shared_curvature_527_528_to_529",
             "transfer_527_only", "transfer_528_only")
    changes = {name: shifted["holdout_rmse_rev_day"][name] -
                reference["holdout_rmse_rev_day"][name] for name in names}
    curvature_changes = {sat: shifted["source_curvatures"][sat] -
                         reference["source_curvatures"][sat] for sat in ("527", "528")}
    maximum = max(abs(v) for v in (*changes.values(), *curvature_changes.values()))
    result.update({"status": "EVALUATED_SYNTHETIC_CONTROL",
                   "donor_epochs_shifted": sum(o.sat in (527, 528) and o.epoch <= cutoff for o in rows),
                   "model_rmse_change_rev_day": changes,
                   "curvature_changes": curvature_changes,
                   "max_abs_numeric_change": maximum,
                   "invariant_within_1e_8": maximum <= 1e-8,
                   "interpretation": "Epoch-invariant donor curvature cannot establish synchronized observation, dynamic coupling or triangulation; numerical deviations are not physical evidence"})
    return result


def run(rows: list[Observation]) -> dict:
    return {"status": "SECONDARY_MIRROR_POST_HOC_BLOCK_CONTROL_NOT_ORBITAL_VALIDATION",
            "source_url": EXPECTED_URL, "source_sha256": EXPECTED_SHA256,
            "no_probability": True, "no_geolocation": True,
            "block_anchor": ANCHOR.isoformat(), "block_widths_days": list(WIDTHS),
            "results": [evaluate_blocks(rows, day, width) for day in CUTOFFS for width in WIDTHS],
            "translation_placebos": [translation_placebo(rows, day) for day in CUTOFFS]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("csv", "parquet", "audit", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = run(load_audited(args.csv, args.audit, args.parquet))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"sha256": EXPECTED_SHA256,
                      "summaries": [{k: v for k, v in res.items() if k != "trials"}
                                    for res in report["results"]],
                      "translation_placebos": report["translation_placebos"]}, ensure_ascii=False))
    if all(res["status"] == "NOT_RUN" for res in report["results"]):
        raise SystemExit("All block controls NOT_RUN; see artifact")


if __name__ == "__main__":
    main()
