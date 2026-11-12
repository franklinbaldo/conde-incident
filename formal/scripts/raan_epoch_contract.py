#!/usr/bin/env python3
"""Exact C241-T10 RAAN epoch-offset arithmetic, not an orbit propagation.

Source: Tartaruga PR #14, commit 1934198e260b9dae8c056587cc7a16c777d58d25;
secondary 528 literal SHA-256 18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd.
This is a cross-check of a known diagnostic, not a new source or
independent observation. No authenticated element frame or drift-rate bound.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path

LEGACY_RAAN_E4 = 2841520
MIRROR_RAAN_E4 = 1985261
EPOCH_OFFSET_US = 16132608
DAY_US = 86400000000
ROUNDING_ALLOWANCE_E4 = 1
FULL_TURN_E4 = 3600000
SOURCE_COMMIT = "1934198e260b9dae8c056587cc7a16c777d58d25"
SECONDARY_TLE_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"


def circular_gap_e4(a: int, b: int) -> int:
    if not 0 <= a < FULL_TURN_E4 or not 0 <= b < FULL_TURN_E4:
        raise ValueError("RAAN must be in [0,360) degrees, scaled by 10^4")
    distance = abs(a - b)
    return min(distance, FULL_TURN_E4 - distance)


def required_rate_floor_deg_day(a: int, b: int, delta_us: int,
                                rounding_e4: int = ROUNDING_ALLOWANCE_E4) -> Fraction:
    if delta_us <= 0 or rounding_e4 < 0:
        raise ValueError("positive epoch separation and nonnegative rounding required")
    gap_floor = max(0, circular_gap_e4(a, b) - rounding_e4)
    return Fraction(gap_floor * DAY_US, delta_us * 10000)


def admissible_under_cap(a: int, b: int, delta_us: int,
                         cap_deg_day: Fraction, rounding_e4: int = 1) -> bool:
    if cap_deg_day < 0:
        raise ValueError("nonnegative cap required")
    return cap_deg_day >= required_rate_floor_deg_day(a, b, delta_us, rounding_e4)


def contract() -> dict:
    rate = required_rate_floor_deg_day(
        LEGACY_RAAN_E4, MIRROR_RAAN_E4, EPOCH_OFFSET_US)
    assert Fraction(458578, 1) < rate < Fraction(458579, 1)
    return {
        "record": "C241-T10",
        "source_commit": SOURCE_COMMIT,
        "source_audit_script": "tools/tle_raan_epoch_offset_j2_audit.py",
        "source_literal_sha256": SECONDARY_TLE_SHA256,
        "matrix_lineage": ["C25#1", "C179#1", "C241-T10"],
        "independent_orbital_source_count": "NOT_ESTABLISHED",
        "primary_1963_tle_custody": "NOT_VERIFIED",
        "historical_frame_equivalence": "NOT_VERIFIED",
        "input_status": "SECONDARY_LITERAL_PLUS_UNAUTHENTICATED_LEGACY",
        "legacy_raan_e4_deg": LEGACY_RAAN_E4,
        "mirror_raan_e4_deg": MIRROR_RAAN_E4,
        "epoch_offset_microseconds": EPOCH_OFFSET_US,
        "combined_decimal_rounding_e4_deg": ROUNDING_ALLOWANCE_E4,
        "shortest_raan_gap_e4_deg": circular_gap_e4(LEGACY_RAAN_E4, MIRROR_RAAN_E4),
        "minimum_gap_e4_deg": circular_gap_e4(LEGACY_RAAN_E4, MIRROR_RAAN_E4) - ROUNDING_ALLOWANCE_E4,
        "required_rate_lower_bound_deg_day_exact": f"{rate.numerator}/{rate.denominator}",
        "required_rate_bracket_deg_day": [458578, 458579],
        "assumption": "SAME_OBJECT_SAME_FRAME_SAME_NODE_EPOCH_SHIFT_ONLY",
        "model_rate_cap_deg_day": None,
        "conditional_result_if_cap_below_required_rate": "EPOCH_OFFSET_ONLY_EXCLUDED",
        "source_selection": "UNRESOLVED",
        "physics_calibration": "NOT_RUN",
        "conde_region_or_impact": None,
        "original_lean_zip_154_151": "NOT_RUN",
        "limitation": "Arithmetic discriminant only; no primary ephemeris, frame verification, calibrated dynamics, orbital state or impact location.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    out = contract()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"record": out["record"],
                      "required_rate_lower_bound_deg_day_exact": out["required_rate_lower_bound_deg_day_exact"],
                      "source_selection": out["source_selection"]}, sort_keys=True))


if __name__ == "__main__":
    main()
