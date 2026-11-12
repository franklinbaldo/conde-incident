#!/usr/bin/env python3
"""Adversarial comparison: legacy TLE-looking 528 versus 45 secondary epochs.

Checks checksum separately from provenance. Never reconstructs an original TLE,
never joins fields from different epochs, never predicts orbit or reentry.
"""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from audit_norad_1963 import (
    angular_distance_deg, tle_epoch_utc, validate_raw_tle,
    TLE_EPOCH_HALF_QUANTUM_US,
)

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


def read_528_csv(path: Path, *, enforce_sha=True):
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if enforce_sha and digest != EXPECTED_528_CSV_SHA256:
        raise ValueError("CSV 528 alterado: SHA256 divergente")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"norad_id", "source_row", "epoch"} | set(LEGACY)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV 528 sem colunas obrigatórias")
        rows = list(reader)
    if not rows:
        raise ValueError("CSV 528 vazio")
    seen = set()
    normalized = []
    for row in rows:
        if row["norad_id"] != "528":
            raise ValueError("CSV contaminado com outro satélite")
        index = int(row["source_row"])
        if index in seen:
            raise ValueError("índice físico de origem duplicado")
        seen.add(index)
        stamp = datetime.fromisoformat(row["epoch"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0 or stamp.year != 1963:
            raise ValueError("época não UTC de 1963")
        parsed = {}
        for name in LEGACY:
            value = float(row[name])
            if not math.isfinite(value):
                raise ValueError("campo orbital não finito: " + name)
            parsed[name] = value
        normalized.append({"source_row": index, "epoch_utc": stamp, "fields": parsed})
    return normalized, digest


def fingerprint(rows, source_sha256):
    # Syntactically valid invented-looking lines remain untrusted data.
    syntax = validate_raw_tle(LEGACY_LINE1, LEGACY_LINE2, 528)
    legacy_epoch = tle_epoch_utc(LEGACY_LINE1)
    annotated = []
    for row in rows:
        deltas = {
            name: (angular_distance_deg(value, LEGACY[name]) if name in CIRCULAR
                   else abs(value - LEGACY[name]))
            for name, value in row["fields"].items()
        }
        matches = {
            name: deltas[name] <= SERIALIZATION_TOLERANCES[name]
            for name in LEGACY
        }
        dt_us = abs(row["epoch_utc"] - legacy_epoch) // __import__("datetime").timedelta(microseconds=1)
        annotated.append({
            "source_row": row["source_row"],
            "epoch_utc": row["epoch_utc"].isoformat().replace("+00:00", "Z"),
            "delta_epoch_seconds": dt_us / 1_000_000,
            "delta_by_field": deltas,
            "fields_within_serialization": matches,
            "all_six_within_serialization": all(matches.values()),
            "same_tle_epoch_quantum": dt_us <= TLE_EPOCH_HALF_QUANTUM_US,
        })
    # Sortings never mix orbital elements across observations.
    same_epoch = sorted((x for x in annotated if x["same_tle_epoch_quantum"]),
                        key=lambda x: (x["delta_epoch_seconds"], x["source_row"]))
    closest_raan = sorted(annotated, key=lambda x:
                          (x["delta_by_field"]["raan"], x["epoch_utc"], x["source_row"]))
    closest_ecc = sorted(annotated, key=lambda x:
                         (x["delta_by_field"]["eccentricity"], x["epoch_utc"], x["source_row"]))
    closest_epoch = sorted(annotated, key=lambda x:
                           (x["delta_epoch_seconds"], x["source_row"]))
    whole = [x for x in annotated if x["all_six_within_serialization"]]
    same_epoch_whole = [x for x in same_epoch if x["all_six_within_serialization"]]
    return {
        "source": {
            "legacy_file": "src/lib/constants.ts on main before PR #14",
            "legacy_git_blob_sha1": LEGACY_BLOB_SHA,
            "legacy_class": "UNVERIFIED_LEGACY_CONSTRUCTED_PAIR",
            "secondary_csv_sha256": source_sha256,
            "secondary_parquet_sha256": "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09",
            "tracking_independence": "NOT_ESTABLISHED",
            "source_row_semantics": "0-based physical row index in pinned 1963 Parquet",
        },
        "legacy_tle_checksum": {
            "line1_syntax": "PASS",
            "line2_syntax": "PASS",
            "authenticity": "NOT_VERIFIED",
        },
        "legacy_claim": {
            "epoch_utc_from_literal_line1": legacy_epoch.isoformat().replace("+00:00", "Z"),
            "elements": LEGACY,
            "reference_frame": "NOT_VERIFIED",
        },
        "comparison": {
            "secondary_epoch_count": len({x["epoch_utc"] for x in annotated}),
            "serialization_only_tolerances": SERIALIZATION_TOLERANCES,
            "legacy_same_epoch_candidates": same_epoch,
            "all_six_elements_match_any_epoch_count": len(whole),
            "all_six_match_same_epoch_count": len(same_epoch_whole),
            "closest_by_raan": closest_raan[:3],
            "closest_by_eccentricity": closest_ecc[:3],
            "closest_by_legacy_epoch": closest_epoch[:3],
            "result": "NO_SIX_FIELD_MATCH_IN_SECONDARY_MIRROR" if not whole else
                      "SECONDARY_FIELD_MATCH_WITHOUT_PRIMARY_AUTHENTICATION",
        },
        "epistemic_limit": "Checksum does not prove origin; no recovered raw 1963 NORAD line set, frame, physical identity, or terminal observation. No trajectory or Conde inference.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, digest = read_528_csv(args.csv)
    report = fingerprint(rows, digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    summary = report["comparison"]
    print(json.dumps({
        "csv_sha256": digest, "epochs": summary["secondary_epoch_count"],
        "same_epoch": len(summary["legacy_same_epoch_candidates"]),
        "all_six_any_epoch": summary["all_six_elements_match_any_epoch_count"],
        "nearest_raan": summary["closest_by_raan"][0],
        "status": summary["result"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
