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
    """Score exactly paired finite observations; never truncate via zip."""
    if not truth or len(truth) != len(predicted):
        raise ValueError("RMSE exige pares não vazios de mesmo comprimento")
    if not all(math.isfinite(v) for v in truth) or not all(math.isfinite(v) for v in predicted):
        raise ValueError("RMSE exige valores finitos, sem NaN/Inf")
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
        donor527 = fixed_curvature_fit(train[529], c527)
        donor528 = fixed_curvature_fit(train[529], c528)
        linear = polynomial_fit(train[529], 1)
        negative = fixed_curvature_fit(train[529], -shared_c)  # deliberate wrong-sign control
    except ValueError as exc:
        summary["reason"] = str(exc)
        return summary
    xs = [x_at(o.epoch, cutoff) for o in test529]
    ys = [o.mean_motion for o in test529]
    estimates = {"quadratic_529_only": baseline, "shared_curvature_527_528_to_529": joint,
                 "transfer_527_only": donor527, "transfer_528_only": donor528,
                 "linear_529_only": linear, "negative_inverted_curvature": negative}
    summary["coefficients"] = {k: list(v) for k, v in estimates.items()}
    summary["source_curvatures"] = {"527": c527, "528": c528}
    summary["holdout_rmse_rev_day"] = {name: rmse(ys, [project(coeff, x) for x in xs])
                                      for name, coeff in estimates.items()}
    b = summary["holdout_rmse_rev_day"]["quadratic_529_only"]
    j = summary["holdout_rmse_rev_day"]["shared_curvature_527_528_to_529"]
    summary["status"] = "JOINT_BETTER" if j < b - 1e-10 else "BASELINE_BETTER" if b < j - 1e-10 else "TIE"
    diagnostics = summary["holdout_rmse_rev_day"]
    summary["posthoc_ablations"] = {
        "joint_beats_both_individual_donors":
            all(j < diagnostics[f"transfer_{sat}_only"] - 1e-10 for sat in (527, 528)),
        "joint_beats_linear_529": j < diagnostics["linear_529_only"] - 1e-10,
        "joint_beats_inverted_curvature": j < diagnostics["negative_inverted_curvature"] - 1e-10,
        "interpretation": "Post-hoc descriptive diagnostics; NOT preregistered, independent or model selection",
    }
    summary["horizon_days"] = [round((o.epoch - cutoff).total_seconds() / 86400, 6) for o in test529]
    return summary


def overlap_diagnostics(rows: list[Observation], results: list[dict]) -> dict:
    """Count duplicate future 529 epochs across evaluated cutoffs, not independent replications."""
    evaluated = [r["cutoff_utc_end_of_day"] for r in results if r["status"] != "NOT_RUN"]
    future = {
        day: {o.epoch for o in rows if o.sat == 529 and o.epoch > utc(day + "T23:59:59Z")}
        for day in evaluated
    }
    if not evaluated:
        return {"status": "NOT_RUN", "reason": "no evaluable target holdout",
                "no_probability": True}
    counts = {day: len(future[day]) for day in evaluated}
    distinct = set().union(*future.values())
    scored = sum(counts.values())
    shared = {
        f"{a}|{b}": len(future[a] & future[b])
        for i, a in enumerate(evaluated) for b in evaluated[i + 1:]
    }
    return {
        "status": "EVALUATED_POST_HOC",
        "target_norad_id": 529,
        "evaluated_cutoffs": evaluated,
        "future_epochs_per_cutoff": counts,
        "total_scored_epoch_occurrences": scored,
        "distinct_future_epochs": len(distinct),
        "reused_epoch_occurrences": scored - len(distinct),
        "epochs_shared_by_all_evaluated_cutoffs": len(set.intersection(*future.values())),
        "pairwise_overlap_counts": shared,
        "independent_replications_established": False,
        "no_probability": True,
        "interpretation": "Repeated chronological scores reuse one secondary catalog; no independent sensors, p-values or orbital validation",
    }



