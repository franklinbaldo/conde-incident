#!/usr/bin/env python3
"""Exact rank and conditional correlation-sensitivity of a toy RAAN error model.

The 1963 NORAD catalogue is a single modern secondary documentary lineage.
This is a structural NON-identifiability certificate, not orbital inference,
a prior, a likelihood calibrated to 1963, or a posterior distribution.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

from raan_chronological_holdout import build_manifest

SCHEMA = "conde.raan-lineage-identifiability/v1"
SOURCE_PATH = "research/statistics/raan_527_528_529_1963.json"
SPLIT_PATH = "research/statistics/raan_chronological_holdout_1963.json"
SPLITS = ("fit", "validation", "evaluation")
OBJECTS = ("527", "528", "529")
# These are illustrative stress tests, NOT estimates/priors for historical rho.
SCENARIO_RHO = (Fraction(0), Fraction(1, 10), Fraction(1, 2),
                Fraction(9, 10))


def wrap_deg(value: float) -> float:
    """Circular phase, invariant under addition of any complete turns."""
    if not math.isfinite(value):
        raise ValueError("nonfinite circular phase")
    return value % 360.0


def phase_prediction(phase_deg: float, source_bias_deg: float,
                     fixed_dynamics_deg: float) -> float:
    """Hypothetical additive model; dynamics are a GIVEN, not fitted here."""
    return wrap_deg(phase_deg + source_bias_deg + fixed_dynamics_deg)


def matrix_rank_exact(rows: list[tuple[int, ...]]) -> int:
    """Gauss-Jordan exact rational rank: no tolerance-dependent conclusions."""
    if not rows:
        return 0
    width = len(rows[0])
    if not width or any(len(row) != width for row in rows):
        raise ValueError("ragged or empty design matrix")
    a = [[Fraction(v) for v in row] for row in rows]
    rank = 0
    for col in range(width):
        pivot = next((r for r in range(rank, len(a)) if a[r][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        coeff = a[rank][col]
        a[rank] = [value / coeff for value in a[rank]]
        for r in range(len(a)):
            if r == rank:
                continue
            factor = a[r][col]
            if factor:
                a[r] = [v - factor * w for v, w in zip(a[r], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def row_for_object(norad: str, source: str = "secondary"):
    """Columns: object phase 527,528,529; one common secondary-source offset."""
    if norad not in OBJECTS or source != "secondary":
        raise ValueError("out-of-contract object or source")
    return tuple(int(o == norad) for o in OBJECTS) + (1,)


def design_effect(n: int, rho: Fraction) -> dict:
    """Equicorrelation illustration for ONE anchored homoscedastic scalar mean.

    Var(sample mean) = sigma^2 * (1 + (n-1)*rho) / n.
    Not the effective sample size of a trend, orbit, dependent epochs, or MCMC.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")
    if not isinstance(rho, Fraction) or not (0 <= rho < 1):
        raise ValueError("only hypothetical nonnegative rho strictly below 1")
    factor = 1 + (n - 1) * rho
    neff = Fraction(n) / factor
    return {
        "n": n,
        "rho": str(rho),
        "variance_inflation": str(factor),
        "n_effective_scalar_mean": str(neff),
        "n_effective_decimal_6_places": f"{float(neff):.6f}",
        "relative_information": str(Fraction(1) / factor),
    }


