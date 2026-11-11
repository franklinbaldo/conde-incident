#!/usr/bin/env python3
"""Blind, reproducible mean-motion holdout; NOT an orbit or impact predictor.

Input is the SHA256-audited numeric mirror produced by audit_norad_1963.py.
Source 527/528 may transfer ONE quadratic curvature coefficient to 529.
All 529 post-cutoff observations remain unseen by every fit. No probabilities.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
EXPECTED_URL = "https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/4b4fb3a/data/tle_1963.parquet"
CUTOFFS = ("1963-08-31", "1963-09-28", "1963-10-11", "1963-10-21")
SATELLITES = (527, 528, 529)
TIME_SCALE_DAYS = 60.0


@dataclass(frozen=True)
class Observation:
    sat: int
    epoch: datetime
    mean_motion: float  # rev / day from secondary numeric TLE mirror


def utc(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
        raise ValueError("UTC explícito obrigatório, sem timestamps ingênuos")
    return result.astimezone(timezone.utc)


def parse_csv(csv_path: Path) -> tuple[list[Observation], list[tuple[int, int, datetime, float]]]:
    """Parse and validate the extracted CSV, retaining its Parquet source-row keys."""
    values: dict[tuple[int, datetime], Observation] = {}
    bindings: list[tuple[int, int, datetime, float]] = []
    with csv_path.open(newline="", encoding="utf-8") as fd:
        for record in csv.DictReader(fd):
            source_row = int(record["source_row"])
            if source_row < 0:
                raise ValueError("source_row negativo")
            sat = int(record["norad_id"])
            if sat not in SATELLITES:
                raise ValueError("satélite inesperado")
            epoch = utc(record["epoch"])
            if epoch.year != 1963:
                raise ValueError("amostra fora de 1963")
            n = float(record["mean_motion"])
            if not math.isfinite(n) or n <= 0:
                raise ValueError("mean motion inválido")
            key = (sat, epoch)
            sample = Observation(sat, epoch, n)
            if key in values and values[key] != sample:
                raise ValueError("duplicatas de época conflitantes")
            values[key] = sample
            bindings.append((source_row, sat, epoch, n))
    for sat in SATELLITES:
        if not any(o.sat == sat for o in values.values()):
            raise ValueError(f"sem observações do objeto {sat}")
    return sorted(values.values(), key=lambda o: (o.sat, o.epoch)), bindings


def source_bindings(parquet_path: Path, audit: dict) -> list[tuple[int, int, datetime, float]]:
    """Independently re-read SHA-pinned bytes, not the extractor's JSON assertions."""
    payload = parquet_path.read_bytes()
    sha256 = hashlib.sha256(payload).hexdigest()
    sha1 = hashlib.sha1(payload).hexdigest()
    if (sha256 != EXPECTED_SHA256 or sha1 != audit["source"]["hashes"].get("sha1")
            or not payload.startswith(b"PAR1") or not payload.endswith(b"PAR1")):
        raise ValueError("custódia: bytes Parquet não conferem com SHA-1/SHA-256")
    import pyarrow.parquet as pq  # only the real-source step requires pyarrow
    expected: list[tuple[int, int, datetime, float]] = []
    for source_row, record in enumerate(
            pq.read_table(parquet_path, columns=["norad_id", "epoch", "mean_motion"]).to_pylist()):
        sat = record["norad_id"]
        if sat not in SATELLITES:
            continue
        epoch = record["epoch"]
        if not isinstance(epoch, datetime) or epoch.tzinfo is None:
            raise ValueError("época do Parquet sem fuso explícito")
        expected.append((source_row, sat, epoch.astimezone(timezone.utc), float(record["mean_motion"])))
    return expected


def require_same_bindings(csv_rows: list[tuple], parquet_rows: list[tuple]) -> None:
    """A matching metadata JSON alone never authenticates a modified/truncated CSV."""
    if Counter(csv_rows) != Counter(parquet_rows):
        raise ValueError("CSV não corresponde a source_row/epoch/mean_motion do Parquet verificado")


def load_audited(csv_path: Path, audit_path: Path, parquet_path: Path) -> list[Observation]:
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    source = audit.get("source", {})
    if source.get("url") != EXPECTED_URL or source.get("hashes", {}).get("sha256") != EXPECTED_SHA256:
        raise ValueError("custódia não confere com o espelho SHA256 fixado")
    if audit.get("problems"):
        raise ValueError("auditoria de entrada registrou anomalias")
    expected = source_bindings(parquet_path, audit)
    rows, bindings = parse_csv(csv_path)
    require_same_bindings(bindings, expected)
    return rows

