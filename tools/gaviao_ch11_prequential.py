#!/usr/bin/env python3
"""Independent next-epoch 529 audit for C243-T10, not a physical orbit solver.

Input: SHA-pinned secondary oxzoid/Space-Track Parquet, read through Gavião's
previous independent custody reader (never imports Texugo). Uses NumPy SVD to
recompute six estimators at each chronological origin, with explicit skipped
origins, unequal horizons, and horizon-stratified squared loss.

Numbers describe this one secondary time series, not independent instruments,
a future blind prediction, historical reentry coordinates, or Lean premises.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

import numpy as np

from gaviao_ch10_independent import Datum, SOURCE, read_parquet, as_utc

MODELS = ("persistence", "quadratic", "donor528", "shared", "donor527", "linear")
EXPECTED = {"persistence": 0.026903935, "quadratic": 0.074988368,
            "donor528": 0.079369300, "shared": 0.097122160,
            "donor527": 0.116988818, "linear": 0.117357459}
HORIZON_BINS = (("up_to_1d", 1.0), ("1_to_7d", 7.0),
                ("7_to_30d", 30.0), ("over_30d", float("inf")))


def coordinate(when: datetime, origin: datetime) -> float:
    return (when - origin).total_seconds() / (86400.0 * 60.0)


def fit(samples: list[Datum], origin: datetime, degree: int,
        fixed_quadratic: float | None = None) -> tuple[float, float, float]:
    """Least squares via NumPy SVD, independent of Texugo's Gram solver."""
    if len(samples) < 3 or degree not in (1, 2):
        raise ValueError("fewer than three training epochs or invalid degree")
    x = np.array([coordinate(d.epoch, origin) for d in samples], dtype=float)
    y = np.array([d.n for d in samples], dtype=float)
    if degree == 2 and fixed_quadratic is None:
        design = np.column_stack((np.ones_like(x), x, x*x))
        adjusted = y
    elif degree == 1:
        design = np.column_stack((np.ones_like(x), x))
        adjusted = y if fixed_quadratic is None else y - fixed_quadratic*x*x
    else:
        raise ValueError("invalid curvature fit")
    coefficients, _, rank, _ = np.linalg.lstsq(design, adjusted, rcond=None)
    if rank != design.shape[1] or not np.isfinite(coefficients).all():
        raise ValueError("singular or nonfinite SVD fit")
    return (float(coefficients[0]), float(coefficients[1]),
            float(coefficients[2]) if degree == 2 else float(fixed_quadratic or 0.0))


def verify_records(records: list[Datum]) -> dict[int, list[Datum]]:
    by_sat = defaultdict(list)
    seen = set()
    for z in records:
        if z.sat not in (527, 528, 529):
            raise ValueError("unexpected object")
        epoch = as_utc(z.epoch)
        if not math.isfinite(z.n) or z.n <= 0.0:
            raise ValueError("invalid movement mean")
        if (z.sat, epoch) in seen:
            raise ValueError("duplicate same-object epoch")
        seen.add((z.sat, epoch))
        by_sat[z.sat].append(Datum(z.sat, epoch, z.n))
    if any(len(by_sat[s]) == 0 for s in (527, 528, 529)):
        raise ValueError("missing object")
    for rows in by_sat.values():
        rows.sort(key=lambda x: x.epoch)
    return by_sat


def classify_horizon(days: float) -> str:
    if not math.isfinite(days) or days <= 0:
        raise ValueError("nonpositive/nonfinite horizon")
    return next(name for name, maximum in HORIZON_BINS if days <= maximum)