def disjoint_horizon_diagnostics(rows: list[Observation], results: list[dict]) -> dict:
    """Re-score existing pre-cutoff fits over disjoint future epochs, POST_HOC.

    Earlier evaluations score the same future 529 epochs up to four times.
    Here each epoch belongs to exactly one (cutoff_i, cutoff_i+1]
    window, with the last window unbounded. Fits are never refit on
    any test epoch. Pooled RMSE weights each distinct epoch once.
    Distinct scores do not imply independent sensors or prospective proof.
    """
    target = sorted((o for o in rows if o.sat == 529), key=lambda o: o.epoch)
    if len({o.epoch for o in target}) != len(target):
        raise ValueError("épocas futuras 529 duplicadas")
    by_cutoff = {r["cutoff_utc_end_of_day"]: r for r in results}
    if len(by_cutoff) != len(results):
        raise ValueError("cortes repetidos na avaliação")
    pooled_sq: dict[str, list[float]] = {}
    segments = []
    for i, day in enumerate(CUTOFFS):
        lower = utc(day + "T23:59:59Z")
        next_day = CUTOFFS[i + 1] if i + 1 < len(CUTOFFS) else None
        upper = utc(next_day + "T23:59:59Z") if next_day else None
        future = [o for o in target if o.epoch > lower and (upper is None or o.epoch <= upper)]
        segment = {"training_cutoff": day, "scoring_until_cutoff_inclusive": next_day,
                   "future_count": len(future),
                   "future_epochs_utc": [o.epoch.isoformat() for o in future],
                   "status": "NOT_RUN"}
        fit = by_cutoff.get(day)
        if not future:
            segment["reason"] = "no target observation inside this disjoint interval"
        elif fit is None or fit.get("status") == "NOT_RUN" or "coefficients" not in fit:
            segment["reason"] = "past-only fit unavailable for this cutoff"
        else:
            coeffs = fit["coefficients"]
            xs = [x_at(o.epoch, lower) for o in future]
            ys = [o.mean_motion for o in future]
            squared = {name: [(y - project(coeff, x)) ** 2 for y, x in zip(ys, xs)]
                       for name, coeff in coeffs.items()}
            segment["rmse_rev_day"] = {
                name: rmse(ys, [project(coeff, x) for x in xs])
                for name, coeff in coeffs.items()
            }
            segment["status"] = "EVALUATED_POST_HOC_DISJOINT"
            segment["joint_minus_quadratic_rmse_rev_day"] = (
                segment["rmse_rev_day"]["shared_curvature_527_528_to_529"] -
                segment["rmse_rev_day"]["quadratic_529_only"])
            if pooled_sq and pooled_sq.keys() != squared.keys():
                raise ValueError("modelos inconsistentes entre cortes")
            for name, values in squared.items():
                pooled_sq.setdefault(name, []).extend(values)
        segments.append(segment)
    available = sum(r["future_count"] for r in segments)
    expected = sum(o.epoch > utc(CUTOFFS[0] + "T23:59:59Z") for o in target)
    if available != expected:
        raise ValueError("corte disjunto perdeu ou duplicou épocas do 529")
    scored = sum(r["future_count"] for r in segments if r["status"] != "NOT_RUN")
    if any(len(v) != scored for v in pooled_sq.values()):
        raise ValueError("escores não pareados no agregado disjunto")
    pooled = {name: math.sqrt(math.fsum(errors) / scored)
              for name, errors in pooled_sq.items()} if scored else None
    return {
        "status": "EVALUATED_POST_HOC" if scored else "NOT_RUN",
        "available_unique_future_epochs": available,
        "scored_unique_future_epochs": scored,
        "unscored_unique_future_epochs": available - scored,
        "pooled_rmse_rev_day": pooled,
        "segments": segments,
        "independent_replications_established": False,
        "no_probability": True,
        "interpretation": "Disjoint observation assignments eliminate repeated scoring, "
                          "not single-source dependence; POST_HOC not orbital validation",
    }



