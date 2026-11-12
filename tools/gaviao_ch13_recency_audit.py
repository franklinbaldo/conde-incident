#!/usr/bin/env python3
"""G13 independent C243-T12 replay. Secondary catalog, not physical data."""
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

SOURCE_URL = "https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/4b4fb3a/data/tle_1963.parquet"
SOURCE_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
DAY = 86400
KNOWN_RMSE = {"secant_2": 0.0109350675, "ols_3": 0.0145442475, "persistence": 0.0269039352}

def validated_rows(rows):
    """Collapse identical duplicates; reject conflicting dates/values."""
    unique = {}
    for sat, epoch, n in rows:
        if sat not in (527, 528, 529):
            continue
        if (not isinstance(epoch, datetime) or epoch.tzinfo is None
                or epoch.utcoffset().total_seconds() != 0 or epoch.year != 1963
                or not isinstance(n, (int, float)) or not math.isfinite(n) or n <= 0):
            raise ValueError("invalid secondary catalog row")
        key = (sat, epoch.astimezone(timezone.utc))
        if key in unique and unique[key] != n:
            raise ValueError("conflicting duplicated catalog epoch")
        unique[key] = n
    groups = {sat: sorted((t, n) for (s, t), n in unique.items() if s == sat)
              for sat in (527, 528, 529)}
    if any(not v for v in groups.values()):
        raise ValueError("missing object in secondary catalog")
    return groups

def recent_forecasts(past, future):
    """Secant and centered OLS independent of Texugo and donor motion."""
    if len(past) < 3 or not past[-3][0] < past[-2][0] < past[-1][0] < future:
        raise ValueError("insufficient or unordered target history")
    horizon = (future - past[-1][0]).total_seconds() / DAY
    delta = (past[-1][0] - past[-2][0]).total_seconds() / DAY
    if delta <= 0 or horizon <= 0:
        raise ValueError("non-positive time interval")
    forecast2 = past[-1][1] + (past[-1][1] - past[-2][1]) * (horizon / delta)
    x = [(t - past[-1][0]).total_seconds() / DAY for t, _ in past[-3:]]
    y = [v for _, v in past[-3:]]
    mx, my = math.fsum(x)/3, math.fsum(y)/3
    spread = math.fsum((z-mx)**2 for z in x)
    if spread <= 0:
        raise ValueError("degenerate OLS times")
    slope = math.fsum((xx-mx)*(yy-my) for xx, yy in zip(x, y)) / spread
    forecast3 = my + slope * (horizon-mx)
    result = {"secant_2": forecast2, "ols_3": forecast3,
              "persistence": past[-1][1]}
    if not all(math.isfinite(v) for v in result.values()):
        raise ValueError("nonfinite prediction")
    return result

def rmse(rows, name):
    return math.sqrt(math.fsum(row["errors"][name]**2 for row in rows) / len(rows)) if rows else None

