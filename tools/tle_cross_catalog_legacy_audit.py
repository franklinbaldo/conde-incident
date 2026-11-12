#!/usr/bin/env python3
"""C241-L8: cross-catalog fingerprint of an UNVERIFIED legacy NORAD 528 vector.

This is a negative-control search in a pinned SECONDARY numeric mirror. Neither
a similar angle nor an entire six-field match authenticates a 1963 instrument,
transfers physical identity across catalog IDs, or predicts reentry in Conde.
"""
import argparse
import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from tle_literal_layout import audit_pair
# Verbatim lines from the former src/lib/constants.ts on main, Git blob
# 0284f1217557b0ea891b5e51b6ac56bd13529d3f, classified UNVERIFIED.
# A valid mod-10 checksum is NOT an attestation by NORAD.
LEGACY_LINE1 = "1 00528U 63003B   63300.61111111  .00000000  00000-0  00000-0 0  9992"
LEGACY_LINE2 = "2 00528  81.8615 284.1520 0084200 142.3150 218.4210 15.74900000 45124"
LEGACY_BLOB_SHA = "0284f1217557b0ea891b5e51b6ac56bd13529d3f"
EXPECTED_528_CSV_SHA256 = "e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e"

# Upper bounds for decimal text quantization plus the mirror's float32 storage.
# Not observational errors, orbital tolerances, or confidence intervals.
SERIALIZATION_TOLERANCES = {
    "inclination": 0.00008, "raan": 0.00008,
    "eccentricity": 0.00000006, "arg_perigee": 0.00008,
    "mean_anomaly": 0.00008, "mean_motion": 0.000000006,
}
CIRCULAR = {"raan", "arg_perigee", "mean_anomaly"}
LEGACY = {
    "inclination": float(LEGACY_LINE2[8:16]),
    "raan": float(LEGACY_LINE2[17:25]),
    "eccentricity": float("0." + LEGACY_LINE2[26:33]),
    "arg_perigee": float(LEGACY_LINE2[34:42]),
    "mean_anomaly": float(LEGACY_LINE2[43:51]),
    "mean_motion": float(LEGACY_LINE2[52:63]),
}



TLE_EPOCH_HALF_QUANTUM_US = 432
EXPECTED = {527:"1963-003A",528:"1963-003B",529:"1963-003C"}

def normalize_designator(raw):
    import re
    match = re.fullmatch(r"\s*(?:63|1963)[ -]?003[ -]*([A-Z])\s*", raw or "")
    if match is None:
        raise ValueError("unrecognized NORAD/COSPAR designator")
    return "1963-003" + match.group(1)

from tle_mean_motion_secant_audit import (
    COUNTS, DISTINCT, CSV_SHA, IDS, PARQUET_SHA, SOURCE, normalize, read_rows,
)

DEGREE = Decimal(360)
LEGACY_FIELDS = {name: Decimal(str(value)) for name, value in LEGACY.items()}
PRECISION_ONLY = {
    name: Decimal(str(value)) for name, value in SERIALIZATION_TOLERANCES.items()
}
ONE_MICROSECOND = timedelta(microseconds=1)


def circular_delta(a: Decimal, b: Decimal) -> Decimal:
    """Unsigned shortest arc, never a physical change of orbital plane."""
    # Decimal % inherits the sign of a negative dividend in Python.
    # Normalize to [0, 360) before taking the unsigned shortest arc.
    delta = (a - b) % DEGREE
    if delta < 0:
        delta += DEGREE
    return min(delta, DEGREE - delta)


def within_epoch_quantum(a, b) -> bool:
    return abs(a - b) // ONE_MICROSECOND <= TLE_EPOCH_HALF_QUANTUM_US


def compare_record(record, legacy_epoch):
    """One complete record per comparison; never stitch fields across rows."""
    deltas = {
        field: circular_delta(record["values"][field], LEGACY_FIELDS[field])
        if field in CIRCULAR
        else abs(record["values"][field] - LEGACY_FIELDS[field])
        for field in LEGACY_FIELDS
    }
    field_matches = {
        key: delta <= PRECISION_ONLY[key] for key, delta in deltas.items()
    }
    gap_us = abs(record["epoch"] - legacy_epoch) // ONE_MICROSECOND
    return {
        "norad_id": record["sat"],
        "cospar": EXPECTED[record["sat"]],
        "source_rows": record["source_rows"],
        "epoch_utc": record["epoch_literal"],
        "epoch_offset_abs_microseconds": gap_us,
        "same_epoch_within_432us": within_epoch_quantum(record["epoch"], legacy_epoch),
        "delta_by_field": {key: format(v, "f") for key, v in deltas.items()},
        "within_serialization_only": field_matches,
        "matched_fields_in_same_record": sum(field_matches.values()),
        "all_six_fields_match_same_record": all(field_matches.values()),
    }