def solve(a: list[list[float]], b: list[float]) -> tuple[float, ...]:
    """Small pivoted system; reject singular rather than silently regularize."""
    n = len(b)
    rows = [list(a[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda i: abs(rows[i][col]))
        if abs(rows[pivot][col]) < 1e-12:
            raise ValueError("épocas insuficientes ou sistema singular")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        for j in range(col, n + 1):
            rows[col][j] /= divisor
        for i in range(n):
            if i == col:
                continue
            factor = rows[i][col]
            for j in range(col, n + 1):
                rows[i][j] -= factor * rows[col][j]
    return tuple(row[-1] for row in rows)


def polynomial_fit(samples: list[tuple[float, float]], degree: int) -> tuple[float, ...]:
    if degree not in (1, 2) or len(samples) < degree + 1:
        raise ValueError("amostras insuficientes para grau declarado")
    columns = degree + 1
    gram = [[math.fsum(x ** (i + j) for x, _ in samples) for j in range(columns)] for i in range(columns)]
    rhs = [math.fsum(y * x ** i for x, y in samples) for i in range(columns)]
    return solve(gram, rhs)


def x_at(epoch: datetime, cutoff: datetime) -> float:
    return (epoch - cutoff).total_seconds() / (86400 * TIME_SCALE_DAYS)


def project(coeff: tuple[float, ...], x: float) -> float:
    return math.fsum(c * x ** i for i, c in enumerate(coeff))


def fixed_curvature_fit(samples: list[tuple[float, float]], curvature: float) -> tuple[float, ...]:
    intercept, slope = polynomial_fit([(x, y - curvature * x * x) for x, y in samples], 1)
    return intercept, slope, curvature


def rmse(truth: list[float], predicted: list[float]) -> float:
    return math.sqrt(math.fsum((a - b) ** 2 for a, b in zip(truth, predicted)) / len(truth))


def evaluate(rows: list[Observation], cutoff_day: str) -> dict:
    cutoff = utc(cutoff_day + "T23:59:59Z")
    train = {s: [(x_at(o.epoch, cutoff), o.mean_motion) for o in rows if o.sat == s and o.epoch <= cutoff]
             for s in SATELLITES}
    test529 = [o for o in rows if o.sat == 529 and o.epoch > cutoff]
    summary = {"cutoff_utc_end_of_day": cutoff_day, "train_counts": {str(s): len(train[s]) for s in SATELLITES},
               "holdout_529_count": len(test529), "status": "NOT_RUN"}
    if any(len(train[s]) < 3 for s in SATELLITES) or not test529:
        summary["reason"] = "<3 épocas por objeto antes do corte ou nenhuma época 529 posterior"
        return summary
    try:
        baseline = polynomial_fit(train[529], 2)
        c527 = polynomial_fit(train[527], 2)[2]
        c528 = polynomial_fit(train[528], 2)[2]
        shared_c = (c527 + c528) / 2  # equal per-object weight, not per TLE record
        joint = fixed_curvature_fit(train[529], shared_c)
        negative = fixed_curvature_fit(train[529], -shared_c)  # deliberate wrong-sign control
    except ValueError as exc:
        summary["reason"] = str(exc)
        return summary
    xs = [x_at(o.epoch, cutoff) for o in test529]
    ys = [o.mean_motion for o in test529]
    estimates = {"quadratic_529_only": baseline, "shared_curvature_527_528_to_529": joint,
                 "negative_inverted_curvature": negative}
    summary["coefficients"] = {k: list(v) for k, v in estimates.items()}
    summary["source_curvatures"] = {"527": c527, "528": c528}
    summary["holdout_rmse_rev_day"] = {name: rmse(ys, [project(coeff, x) for x in xs])
                                      for name, coeff in estimates.items()}
    b = summary["holdout_rmse_rev_day"]["quadratic_529_only"]
    j = summary["holdout_rmse_rev_day"]["shared_curvature_527_528_to_529"]
    summary["status"] = "JOINT_BETTER" if j < b - 1e-10 else "BASELINE_BETTER" if b < j - 1e-10 else "TIE"
    summary["horizon_days"] = [round((o.epoch - cutoff).total_seconds() / 86400, 6) for o in test529]
    return summary


def run(rows: list[Observation]) -> dict:
    return {
        "status": "EXPLORATORY_NUMERIC_MIRROR_NOT_ORBITAL_VALIDATION",
        "source_url": EXPECTED_URL, "source_sha256": EXPECTED_SHA256,
        "training_rule": "527,528 and 529 epochs <= cutoff; target 529 > cutoff never used in fitting",
        "models": "quadratic on 529 vs per-object equal-mean 527/528 curvature transferred to 529; not a physical coupled propagator",
        "no_probability": True,
        "results": [evaluate(rows, date) for date in CUTOFFS],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--parquet", required=True, type=Path,
                        help="bytes originais SHA256-pinned, para conferir cada linha do CSV")
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = run(load_audited(args.csv, args.audit, args.parquet))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"source_sha256": EXPECTED_SHA256, "cuts": [{"date": r["cutoff_utc_end_of_day"],
          "status": r["status"], "train": r["train_counts"], "holdout": r["holdout_529_count"],
          "rmse": r.get("holdout_rmse_rev_day"), "reason": r.get("reason")}
          for r in result["results"]]}, ensure_ascii=False))
    if all(r["status"] == "NOT_RUN" for r in result["results"]):
        raise SystemExit("No evaluable cutoff; see output JSON")


if __name__ == "__main__":
    main()
