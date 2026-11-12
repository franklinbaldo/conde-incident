#!/usr/bin/env python3
"""C241-P6: falsify a simple Greenwich z-rotation explanation for legacy RAAN.

No original TEME/PEF framing is authenticated. UTC is used as a deliberately
labelled UT1 proxy for an *algebraic control*, not historical frame calibration.
No orbital state is propagated and no physical constraint is activated.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path

from tle_cross_catalog_legacy_audit import (
    LEGACY_BLOB_SHA, LEGACY_LINE1, LEGACY_LINE2,
)
from tle_literal_layout import audit_literal_file, audit_pair

LITERAL = Path(__file__).resolve().parents[1] / "research/tle_custody/mirror_528_1963-10-27.tle"
LITERAL_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
EARTH_TURN_DEG_PER_UTC_PROXY_SECOND = 360.98564736629 / 86400.0


def jd_utc_proxy(when: datetime) -> float:
    """Gregorian JD using an explicitly labelled UTC proxy for UT1."""
    if when.tzinfo != timezone.utc:
        raise ValueError("explicit UTC timezone required")
    year, month = when.year, when.month
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    fraction = (when.hour * 3600 + when.minute * 60 + when.second
                + when.microsecond / 1_000_000) / 86400
    return (math.floor(365.25 * (year + 4716))
            + math.floor(30.6001 * (month + 1))
            + when.day + b - 1524.5 + fraction)


def gmst_utc_proxy_deg(when: datetime) -> float:
    """Conventional polynomial GMST in degrees, *if* input is UT1.

    The UT1/UTC difference in 1963 is NOT supplied by the record. The result
    is an explicit counterfactual with UTC inserted for UT1, not a recovered
    historical reference-frame transformation.
    """
    jd = jd_utc_proxy(when)
    centuries = (jd - 2451545.0) / 36525.0
    return (280.46061837 + 360.98564736629 * (jd - 2451545.0)
            + 0.000387933 * centuries**2 - centuries**3 / 38710000) % 360.0


def signed_circular_difference_deg(a: float, b: float) -> float:
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError("non-finite angular input")
    return (a - b + 180.0) % 360.0 - 180.0


def utc_from_tle_report(stamp: str) -> datetime:
    if not stamp.endswith("Z"):
        raise ValueError("source report requires explicit Z timezone")
    when = datetime.fromisoformat(stamp[:-1] + "+00:00")
    if when.tzinfo != timezone.utc:
        raise ValueError("source report must use UTC")
    return when


def evaluate(utc_proxy_stress_seconds: float = 60.0) -> dict:
    """Test ±GMST and no-rotation baselines at both literal printed epochs.

    The ±60-second variation is a declared stress parameter, NOT a historical
    measured bound on DUT1 and NOT a physical observational covariance.
    """
    if (not math.isfinite(utc_proxy_stress_seconds)
            or not 0 <= utc_proxy_stress_seconds <= 3600):
        raise ValueError("invalid declared UTC-proxy stress range")
    actual_sha = hashlib.sha256(LITERAL.read_bytes()).hexdigest()
    if actual_sha != LITERAL_SHA256:
        raise ValueError("pinned secondary literal TLE SHA256 mismatch")
    legacy = audit_pair(LEGACY_LINE1, LEGACY_LINE2, expected_sat=528)
    secondary = audit_literal_file(LITERAL)
    legacy_raan = float(legacy["values"]["raan"]["decimal"])
    secondary_raan = float(secondary["values"]["raan"]["decimal"])
    if (legacy_raan, secondary_raan) != (284.1520, 198.5261):
        raise ValueError("pinned competing RAAN values changed")
    epochs = {
        "constructed_legacy_printed": utc_from_tle_report(legacy["epoch_utc"]),
        "secondary_528_literal": utc_from_tle_report(secondary["epoch_utc"]),
    }
    results = {}
    for label, epoch in epochs.items():
        gmst = gmst_utc_proxy_deg(epoch)
        trials = {}
        for sign in (-1, 1):
            predicted = (secondary_raan + sign * gmst) % 360.0
            residual = signed_circular_difference_deg(legacy_raan, predicted)
            ends = [
                (secondary_raan + sign * gmst_utc_proxy_deg(
                    epoch + timedelta(seconds=s))) % 360.0
                for s in (-utc_proxy_stress_seconds, utc_proxy_stress_seconds)
            ]
            end_residuals = [
                signed_circular_difference_deg(legacy_raan, candidate)
                for candidate in ends
            ]
            # Stress window <= 1h; for THESE pinned angles neither branch
            # crosses zero or the +/-180 discontinuity. Fail closed otherwise.
            if (end_residuals[0] * end_residuals[1] <= 0
                    or abs(end_residuals[0] - end_residuals[1]) >= 180):
                raise ValueError("stress endpoints require circular subdivision")
            trials["minus_gmst" if sign == -1 else "plus_gmst"] = {
                "predicted_angle_deg": predicted,
                "signed_residual_to_legacy_deg": residual,
                "minimum_abs_residual_within_stress_deg": min(
                    abs(x) for x in end_residuals),
            }
        results[label] = {
            "epoch_utc_as_printed": epoch.isoformat().replace("+00:00", "Z"),
            "gmst_deg_using_UTC_as_UT1_proxy": gmst,
            "rotations": trials,
        }
    seconds_between = (
        epochs["secondary_528_literal"] - epochs["constructed_legacy_printed"]
    ).total_seconds()
    closest = results["secondary_528_literal"]["rotations"]["minus_gmst"]
    return {
        "question": "Does a single Greenwich z-rotation reconcile both RAAN values at their printed October 1963 epochs?",
        "classification": "CONDITIONAL_ALGEBRAIC_FRAME_CONTROL_NOT_TRACKING",
        "source_occurrences": ["C25#1", "C179#1", "C241-L8", "C241-P5"],
        "secondary_tle_file": str(LITERAL.relative_to(Path(__file__).resolve().parents[1])),
        "secondary_tle_sha256": actual_sha,
        "legacy_git_blob_sha1": LEGACY_BLOB_SHA,
        "source_family": "SECONDARY_MIRROR_AND_UNVERIFIED_SITE_CONSTRUCTION",
        "declared_utc_proxy_stress_seconds_not_DUT1_bound": utc_proxy_stress_seconds,
        "secondary_raan_deg": secondary_raan,
        "legacy_raan_deg": legacy_raan,
        "unrotated_abs_difference_deg": abs(
            signed_circular_difference_deg(legacy_raan, secondary_raan)),
        "printed_epoch_separation_seconds": seconds_between,
        "results_by_printed_epoch": results,
        "best_minus_gmst_at_secondary_epoch_abs_residual_deg": abs(
            closest["signed_residual_to_legacy_deg"]),
        "approx_extra_time_shift_to_zero_minus_gmst_seconds": abs(
            closest["signed_residual_to_legacy_deg"]) /
            EARTH_TURN_DEG_PER_UTC_PROXY_SECOND,
        "verdict_within_declared_stress": (
            "SIMPLE_GREENWICH_Z_ROTATION_NOT_SUFFICIENT_AT_PRINTED_EPOCHS"
        ),
        "missing_to_test_REAL_frame_hypothesis": (
            "legacy primary full TLE/epoch/frame, 1963 UT1-UTC, "
            "TEME/PEF convention, sensor calibration and errors"
        ),
        "active_Lean_physical_constraint": False,
        "physical_domain_delta": "NONE",
        "site_of_reentry": "INDETERMINATE",
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True, ensure_ascii=False))
