#!/usr/bin/env python3
"""C241-T11: mean-motion secants vs. encoded n-dot in a SECONDARY TLE mirror.

No original line1/line2, calibrated force model, physical derivative,
independent tracking, or terminal reentry is inferred by this arithmetic.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

SOURCE = "https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet"
PARQUET_SHA = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
CSV_SHA = "3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231"
IDS = (527, 528, 529)
COUNTS = {527: 21, 528: 45, 529: 57}
DISTINCT = {527: 20, 528: 45, 529: 54}
US = timedelta(microseconds=1)
DAY_US = 86_400_000_000
NUMERIC = ("inclination", "raan", "eccentricity", "arg_perigee",
           "mean_anomaly", "mean_motion", "mean_motion_dot", "bstar")
REQUIRED = {"source_row", "norad_id", "epoch", "intl_designator", *NUMERIC}


def read_rows(path: Path, enforce_sha=True):
    payload = path.read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    if enforce_sha and sha != CSV_SHA:
        raise ValueError("pinned secondary CSV SHA256 mismatch")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError("missing custody CSV columns")
        rows = list(reader)
    return rows, sha


def normalize(rows, *, counts=None, distinct=None):
    parsed, source_ids = [], set()
    for row in rows:
        try:
            ix, sid = int(row["source_row"]), int(row["norad_id"])
            if (ix < 0 or row["source_row"] != str(ix) or ix in source_ids or
                    sid not in IDS or row["norad_id"] != str(sid)):
                raise ValueError("invalid/duplicate source_row or catalog")
            source_ids.add(ix)
            original_epoch = row["epoch"]
            epoch = datetime.fromisoformat(original_epoch.replace("Z", "+00:00"))
            midnight = epoch.replace(hour=0, minute=0, second=0, microsecond=0)
            if (not original_epoch.endswith("Z") or epoch.year != 1963 or
                    epoch.utcoffset() != timedelta(0) or
                    ((epoch - midnight) // US) % 864):
                raise ValueError("invalid 1963 UTC TLE epoch grid")
            values = {k: Decimal(row[k]) for k in NUMERIC}
            if not all(x.is_finite() for x in values.values()):
                raise ValueError("nonfinite numeric field")
            if values["mean_motion"] <= 0:
                raise ValueError("mean_motion must be positive rev/day")
            designator = row["intl_designator"]
            if not isinstance(designator, str) or not designator.strip():
                raise ValueError("missing international designator")
        except (KeyError, TypeError, AttributeError, InvalidOperation) as exc:
            raise ValueError("invalid custody CSV field") from exc
        parsed.append({"index": ix, "sat": sid, "epoch": epoch,
                       "epoch_literal": original_epoch, "values": values,
                       "designator": designator})
    if not parsed:
        raise ValueError("empty numeric mirror")
    observed = dict(Counter(x["sat"] for x in parsed))
    if counts is not None and observed != counts:
        raise ValueError("pinned catalog row counts changed")
    grouped = {}
    for row in parsed:
        grouped.setdefault((row["sat"], row["epoch"]), []).append(row)
    unique, duplicates = [], {}
    for (sid, epoch), group in sorted(grouped.items()):
        first = group[0]
        if any(x["values"] != first["values"] or
               x["designator"] != first["designator"] for x in group[1:]):
            raise ValueError("contradictory same-epoch catalog state")
        indices = sorted(x["index"] for x in group)
        if len(indices) > 1:
            duplicates[f"{sid}:{first['epoch_literal']}"] = indices
        unique.append({**first, "source_rows": indices})
    observed_distinct = dict(Counter(x["sat"] for x in unique))
    if distinct is not None and observed_distinct != distinct:
        raise ValueError("pinned distinct epoch counts changed")
    return unique, duplicates, observed


def fmt(x):
    return format(x, "f")


def interval(first, last):
    microseconds = (last["epoch"] - first["epoch"]) // US
    if microseconds <= 0:
        raise ValueError("non-increasing catalog epoch")
    days = Decimal(microseconds) / Decimal(DAY_US)
    n1, n2 = first["values"]["mean_motion"], last["values"]["mean_motion"]
    d1, d2 = first["values"]["mean_motion_dot"], last["values"]["mean_motion_dot"]
    delta = n2 - n1
    # Explicitly conditional: T9 identified encoded n-dot/2 at ONE 528 epoch.
    # It did NOT authenticate this convention at all 123 numerical records.
    naive_delta = days * (d1 + d2)
    return {
        "source_rows_earlier": first["source_rows"],
        "source_rows_later": last["source_rows"],
        "epoch_earlier_utc": first["epoch_literal"],
        "epoch_later_utc": last["epoch_literal"],
        "gap_microseconds": microseconds,
        "gap_days": fmt(days),
        "delta_mean_motion_rev_day": fmt(delta),
        "secant_rev_day2": fmt(delta / days),
        "encoded_half_dot_endpoints_rev_day2": [fmt(d1), fmt(d2)],
        "naive_midpoint_delta_rev_day": fmt(naive_delta),
        "naive_midpoint_residual_rev_day": fmt(delta - naive_delta),
        "positive_encoded_dots_but_decreasing_n": bool(d1 > 0 and d2 > 0 and delta < 0),
        "interpretation": "SECANT_OF_DISTINCT_CATALOG_FITS_NOT_MEASURED_DERIVATIVE",
    }


def summary(intervals, limit_days=None):
    selection = [x for x in intervals
                 if limit_days is None or
                 Decimal(x["gap_days"]) <= Decimal(limit_days)]
    residuals = [abs(Decimal(x["naive_midpoint_residual_rev_day"])) for x in selection]
    return {
        "pairs": len(selection),
        "positive_dots_but_decreasing_n": sum(
            x["positive_encoded_dots_but_decreasing_n"] for x in selection),
        "naive_mean_abs_residual_rev_day":
            fmt(sum(residuals) / Decimal(len(residuals))) if residuals else None,
        "model_status": "UNCALIBRATED_DIAGNOSTIC_NOT_HOLDOUT",
    }


def audit(rows, source_sha, *, counts=None, distinct=None):
    unique, duplicates, observed = normalize(rows, counts=counts, distinct=distinct)
    result, total = {}, []
    for sid in IDS:
        elements = [x for x in unique if x["sat"] == sid]
        pairs = [interval(x, y) for x, y in zip(elements, elements[1:])]
        total.extend(pairs)
        result[str(sid)] = {
            "raw_rows": observed.get(sid, 0), "distinct_epochs": len(elements),
            "up_to_24h": summary(pairs, 1),
            "up_to_72h": summary(pairs, 3),
            "all_intervals": summary(pairs),
            "per_adjacent_epoch": pairs,
        }
    return {
        "evidence_id": "C241-T11",
        "status": "SECONDARY_NUMERIC_INTERNAL_CONTROL_ONLY",
        "provenance": {
            "parquet_url": SOURCE,
            "parquet_sha256": PARQUET_SHA,
            "derived_csv_sha256": source_sha,
            "primary_1963_TLE_pairs": "NOT_RECOVERED",
            "reference_frame_sensor_errors": "NOT_VERIFIED",
            "instrumental_independence": "NOT_ESTABLISHED"},
        "raw_rows": len(rows), "distinct_epochs": len(unique),
        "duplicate_epoch_source_rows_not_independent": duplicates,
        "global": summary(total), "by_norad": result,
        "conditional_scale": "T9_HALF_DOT_MATCH_ONLY_AT_ONE_528_EPOCH",
        "interpretive_limit": (
            "A comparison across epochs of separately fitted catalog mean-motion "
            "parameters is NOT a physical derivative or measurement of atmospheric "
            "drag. The illustrative midpoint rule assumes the n-dot/2 convention "
            "at every epoch and a smooth rate between observations. Neither "
            "assumption has been validated for original 1963 NORAD material."),
        "lean_4_35_physical_restriction": "NOT_PROMOTED_NO_PRIMARY_FRAME_ERRORS",
        "validated_simulation_or_holdout": "NOT_RUN",
        "raan_198_5261_vs_284_1520": "UNRESOLVED_PRIMARY_ORIGIN",
        "conde": "INDETERMINATE",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    rows, sha = read_rows(args.csv)
    report = audit(rows, sha, counts=COUNTS, distinct=DISTINCT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps({
        "id": report["evidence_id"], "global": report["global"],
        "catalogs": {k: {"raw_rows": v["raw_rows"],
                         "up_to_72h": v["up_to_72h"]}
                     for k, v in report["by_norad"].items()},
        "lean": report["lean_4_35_physical_restriction"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
