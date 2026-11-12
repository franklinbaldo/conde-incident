#!/usr/bin/env python3
"""Polvo C241-P1: REAL secondary catalogue RAAN, frozen time holdouts.

Test two PREDECLARED predictive baselines from the FIT block only:
 - last-fit RAAN persistence
 - ordinary least squares constant angular drift, with sequential unwrapping.
Never call this an observational orbit, instrumental holdout or constraint on Conde.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_coepoch_audit import parse_records  # noqa: E402
from raan_chronological_holdout import build_manifest  # noqa: E402

SOURCE = ROOT / "research/statistics/raan_527_528_529_1963.json"
FROZEN = ROOT / "research/statistics/raan_chronological_holdout_1963.json"
SPLITS = ("fit", "validation", "evaluation")
IDS = ("527", "528", "529")
SCHEMA = "conde.secondary-raan-fitonly-drift-control/v1"


def wrap_deg(x: float) -> float:
    if not math.isfinite(x):
        raise ValueError("nonfinite angle")
    return (x + 180.0) % 360.0 - 180.0


def elapsed_days(t: datetime, t0: datetime) -> float:
    return (t - t0).total_seconds() / 86400.0


def fit_only(rows: list[tuple[datetime, float]]) -> dict:
    """Never read validation/evaluation in this function."""
    if len(rows) < 3 or any(a[0] >= b[0] for a, b in zip(rows, rows[1:])):
        raise ValueError("at least three distinct, sorted fit timestamps required")
    first = rows[0][0]
    xs = [elapsed_days(t, first) for t, _ in rows]
    ys = [rows[0][1]]
    for (_, prev), (_, now) in zip(rows, rows[1:]):
        d = wrap_deg(now - prev)
        if abs(d) >= 180 - 1e-9:
            raise ValueError("ambiguous half-turn across fit epoch gap")
        ys.append(ys[-1] + d)
    xm = math.fsum(xs) / len(xs)
    ym = math.fsum(ys) / len(ys)
    den = math.fsum((x - xm) ** 2 for x in xs)
    if den <= 0:
        raise ValueError("time fit has no nonzero span")
    slope = math.fsum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / den
    intercept = ym - slope * xm
    if not (math.isfinite(slope) and math.isfinite(intercept)):
        raise ValueError("unbounded OLS")
    return {
        "origin": first,
        "slope_deg_per_day": slope,
        "intercept_deg_unwrapped": intercept,
        "last_fit_epoch": rows[-1][0],
        "last_fit_raan_deg": rows[-1][1],
        "fit_count": len(rows),
        "largest_fit_angular_step_deg": max(abs(wrap_deg(now[1]-prev[1]))
                                             for prev, now in zip(rows, rows[1:])),
    }


def score(rows: list[tuple[datetime, float]], frozen_model: dict) -> dict:
    if not rows:
        raise ValueError("empty holdout cannot be treated as passing")
    errors = {"persistence": [], "fitonly_linear": []}
    largest_horizon = 0.0
    for t, observed in rows:
        if t <= frozen_model["last_fit_epoch"]:
            raise ValueError("holdout leakage, epoch not after last fit")
        horizon = elapsed_days(t, frozen_model["last_fit_epoch"])
        largest_horizon = max(largest_horizon, horizon)
        static = frozen_model["last_fit_raan_deg"]
        trend = (frozen_model["intercept_deg_unwrapped"] +
                 frozen_model["slope_deg_per_day"] * elapsed_days(t, frozen_model["origin"]))
        errors["persistence"].append(wrap_deg(observed-static))
        errors["fitonly_linear"].append(wrap_deg(observed-trend))
    metrics = {}
    for name, signed in errors.items():
        metrics[name] = {
            "mae_deg": math.fsum(abs(e) for e in signed) / len(signed),
            "rmse_deg": math.sqrt(math.fsum(e * e for e in signed) / len(signed)),
            "max_abs_error_deg": max(abs(e) for e in signed),
            "signed_bias_deg": math.fsum(signed) / len(signed),
            "last_epoch_signed_error_deg": signed[-1],
        }
    return {"n": len(rows), "first_epoch_utc": iso(rows[0][0]),
            "last_epoch_utc": iso(rows[-1][0]),
            "max_horizon_from_last_fit_days": largest_horizon, "models": metrics,
            "linear_better_in_mae": (metrics["fitonly_linear"]["mae_deg"] <
                                     metrics["persistence"]["mae_deg"])}


def iso(t: datetime) -> str:
    return t.isoformat(timespec="microseconds").replace("+00:00", "Z")


def compute(source_bytes: bytes, frozen_bytes: bytes) -> dict:
    source = json.loads(source_bytes)
    frozen = json.loads(frozen_bytes)
    if build_manifest(source_bytes) != frozen:
        raise ValueError("holdout membership/source changed: no refitting allowed")
    if (frozen["design_status"] != "RETROSPECTIVE_TIME_SPLIT_NOT_BLINDED"
        or frozen["independence_status"] !=
            "SAME_SECONDARY_DOCUMENTARY_LINEAGE_NOT_INDEPENDENT"):
        raise ValueError("lineage/custody status changed")
    if source["provenance"]["status"] != "SECONDARY_CATALOGUE_DERIVED_NOT_ORIGINAL_TRACK":
        raise ValueError("not a secondary catalogue")
    grouped, duplicates = parse_records(source)
    report = {
        "schema": SCHEMA,
        "source": {"path": str(SOURCE.relative_to(ROOT)),
                   "exact_bytes_sha256": hashlib.sha256(source_bytes).hexdigest(),
                   "secondary_url": source["provenance"]["source_url"],
                   "evidence_occurrences": ["C25#1", "C179#1", "C180#1", "C181#1", "C241-L3", "C241-P1"],
                   "historical_instrumental_tracking": "NOT_RECOVERED",
                   "same_lineage": True},
        "frozen_split_sha256": hashlib.sha256(frozen_bytes).hexdigest(),
        "method": {"fit_until_exclusive_utc": frozen["boundaries"]["fit_before_utc"],
                   "validation_until_exclusive_utc": frozen["boundaries"]["validation_before_utc"],
                   "evaluation_from_inclusive_utc": frozen["boundaries"]["evaluation_from_utc"],
                   "baseline": "LAST_FIT_RAAN_PERSISTENCE",
                   "comparison": "FIT_ONLY_UNWRAPPED_LINEAR_OLS_NO_HOLDOUT_REFIT",
                   "loss": "CIRCULAR_MAE_RMSE_DEGREES",
                   "status": "RETROSPECTIVE_NOT_BLINDED_SAME_DOCUMENTARY_LINEAGE",
                   "physical_constraint": "NOT_ACTIVATED"},
        "objects": {}
    }
    for norad in IDS:
        by_time = {iso(t): (t, ra) for t, ra in grouped[int(norad)]}
        blocks = {}
        for block in SPLITS:
            keys = frozen["memberships"][norad][block]
            if len(keys) != len(set(keys)) or any(key not in by_time for key in keys):
                raise ValueError("missing/duplicate holdout membership")
            blocks[block] = [by_time[key] for key in keys]
            if blocks[block] != sorted(blocks[block]):
                raise ValueError("split epochs out of sequence")
        model = fit_only(blocks["fit"])
        if (model["last_fit_epoch"] >= datetime(1963, 8, 1, tzinfo=timezone.utc)
            or any(t < datetime(1963, 8, 1, tzinfo=timezone.utc)
                   for block in ("validation", "evaluation") for t, _ in blocks[block])):
            raise ValueError("split chronology broken")
        report["objects"][norad] = {
            "raw_rows": len(grouped[int(norad)]) + duplicates[int(norad)],
            "fit": {"n": model["fit_count"], "first_epoch_utc": iso(model["origin"]),
                    "last_epoch_utc": iso(model["last_fit_epoch"]),
                    "last_fit_raan_deg": model["last_fit_raan_deg"],
                    "linear_slope_deg_per_day": model["slope_deg_per_day"],
                    "linear_intercept_deg_unwrapped": model["intercept_deg_unwrapped"],
                    "largest_fit_angular_step_deg": model["largest_fit_angular_step_deg"]},
            "validation": score(blocks["validation"], model),
            "evaluation": score(blocks["evaluation"], model),
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.check and args.output:
        parser.error("choose --check or --output")
    report = compute(SOURCE.read_bytes(), FROZEN.read_bytes())
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.check:
        if args.check.read_text(encoding="utf-8") != payload:
            raise SystemExit("FAIL: frozen RAAN predictive report does not reproduce")
        print("FROZEN_HOLDOUT_REPRODUCED", {
            sat: {block: round(report["objects"][sat][block]["models"]["fitonly_linear"]["mae_deg"], 6)
                  for block in ("validation", "evaluation")}
            for sat in IDS})
    elif args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