def rolling_origin_diagnostics(rows: list[Observation]) -> dict:
    """Retrospective next-529-epoch forecasts; each origin uses strictly past data.

    Previously scored targets enter later fits (prequential, not independent).
    This tests a different horizon, not a physical orbit or a terminal location.
    """
    target = sorted((o for o in rows if o.sat == 529), key=lambda o: o.epoch)
    if len({o.epoch for o in target}) != len(target):
        raise ValueError("rolling: epocas 529 duplicadas")
    donors = {s: sorted((o for o in rows if o.sat == s), key=lambda o: o.epoch)
              for s in (527, 528)}
    names = ("quadratic_529_only", "shared_curvature_527_528_to_529",
             "transfer_527_only", "transfer_528_only", "linear_529_only",
             "persistence_529_last_epoch")
    square_errors = {name: [] for name in names}
    outcomes = {"JOINT_BETTER": 0, "BASELINE_BETTER": 0, "TIE": 0}
    steps = []
    for i in range(1, len(target)):
        past529, future = target[:i], target[i]
        origin = past529[-1].epoch
        horizon = (future.epoch - origin).total_seconds() / 86400
        if horizon <= 0:
            raise ValueError("rolling: horizonte nao positivo")
        donor_past = {s: [o for o in donors[s] if o.epoch <= origin]
                      for s in donors}
        counts = {"527": len(donor_past[527]), "528": len(donor_past[528]),
                  "529": len(past529)}
        step = {"origin_epoch_utc": origin.isoformat(),
                "target_epoch_utc": future.epoch.isoformat(),
                "horizon_days": horizon, "train_counts": counts,
                "status": "NOT_RUN"}
        if min(counts.values()) < 3:
            step["reason"] = "fewer than 3 past epochs for one or more objects"
            steps.append(step)
            continue
        target_train = [(x_at(o.epoch, origin), o.mean_motion) for o in past529]
        donor_train = {s: [(x_at(o.epoch, origin), o.mean_motion)
                           for o in donor_past[s]] for s in donors}
        try:
            c527, c528 = (polynomial_fit(donor_train[s], 2)[2] for s in (527, 528))
            coef = {"quadratic_529_only": polynomial_fit(target_train, 2),
                    "shared_curvature_527_528_to_529":
                        fixed_curvature_fit(target_train, (c527 + c528) / 2),
                    "transfer_527_only": fixed_curvature_fit(target_train, c527),
                    "transfer_528_only": fixed_curvature_fit(target_train, c528),
                    "linear_529_only": polynomial_fit(target_train, 1)}
            xx = x_at(future.epoch, origin)
            forecasts = {name: project(coeff, xx) for name, coeff in coef.items()}
            forecasts["persistence_529_last_epoch"] = past529[-1].mean_motion
            errors = {name: future.mean_motion - v for name, v in forecasts.items()}
            if not all(math.isfinite(v) for v in [*forecasts.values(), *errors.values()]):
                raise ValueError("rolling: nonfinite forecast or error")
            squared = {name: value * value for name, value in errors.items()}
            if not all(math.isfinite(v) for v in squared.values()):
                raise ValueError("rolling: nonfinite squared error")
        except (ValueError, OverflowError) as exc:
            step["reason"] = str(exc)
            steps.append(step)
            continue
        for name in names:
            square_errors[name].append(squared[name])
        b, j = abs(errors["quadratic_529_only"]), abs(errors["shared_curvature_527_528_to_529"])
        result = ("JOINT_BETTER" if j < b - 1e-10 else
                  "BASELINE_BETTER" if b < j - 1e-10 else "TIE")
        outcomes[result] += 1
        step.update({"status": "EVALUATED_RETROSPECTIVE_PREQUENTIAL",
                     "observed_mean_motion_rev_day": future.mean_motion,
                     "predicted_rev_day": forecasts, "error_rev_day": errors,
                     "joint_vs_quadratic": result})
        steps.append(step)
    scored = sum(s["status"] != "NOT_RUN" for s in steps)
    if any(len(e) != scored for e in square_errors.values()):
        raise ValueError("rolling: unpaired model scores")
    pooled = {name: math.sqrt(math.fsum(e) / scored) for name, e in square_errors.items()} if scored else None
    return {"status": "EVALUATED_RETROSPECTIVE_PREQUENTIAL" if scored else "NOT_RUN",
            "target_norad_id": 529,
            "origin_rule": "previous 529 epoch; donor epochs <= origin; predict next 529 epoch",
            "candidate_targets": len(steps), "scored_distinct_targets": scored,
            "skipped_targets": len(steps) - scored, "pooled_rmse_rev_day": pooled,
            "joint_vs_quadratic_one_step_counts": outcomes, "steps": steps,
            "independent_replications_established": False,
            "prospective_validation_established": False, "no_probability": True,
            "interpretation": "POST_HOC single secondary source; earlier scored targets "
                              "join later training. Not physical orbit, p-value or impact inference."}




