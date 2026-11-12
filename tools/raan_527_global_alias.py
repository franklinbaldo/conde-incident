#!/usr/bin/env python3
"""Exact circular winding aliases for a counterfactual second 527 epoch.

A rank gain in a local real-valued design is NOT global S1 identification.
No invented 1963 observations, orbital physics or posterior.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from raan_lineage_identifiability import build_report, matrix_rank_exact
from raan_holdout_estimability import rows_for
from raan_temporal_gauge import days_from_reference, model_row

SCHEMA = "conde.raan-527-global-circular-alias/v1"
SOURCE = "research/statistics/raan_527_528_529_1963.json"
SPLIT = "research/statistics/raan_chronological_holdout_1963.json"


def rational(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def alias_witness(t0: Fraction, t1: Fraction, evaluation: list[Fraction]) -> dict:
    """Two exact wrapped measurements admit beta + 360*k/(t1-t0)."""
    if t1 <= t0:
        raise ValueError("second UTC instant must follow first")
    if not evaluation or any(t == t0 or t == t1 for t in evaluation):
        raise ValueError("holdout must be nonempty and distinct from design")
    delta_beta = Fraction(360) / (t1 - t0)
    delta_phase = -delta_beta * t0
    def change(t: Fraction) -> Fraction:
        return (delta_phase + delta_beta * t) % 360
    if change(t0) or change(t1):
        raise AssertionError("circular alias must preserve both design observations")
    changes = [change(t) for t in evaluation]
    if not any(changes):
        raise AssertionError("this candidate cannot discriminate any holdout")
    return {
        "candidate": "COUNTERFACTUAL_SECOND_527_EPOCH_NO_MEASUREMENT",
        "delta_days": rational(t1 - t0),
        "rate_alias_spacing_deg_per_day": rational(delta_beta),
        "k_1_phase_shift_deg": rational(delta_phase),
        "k_1_rate_shift_deg_per_day": rational(delta_beta),
        "design_wrapped_prediction_shifts_deg": [rational(change(t0)), rational(change(t1))],
        "evaluation_527_wrapped_shifts_deg": [rational(x) for x in changes],
        "evaluation_527_changed_count": sum(x != 0 for x in changes),
        "global_rate_unique_from_two_circular_points": False,
        "conditional_prior_width_criterion": (
            "Only with noise-free precisely timed angles and a justified "
            "rate interval narrower than this alias spacing can at most "
            "one integer winding branch lie inside the interval."
        ),
    }


def build(raw: bytes, frozen: bytes) -> dict:
    history = build_report(raw, frozen)
    manifest = json.loads(frozen)
    if manifest["unique_total"] != 119:
        raise ValueError("historical holdout manifest changed")
    validation = manifest["memberships"]["527"]["validation"]
    if len(validation) != 1:
        raise ValueError("requires the single frozen 527 validation epoch")
    evaluation = manifest["memberships"]["527"]["evaluation"]
    if len(evaluation) != 4:
        raise ValueError("requires four untouched 527 evaluation epochs")
    t0 = days_from_reference(validation[0])
    eval_days = [days_from_reference(e) for e in evaluation]
    train = rows_for(manifest, ("validation",))
    if matrix_rank_exact(train) != 5 or len(train) != 23:
        raise ValueError("frozen local design changed")
    designs = []
    for lag in (Fraction(1, 2), Fraction(1)):
        t1 = t0 + lag
        if matrix_rank_exact(train + [model_row("527", t1)]) != 6:
            raise AssertionError("local rank should gain one dimension")
        design = alias_witness(t0, t1, eval_days)
        design["rank_before_second_epoch"] = 5
        design["rank_after_second_epoch"] = 6
        design["remaining_global_winding_aliases_without_rate_bound"] = "COUNTABLY_INFINITE"
        designs.append(design)
    return {
        "schema": SCHEMA,
        "classification": "CONDITIONAL_EXACT_GLOBAL_S1_ALIAS_NOT_HISTORICAL_POSTERIOR",
        "source": {
            "path": SOURCE, "sha256": hashlib.sha256(raw).hexdigest(),
            "occurrence_ids": ["C25#1", "C179#1", "C180#1", "C181#1", "C241-L3"],
            "documentary_lineages": 1, "calibrated_sensor": None,
        },
        "frozen_manifest": {
            "path": SPLIT, "sha256": hashlib.sha256(frozen).hexdigest(),
            "retrospective_not_blinded": True,
            "unique_epochs": sum(
                history["per_split"][p]["unique_catalogue_epochs"]
                for p in ("fit", "validation", "evaluation")
            ),
            "sole_527_validation_epoch_utc": validation[0],
            "evaluation_527_epoch_utc": evaluation,
        },
        "hypothesis": (
            "wrap(F_527(t)+alpha_527+beta_527*t+source_offset+source_drift*t); "
            "F_527(t) fixed but unknown, offset and drift uncalibrated. "
            "At two exact times, shifting beta by 360*k/Delta_t and alpha "
            "by -t0*360*k/Delta_t leaves both wrapped angles unchanged."
        ),
        "counterfactual_designs": designs,
        "active_constraint": False,
        "historical_rate_prior": None,
        "historical_epoch_error": None,
        "historical_angular_error": None,
        "forward_physical_operator": None,
        "calibrated_historical_mcmc": "NOT_RUN",
        "historical_holdout_logscore": "NOT_RUN",
        "conde_admissible_geography_change": "NOT_EVALUABLE",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--split", type=Path, required=True)
    out = p.add_mutually_exclusive_group(required=True)
    out.add_argument("--output", type=Path)
    out.add_argument("--check", type=Path)
    a = p.parse_args()
    payload = (json.dumps(build(a.input.read_bytes(), a.split.read_bytes()),
                          sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
    if a.check:
        if a.check.read_bytes() != payload:
            raise SystemExit("FAIL: global alias certificate differs from frozen input")
        print("RAAN_GLOBAL_ALIAS_REPRODUCED")
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_bytes(payload)


if __name__ == "__main__":
    main()