def audit_cross_catalog(rows, source_sha, *, counts=None, distinct=None):
    syntax = audit_pair(LEGACY_LINE1, LEGACY_LINE2, expected_sat=528)
    legacy_epoch = datetime.fromisoformat(syntax["epoch_utc"].replace("Z", "+00:00"))
    unique, duplicates, observed = normalize(rows, counts=counts, distinct=distinct)
    records = {}
    for record in unique:
        sid = record["sat"]
        if normalize_designator(record["designator"]) != EXPECTED[sid]:
            raise ValueError("NORAD/COSPAR mismatch in secondary source_row")
        records.setdefault(sid, []).append(compare_record(record, legacy_epoch))

    by_catalog = {}
    for sid in IDS:
        candidates = records.get(sid, [])
        nearest_raan = sorted(candidates, key=lambda x: (
            Decimal(x["delta_by_field"]["raan"]),
            x["epoch_utc"], x["source_rows"][0]))
        best_joint = sorted(candidates, key=lambda x: (
            -x["matched_fields_in_same_record"],
            x["epoch_offset_abs_microseconds"], x["source_rows"][0]))
        both = [x for x in candidates if
                x["all_six_fields_match_same_record"] and
                x["same_epoch_within_432us"]]
        by_catalog[str(sid)] = {
            "rows": observed.get(sid, 0),
            "distinct_epochs": len(candidates),
            "all_six_any_epoch_count": sum(
                x["all_six_fields_match_same_record"] for x in candidates),
            "all_six_at_legacy_epoch_count": len(both),
            "same_epoch_only_count": sum(
                x["same_epoch_within_432us"] for x in candidates),
            "closest_raan_same_record": nearest_raan[:2],
            "most_matched_fields_in_one_record": best_joint[:2],
            "same_epoch_candidates": [
                x for x in candidates if x["same_epoch_within_432us"]],
        }

    alternative_matches = sum(
        by_catalog[str(sid)]["all_six_any_epoch_count"] for sid in (527, 529))
    all_matches = sum(
        by_catalog[str(sid)]["all_six_any_epoch_count"] for sid in IDS)
    return {
        "evidence_id": "C241-L8",
        "kind": "SECONDARY_CROSS_CATALOG_FINGERPRINT_NOT_PRIMARY_TRACKING",
        "provenance": {
            "secondary_parquet_url": SOURCE,
            "secondary_parquet_sha256": PARQUET_SHA,
            "derived_csv_sha256": source_sha,
            "pinned_csv_sha256": CSV_SHA,
            "legacy_tle_git_blob_sha1": LEGACY_BLOB_SHA,
            "legacy_checksum_syntax_only": syntax["checksums"],
            "original_norad_pairs_all_45_epochs": "NOT_RECOVERED",
            "instrumental_independence": "NOT_ESTABLISHED",
            "frame_sensor_uncertainty": "NOT_VERIFIED",
        },
        "comparison": {
            "legacy_claimed_norad_id": 528,
            "legacy_epoch_utc": legacy_epoch.isoformat().replace("+00:00", "Z"),
            "legacy_raan_deg": "284.1520",
            "serialization_tolerances_not_orbital_errors": {
                key: format(value, "f") for key, value in PRECISION_ONLY.items()
            },
            "records_scanned": len(rows),
            "distinct_catalog_epochs_scanned": len(unique),
            "duplicates_preserved_by_source_index": duplicates,
            "by_catalog": by_catalog,
            "all_six_any_epoch_all_catalogs": all_matches,
            "all_six_any_epoch_527_or_529": alternative_matches,
            "cross_catalog_copy_hypothesis": (
                "COMPATIBLE_WITH_SECONDARY_NUMBERS_ONLY_NOT_AUTHENTICATED"
                if alternative_matches else
                "NO_SIX_FIELD_MATCH_IN_527_OR_529_PINNED_MIRROR"),
            "full_legacy_vector_any_catalog_hypothesis": (
                "COMPATIBLE_WITH_SECONDARY_NUMBERS_ONLY_NOT_AUTHENTICATED"
                if all_matches else
                "NO_SIX_FIELD_MATCH_IN_PINNED_MIRROR"),
        },
        "limit": (
            "A nearest RAAN or a subset of shared fields never establishes a "
            "transcription path; records at different epochs cannot be combined. "
            "Even a six-field match in 527/529 would not identify the original "
            "issuer, fragment, sensor or reference frame. Quantization tolerances "
            "are not observational uncertainties."
        ),
        "legacy_raan_284_1520_vs_secondary_198_5261": "UNRESOLVED_PRIMARY_ORIGIN",
        "lean_physical_restriction": "NOT_PROMOTED_NO_PRIMARY_FRAME_ERRORS",
        "calibrated_physics_and_holdout": "NOT_RUN",
        "physical_component_528": "NOT_IDENTIFIED_BY_ENGINEERING_RECORD",
        "constraint_link": {
            "state": "CONNECTED_PENDING_CALIBRATION",
            "occurrence": "C241-L8:legacy_fingerprint_per_catalog_epoch",
            "observable_equation": "absolute/circular difference of six elements per complete epoch",
            "reference_frame_historical": None,
            "measurement_sigma": None,
            "sensor_independence": "NOT_ESTABLISHED",
            "candidate_Lean_4_35_0_predicate": "NOT_PROMOTED",
            "physical_parameter_domain_reduced": False,
            "physical_holdout": "NOT_RUN",
        },
        "conde_impact": "INDETERMINATE",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, sha = read_rows(args.csv)
    report = audit_cross_catalog(rows, sha, counts=COUNTS, distinct=DISTINCT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(json.dumps({
        "C241-L8": report["comparison"]["full_legacy_vector_any_catalog_hypothesis"],
        "by_catalog": {k: {
            "epochs": v["distinct_epochs"],
            "six_fields": v["all_six_any_epoch_count"],
            "same_epoch": v["same_epoch_only_count"],
            "nearest_raan": v["closest_raan_same_record"][:1],
        } for k, v in report["comparison"]["by_catalog"].items()},
        "unresolved": report["legacy_raan_284_1520_vs_secondary_198_5261"],
        "conde": report["conde_impact"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
