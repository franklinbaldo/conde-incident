#!/usr/bin/env python3
"""C241-P2: frozen first-order J2 rate versus frozen empirical RAAN trend.

Every orbital field is taken from the LAST FIT epoch of each NORAD, never the
validation/evaluation states. Source is the SHA-pinned SECONDARY 1963 Parquet
mirror. This is an out-of-time catalog diagnostic, NOT tracking accuracy.
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
sys.path.insert(0, str(ROOT / "formal" / "scripts"))

from cross_object_epoch_support import (  # noqa: E402
    EXPECTED_CSV_SHA256, SOURCE_SHA256, SOURCE_URL, FIELDS,
    normalize, read_pinned_csv,
)
from audit_secondary_j2_raan import j2_nodal_deg_day  # noqa: E402
from raan_frozen_trend_holdout import (  # noqa: E402
    SOURCE, FROZEN, IDS, SPLITS, compute as p1_compute,
    elapsed_days, fit_only, iso, wrap_deg,
)
from raan_coepoch_audit import parse_records  # noqa: E402

SCHEMA = "conde.secondary-frozen-j2-outoftime/v1"
MAX_RAAN_SERIALIZATION_DELTA_DEG = 0.00008
EXPECTED_COUNTS = {527: 21, 528: 45, 529: 57}
EXPECTED_UNIQUE = {527: 20, 528: 45, 529: 54}


def align_rows(raw_rows: list[dict], source: dict) -> tuple[dict, dict]:
    """Reject epoch, identity, RAAN or duplicate disagreement across exports."""
    csv_by_sat, counts = normalize(raw_rows)
    if counts != EXPECTED_COUNTS:
        raise ValueError("pinned CSV counts changed")
    if {sid: len(rows) for sid, rows in csv_by_sat.items()} != EXPECTED_UNIQUE:
        raise ValueError("unique epoch count changed")
    reference, _ = parse_records(source)
    for sid in EXPECTED_COUNTS:
        numeric = {row["epoch"]: row for row in csv_by_sat[sid]}
        if len(numeric) != len(reference[sid]):
            raise ValueError("P1/CSV epoch inventory mismatch")
        for stamp, ra in reference[sid]:
            row = numeric.get(stamp)
            if row is None:
                raise ValueError("P1/CSV epoch mismatch")
            serialized = float(row["state"][FIELDS.index("raan")])
            if abs(wrap_deg(serialized - ra)) > MAX_RAAN_SERIALIZATION_DELTA_DEG:
                raise ValueError("RAAN conflict between secondary extracts")
    return csv_by_sat, reference


def frozen_j2_rate(fit_epochs: list[tuple[datetime, float]], full_csv: list[dict]) -> dict:
    """Choose the exact last FIT state; inspect neither future epoch nor its state."""
    if len(fit_epochs) < 3:
        raise ValueError("missing fit")
    stamp = fit_epochs[-1][0]
    matches = [row for row in full_csv if row["epoch"] == stamp]
    if len(matches) != 1:
        raise ValueError("missing/ambiguous last-fit orbital state")
    chosen = matches[0]
    if abs(wrap_deg(float(chosen["state"][FIELDS.index("raan")]) -
                    fit_epochs[-1][1])) > MAX_RAAN_SERIALIZATION_DELTA_DEG:
        raise ValueError("last FIT RAAN mismatch")
    rate = j2_nodal_deg_day(chosen["state"])
    if not math.isfinite(rate):
        raise ValueError("nonfinite J2 rate")
    return {"rate_deg_per_day": rate, "anchor_epoch_utc": iso(stamp),
            "anchor_raan_deg": fit_epochs[-1][1],
            "source_rows": chosen["source_rows"],
            "inclination_deg": float(chosen["state"][FIELDS.index("inclination")]),
            "eccentricity": float(chosen["state"][FIELDS.index("eccentricity")]),
            "mean_motion_rev_day": float(chosen["state"][FIELDS.index("mean_motion")])}


def j2_predict(anchor: dict, t: datetime, *, epoch: datetime) -> float:
    dt = elapsed_days(t, epoch)
    if dt <= 0:
        raise ValueError("J2 holdout prediction cannot use fit/past epoch")
    return (anchor["anchor_raan_deg"] + anchor["rate_deg_per_day"] * dt) % 360


def compare(rows: list[tuple[datetime, float]], anchor: dict, fit_model: dict) -> dict:
    if not rows:
        raise ValueError("empty holdout")
    epoch = fit_model["last_fit_epoch"]
    errors = {"persistence": [], "fitonly_linear": [], "last_fit_j2_proxy": []}
    details = []
    for t, observed in rows:
        if t <= epoch:
            raise ValueError("temporal leakage")
        horizon = elapsed_days(t, epoch)
        predictions = {
            "persistence": fit_model["last_fit_raan_deg"],
            "fitonly_linear": (fit_model["intercept_deg_unwrapped"] +
                               fit_model["slope_deg_per_day"] *
                               elapsed_days(t, fit_model["origin"])) % 360,
            "last_fit_j2_proxy": j2_predict(anchor, t, epoch=epoch)}
        signed = {key: wrap_deg(observed - val) for key, val in predictions.items()}
        for key, value in signed.items():
            errors[key].append(value)
        details.append({"epoch_utc": iso(t), "observed_secondary_raan_deg": observed,
                        "horizon_since_last_fit_days": horizon,
                        "signed_error_deg": signed})
    def metrics(values: list[float]) -> dict:
        return {"mae_deg": math.fsum(abs(x) for x in values) / len(values),
                "rmse_deg": math.sqrt(math.fsum(x*x for x in values)/len(values)),
                "max_abs_error_deg": max(abs(x) for x in values),
                "signed_bias_deg": math.fsum(values)/len(values)}
    result = {key: metrics(values) for key, values in errors.items()}
    return {"n": len(rows), "first_epoch_utc": iso(rows[0][0]),
            "last_epoch_utc": iso(rows[-1][0]), "models": result,
            "j2_better_than_linear_mae": (result["last_fit_j2_proxy"]["mae_deg"] <
                                           result["fitonly_linear"]["mae_deg"]),
            "details": details}


def compute(raw_rows: list[dict], source_bytes: bytes, frozen_bytes: bytes) -> dict:
    # P1 asserts all split memberships are the original fixed manifest.
    reference = json.loads(source_bytes)
    manifest = json.loads(frozen_bytes)
    p1 = p1_compute(source_bytes, frozen_bytes)
    by_sat, catalog_rows = align_rows(raw_rows, reference)
    output = {"schema": SCHEMA, "source": {
        "url": SOURCE_URL, "parquet_sha256": SOURCE_SHA256,
        "csv_sha256": EXPECTED_CSV_SHA256,
        "p1_json_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "frozen_split_sha256": hashlib.sha256(frozen_bytes).hexdigest(),
        "occurrences": ["C25#1", "C179#1", "C180#1", "C181#1", "C241-L4", "C241-P1", "C241-P2"],
        "independence": "SAME_SECONDARY_SPACE_TRACK_LINEAGE_NOT_INSTRUMENTAL_HOLDOUT"},
        "method": {"fixed_fit_before_utc": manifest["boundaries"]["fit_before_utc"],
                   "j2_orbit_fields_from": "LAST_FIT_EPOCH_ONLY",
                   "J2_rate_type": "UNFITTED_FIRST_ORDER_MEAN_ELEMENTS_PROXY",
                   "j2_field_units": "inclination degree, eccentricity dimensionless, n rev/day",
                   "loss": "CIRCULAR_DEGREES",
                   "frozen_statistical_baseline": "P1_FIT_ONLY_OLS",
                   "not_observational_sigma": True,
                   "physical_domain_reduction": "NOT_ACTIVATED"}, "objects": {}}
    for sat in IDS:
        sid = int(sat)
        entries = {iso(t): (t, ra) for t, ra in catalog_rows[sid]}
        blocks = {}
        for block in SPLITS:
            keys = manifest["memberships"][sat][block]
            blocks[block] = [entries[k] for k in keys]
        fit_model = fit_only(blocks["fit"])
        frozen_j2 = frozen_j2_rate(blocks["fit"], by_sat[sid])
        item = {"fit_n": len(blocks["fit"]), "anchor": frozen_j2,
                "fitonly_linear_rate_deg_per_day": fit_model["slope_deg_per_day"],
                "validation": compare(blocks["validation"], frozen_j2, fit_model),
                "evaluation": compare(blocks["evaluation"], frozen_j2, fit_model)}
        for block in ("validation", "evaluation"):
            current = item[block]
            p1_block = p1["objects"][sat][block]
            for model in ("persistence", "fitonly_linear"):
                if not math.isclose(current["models"][model]["mae_deg"],
                                    p1_block["models"][model]["mae_deg"],
                                    rel_tol=0, abs_tol=1e-10):
                    raise ValueError("P1 baseline drifted")
        output["objects"][sat] = item
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--check", type=Path)
    args = ap.parse_args()
    if args.output and args.check:
        ap.error("one of --output / --check")
    report = compute(read_pinned_csv(args.csv), SOURCE.read_bytes(), FROZEN.read_bytes())
    content = json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2)+"\n"
    if args.check:
        if args.check.read_text() != content:
            raise SystemExit("FAIL: C241-P2 frozen J2 results changed")
    elif args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)
    else:
        print(content, end="")
    for sat, item in report["objects"].items():
        m = item["evaluation"]["models"]
        print("C241_P2_EVAL", sat, "N", item["evaluation"]["n"],
              "J2", round(m["last_fit_j2_proxy"]["mae_deg"], 6),
              "LINEAR", round(m["fitonly_linear"]["mae_deg"], 6),
              "STATIC", round(m["persistence"]["mae_deg"], 6))


if __name__ == "__main__":
    main()
