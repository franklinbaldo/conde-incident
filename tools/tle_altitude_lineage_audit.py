#!/usr/bin/env python3
"""C241-T13: test whether altitude_km is independent of mean motion.

Secondary Parquet fields ONLY. Keplerian two-body algebra gives proxies, not
historical observations, SGP4 propagation, a calibrated fit, or a reentry.
Numerical coincidence cannot establish a data-generation mechanism.
"""
import argparse
import json
import math
from decimal import Decimal, InvalidOperation
from pathlib import Path

from tle_mean_motion_secant_audit import (
    COUNTS, CSV_SHA, DISTINCT, IDS, PARQUET_SHA, SOURCE, normalize, read_rows,
)

MU_KM3_S2 = 398600.4418
RADIUS_CANDIDATES_KM = {"WGS84_equatorial": 6378.137, "mean_earth": 6371.0}
DAY_SECONDS = 86400.0
# Diagnostic thresholds, not instrument precision or orbital error bars.
RESIDUAL_REPORTING_KM = (0.1, 1.0, 10.0)
RADIUS_SPREAD_REPORTING_KM = 2.0


def proxy_semimajor_km(mean_motion_rev_day):
    n = float(mean_motion_rev_day)
    if not math.isfinite(n) or n <= 0:
        raise ValueError("mean_motion rev/day must be finite positive")
    angular_speed = n * 2.0 * math.pi / DAY_SECONDS
    semimajor = (MU_KM3_S2 / angular_speed ** 2) ** (1.0 / 3.0)
    if not math.isfinite(semimajor) or semimajor <= 0:
        raise ValueError("invalid two-body semimajor proxy")
    return semimajor


def finite_altitude(value):
    try:
        number = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("missing/invalid altitude_km") from exc
    if not number.is_finite():
        raise ValueError("nonfinite altitude_km")
    return float(number)


def audit(rows, source_sha, *, counts=None, distinct=None):
    unique, duplicate_indices, original_counts = normalize(
        rows, counts=counts, distinct=distinct)
    by_index = {}
    for raw in rows:
        index = int(raw["source_row"])
        if index in by_index:
            raise ValueError("duplicate source_row")
        by_index[index] = finite_altitude(raw.get("altitude_km"))
    output = []
    for record in unique:
        values = record["values"]
        eccentricity = float(values["eccentricity"])
        inclination = float(values["inclination"])
        if (not math.isfinite(eccentricity) or
                not 0 <= eccentricity < 1 or
                not 0 <= inclination <= 180):
            raise ValueError("invalid inclination/eccentricity in custody row")
        altitudes = [by_index[ix] for ix in record["source_rows"]]
        if any(x != altitudes[0] for x in altitudes[1:]):
            raise ValueError("contradictory altitude_km in same-epoch duplicates")
        a = proxy_semimajor_km(values["mean_motion"])
        reported = altitudes[0]
        # Use one explicit radius for all three illustration proxies. The
        # inferred radius a - h has no independently verified historical
        # frame, Earth radius convention or underlying dynamics.
        reference_radius = RADIUS_CANDIDATES_KM["WGS84_equatorial"]
        proxies = {
            "mean_a_minus_radius": a - reference_radius,
            "perigee_a_times_1_minus_e_minus_radius":
                a * (1.0 - eccentricity) - reference_radius,
            "apogee_a_times_1_plus_e_minus_radius":
                a * (1.0 + eccentricity) - reference_radius,
            "perigee_using_mean_earth_radius_6371":
                a * (1.0 - eccentricity) - RADIUS_CANDIDATES_KM["mean_earth"],
        }
        residuals = {k: reported - v for k, v in proxies.items()}
        candidates = sorted(residuals, key=lambda k: (abs(residuals[k]), k))
        output.append({
            "norad_id": record["sat"],
            "source_rows": record["source_rows"],
            "epoch_utc": record["epoch_literal"],
            "reported_altitude_km": reported,
            "mean_motion_rev_day": str(values["mean_motion"]),
            "eccentricity": str(values["eccentricity"]),
            "semimajor_two_body_proxy_km": round(a, 9),
            "implied_radius_if_altitude_equals_a_minus_radius_km":
                round(a - reported, 9),
            "implied_radius_if_altitude_equals_perigee_minus_radius_km":
                round(a * (1.0 - eccentricity) - reported, 9),
            "proxies_km": {k: round(v, 9) for k, v in proxies.items()},
            "reported_minus_proxy_km": {
                k: round(v, 9) for k, v in residuals.items()},
            "closest_arithmetic_proxy_not_field_identification":
                candidates[0],
        })
    by_catalog = {}
    for sat in IDS:
        records = [r for r in output if r["norad_id"] == sat]
        by_catalog[str(sat)] = summarize(records, original_counts.get(sat, 0))
    global_summary = summarize(output, len(rows))
    return {
        "evidence_id": "C241-T13",
        "type": "SECONDARY_ALTITUDE_FIELD_DEPENDENCE_DIAGNOSTIC",
        "source": {
            "url": SOURCE,
            "parquet_sha256": PARQUET_SHA,
            "derived_csv_sha256": source_sha,
            "expected_pinned_csv_sha256": CSV_SHA,
            "original_1963_NORAD_TLE_pairs": "NOT_RECOVERED",
            "ETL_formula_for_altitude_km": "NOT_VERIFIED",
            "independent_altitude_measurement": "NOT_ESTABLISHED",
            "historical_frame_sensor_and_error": "NOT_VERIFIED",
        },
        "algorithm": {
            "mu_km3_per_s2": MU_KM3_S2,
            "seconds_per_day": DAY_SECONDS,
            "candidate_radius_km": RADIUS_CANDIDATES_KM,
            "a_proxy_formula": "(mu/(2*pi*n_rev_day/86400)^2)^(1/3)",
            "two_body_proxy_only": True,
            "independent_height_or_observation_claim": False,
            "perigee_6371_is_only_a_candidate_formula": True,
            "report_thresholds_not_error_bars_km": RESIDUAL_REPORTING_KM,
            "radius_spread_diagnostic_not_identity_km":
                RADIUS_SPREAD_REPORTING_KM,
        },
        "source_rows_total": len(rows),
        "distinct_catalog_epochs": len(output),
        "duplicate_rows_not_independent": duplicate_indices,
        "overall": global_summary,
        "by_norad": by_catalog,
        "per_distinct_epoch": output,
        "interpretive_limit": (
            "Matching altitude_km to an algebraic function of mean_motion "
            "would suggest potential feature dependence, NOT prove the "
            "exporter formula nor authenticate a NORAD height observation. "
            "The two-body mean-motion proxy is not SGP4, neither mean-element "
            "compatibility nor an original 1963 frame has been established. "
            "No threshold here is a sensor error, likelihood or holdout."),
        "raan_198_5261_vs_284_1520": "UNRESOLVED_PRIMARY_ORIGIN",
        "physical_528_component": "NOT_IDENTIFIED",
        "lean_4_35_physical_restriction": "NOT_PROMOTED",
        "calibrated_simulation_holdout": "NOT_RUN",
        "conde_impact": "INDETERMINATE",
    }


