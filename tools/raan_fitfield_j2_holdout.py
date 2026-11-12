#!/usr/bin/env python3
"""C241-P3: FIT-ONLY secular drift of TLE mirror fields inside integrated J2.

This is a secondary catalogue consistency experiment. Neither the numerical
integrator nor the fit-only field drift is an observed force or sensor error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "formal" / "scripts")]

from cross_object_epoch_support import (  # noqa: E402
    EXPECTED_CSV_SHA256, FIELDS, SOURCE_SHA256, SOURCE_URL,
    normalize, read_pinned_csv,
)
from audit_secondary_j2_raan import j2_nodal_deg_day  # noqa: E402
from raan_coepoch_audit import parse_records  # noqa: E402
from raan_frozen_j2_holdout import (  # noqa: E402
    MAX_RAAN_SERIALIZATION_DELTA_DEG, align_rows,
    compute as p2_compute,
)
from raan_frozen_trend_holdout import (  # noqa: E402
    IDS, SPLITS, FROZEN, SOURCE, elapsed_days, iso, wrap_deg,
)
from raan_chronological_holdout import build_manifest  # noqa: E402

SCHEMA = "conde.secondary-fitfield-j2-outoftime/v1"
FIELDS_TO_DRIFT = ("inclination", "eccentricity", "mean_motion")
MAX_NUMERICAL_REFINEMENT_DEG = 0.00001  # solver convergence only, NOT sensor sigma
STEP_DAYS = 0.25  # fixed before any validation/evaluation inspection


def slope_fit_only(times: list[float], values: list[float]) -> float:
    if len(times) < 3 or len(times) != len(values):
        raise ValueError("at least three FIT times required")
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("unordered or repeated FIT epochs")
    x0 = math.fsum(times) / len(times)
    y0 = math.fsum(values) / len(values)
    den = math.fsum((x-x0)**2 for x in times)
    if den <= 0 or not math.isfinite(den):
        raise ValueError("FIT OLS has no finite duration")
    value = math.fsum((x-x0)*(y-y0) for x, y in zip(times, values)) / den
    if not math.isfinite(value):
        raise ValueError("nonfinite FIT field drift")
    return value


def fit_field_trends(rows: list[dict], fit_epoch_keys: list[str]) -> dict:
    """Only take whole FIT membership, never interpolate future orbital states."""
    by_key = {iso(r["epoch"]): r for r in rows}
    if len(by_key) != len(rows):
        raise ValueError("duplicate orbital state epoch")
    if len(fit_epoch_keys) != len(set(fit_epoch_keys)):
        raise ValueError("duplicate FIT membership")
    fit = [by_key[k] for k in fit_epoch_keys]
    if len(fit) < 3 or any(a["epoch"] >= b["epoch"] for a, b in zip(fit, fit[1:])):
        raise ValueError("invalid frozen FIT list")
    anchor = fit[-1]
    dt = [elapsed_days(r["epoch"], anchor["epoch"]) for r in fit]
    fields = {}
    for name in FIELDS_TO_DRIFT:
        ix = FIELDS.index(name)
        values = [float(r["state"][ix]) for r in fit]
        fields[name] = {"anchor": values[-1], "slope_per_day": slope_fit_only(dt, values)}
    ra_ix = FIELDS.index("raan")
    return {"anchor_epoch": anchor["epoch"], "anchor_raan_deg": float(anchor["state"][ra_ix]),
            "anchor_state": anchor["state"], "anchor_source_rows": anchor["source_rows"],
            "fit_n": len(fit), "fit_first_epoch_utc": iso(fit[0]["epoch"]),
            "fields": fields}


def state_at(model: dict, days_from_anchor: float) -> tuple[str, ...]:
    if days_from_anchor < 0 or not math.isfinite(days_from_anchor):
        raise ValueError("invalid forward integration time")
    state = list(model["anchor_state"])
    for name in FIELDS_TO_DRIFT:
        item = model["fields"][name]
        value = item["anchor"] + item["slope_per_day"] * days_from_anchor
        if not math.isfinite(value):
            raise ValueError("nonfinite extrapolated field")
        state[FIELDS.index(name)] = str(value)
    # j2_nodal_deg_day itself rejects invalid i, n or e (no clamping).
    return tuple(state)


def integrate_secular_node_deg(model: dict, days: float, step_days: float = STEP_DAYS) -> dict:
    """Midpoint quadrature at two resolutions; reject nonphysical extrapolations."""
    if not (math.isfinite(days) and days > 0 and
            math.isfinite(step_days) and step_days > 0):
        raise ValueError("invalid forward horizon/step")
    n = max(1, math.ceil(days / step_days))
    def midpoint(count: int) -> float:
        h = days / count
        return math.fsum(j2_nodal_deg_day(state_at(model, (i+0.5)*h))
                         for i in range(count)) * h
    coarse = midpoint(n)
    fine = midpoint(2*n)
    delta = abs(fine-coarse)
    if delta > MAX_NUMERICAL_REFINEMENT_DEG:
        raise ValueError("J2 numeric integration did not converge")
    return {"nodal_delta_deg": fine, "numerical_refinement_delta_deg": delta,
            "fine_steps": 2*n}


def compare_holdout(rows: list[dict], model: dict, baseline: dict) -> dict:
    if not rows:
        raise ValueError("no holdout observations")
    pred_errors = []
    epochs = []
    for row in rows:
        t = row["epoch"]
        if t <= model["anchor_epoch"]:
            raise ValueError("temporal leakage into holdout")
        horizon = elapsed_days(t, model["anchor_epoch"])
        integration = integrate_secular_node_deg(model, horizon)
        ix = FIELDS.index("raan")
        obs = float(row["state"][ix])
        predicted = (model["anchor_raan_deg"] + integration["nodal_delta_deg"]) % 360.0
        residual = wrap_deg(obs - predicted)
        pred_errors.append(residual)
        epochs.append({
            "epoch_utc": iso(t),
            "source_rows": row["source_rows"],
            "horizon_days": horizon,
            "observed_secondary_raan_deg": obs,
            "predicted_raan_deg": predicted,
            "signed_residual_deg": residual,
            "quadrature_refinement_delta_deg": integration["numerical_refinement_delta_deg"],
        })
    metrics = {
        "mae_deg": math.fsum(abs(e) for e in pred_errors) / len(pred_errors),
        "rmse_deg": math.sqrt(math.fsum(e*e for e in pred_errors)/len(pred_errors)),
        "max_abs_error_deg": max(abs(e) for e in pred_errors),
        "signed_bias_deg": math.fsum(pred_errors)/len(pred_errors),
        "max_quadrature_refinement_delta_deg": max(
            e["quadrature_refinement_delta_deg"] for e in epochs),
    }
    if len(rows) != baseline["n"]:
        raise ValueError("P2 future membership count changed")
    for old, new in zip(baseline["details"], epochs):
        if old["epoch_utc"] != new["epoch_utc"]:
            raise ValueError("P2 holdout epoch identity changed")
        if abs(wrap_deg(old["observed_secondary_raan_deg"] -
                        new["observed_secondary_raan_deg"])) > MAX_RAAN_SERIALIZATION_DELTA_DEG:
            raise ValueError("future RAAN diverges from P2 secondary reference")
    return {"n": len(rows), "metrics": metrics, "details": epochs}


def compute(raw: list[dict], source_bytes: bytes, frozen_bytes: bytes) -> dict:
    manifest = json.loads(frozen_bytes)
    if build_manifest(source_bytes) != manifest:
        raise ValueError("frozen temporal manifest/source changed")
    grouped, _ = align_rows(raw, json.loads(source_bytes))
    p2 = p2_compute(raw, source_bytes, frozen_bytes)
    out = {
        "schema": SCHEMA,
        "source": {
            "secondary_url": SOURCE_URL,
            "parquet_sha256": SOURCE_SHA256, "csv_sha256": EXPECTED_CSV_SHA256,
            "raan_json_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "split_manifest_sha256": hashlib.sha256(frozen_bytes).hexdigest(),
            "occurrences": ["C25#1", "C179#1", "C180#1", "C181#1", "C241-P1#1", "C241-P2#1", "C241-P3#1"],
            "independence": "SAME_SECONDARY_CATALOGUE_NO_SENSOR_HOLDOUT",
        },
        "method": {
            "all_field_slopes_from": "FROZEN_FIT_EPOCHS_ONLY",
            "anchor": "LAST_FIT_RAAN_AND_LAST_FIT_ORBITAL_STATE",
            "drift_fields": ["inclination_deg", "eccentricity_dimensionless", "mean_motion_rev_day"],
            "drift_units": ["deg/day", "1/day", "rev/day^2"],
            "physics": "J2_SECULAR_PROXY_WITH_EMPIRICALLY_EXTRAPOLATED_MEAN_ELEMENTS",
            "integration": "MIDPOINT_REFINE_2X_NO_REFIT",
            "quadrature_tolerance_deg": MAX_NUMERICAL_REFINEMENT_DEG,
            "quadrature_tolerance_is_sensor_error": False,
            "fit_before_utc": manifest["boundaries"]["fit_before_utc"],
            "domain_reduction": "NONE_NO_PRIMARY_TRACKING_FRAME_OR_SENSOR_ERRORS",
        },
        "objects": {}
    }
    for sid in IDS:
        rows = grouped[int(sid)]
        lookup = {iso(r["epoch"]): r for r in rows}
        memberships = manifest["memberships"][sid]
        field_model = fit_field_trends(rows, memberships["fit"])
        b = p2["objects"][sid]
        if iso(field_model["anchor_epoch"]) != b["anchor"]["anchor_epoch_utc"]:
            raise ValueError("P2 fit anchor epoch changed")
        if abs(wrap_deg(field_model["anchor_raan_deg"] - b["anchor"]["anchor_raan_deg"])) > MAX_RAAN_SERIALIZATION_DELTA_DEG:
            raise ValueError("P2 anchor RAAN drift")
        sections = {}
        for block in ("validation", "evaluation"):
            holdout = [lookup[k] for k in memberships[block]]
            sections[block] = compare_holdout(holdout, field_model, b[block])
        out["objects"][sid] = {
            "fit_n": field_model["fit_n"],
            "fit_first_epoch_utc": field_model["fit_first_epoch_utc"],
            "anchor_epoch_utc": iso(field_model["anchor_epoch"]),
            "anchor_source_rows": field_model["anchor_source_rows"],
            "frozen_fields": field_model["fields"],
            "validation": sections["validation"], "evaluation": sections["evaluation"],
            "P2_existing_models": {
                block: {name: b[block]["models"][name]["mae_deg"]
                        for name in ("last_fit_j2_proxy", "fitonly_linear")}
                for block in ("validation", "evaluation")
            },
        }
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = compute(read_pinned_csv(args.csv), SOURCE.read_bytes(), FROZEN.read_bytes())
    payload = json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    for sid, item in report["objects"].items():
        print("C241_P3", sid, "FIT", item["fit_n"],
              "EVAL", item["evaluation"]["n"],
              "MAE_DRIFT_DEG", round(item["evaluation"]["metrics"]["mae_deg"], 6),
              "MAE_P2_J2_DEG", round(item["P2_existing_models"]["evaluation"]["last_fit_j2_proxy"], 6),
              "MAE_OLS_DEG", round(item["P2_existing_models"]["evaluation"]["fitonly_linear"], 6),
              "QUADRATURE_MAX_DEG",
              round(item["evaluation"]["metrics"]["max_quadrature_refinement_delta_deg"], 10))


if __name__ == "__main__":
    main()
