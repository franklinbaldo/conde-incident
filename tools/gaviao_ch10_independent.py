#!/usr/bin/env python3
"""Independent, fail-closed audit of the C243-T8/T9 four-cutoff holdout.

No imports from Texugo; regression uses NumPy least squares rather than the
upstream hand-written normal-equation solver. The same SHA-pinned secondary
Parquet is read directly. This validates a numeric experiment, NOT a 1963
instrumental observation, state vector, Lean physical constraint or impact.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

import numpy as np

SOURCE = "https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/4b4fb3a/data/tle_1963.parquet"
SOURCE_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
CUTS = ("1963-08-31", "1963-09-28", "1963-10-11", "1963-10-21")
EXPECTED_COUNTS = (4, 3, 1, 20)
EXPECTED_Q = (0.010525039, 0.010711596, 0.018127297, 0.223236815)
EXPECTED_J = (0.011014283, 0.009848541, 0.016582726, 0.215116674)
EXPECTED_POOLED = {"quadratic": 0.188775134, "shared": 0.181909995,
                   "donor528": 0.145072060}


@dataclass(frozen=True)
class Datum:
    sat: int
    epoch: datetime
    n: float


def as_utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError("epoch without explicit timezone")
    result = value.astimezone(timezone.utc)
    if result.year != 1963:
        raise ValueError("epoch outside 1963")
    return result


def read_parquet(payload: bytes) -> list[Datum]:
    if hashlib.sha256(payload).hexdigest() != SOURCE_SHA256:
        raise ValueError("Parquet SHA-256 mismatch; refuse numeric claim")
    if payload[:4] != b"PAR1" or payload[-4:] != b"PAR1":
        raise ValueError("invalid Parquet magic")
    import pyarrow.parquet as pq

    table = pq.read_table(io.BytesIO(payload), columns=["norad_id", "epoch", "mean_motion"])
    unique: dict[tuple[int, datetime], Datum] = {}
    for record in table.to_pylist():
        sat = record["norad_id"]
        if sat not in (527, 528, 529):
            continue
        epoch = as_utc(record["epoch"])
        n = float(record["mean_motion"])
        if not math.isfinite(n) or n <= 0:
            raise ValueError("nonfinite / nonpositive mean motion")
        key = (sat, epoch)
        entry = Datum(sat, epoch, n)
        if key in unique and unique[key] != entry:
            raise ValueError("conflicting duplicate epoch")
        unique[key] = entry
    return sorted(unique.values(), key=lambda z: (z.sat, z.epoch))


def cutoff(day: str) -> datetime:
    return datetime.fromisoformat(day + "T23:59:59+00:00")


def coordinate(epoch: datetime, edge: datetime) -> float:
    return (epoch - edge).total_seconds() / (86400.0 * 60)


def regress(samples: list[Datum], edge: datetime, degree: int,
            locked_curvature: float | None = None) -> tuple[float, float, float]:
    """Independent regression via SVD-based least squares, not normal equations."""
    if len(samples) < 3:
        raise ValueError("not enough training records")
    x = np.array([coordinate(z.epoch, edge) for z in samples], dtype=np.float64)
    y = np.array([z.n for z in samples], dtype=np.float64)
    if degree == 2 and locked_curvature is None:
        matrix = np.column_stack((np.ones_like(x), x, x * x))
        rhs = y
    elif degree == 1 and locked_curvature is not None:
        matrix = np.column_stack((np.ones_like(x), x))
        rhs = y - locked_curvature * x * x
    else:
        raise ValueError("unsupported regression")
    coef, _, rank, _ = np.linalg.lstsq(matrix, rhs, rcond=None)
    if rank != matrix.shape[1] or not np.all(np.isfinite(coef)):
        raise ValueError("rank-deficient fit")
    return (float(coef[0]), float(coef[1]),
            float(coef[2]) if locked_curvature is None else locked_curvature)


def validate_and_score(data: list[Datum]) -> dict:
    grouped: dict[int, list[Datum]] = defaultdict(list)
    seen: set[tuple[int, datetime]] = set()
    for d in data:
        if d.sat not in (527, 528, 529) or not math.isfinite(d.n) or d.n <= 0:
            raise ValueError("invalid input datum")
        epoch = as_utc(d.epoch)
        if (d.sat, epoch) in seen:
            raise ValueError("repeated epoch cannot be counted twice")
        seen.add((d.sat, epoch))
        grouped[d.sat].append(Datum(d.sat, epoch, d.n))
    for sat in (527, 528, 529):
        grouped[sat].sort(key=lambda z: z.epoch)
    if any(not grouped[sat] for sat in (527, 528, 529)):
        raise ValueError("one NORAD target/donor missing")

    segments, all_errors = [], defaultdict(list)
    target_future = {d.epoch for d in grouped[529] if d.epoch > cutoff(CUTS[0])}
    assigned = set()
    overlapping_scores = 0
    for i, day in enumerate(CUTS):
        edge = cutoff(day)
        next_edge = cutoff(CUTS[i + 1]) if i + 1 < len(CUTS) else None
        train = {sat: [d for d in grouped[sat] if d.epoch <= edge]
                 for sat in (527, 528, 529)}
        if any(len(train[sat]) < 3 for sat in train):
            raise ValueError("cutoff cannot be fitted on past data")
        for d in grouped[529]:
            if d.epoch > edge:
                overlapping_scores += 1
        test = [d for d in grouped[529] if d.epoch > edge and
                (next_edge is None or d.epoch <= next_edge)]
        if assigned.intersection(d.epoch for d in test):
            raise ValueError("test epoch counted twice")
        assigned.update(d.epoch for d in test)

        quadratic = regress(train[529], edge, 2)
        donor_curvature = [regress(train[sat], edge, 2)[2] for sat in (527, 528)]
        shared = regress(train[529], edge, 1, sum(donor_curvature) / 2)
        solo528 = regress(train[529], edge, 1, donor_curvature[1])
        errors = {}
        for name, coef in (("quadratic", quadratic), ("shared", shared), ("donor528", solo528)):
            squared = []
            for datum in test:
                x = coordinate(datum.epoch, edge)
                prediction = coef[0] + coef[1] * x + coef[2] * x * x
                squared.append((datum.n - prediction) ** 2)
            errors[name] = math.sqrt(math.fsum(squared) / len(test)) if test else None
            all_errors[name].extend(squared)
        segments.append({"after": day, "until": CUTS[i+1] if next_edge else None,
                         "count": len(test), "rmse_rev_day": errors,
                         "training_counts": {str(sat): len(train[sat]) for sat in train}})
    if assigned != target_future:
        raise ValueError("disjoint assignment did not cover all future epochs")
    count = len(assigned)
    pooled = {name: math.sqrt(math.fsum(sq) / count) for name, sq in all_errors.items()}
    sse = {name: math.fsum(sq) for name, sq in all_errors.items()}
    last_shares = {name: segments[-1]["count"] * segments[-1]["rmse_rev_day"][name] ** 2 / sse[name]
                   for name in sse}
    q_last = segments[-1]["count"] * segments[-1]["rmse_rev_day"]["quadratic"] ** 2
    j_last = segments[-1]["count"] * segments[-1]["rmse_rev_day"]["shared"] ** 2
    advantage_sse = sse["quadratic"] - sse["shared"]
    return {"source_kind": "secondary_numeric_mirror_not_original_instrument",
            "cutoffs": CUTS, "overlapping_score_uses": overlapping_scores,
            "unique_future_epochs": count, "segments": segments,
            "pooled_rmse_rev_day": pooled, "last_segment_sse_share": last_shares,
            "last_segment_share_of_sse_advantage": (q_last-j_last)/advantage_sse,
            "no_physical_localization": True, "not_lean_or_impact_evidence": True}


def assert_pinned_result(result: dict) -> None:
    """Fail if underlying historical numbers change, including a silent reader regression."""
    if result["overlapping_score_uses"] != 93 or result["unique_future_epochs"] != 28:
        raise AssertionError("nested holdout inventory changed")
    if tuple(x["count"] for x in result["segments"]) != EXPECTED_COUNTS:
        raise AssertionError("disjoint horizon count changed")
    for i, seg in enumerate(result["segments"]):
        for name, expected in (("quadratic", EXPECTED_Q[i]), ("shared", EXPECTED_J[i])):
            if abs(seg["rmse_rev_day"][name] - expected) > 0.000002:
                raise AssertionError(f"independent regression differs for {i} {name}")
    for name, expected in EXPECTED_POOLED.items():
        if abs(result["pooled_rmse_rev_day"][name] - expected) > 0.000002:
            raise AssertionError(f"pooled {name} differs from pinned table")
    if result["segments"][0]["rmse_rev_day"]["shared"] <= result["segments"][0]["rmse_rev_day"]["quadratic"]:
        raise AssertionError("false claim of universal win")
    if result["last_segment_sse_share"]["quadratic"] <= 0.99:
        raise AssertionError("last segment no longer dominates square loss")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--parquet", type=Path, help="optional already-downloaded original bytes")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    if args.parquet:
        payload = args.parquet.read_bytes()
    else:
        with urlopen(SOURCE, timeout=60) as resp:
            payload = resp.read()
    result = validate_and_score(read_parquet(payload))
    assert_pinned_result(result)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