def audit(records: list[Datum]) -> dict:
    by_sat = verify_records(records)
    target = by_sat[529]
    steps = []
    residuals = {name: [] for name in MODELS}
    outcomes = {"quadratic_better": 0, "shared_better": 0, "tie": 0}
    for i in range(1, len(target)):
        origin = target[i-1].epoch
        actual = target[i]
        days = (actual.epoch - origin).total_seconds()/86400.0
        bucket = classify_horizon(days)
        past = {529: target[:i]}
        for donor in (527, 528):
            past[donor] = [d for d in by_sat[donor] if d.epoch <= origin]
        counts = {str(k): len(v) for k, v in past.items()}
        item = {"origin": origin.isoformat(), "target": actual.epoch.isoformat(),
                "horizon_days": days, "horizon_bin": bucket,
                "train_counts": counts, "status": "NOT_RUN"}
        if any(len(v) < 3 for v in past.values()):
            item["reason"] = "insufficient history"
            steps.append(item)
            continue
        try:
            quad = fit(past[529], origin, 2)
            curvature527 = fit(past[527], origin, 2)[2]
            curvature528 = fit(past[528], origin, 2)[2]
            coefficients = {
                "quadratic": quad,
                "donor527": fit(past[529], origin, 1, curvature527),
                "donor528": fit(past[529], origin, 1, curvature528),
                "shared": fit(past[529], origin, 1, (curvature527+curvature528)/2),
                "linear": fit(past[529], origin, 1),
            }
            x = coordinate(actual.epoch, origin)
            pred = {name: float(a + b*x + c*x*x)
                    for name, (a,b,c) in coefficients.items()}
            pred["persistence"] = past[529][-1].n
            errors = {name: actual.n - pred[name] for name in MODELS}
            if not all(math.isfinite(e) for e in errors.values()):
                raise ValueError("nonfinite predictions")
        except (ValueError, OverflowError, np.linalg.LinAlgError) as e:
            item["reason"] = "fit or extrapolation: " + str(e)
            steps.append(item)
            continue
        for name in MODELS:
            residuals[name].append(errors[name])
        delta = abs(errors["quadratic"]) - abs(errors["shared"])
        winner = ("shared_better" if delta > 1e-10 else
                  "quadratic_better" if delta < -1e-10 else "tie")
        outcomes[winner] += 1
        item.update({"status": "SCORED_RETROSPECTIVE", "observed": actual.n,
                     "predictions": pred, "errors": errors, "quadratic_vs_shared": winner})
        steps.append(item)
    scored = [s for s in steps if s["status"] == "SCORED_RETROSPECTIVE"]
    count = len(scored)
    if not count or any(len(v) != count for v in residuals.values()):
        raise ValueError("unpaired or no scored epochs")
    pooled = {name: math.sqrt(math.fsum(e*e for e in residuals[name])/count)
              for name in MODELS}
    strata = {}
    for bucket, _ in HORIZON_BINS:
        subset = [s for s in scored if s["horizon_bin"] == bucket]
        n = len(subset)
        strata[bucket] = {
            "scored": n, "horizon_min_days": min((s["horizon_days"] for s in subset), default=None),
            "horizon_max_days": max((s["horizon_days"] for s in subset), default=None),
            "rmse_rev_day": ({name: math.sqrt(math.fsum(s["errors"][name]**2 for s in subset)/n)
                               for name in MODELS} if n else None)}
    if sum(v["scored"] for v in strata.values()) != count:
        raise AssertionError("stratification lost scored epochs")
    return {"kind": "secondary_catalog_retrospective_prequential_not_orbital",
            "possible_targets": len(steps), "scored": count,
            "not_run": len(steps)-count, "models": MODELS,
            "pooled_rmse_rev_day": pooled, "quad_vs_shared_abs_error_counts": outcomes,
            "horizon_strata": strata, "steps": steps, "independent_instruments": False,
            "blind_prospective": False, "physical_orbital_constraint": False,
            "conclusao_conde": "INDETERMINADO"}


def assert_published_metrics(result: dict) -> None:
    if (result["possible_targets"], result["scored"], result["not_run"]) != (53, 51, 2):
        raise AssertionError("C243-T10 inventory differs")
    if result["quad_vs_shared_abs_error_counts"] != {
            "quadratic_better": 33, "shared_better": 18, "tie": 0}:
        raise AssertionError("C243-T10 paired wins differ")
    for name, expected in EXPECTED.items():
        if abs(result["pooled_rmse_rev_day"][name]-expected) > 0.000002:
            raise AssertionError("C243-T10 RMSE differs for "+name)
    if not (result["pooled_rmse_rev_day"]["persistence"]
            < result["pooled_rmse_rev_day"]["quadratic"]
            < result["pooled_rmse_rev_day"]["shared"]):
        raise AssertionError("published comparison no longer holds")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--parquet", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.parquet:
        raw = args.parquet.read_bytes()
    else:
        with urlopen(SOURCE, timeout=90) as stream:
            raw = stream.read()
    result = audit(read_parquet(raw))
    assert_published_metrics(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="steps"},
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
