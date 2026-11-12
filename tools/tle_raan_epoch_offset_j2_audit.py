#!/usr/bin/env python3
"""C241-T10: falsify epoch-offset-only explanation of the 528 RAAN conflict.

A numerical J2 *conditional diagnostic*, not SGP4, a historical element
reconstruction, a terminal propagation, or an authenticated 1963 measurement.
The legacy vector has no established NORAD provenance or historical frame.
"""
import argparse
import hashlib
import json
import math
from datetime import timedelta
from pathlib import Path

from audit_norad_1963 import angular_distance_deg, tle_epoch_utc, validate_raw_tle
from legacy_528_fingerprint import (
    LEGACY_BLOB_SHA, LEGACY_LINE1, LEGACY_LINE2,
    EXPECTED_528_CSV_SHA256, read_528_csv,
)

PAIR_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
PARQUET_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
J2 = 1.08262668e-3
MU_KM3_S2 = 398600.4418
EARTH_EQUATORIAL_RADIUS_KM = 6378.137
SECONDS_PER_DAY = 86400
MICROSECOND = timedelta(microseconds=1)
# Two four-decimal RAAN text fields: at most 0.0001 deg combined rounding.
COMBINED_RAAN_DECIMAL_ERROR_DEG = 0.0001


def elements(line2):
    return {"inclination_deg": float(line2[8:16]),
            "raan_deg": float(line2[17:25]),
            "eccentricity": float("0." + line2[26:33]),
            "mean_motion_rev_per_day": float(line2[52:63])}


def j2_secular_node_rate_deg_per_day(inc_deg, ecc, rev_per_day):
    """First-order two-body/J2 secular node rate, only under assumed model.

    Uses n as a Keplerian proxy for TLE mean motion. TEME/mean-element
    conventions, SGP4 secular terms and 1963 observation errors are NOT
    certified by this proxy.
    """
    values = (inc_deg, ecc, rev_per_day)
    if (not all(math.isfinite(x) for x in values) or
            not 0 <= inc_deg <= 180 or not 0 <= ecc < 1 or
            rev_per_day <= 0):
        raise ValueError("invalid J2 proxy orbital elements")
    n = rev_per_day * 2 * math.pi / SECONDS_PER_DAY
    a = (MU_KM3_S2 / (n * n)) ** (1 / 3)
    if a <= EARTH_EQUATORIAL_RADIUS_KM:
        raise ValueError("J2 proxy semimajor axis below Earth radius")
    p = a * (1 - ecc * ecc)
    if p <= EARTH_EQUATORIAL_RADIUS_KM:
        raise ValueError("J2 proxy pericenter inside reference ellipsoid")
    rate_rad_s = (-1.5 * J2 * n *
                  (EARTH_EQUATORIAL_RADIUS_KM / p) ** 2 *
                  math.cos(math.radians(inc_deg)))
    return rate_rad_s * 180 / math.pi * SECONDS_PER_DAY


