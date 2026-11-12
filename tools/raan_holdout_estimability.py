#!/usr/bin/env python3
"""Exact *conditional* holdout estimability for the eight-column RAAN design.

No RAAN dynamics, catalog calibration, noise covariance or historical likelihood.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from raan_lineage_identifiability import OBJECTS, SPLITS, build_report, matrix_rank_exact
from raan_temporal_gauge import (
    PHASE_528_ANCHOR, RATE_528_ANCHOR, days_from_reference, model_row,
)

SCHEMA = "conde.raan-holdout-estimability/v1"
SOURCE = "research/statistics/raan_527_528_529_1963.json"
SPLIT = "research/statistics/raan_chronological_holdout_1963.json"


def estimable(training: list[tuple[Fraction, ...]],
              target: tuple[Fraction, ...]) -> bool:
    """A linear functional is estimable iff it is in the training row space."""
    if not training or len(target) != 8 or any(len(row) != 8 for row in training):
        raise ValueError("nonempty eight-column design required")
    return matrix_rank_exact(training + [target]) == matrix_rank_exact(training)


def rows_for(manifest: dict, parts: tuple[str, ...]) -> list[tuple[Fraction, ...]]:
    return [
        model_row(obj, days_from_reference(epoch))
        for part in parts for obj in OBJECTS
        for epoch in manifest["memberships"][obj][part]
    ]


def holdout_counts(manifest: dict, training_parts: tuple[str, ...],
                   test_part: str) -> dict:
    if not training_parts or any(p not in SPLITS for p in training_parts):
        raise ValueError("unknown training partition")
    if test_part not in SPLITS or test_part in training_parts:
        raise ValueError("holdout may not appear in training")
    train = rows_for(manifest, training_parts)
    rank = matrix_rank_exact(train)
    by_object = {}
    for obj in OBJECTS:
        targets = [model_row(obj, days_from_reference(x))
                   for x in manifest["memberships"][obj][test_part]]
        successes = sum(estimable(train, target) for target in targets)
        by_object[obj] = {"total": len(targets), "estimable": successes,
                          "not_estimable": len(targets) - successes}
    return {
        "training": list(training_parts), "holdout": test_part,
        "training_rows": len(train), "training_rank": rank,
        "row_space_only_no_physical_prediction": True,
        "by_object": by_object,
        "total_estimated": sum(v["estimable"] for v in by_object.values()),
        "total_holdout": sum(v["total"] for v in by_object.values()),
    }


def counterfactual_527(manifest: dict) -> dict:
    """Give a constructive witness of 527's lost rate in validation."""
    t0 = days_from_reference(manifest["memberships"]["527"]["validation"][0])
    train = rows_for(manifest, ("validation",))
    # Alter phase_527 by -t0 degrees and rate_527 by +1 degree/day.
    # This vector annihilates the whole validation block, but NOT later 527 rows.
    witness = (-t0, Fraction(0), Fraction(0), Fraction(1),
               Fraction(0), Fraction(0), Fraction(0), Fraction(0))
    if any(sum(x*y for x, y in zip(r, witness)) != 0 for r in train):
        raise AssertionError("witness must annihilate validation rows")
    targets = [model_row("527", days_from_reference(t))
               for t in manifest["memberships"]["527"]["evaluation"]]
    if any(sum(x*y for x, y in zip(r, witness)) == 0 for r in targets):
        raise AssertionError("evaluation must discriminate the witness")
    # Hypothetical one extra 527 time point; NOT from evaluation or any document.
    extra = model_row("527", t0 + Fraction(1))
    if estimable(train, extra):
        raise AssertionError("additional distinct time must add a rank")
    with_extra = train + [extra]
    with_anchors = train + [PHASE_528_ANCHOR, RATE_528_ANCHOR]
    with_both = with_extra + [PHASE_528_ANCHOR, RATE_528_ANCHOR]
    return {
        "classification": "COUNTERFACTUAL_NOT_A_HISTORICAL_OBSERVATION",
        "sole_527_validation_epoch": manifest["memberships"]["527"]["validation"][0],
        "witness_delta": {
            "phase_527_deg": f"{-t0.numerator}/{t0.denominator}",
            "rate_527_deg_per_day": "1",
            "all_other_parameters": "0",
        },
        "witness_validation_prediction_change_deg": "0",
        "evaluation_527_prediction_changes_nonzero": True,
        "validation_rank": matrix_rank_exact(train),
        "with_two_absolute_528_anchors_rank": matrix_rank_exact(with_anchors),
        "with_one_527_extra_epoch_rank": matrix_rank_exact(with_extra),
        "with_extra_and_both_528_anchors_rank": matrix_rank_exact(with_both),
        "counterfactual_extra_time": "validation_527_epoch + 1 exact day (DESIGN ONLY)",
        "minimal_additional_local_measurement": (
            "one 527 angular measurement at a second distinct UTC epoch "
            "to make its local phase/rate combination estimable, conditional on "
            "a fixed physical F_527, identical calibrated convention and model"
        ),
        "independent_angular_calibration_still_required": True,
        "error_calibration_and_global_circle_aliases_still_unresolved": True,
    }