def build_report(source_bytes: bytes, committed_split_bytes: bytes) -> dict:
    """Read actual source + immutable membership manifest, never tune/evaluate."""
    frozen = json.loads(committed_split_bytes)
    recomputed = build_manifest(source_bytes)
    if recomputed != frozen:
        raise ValueError("pinned source/holdout mismatch")
    if frozen["design_status"] != "RETROSPECTIVE_TIME_SPLIT_NOT_BLINDED":
        raise ValueError("unexpected holdout semantics")
    if frozen["independence_status"] != "SAME_SECONDARY_DOCUMENTARY_LINEAGE_NOT_INDEPENDENT":
        raise ValueError("source independence assertion changed")
    provenance = json.loads(source_bytes)["provenance"]
    if provenance["status"] != "SECONDARY_CATALOGUE_DERIVED_NOT_ORIGINAL_TRACK":
        raise ValueError("source provenance status changed")
    if "Single historical Space-Track mirror" not in provenance["lineage"]:
        raise ValueError("unsupported source lineage")

    by_split = {}
    for split in SPLITS:
        members = [
            (norad, epoch)
            for norad in OBJECTS
            for epoch in frozen["memberships"][norad][split]
        ]
        rows = [row_for_object(norad) for norad, _ in members]
        # For ALL rows the gauge vector (+1,+1,+1,-1) is in the nullspace.
        gauge = (1, 1, 1, -1)
        if any(sum(a*b for a, b in zip(row, gauge)) for row in rows):
            raise AssertionError("gauge cancellation failed")
        rank = matrix_rank_exact(rows)
        n_unique = {norad: len(frozen["memberships"][norad][split])
                    for norad in OBJECTS}
        if rank != len([n for n in n_unique.values() if n > 0]):
            raise AssertionError("design rank unexpectedly changed")
        by_split[split] = {
            "unique_catalogue_epochs": len(rows),
            "per_norad": n_unique,
            "hypothetical_design_columns": [
                "phase_527", "phase_528", "phase_529", "source_bias"
            ],
            "exact_rational_rank": rank,
            "rank_deficiency": 4-rank,
            "null_direction": list(gauge),
            "rho_sensitivity_of_ONE_ANCHORED_SCALAR_MEAN_ONLY": {
                str(rho): {
                    "single_common_source_block": design_effect(len(rows), rho),
                    "separate_object_blocks": {
                        norad: design_effect(n, rho)
                        for norad, n in n_unique.items() if n
                    }
                }
                for rho in SCENARIO_RHO
            },
        }

    if (by_split["fit"]["per_norad"] != {"527": 15, "528": 24, "529": 22}
            or sum(x["unique_catalogue_epochs"] for x in by_split.values()) != 119):
        raise ValueError("unexpected historical membership counts")
    return {
        "schema": SCHEMA,
        "source": {
            "path": SOURCE_PATH,
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "evidence_ids": ["C25#1", "C179#1", "C180#1", "C181#1", "C241-L3"],
            "lineage": provenance["lineage"],
            "original_track_and_instrument_model": "NOT_RECOVERED",
        },
        "frozen_holdout": {
            "path": SPLIT_PATH,
            "sha256": hashlib.sha256(committed_split_bytes).hexdigest(),
            "not_blinded": True,
        },
        "model_hypothesis_NOT_EVIDENCE": (
            "Omega_jt=wrap(f_j(t; theta_other) + phase_j + b_source + error_jt). "
            "With free phase_j and free common b_source, an arbitrary rotation "
            "phase_j+a, b_source-a is exactly observationally equivalent."
        ),
        "gauge_transform": "phase_j += a (all 3 objects); b_source -= a",
        "hypothetical_error_correlation": (
            "rho in {0,1/10,1/2,9/10} is a declared algebraic scenario, "
            "not fitted or sourced. n_eff concerns ONLY an anchored, "
            "homoscedastic one-mean tangent-space model; not orbital-state "
            "precision and not MCMC ESS."
        ),
        "per_split": by_split,
        "inference_status": "STRUCTURAL_NONIDENTIFIABILITY_CONDITIONAL",
        "prior_status": "NOT_SPECIFIED",
        "historical_likelihood_status": "NOT_CALIBRATED",
        "posterior_mcmc_status": "NOT_RUN",
        "physical_domain_reduction": "NOT_COMPUTED",
        "needs": [
            "Primary tracking/sensor lineage and frame (Tartaruga)",
            "Validated forward map from osculating state to catalog RAAN (Castor)",
            "Independent angular reference or justified anchor for common-bias gauge",
            "Instrumental covariance and selection model before likelihood"
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--split", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args()
    result = build_report(args.input.read_bytes(), args.split.read_bytes())
    payload = (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    if args.check:
        if args.check.read_bytes() != payload:
            raise SystemExit("FAIL: identifiability report does not reproduce byte-for-byte")
        print("IDENTIFIABILITY_REPLAY_OK", result["per_split"]["fit"]["exact_rational_rank"],
              result["per_split"]["fit"]["unique_catalogue_epochs"])
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)


if __name__ == "__main__":
    main()