def conditional_epoch_offset_test(legacy_epoch, mirror_epoch, legacy, mirror):
    """Discriminate only the subhypothesis 'same frame + offset in epoch'.

    Do not reject alternate reference frames, data lineage errors, or
    unobserved orbit changes. Not an empirical confidence interval.
    """
    if (legacy_epoch.tzinfo is None or mirror_epoch.tzinfo is None or
            legacy_epoch.utcoffset() != timedelta(0) or
            mirror_epoch.utcoffset() != timedelta(0)):
        raise ValueError("epochs must be UTC")
    duration_us = abs((mirror_epoch - legacy_epoch) // MICROSECOND)
    if duration_us == 0:
        raise ValueError("no epoch offset: cannot calculate required rate")
    days = duration_us / (SECONDS_PER_DAY * 1_000_000)
    rates = {
        "legacy_unverified": j2_secular_node_rate_deg_per_day(
            legacy["inclination_deg"], legacy["eccentricity"],
            legacy["mean_motion_rev_per_day"]),
        "secondary_mirror": j2_secular_node_rate_deg_per_day(
            mirror["inclination_deg"], mirror["eccentricity"],
            mirror["mean_motion_rev_per_day"]),
    }
    discrepancy = angular_distance_deg(legacy["raan_deg"], mirror["raan_deg"])
    max_proxy_drift = max(map(abs, rates.values())) * days
    gap_floor = max(0.0, discrepancy - COMBINED_RAAN_DECIMAL_ERROR_DEG)
    excluded = gap_floor > max_proxy_drift
    return {
        "epoch_separation_microseconds": duration_us,
        "epoch_separation_days": days,
        "shortest_raan_difference_deg": discrepancy,
        "combined_rounding_bound_deg": COMBINED_RAAN_DECIMAL_ERROR_DEG,
        "minimum_required_node_rate_deg_per_day": gap_floor / days,
        "j2_proxy_rates_deg_per_day": rates,
        "max_j2_proxy_drift_deg_during_offset": max_proxy_drift,
        "epoch_offset_only_j2_model": (
            "EXCLUDED_CONDITIONALLY" if excluded else "NOT_EXCLUDED_BY_THIS_BOUND"),
        "physical_1963_raan_origin": "UNRESOLVED",
    }


def audit(rows, csv_sha, pair_path, *, expected_count=45):
    if expected_count is not None and len(rows) != expected_count:
        raise ValueError("528 source count changed")
    payload = pair_path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != PAIR_SHA256:
        raise ValueError("literal 528 pair SHA256 mismatch")
    pair = payload.decode("ascii").splitlines()
    if len(pair) != 2:
        raise ValueError("literal pair must have two lines")
    validate_raw_tle(pair[0], pair[1], 528)
    validate_raw_tle(LEGACY_LINE1, LEGACY_LINE2, 528)
    mirror_epoch = tle_epoch_utc(pair[0])
    legacy_epoch = tle_epoch_utc(LEGACY_LINE1)
    mirror = elements(pair[1])
    legacy = elements(LEGACY_LINE2)
    matches = [
        row for row in rows
        if abs((row["epoch_utc"] - mirror_epoch) // MICROSECOND) <= 432
    ]
    if len(matches) != 1:
        raise ValueError("missing or ambiguous same-epoch 528 numeric sample")
    matching = matches[0]
    if angular_distance_deg(matching["fields"]["raan"], mirror["raan_deg"]) > 0.00008:
        raise ValueError("literal/mirror same-epoch RAAN differs")
    diagnostic = conditional_epoch_offset_test(legacy_epoch, mirror_epoch, legacy, mirror)
    return {
        "record_id": "C241-T10",
        "class": "SECONDARY_PROVENANCE_CONFLICT_CONDITIONAL_J2_FALSIFICATION",
        "source": {
            "numeric_1963_mirror_url":
                "https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet",
            "numeric_1963_sha256": PARQUET_SHA256,
            "secondary_528_csv_sha256": csv_sha,
            "secondary_literal_url": "https://www.itau.magnetic-declination.com/satellite/?s=528",
            "secondary_literal_sha256": PAIR_SHA256,
            "legacy_code_git_blob_sha1": LEGACY_BLOB_SHA,
            "format_reference": "https://celestrak.org/columns/v04n03/",
            "primary_norad_source": "NOT_RECOVERED",
            "independent_tracking_chains": "NOT_ESTABLISHED",
            "historical_reference_frame_and_errors": "NOT_VERIFIED",
        },
        "mirror_528_sample_count": len(rows),
        "literal_mirror_epoch_utc": mirror_epoch.isoformat().replace("+00:00", "Z"),
        "legacy_unverified_epoch_utc": legacy_epoch.isoformat().replace("+00:00", "Z"),
        "same_epoch_numeric_source_row": matching["source_row"],
        "same_epoch_numeric_raan_deg": matching["fields"]["raan"],
        "legacy_literal_elements": legacy,
        "mirror_literal_elements": mirror,
        "diagnostic": diagnostic,
        "j2_proxy_model": {
            "J2": J2, "mu_km3_s2": MU_KM3_S2,
            "equatorial_radius_km": EARTH_EQUATORIAL_RADIUS_KM,
            "mean_motion_treated_as_keplerian_proxy": True,
            "historical_1963_mean_element_frame_verified": False,
            "observational_error_distribution": "UNKNOWN",
            "model_status": "EXPLORATORY_CONDITIONAL_NOT_SGP4",
        },
        "lean_4_35_physical_restriction": "NOT_PROMOTED_NO_PRIMARY_FRAME_OR_ERRORS",
        "physical_calibrated_simulation_and_holdout": "NOT_RUN",
        "component_528_identity": "NOT_IDENTIFIED_FROM_PRIMARY_ENGINEERING_RECORD",
        "reentry_and_conde": "INDETERMINATE",
        "limit": ("Excludes only the 16-second timing-shift explanation under the "
                  "declared common-frame, first-order J2 proxy. Does not "
                  "authenticate either vector, determine historical frames, "
                  "select a true RAAN, predict reentry or establish impact."),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--pair", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, sha = read_528_csv(args.csv)
    if sha != EXPECTED_528_CSV_SHA256:
        raise ValueError("secondary CSV SHA256 mismatch")
    report = audit(rows, sha, args.pair)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True,
                                      ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"diagnostic": report["diagnostic"],
                      "status": report["reentry_and_conde"]}, sort_keys=True))


if __name__ == "__main__":
    main()
