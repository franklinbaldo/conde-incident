#!/usr/bin/env python3
"""C241-T9. Line1 n-dot/BSTAR provenance audit; no physical drag inference."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from tle_literal_layout import audit_literal_file

PARQUET_SHA = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
CSV_SHA = "3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231"
PAIR_SHA = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
COUNTS = {527: 21, 528: 45, 529: 57}
NDOT_TOL = Decimal("0.00000001")  # serialization only
BSTAR_TOL = Decimal("0.000000000001")  # serialization only


def implicit_exponent(token):
    if re.fullmatch(r"[ +\-][0-9]{5}[+\-][0-9]", token, re.ASCII) is None:
        raise ValueError("invalid TLE implicit-exponent field")
    sign = -1 if token[0] == "-" else 1
    return sign * Decimal("0." + token[1:6]) * (Decimal(10) ** int(token[-2:]))


def read_csv(path, enforce_sha=True):
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if enforce_sha and sha != CSV_SHA:
        raise ValueError("pinned CSV SHA256 mismatch")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = {"source_row", "norad_id", "epoch", "mean_motion_dot", "bstar"}
        if not fields.issubset(reader.fieldnames or []):
            raise ValueError("missing n-dot/BSTAR custody fields")
        return list(reader), sha


def validate_rows(raw_rows, expected_counts=None):
    seen, output = set(), []
    for raw in raw_rows:
        try:
            sid, idx = int(raw["norad_id"]), int(raw["source_row"])
            if sid not in COUNTS or raw["norad_id"] != str(sid):
                raise ValueError("unexpected catalog")
            if idx < 0 or idx in seen or str(idx) != raw["source_row"]:
                raise ValueError("duplicate/invalid source_row")
            seen.add(idx)
            stamp_string = raw["epoch"]
            epoch = datetime.fromisoformat(stamp_string.replace("Z", "+00:00"))
            if (not stamp_string.endswith("Z") or epoch.year != 1963 or
                    epoch.utcoffset() != timedelta(0)):
                raise ValueError("invalid UTC 1963 epoch")
            values = {key: Decimal(str(raw[key]))
                      for key in ("mean_motion_dot", "bstar")}
            if not all(x.is_finite() for x in values.values()):
                raise ValueError("nonfinite derivative or BSTAR")
        except (KeyError, TypeError, InvalidOperation, AttributeError) as exc:
            raise ValueError("invalid/missing catalog custody field") from exc
        output.append({"norad_id": sid, "source_row": idx, "epoch": epoch,
                       **values})
    if not output:
        raise ValueError("empty numeric corpus")
    if expected_counts is not None and dict(Counter(x["norad_id"] for x in output)) != expected_counts:
        raise ValueError("pinned counts changed")
    return sorted(output, key=lambda r: (r["norad_id"], r["epoch"], r["source_row"]))


def audit(rows, pair, source_csv_sha, expected_counts=None):
    rows = validate_rows(rows, expected_counts)
    if (pair["catalog"] != 528 or pair["source"]["sha256"] != PAIR_SHA or
            pair["primary_norad_1963_provenance"] != "NOT_VERIFIED"):
        raise ValueError("literal pair or provenance mismatch")
    epoch = datetime.fromisoformat(pair["epoch_utc"].replace("Z", "+00:00"))
    same = [r for r in rows if r["norad_id"] == 528 and
            abs((r["epoch"] - epoch) // timedelta(microseconds=1)) <= 432]
    if len(same) != 1:
        raise ValueError("missing or ambiguous same-epoch 528")
    row = same[0]
    fields = pair["line1_other_fields"]
    half = Decimal(fields["mean_motion_first_derivative_half"].strip())
    ddot = implicit_exponent(fields["mean_motion_second_derivative_sixth"])
    bstar = implicit_exponent(fields["bstar"])
    ndot = row["mean_motion_dot"]
    matched = {
        "as_tle_encoded_half": abs(ndot - half) <= NDOT_TOL,
        "as_twice_tle_field": abs(ndot - 2 * half) <= NDOT_TOL,
    }
    if all(matched.values()):
        scale = "NON_DISCRIMINATING_ZERO_OR_ROUNDING"
    elif matched["as_tle_encoded_half"]:
        scale = "MATCHES_TLE_ENCODED_HALF"
    elif matched["as_twice_tle_field"]:
        scale = "MATCHES_TWICE_TLE_FIELD"
    else:
        scale = "NEITHER_CONVENTION_MATCHES"
    summary = {}
    for sid in COUNTS:
        subset = [r for r in rows if r["norad_id"] == sid]
        summary[str(sid)] = {
            "rows": len(subset), "unique_epochs": len({r["epoch"] for r in subset}),
            "n_dot_zero": sum(r["mean_motion_dot"] == 0 for r in subset),
            "n_dot_nonzero": sum(r["mean_motion_dot"] != 0 for r in subset),
            "bstar_zero": sum(r["bstar"] == 0 for r in subset),
            "bstar_nonzero": sum(r["bstar"] != 0 for r in subset),
            "n_dot_range": [str(min(r["mean_motion_dot"] for r in subset)),
                            str(max(r["mean_motion_dot"] for r in subset))] if subset else [],
            "bstar_range": [str(min(r["bstar"] for r in subset)),
                            str(max(r["bstar"] for r in subset))] if subset else [],
        }
    return {
        "status": "SECONDARY_NUMERIC_LINE1_CUSTODY_ONLY",
        "provenance": {
            "original_1963_norad_lines": "NOT_RECOVERED",
            "independent_tracking": "NOT_ESTABLISHED",
            "source_parquet_url": "https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/4b4fb3a/data/tle_1963.parquet",
            "parquet_sha256": PARQUET_SHA,
            "derived_csv_sha256": source_csv_sha,
            "literal_pair_sha256": PAIR_SHA,
            "format_reference": "https://celestrak.org/columns/v04n03/",
            "dataset_schema": "https://huggingface.co/datasets/oxzoid/space-track-tle-history",
        },
        "rows": len(rows), "by_norad": summary,
        "same_epoch_528": {
            "source_row": row["source_row"], "epoch_utc": pair["epoch_utc"],
            "literal_n_dot_over_two": str(half), "twice_literal_field": str(2 * half),
            "parquet_mean_motion_dot": str(ndot), "matches": matched,
            "numeric_scale_test": scale,
            "literal_n_ddot_over_six": str(ddot),
            "parquet_n_ddot_over_six": "COLUMN_ABSENT",
            "literal_bstar": str(bstar), "parquet_bstar": str(row["bstar"]),
            "bstar_matches": abs(row["bstar"] - bstar) <= BSTAR_TOL,
            "n_dot_tolerance_serialization_only_rev_day2": str(NDOT_TOL),
            "bstar_tolerance_serialization_only": str(BSTAR_TOL),
        },
        "limit": ("n-dot/2 printed in TLE is not the full physical derivative; "
                  "Parquet column convention requires audit. BSTAR zero is not "
                  "proof of zero drag. No primary NORAD lines, sensor/frame/errors, "
                  "mass, material, validated propagation or impact coordinates."),
        "lean_physical_premise": "NOT_PROMOTED",
        "calibrated_simulation_holdout": "NOT_RUN",
        "raan_conflict": "UNRESOLVED_PRIMARY_ORIGIN",
        "conde": "INDETERMINATE",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--pair", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows, sha = read_csv(args.csv)
    report = audit(rows, audit_literal_file(args.pair), sha, expected_counts=COUNTS)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True,
                                      ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"rows": report["rows"], "by_norad": report["by_norad"],
                      "comparison": report["same_epoch_528"],
                      "lean": report["lean_physical_premise"]}, sort_keys=True))


if __name__ == "__main__":
    main()