def summarize(records, raw_count):
    radii = [r["implied_radius_if_altitude_equals_a_minus_radius_km"]
             for r in records]
    absolute_residual = {
        key: [abs(r["reported_minus_proxy_km"][key]) for r in records]
        for key in (
            "mean_a_minus_radius",
            "perigee_a_times_1_minus_e_minus_radius",
            "apogee_a_times_1_plus_e_minus_radius",
            "perigee_using_mean_earth_radius_6371")
    }
    spread = max(radii) - min(radii) if radii else None
    perigee_radii = [
        r["implied_radius_if_altitude_equals_perigee_minus_radius_km"]
        for r in records]
    perigee_spread = (
        max(perigee_radii) - min(perigee_radii) if perigee_radii else None)
    return {
        "original_rows": raw_count,
        "distinct_epochs": len(records),
        "implied_radius_range_km": (
            [round(min(radii), 9), round(max(radii), 9)] if radii else None),
        "implied_radius_spread_km": round(spread, 9) if radii else None,
        "perigee_implied_radius_range_km": (
            [round(min(perigee_radii), 9), round(max(perigee_radii), 9)]
            if perigee_radii else None),
        "perigee_implied_radius_spread_km": (
            round(perigee_spread, 9) if perigee_radii else None),
        "perigee_6371_numerical_match_at_0_1km_not_ETL_proof":
            sum(abs(r["reported_minus_proxy_km"][
                "perigee_using_mean_earth_radius_6371"]) <= 0.1
                for r in records),
        "constant_radius_2km_spread_diagnostic": (
            "NUMERICALLY_COMPATIBLE_NOT_PROVEN_DERIVED"
            if spread is not None and spread <= RADIUS_SPREAD_REPORTING_KM
            else "NOT_COMPATIBLE_AT_THIS_DIAGNOSTIC_THRESHOLD"
            if spread is not None else "NO_SAMPLES"),
        "proxy_comparisons": {
            key: {
                "mean_absolute_residual_km":
                    round(sum(values) / len(values), 9) if values else None,
                "counts_at_arbitrary_thresholds_km": {
                    str(threshold): sum(v <= threshold for v in values)
                    for threshold in RESIDUAL_REPORTING_KM},
            }
            for key, values in absolute_residual.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, source_sha = read_rows(args.csv)
    report = audit(rows, source_sha, counts=COUNTS, distinct=DISTINCT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True,
                                      ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "C241-T13": report["type"],
        "overall": report["overall"],
        "by_norad": {
            key: {"epochs": v["distinct_epochs"],
                  "perigee_implied_radius_spread_km":
                      v["perigee_implied_radius_spread_km"],
                  "perigee_6371_match_at_0_1km":
                      v["perigee_6371_numerical_match_at_0_1km_not_ETL_proof"]}
            for key, v in report["by_norad"].items()},
        "primary": report["source"]["original_1963_NORAD_TLE_pairs"],
        "conde": report["conde_impact"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