def audit(rows):
    groups = validated_rows(rows)
    target = groups[529]
    evaluated, not_run = [], []
    for i in range(1, len(target)):
        origin, _ = target[i-1]
        end, truth = target[i]
        donors = {s: sum(t <= origin for t, _ in groups[s]) for s in (527, 528)}
        # Matching the original comparison cohort is NOT autonomous eligibility:
        # the two target-only formulas still rely on donor availability for scoring.
        if min(i, *donors.values()) < 3:
            not_run.append({"target_epoch": end.isoformat(), "reason": "cohort eligibility",
                            "past_529": i, "donor_counts": donors})
            continue
        predictions = recent_forecasts(target[:i], end)
        evaluated.append({
            "target_epoch": end.isoformat(), "origin_epoch": origin.isoformat(),
            "horizon_days": (end - origin).total_seconds() / DAY,
            "observed": truth, "donor_counts": donors,
            "predictions": predictions,
            "errors": {name: truth - forecast for name, forecast in predictions.items()}
        })
    if len({row["target_epoch"] for row in evaluated}) != len(evaluated):
        raise ValueError("reused scored target")
    all_rmse = {name: rmse(evaluated, name) for name in KNOWN_RMSE}
    cohorts = {"<=1d": [], "(1,7]d": [], "(7,30]d": [], ">30d": []}
    for row in evaluated:
        h = row["horizon_days"]
        cohort = "<=1d" if h <= 1 else "(1,7]d" if h <= 7 else "(7,30]d" if h <= 30 else ">30d"
        cohorts[cohort].append(row)
    horizon_scores = {name: {"count": len(part),
                             "rmse_rev_day": {model: rmse(part, model) for model in KNOWN_RMSE}}
                      for name, part in cohorts.items()}
    loo = []
    for i, row in enumerate(evaluated):
        rest = evaluated[:i] + evaluated[i+1:]
        if not rest:
            continue
        scores = {model: rmse(rest, model) for model in KNOWN_RMSE}
        loo.append((scores["secant_2"] < scores["persistence"], scores["secant_2"] < scores["ols_3"]))
    secant_sse = math.fsum(r["errors"]["secant_2"]**2 for r in evaluated)
    largest = max(evaluated, key=lambda r: abs(r["errors"]["secant_2"])) if evaluated else None
    return {
        "record_id": "C243-T12-G13", "source_class": "SECONDARY_CATALOG_NUMERIC",
        "source_sha256": SOURCE_SHA256,
        "unique_epochs_by_object": {str(s): len(x) for s, x in groups.items()},
        "candidate_targets": len(target)-1, "scored": len(evaluated), "not_run": not_run,
        "models_use_only_past_529": True, "cohort_eligibility_depends_on_donor_availability": True,
        "provenance_independence": "SINGLE_SECONDARY_MIRROR",
        "posthoc_window_choice": "T12_DESIGNED_AFTER_T10_T11",
        "rmse_rev_day": all_rmse, "by_horizon": horizon_scores,
        "leave_one_target_out": {"evaluated": len(loo),
            "secant_beats_persistence_in": sum(x[0] for x in loo),
            "secant_beats_ols_3_in": sum(x[1] for x in loo)},
        "largest_secant_squared_error": {
            "target_epoch": largest["target_epoch"],
            "fraction_of_secant_sse": largest["errors"]["secant_2"]**2 / secant_sse,
        } if largest and secant_sse > 0 else None,
        "steps": evaluated,
        "lean_empirical_premise": "NOT_ESTABLISHED",
        "admissible_physical_domain_reduced": False,
        "terminal_simulator_holdout": "NOT_RUN", "conde": "INDETERMINATE"
    }

def load_pinned(path: Path, download: bool):
    if download:
        with urlopen(SOURCE_URL, timeout=60) as response:
            body = response.read()
        if hashlib.sha256(body).hexdigest() != SOURCE_SHA256:
            raise ValueError("Parquet source SHA256 mismatch")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    body = path.read_bytes()
    if (hashlib.sha256(body).hexdigest() != SOURCE_SHA256
            or not body.startswith(b"PAR1") or not body.endswith(b"PAR1")):
        raise ValueError("Parquet verification failed")
    import pyarrow.parquet as pq
    table = pq.read_table(path, columns=["norad_id", "epoch", "mean_motion"])
    return [(r["norad_id"], r["epoch"], float(r["mean_motion"]))
            for r in table.to_pylist() if r["norad_id"] in (527, 528, 529)]

def verify_published(result):
    if result["candidate_targets"] != 53 or result["scored"] != 51 or len(result["not_run"]) != 2:
        raise ValueError("target cohort diverges from C243-T12")
    for model, expected in KNOWN_RMSE.items():
        if abs(result["rmse_rev_day"][model] - expected) > 0.0000005:
            raise ValueError("independent %s RMSE diverges from reported C243-T12" % model)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", type=Path, required=True)
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = audit(load_pinned(args.parquet, args.download))
    verify_published(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "steps"},
                     ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