def rolling_tail_sensitivity_diagnostics(rolling: dict) -> dict:
    """Paired post-hoc target deletions; NO refitting or independence claim.

    Unlike training-epoch exclusions, these remove *scored target epochs*.
    The same six forecasts remain fixed. Every candidate is evaluated on
    exactly the same remaining targets, including overlapping 28-day blocks.
    """
    steps = rolling.get("steps", [])
    selected = [s for s in steps if s["status"] != "NOT_RUN"]
    if not selected:
        return {"status": "NOT_RUN", "reason": "no paired next-epoch forecasts",
                "no_probability": True}
    if any(s["status"] != "EVALUATED_RETROSPECTIVE_PREQUENTIAL" for s in selected):
        raise ValueError("tail sensitivity: unknown scored status")
    declared = rolling.get("pooled_rmse_rev_day")
    required = {"quadratic_529_only", "shared_curvature_527_528_to_529",
                "persistence_529_last_epoch"}
    if not declared or not required.issubset(declared):
        raise ValueError("tail sensitivity: missing paired benchmark models")
    names = tuple(declared)
    scores = []
    seen = set()
    for step in selected:
        epoch = utc(step["target_epoch_utc"])
        if epoch in seen:
            raise ValueError("tail sensitivity: duplicated scored target epoch")
        seen.add(epoch)
        errors = step.get("error_rev_day", {})
        if set(errors) != set(names) or not all(
                isinstance(errors[k], (int, float)) and math.isfinite(errors[k])
                for k in names):
            raise ValueError("tail sensitivity: nonfinite or unpaired errors")
        if not isinstance(step.get("horizon_days"), (int, float)) or (
                not math.isfinite(step["horizon_days"]) or step["horizon_days"] <= 0):
            raise ValueError("tail sensitivity: invalid time horizon")
        scores.append((epoch, errors))
    if len(scores) != rolling.get("scored_distinct_targets"):
        raise ValueError("tail sensitivity: scored inventory differs from rolling origin")
    n = len(scores)
    mae = {}
    medae = {}
    top_sse_share = {}
    top_sse_epoch = {}
    for name in names:
        absolute = sorted(abs(e[name]) for _, e in scores)
        mae[name] = math.fsum(absolute) / n
        mid = n // 2
        medae[name] = (absolute[mid] if n % 2 else
                       (absolute[mid - 1] + absolute[mid]) / 2)
        sse = [e[name] ** 2 for _, e in scores]
        total = math.fsum(sse)
        recomputed_rmse = math.sqrt(total / n)
        if not math.isclose(recomputed_rmse, declared[name], rel_tol=1e-9, abs_tol=1e-10):
            raise ValueError("tail sensitivity: inconsistent pooled RMSE")
        dominant = max(range(n), key=lambda i: sse[i])
        top_sse_share[name] = sse[dominant] / total if total else 0.0
        top_sse_epoch[name] = scores[dominant][0].isoformat() if total else None

    baseline = "quadratic_529_only"
    joint = "shared_curvature_527_528_to_529"

    def winner(survivors: list[tuple]) -> str:
        if not survivors:
            return "NOT_RUN"
        b = math.sqrt(math.fsum(e[baseline] ** 2 for _, e in survivors) / len(survivors))
        j = math.sqrt(math.fsum(e[joint] ** 2 for _, e in survivors) / len(survivors))
        return ("JOINT_BETTER" if j < b - 1e-10 else
                "BASELINE_BETTER" if b < j - 1e-10 else "TIE")

    original = winner(scores)
    single = []
    for i, (epoch, _) in enumerate(scores):
        verdict = winner(scores[:i] + scores[i + 1:])
        single.append((epoch, verdict))
    from datetime import timedelta
    calendar = []
    for anchor, _ in scores:
        remain = [(t, e) for t, e in scores
                  if not (anchor <= t < anchor + timedelta(days=28))]
        calendar.append((anchor, n - len(remain), winner(remain)))
    paired_deltas = [(epoch, e[joint] ** 2 - e[baseline] ** 2) for epoch, e in scores]
    delta_abs_sum = math.fsum(abs(delta) for _, delta in paired_deltas)
    leaders = sorted(paired_deltas, key=lambda item: abs(item[1]), reverse=True)[:3]
    return {
        "status": "EVALUATED_POST_HOC_PAIRED_DELETIONS",
        "scored_distinct_target_epochs": n,
        "original_joint_vs_quadratic": original,
        "model_mae_rev_day": mae,
        "model_median_absolute_error_rev_day": medae,
        "largest_one_target_sse_fraction_by_model": top_sse_share,
        "largest_one_target_sse_epoch_utc_by_model": top_sse_epoch,
        "paired_joint_minus_quadratic_total_sse": math.fsum(d for _, d in paired_deltas),
        "top_three_absolute_paired_sse_contributors": [
            {"target_epoch_utc": epoch.isoformat(),
             "joint_minus_quadratic_squared_error": delta,
             "fraction_of_absolute_paired_sse_differences":
                 abs(delta) / delta_abs_sum if delta_abs_sum else 0.0}
            for epoch, delta in leaders],
        "single_scored_target_deletion": {
            "evaluated": sum(verdict != "NOT_RUN" for _, verdict in single),
            "not_run": sum(verdict == "NOT_RUN" for _, verdict in single),
            "ranking_changes": sum(verdict != original and verdict != "NOT_RUN"
                                   for _, verdict in single),
            "first_three_changes": [
                {"removed_target_epoch_utc": epoch.isoformat(), "remaining_winner": verdict}
                for epoch, verdict in single if verdict != original and verdict != "NOT_RUN"
            ][:3],
        },
        "forward_28_day_scored_target_block_deletion": {
            "calendar_anchors": len(calendar),
            "evaluated": sum(verdict != "NOT_RUN" for _, _, verdict in calendar),
            "not_run": sum(verdict == "NOT_RUN" for _, _, verdict in calendar),
            "ranking_changes": sum(verdict != original and verdict != "NOT_RUN"
                                   for _, _, verdict in calendar),
            "first_three_changes": [
                {"block_start_utc": anchor.isoformat(),
                 "removed_targets": removed, "remaining_winner": verdict}
                for anchor, removed, verdict in calendar
                if verdict != original and verdict != "NOT_RUN"
            ][:3],
        },
        "training_refit_performed": False,
        "independent_replications_established": False,
        "prospective_validation_established": False,
        "no_probability": True,
        "interpretation": "Post-hoc loss concentration and paired target deletions from "
                          "one secondary TLE lineage. Overlapping blocks are not independent "
                          "trials; no physical reconstruction, p-value or impact inference.",
    }

def run(rows: list[Observation]) -> dict:
    results = [evaluate(rows, date) for date in CUTOFFS]
    return {
        "status": "EXPLORATORY_NUMERIC_MIRROR_NOT_ORBITAL_VALIDATION",
        "source_url": EXPECTED_URL, "source_sha256": EXPECTED_SHA256,
        "training_rule": "527,528 and 529 epochs <= cutoff; target 529 > cutoff never used in fitting",
        "models": "quadratic on 529 vs equal-mean 527/528 curvature transferred; post-hoc ablations 527 alone, 528 alone, linear 529, inverted sign; not a physical coupled propagator",
        "no_probability": True,
        "results": results,
        "holdout_overlap": overlap_diagnostics(rows, results),
        "disjoint_holdout": disjoint_horizon_diagnostics(rows, results),
        "rolling_origin_holdout": rolling_origin_diagnostics(rows),
        "rolling_tail_sensitivity": rolling_tail_sensitivity_diagnostics(rolling_origin_diagnostics(rows)),
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
