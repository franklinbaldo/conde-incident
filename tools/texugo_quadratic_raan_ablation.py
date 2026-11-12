#!/usr/bin/env python3
"""Independent quadratic ablation of C241-P2's frozen J2 RAAN comparison.

All models use the identical pinned, secondary-catalogue time split.
This is a model-selection falsifier, NOT a physical orbit or impact forecast.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from cross_object_epoch_support import read_pinned_csv  # noqa: E402
from raan_frozen_j2_holdout import compute as j2_compute  # noqa: E402
from raan_frozen_trend_holdout import (  # noqa: E402
    SOURCE, FROZEN, IDS, elapsed_days, fit_only, iso, wrap_deg,
)
from raan_coepoch_audit import parse_records  # noqa: E402

SCHEMA = "conde.texugo-quadratic-raan-ablation/v1"


def solve_3x3(matrix: list[list[float]], rhs: list[float]) -> tuple[float, float, float]:
    """Partial-pivot elimination on normalized, finite 3x3 least squares."""
    a = [row[:] + [v] for row, v in zip(matrix, rhs)]
    for col in range(3):
        best = max(range(col, 3), key=lambda i: abs(a[i][col]))
        if abs(a[best][col]) < 1e-11:
            raise ValueError("singular quadratic fit")
        a[col], a[best] = a[best], a[col]
        diag = a[col][col]
        for j in range(col, 4):
            a[col][j] /= diag
        for i in range(3):
            if i == col:
                continue
            factor = a[i][col]
            for j in range(col, 4):
                a[i][j] -= factor * a[col][j]
    result = tuple(row[3] for row in a)
    if not all(math.isfinite(v) for v in result):
        raise ValueError("nonfinite quadratic coefficients")
    return result


def fit_quadratic(fit_rows: list[tuple[datetime, float]]) -> dict:
    """Fit only before-cutoff RAAN; sequential unwrap, fixed x scaling."""
    baseline = fit_only(fit_rows)
    last_fit = baseline["last_fit_epoch"]
    origin = baseline["origin"]
    xs = [elapsed_days(t, last_fit) for t, _ in fit_rows]
    scale = max(abs(x) for x in xs)
    if scale <= 0:
        raise ValueError("quadratic epoch span vanished")
    zs = [x / scale for x in xs]
    ys = [fit_rows[0][1]]
    for (_, before), (_, after) in zip(fit_rows, fit_rows[1:]):
        ys.append(ys[-1] + wrap_deg(after - before))
    if any(not math.isfinite(y) for y in ys):
        raise ValueError("nonfinite unwrapped RAAN")
    cols = [[1.0 for _ in zs], zs, [z * z for z in zs]]
    gram = [[math.fsum(x * y for x, y in zip(a, b)) for b in cols] for a in cols]
    rhs = [math.fsum(x * y for x, y in zip(col, ys)) for col in cols]
    coeff = solve_3x3(gram, rhs)
    return {"origin": origin, "last_fit_epoch": last_fit, "fit_n": len(fit_rows),
            "scale_days": scale, "coeff_unwrapped_deg": coeff,
            "baseline_fit": baseline}


def quadratic_predict(model: dict, t: datetime) -> float:
    if t <= model["last_fit_epoch"]:
        raise ValueError("quadratic holdout leakage")
    z = elapsed_days(t, model["last_fit_epoch"]) / model["scale_days"]
    a, b, c = model["coeff_unwrapped_deg"]
    value = a + b * z + c * z * z
    if not math.isfinite(value):
        raise ValueError("quadratic extrapolation nonfinite")
    return value % 360


def metrics(errors: list[float]) -> dict:
    if not errors:
        raise ValueError("empty evaluation")
    return {"n": len(errors),
            "mae_deg": math.fsum(abs(x) for x in errors) / len(errors),
            "rmse_deg": math.sqrt(math.fsum(x*x for x in errors)/len(errors)),
            "max_abs_error_deg": max(abs(x) for x in errors)}


def compute(rows: list[dict], source_bytes: bytes, frozen_bytes: bytes) -> dict:
    """Cross-check the J2 benchmark independently, without reading its output."""
    j2 = j2_compute(rows, source_bytes, frozen_bytes)
    source, frozen = json.loads(source_bytes), json.loads(frozen_bytes)
    parsed, _ = parse_records(source)
    result = {
        "schema": SCHEMA,
        "source": {"primary_instrumental_data": "NOT_RECOVERED",
                   "type": "SECONDARY_MIRROR_ONE_UPSTREAM_LINEAGE",
                   "parquet_sha256": j2["source"]["parquet_sha256"],
                   "csv_sha256": j2["source"]["csv_sha256"],
                   "raan_json_sha256": hashlib.sha256(source_bytes).hexdigest(),
                   "frozen_split_sha256": hashlib.sha256(frozen_bytes).hexdigest(),
                   "occurrences": ["C25#1", "C179#1", "C180#1", "C181#1",
                                   "C241-P1", "C241-P2", "QA-TX-QUAD-01"]},
        "design": {"fit_epoch_cutoff": frozen["boundaries"]["fit_before_utc"],
                   "evaluation_start": frozen["boundaries"]["evaluation_from_utc"],
                   "three_predictors": ["fitonly_linear", "last_fit_j2_proxy",
                                        "fitonly_quadratic"],
                   "model_selection_status": "RETROSPECTIVE_NOT_BLINDED",
                   "validation_used_to_tune": False,
                   "evaluation_used_to_fit": False,
                   "loss": "CIRCULAR_DEGREES",
                   "physical_domain_reduction": "NONE"},
        "objects": {},
    }
    for sat in IDS:
        by_time = {iso(t): (t, ra) for t, ra in parsed[int(sat)]}
        fit = [by_time[key] for key in frozen["memberships"][sat]["fit"]]
        model = fit_quadratic(fit)
        if model["last_fit_epoch"] != datetime.fromisoformat(
                j2["objects"][sat]["anchor"]["anchor_epoch_utc"].replace("Z", "+00:00")):
            raise ValueError("quadratic/J2 training anchor diverged")
        blocks = {}
        for block in ("validation", "evaluation"):
            eval_rows = [by_time[key] for key in frozen["memberships"][sat][block]]
            j2_block = j2["objects"][sat][block]
            expected = [row["epoch_utc"] for row in j2_block["details"]]
            if [iso(t) for t, _ in eval_rows] != expected:
                raise ValueError("quadratic/J2 evaluation epochs diverged")
            quad_errors = [wrap_deg(ra - quadratic_predict(model, t))
                           for t, ra in eval_rows]
            quad = metrics(quad_errors)
            others = {name: j2_block["models"][name] for name in
                      ("fitonly_linear", "last_fit_j2_proxy")}
            blocks[block] = {
                "n": len(eval_rows),
                "models": {**others, "fitonly_quadratic": quad},
                "quadratic_minus_j2_mae_deg": (
                    quad["mae_deg"] - others["last_fit_j2_proxy"]["mae_deg"]),
                "quadratic_minus_linear_mae_deg": (
                    quad["mae_deg"] - others["fitonly_linear"]["mae_deg"]),
                "quadratic_better_than_j2_mae": (
                    quad["mae_deg"] < others["last_fit_j2_proxy"]["mae_deg"]),
                "quadratic_better_than_linear_mae": (
                    quad["mae_deg"] < others["fitonly_linear"]["mae_deg"]),
                "per_epoch": [{"epoch_utc": iso(t),
                               "quadratic_signed_error_deg": quad_errors[i],
                               "j2_signed_error_deg":
                                   j2_block["details"][i]["signed_error_deg"]["last_fit_j2_proxy"]}
                              for i, (t, _) in enumerate(eval_rows)],
            }
        result["objects"][sat] = {
            "fit_n": model["fit_n"], "fit_origin_utc": iso(model["origin"]),
            "last_fit_epoch_utc": iso(model["last_fit_epoch"]),
            "quad_time_scale_days": model["scale_days"],
            "quad_unwrapped_coeff_deg": model["coeff_unwrapped_deg"],
            **blocks,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = compute(read_pinned_csv(args.csv), SOURCE.read_bytes(), FROZEN.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    for sat, item in result["objects"].items():
        d = item["evaluation"]
        print("TEXUGO_QUAD_EVAL", sat, d["n"],
              "QUADRATIC", round(d["models"]["fitonly_quadratic"]["mae_deg"], 6),
              "J2", round(d["models"]["last_fit_j2_proxy"]["mae_deg"], 6),
              "LINEAR", round(d["models"]["fitonly_linear"]["mae_deg"], 6),
              "QUAD_MINUS_J2", round(d["quadratic_minus_j2_mae_deg"], 6))


if __name__ == "__main__":
    main()