def build(source: bytes, frozen: bytes) -> dict:
    verified = build_report(source, frozen)
    manifest = json.loads(frozen)
    if manifest["unique_total"] != 119:
        raise ValueError("unexpected historical count")
    comparisons = [
        holdout_counts(manifest, ("fit",), "validation"),
        holdout_counts(manifest, ("fit",), "evaluation"),
        holdout_counts(manifest, ("validation",), "evaluation"),
        holdout_counts(manifest, ("fit", "validation"), "evaluation"),
    ]
    if [c["training_rows"] for c in comparisons] != [61, 61, 23, 84]:
        raise AssertionError("frozen holdout split mismatch")
    if [c["training_rank"] for c in comparisons] != [6, 6, 5, 6]:
        raise AssertionError("frozen design rank mismatch")
    return {
        "schema": SCHEMA,
        "classification": "EXACT_CONDITIONAL_LOCAL_LINEAR_ROW_SPACE_NOT_PHYSICAL_PREDICTION",
        "source": {"path": SOURCE, "sha256": hashlib.sha256(source).hexdigest(),
                   "occurrence_ids": ["C25#1", "C179#1", "C180#1", "C181#1", "C241-L3"],
                   "documentary_lineages": 1, "instrument_calibration": None},
        "frozen_manifest": {"path": SPLIT, "sha256": hashlib.sha256(frozen).hexdigest(),
                            "retrospective_not_blind": True,
                            "verified_total_unique_epochs": sum(verified["per_split"][part]["unique_catalogue_epochs"]
                                for part in SPLITS)},
        "model": (
            "wrap(F_j(t)+phase_j+rate_j*t+catalog_offset+catalog_drift*t); "
            "F_j(t) entirely unknown/unvalidated, noise and source selection unknown"
        ),
        "comparisons": comparisons,
        "validation_527_counterexample": counterfactual_527(manifest),
        "interpretation": (
            "Row-space estimability is an exact LOCAL algebraic condition in an "
            "assumed linear design. It is not predictive calibration, posterior "
            "identification, a physical orbit, independent evidence or a "
            "geographic exclusion. Wrapped RAAN can have global aliases."
        ),
        "historical_mcmc": "NOT_RUN",
        "historical_likelihood": "NOT_CALIBRATED",
        "holdout_logscore": "NOT_RUN",
        "geographic_domain_change": "NOT_EVALUABLE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--split", required=True, type=Path)
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument("--output", type=Path)
    output.add_argument("--check", type=Path)
    args = parser.parse_args()
    report = build(args.input.read_bytes(), args.split.read_bytes())
    data = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    if args.check:
        if args.check.read_bytes() != data:
            raise SystemExit("FAIL: holdout estimability replay differs")
        print("RAAN_HOLDOUT_ESTIMABILITY_REPRODUCED", len(report["comparisons"]))
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)


if __name__ == "__main__":
    main()
