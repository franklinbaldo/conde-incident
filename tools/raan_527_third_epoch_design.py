#!/usr/bin/env python3
"""Exact three-epoch circular rate alias design, never a 1963 observation.

A tiny exact gcd does not demonstrate noise-robust rate identification.
The forward physical term F_527 must be fixed and independently validated.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from functools import reduce
import hashlib
import json
from math import gcd, lcm
from pathlib import Path

from raan_lineage_identifiability import build_report
from raan_temporal_gauge import days_from_reference

SCHEMA = "conde.raan-527-third-epoch-discrimination/v1"
SOURCE = "research/statistics/raan_527_528_529_1963.json"
SPLIT = "research/statistics/raan_chronological_holdout_1963.json"


def rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def rational_gcd(intervals: tuple[Fraction, ...]) -> Fraction:
    """Maximal rational time quantum dividing all positive lags exactly."""
    if not intervals or any(x <= 0 for x in intervals):
        raise ValueError("nonempty strictly positive time differences required")
    den = lcm(*(x.denominator for x in intervals))
    numerators = [int(x * den) for x in intervals]
    return Fraction(reduce(gcd, numerators), den)


def circular_distance_from_zero(angle: Fraction) -> Fraction:
    remainder = angle % 360
    return min(remainder, 360 - remainder)


def design(delta_01: Fraction, delta_02: Fraction, k_max: int = 4) -> dict:
    """Compare branches from the first two exact wrapped angles at a third time.

    Absolute phase, unknown source offset and affine documentary drift cancel
    from branch contrasts; this requires a fixed physical F(t) and same source.
    The three-angle independent *bounded* error model is hypothetical.
    """
    if delta_01 <= 0 or delta_02 <= delta_01:
        raise ValueError("strictly increasing three-epoch design required")
    if not isinstance(k_max, int) or isinstance(k_max, bool) or k_max < 1:
        raise ValueError("k_max must be a positive integer")
    ratio = delta_02 / delta_01
    quantum = rational_gcd((delta_01, delta_02))
    lattice_spacing = Fraction(360) / quantum
    distances = [circular_distance_from_zero(360 * k * ratio)
                 for k in range(1, k_max + 1)]
    # For |e_i| <= epsilon on THREE independent scalar angles, the
    # k-branch extrapolation's third residual is bounded by C*epsilon.
    # Two candidate residual intervals are guaranteed disjoint only when
    # circle distance > 2*C*epsilon. This is a sufficient condition,
    # never an instrument error estimate or calibrated likelihood.
    coefficient = abs(1-ratio) + abs(ratio) + 1
    minimum = min(distances)
    tolerance = minimum / (2 * coefficient)
    return {
        "t1_minus_t0_days": rational(delta_01),
        "t2_minus_t0_days": rational(delta_02),
        "t2_over_t1_relative_to_t0": rational(ratio),
        "gcd_days_exact": rational(quantum),
        "global_alias_spacing_deg_per_day_exact_noise_free": rational(lattice_spacing),
        "first_k_max": k_max,
        "first_aliases_circular_discrimination_deg": [rational(x) for x in distances],
        "min_discrimination_first_k_deg": rational(minimum),
        "first_k_all_distinguishable_exact": minimum > 0,
        "bounded_error_residual_factor": rational(coefficient),
        "sufficient_per_angle_error_for_disjoint_candidate_bands_deg_strictly_below": (
            rational(tolerance) if minimum else None
        ),
        "condition": "ASSUMED |angular error at each of 3 times|<=epsilon (no independence assumed); "
                     "exact timestamps, common frame, fixed physical F_527; "
                     "two candidate extrapolation bands are separated if "
                     "epsilon<min_distance/(2*(abs(1-r)+abs(r)+1)).",
        "no_historical_error_or_prior_calibrated": True,
    }


def build(source_bytes: bytes, frozen_bytes: bytes) -> dict:
    audit = build_report(source_bytes, frozen_bytes)
    split = json.loads(frozen_bytes)
    if split["unique_total"] != 119:
        raise ValueError("source/split drift")
    val = split["memberships"]["527"]["validation"]
    evaluation = split["memberships"]["527"]["evaluation"]
    if len(val) != 1 or len(evaluation) != 4:
        raise ValueError("frozen 527 validation/evaluation membership drift")
    if sum(audit["per_split"][part]["unique_catalogue_epochs"]
           for part in ("fit", "validation", "evaluation")) != 119:
        raise ValueError("frozen total mismatch")
    t0 = days_from_reference(val[0])
    if not all(days_from_reference(x) > t0 for x in evaluation):
        raise ValueError("evaluation must occur after validation")
    one = Fraction(1)
    return {
        "schema": SCHEMA,
        "classification": "EXACT_COUNTERFACTUAL_DESIGN_NOT_HISTORICAL_INFERENCE",
        "source": {
            "path": SOURCE, "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "occurrence_ids": ["C25#1", "C179#1", "C180#1", "C181#1", "C241-L3"],
            "documentary_lineages": 1, "sensor_calibration": None,
        },
        "frozen_holdout": {
            "path": SPLIT, "sha256": hashlib.sha256(frozen_bytes).hexdigest(),
            "unique_epochs": 119, "split_counts": [61, 23, 35],
            "validation_527_epoch_utc": val[0],
            "evaluation_527_epochs_utc": evaluation,
            "retrospective_nonblind": True,
            "evaluation_observations_used_for_fit": False,
        },
        "reference_times": {
            "t0": "actual 527 validation UTC epoch (timing only)",
            "t1": "t0 + 1 exact day; NO measurement exists at that time",
            "t2": "three alternative counterfactual timings; NO measurement exists",
        },
        "hypothesis": "wrap(F_527(t)+alpha_527+beta_527*t+catalog_offset+catalog_drift*t); "
                      "fixed F_527 is not yet validated. For exact 3 times, "
                      "rate aliases have lattice spacing 360/gcd(t1-t0,t2-t0). "
                      "Finite-time-error, angle-error and physical calibration unknown.",
        "designs": {
            "adjacent_one_tle_tick": design(one, one + Fraction(1, 100000000)),
            "half_day_offset": design(one, Fraction(3, 2)),
            "one_fifth_day_offset": design(one, Fraction(6, 5)),
        },
        "rank_does_not_prove_robust_identification": True,
        "tick_864_microseconds_is_format_grid_not_instrument_accuracy": True,
        "k_max_is_exploratory_not_a_physical_prior": True,
        "active_constraint": False,
        "historical_angular_error": None,
        "historical_timestamp_error": None,
        "historical_physical_rate_interval": None,
        "forward_physical_operator": None,
        "historical_mcmc": "NOT_RUN",
        "calibrated_holdout_likelihood": "NOT_RUN",
        "conde_geographic_domain_change": "NOT_EVALUABLE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--split", required=True, type=Path)
    out = parser.add_mutually_exclusive_group(required=True)
    out.add_argument("--output", type=Path)
    out.add_argument("--check", type=Path)
    args = parser.parse_args()
    content = (json.dumps(build(args.input.read_bytes(), args.split.read_bytes()),
                          ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    if args.check:
        if args.check.read_bytes() != content:
            raise SystemExit("FAIL: third-epoch alias certificate changed")
        print("RAAN_527_THIRD_EPOCH_DISCRIMINATION_REPRODUCED")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)


if __name__ == "__main__":
    main()
