#!/usr/bin/env python3
"""Cervo: descriptive circular RAAN co-epoch audit, NOT orbital fitting/MCMC.

Scientific source is a secondary Space-Track mirror, not original observations.
This module deliberately never transports an orbit to a different epoch.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from statistics import median

WINDOWS_MIN = (10, 60, 360, 1440)
PAIR_IDS = ((527, 528), (528, 529), (527, 529))
SCHEMA = "conde.raan-secondary-catalogue-snapshot/v1"


def circular_difference_deg(a: float, b: float) -> float:
    """Signed minimal angular displacement a-b, [-180,180)."""
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError("nonfinite RAAN")
    return (a - b + 180.0) % 360.0 - 180.0


def parse_records(document: dict) -> tuple[dict[int, list[tuple[datetime, float]]], dict[int, int]]:
    if document.get("schema") != SCHEMA:
        raise ValueError("unsupported or missing snapshot schema")
    provenance = document.get("provenance")
    if not isinstance(provenance, dict) or not provenance.get("source_url") or not provenance.get("claimed_parquet_sha256_from_preexisting_extract"):
        raise ValueError("source and provenance mandatory")
    if provenance.get("status") != "SECONDARY_CATALOGUE_DERIVED_NOT_ORIGINAL_TRACK":
        raise ValueError("unexpected source status")
    rows = document.get("records")
    if not isinstance(rows, list) or not rows:
        raise ValueError("empty records")
    result: dict[int, list[tuple[datetime, float]]] = {k: [] for k in (527, 528, 529)}
    seen = {}
    duplicates: dict[int, int] = {k: 0 for k in result}
    for row in rows:
        if not isinstance(row, dict) or row.get("norad") not in result or isinstance(row.get("norad"), bool):
            raise ValueError("unexpected NORAD ID")
        epoch = row.get("epoch_utc")
        if not isinstance(epoch, str) or not epoch.endswith("Z"):
            raise ValueError("epoch must be explicit UTC Z")
        try:
            dt = datetime.fromisoformat(epoch[:-1] + "+00:00")
        except ValueError as error:
            raise ValueError("invalid timestamp") from error
        if dt.tzinfo != timezone.utc:
            raise ValueError("timestamp must be UTC")
        ra = row.get("raan_deg")
        if not isinstance(ra, (int, float)) or isinstance(ra, bool) or not math.isfinite(ra) or not (0 <= ra < 360):
            raise ValueError("invalid RAAN degrees")
        key = (row["norad"], dt)
        if key in seen:
            if seen[key] != float(ra):
                raise ValueError("conflicting RAAN values for one object/epoch")
            # Duplicate raw rows are not an independent datum. Retain count.
            duplicates[row["norad"]] += 1
            continue
        seen[key] = float(ra)
        result[row["norad"]].append((dt, float(ra)))
    for items in result.values():
        items.sort(key=lambda x: x[0])
    return result, duplicates


def match_epochs(left: list[tuple[datetime, float]], right: list[tuple[datetime, float]],
                 window_s: float) -> list[dict]:
    """One-to-one nearest-time greedy matching, with NO physical propagation.

    Greedy is a deterministic descriptive matching rule, not a globally optimal
    orbit association nor a statistical claim of independent measurements.
    """
    if not math.isfinite(window_s) or window_s < 0:
        raise ValueError("invalid window")
    candidates = []
    for i, (ta, _) in enumerate(left):
        for j, (tb, _) in enumerate(right):
            delay = abs((ta - tb).total_seconds())
            if delay <= window_s:
                candidates.append((delay, ta, tb, i, j))
    candidates.sort()
    matched_left, matched_right = set(), set()
    out = []
    for dt, ta, tb, i, j in candidates:
        if i in matched_left or j in matched_right:
            continue
        matched_left.add(i)
        matched_right.add(j)
        diff = circular_difference_deg(left[i][1], right[j][1])
        out.append({
            "left_utc": ta.isoformat().replace("+00:00", "Z"),
            "right_utc": tb.isoformat().replace("+00:00", "Z"),
            "delta_t_s": round(dt, 6),
            "delta_raan_deg_signed": round(diff, 8),
            "abs_delta_raan_deg": round(abs(diff), 8),
        })
    return sorted(out, key=lambda r: (r["left_utc"], r["right_utc"]))


def report(document: dict) -> dict:
    grouped, duplicates = parse_records(document)
    cases = []
    for a, b in PAIR_IDS:
        for minutes in WINDOWS_MIN:
            matches = match_epochs(grouped[a], grouped[b], minutes * 60)
            cases.append({
                "left": a, "right": b, "window_minutes": minutes,
                "count": len(matches),
                "median_abs_epoch_gap_s": round(median(r["delta_t_s"] for r in matches), 6) if matches else None,
                "median_abs_circular_raan_difference_deg": round(
                    median(r["abs_delta_raan_deg"] for r in matches), 8
                ) if matches else None,
                "earliest_pair": matches[0] if matches else None,
                "latest_pair": matches[-1] if matches else None,
            })
    return {
        "schema":"conde.raan-coepoch-audit/v1",
        "source":document["provenance"],
        "raw_rows_per_object":{str(k):len(v)+duplicates[k] for k,v in grouped.items()},
        "unique_epochs_per_object":{str(k):len(v) for k,v in grouped.items()},
        "exact_duplicate_epoch_rows_per_object":{str(k):duplicates[k] for k in grouped},
        "raw_total_rows":sum(len(v)+duplicates[k] for k,v in grouped.items()),
        "unique_epoch_total":sum(len(v) for v in grouped.values()),
        "method":"one-to-one minimum-epoch-gap greedy pairs; no dynamic transport, no covariance, no likelihood",
        "unmatched_samples_are_not_negative_observations":True,
        "cases":cases,
        "inference_status":"DESCRIPTIVE_ONLY_NOT_POSTERIOR",
        "physical_domain_reduction":"NOT_RUN_NO_FRAME_ERROR_OR_EPOCH_PROPAGATION",
    }


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--check", type=Path, help="Fail if frozen report differs from generated report")
    args=ap.parse_args()
    if args.output and args.check:
        ap.error("choose --output or --check")
    result=report(json.loads(args.input.read_text()))
    payload=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if args.check:
        if args.check.read_text()!=payload:
            raise SystemExit("stale or mismatched report")
    elif args.output:
        args.output.parent.mkdir(exist_ok=True,parents=True)
        args.output.write_text(payload)
    else:
        print(payload,end="")


if __name__ == "__main__":
    main()
