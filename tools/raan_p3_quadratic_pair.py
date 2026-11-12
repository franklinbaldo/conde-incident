#!/usr/bin/env python3
"""C241-P4: paired, same-epoch falsification of P3 against Texugo quadratic.

No model is fitted here. Inputs must be independently generated from the
same pinned secondary CSV and frozen split. This scores no terminal orbit.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path

SCHEMA = "conde.raan-p3-quadratic-paired/v1"
IDS = ("527", "528", "529")
BLOCKS = ("validation", "evaluation")
# C241-L3 chronological frozen split, not a tunable fit hyperparameter.
FIT_END_UTC = datetime(1963, 8, 1, tzinfo=timezone.utc)
EVALUATION_END_UTC = datetime(1964, 1, 1, tzinfo=timezone.utc)
EVALUATION_FROM_UTC = datetime(1963, 10, 1, tzinfo=timezone.utc)
COUNTS = {"527": 4, "528": 8, "529": 23}


def finite_angle(x: object) -> float:
    if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x):
        raise ValueError("nonfinite or nonnumeric angular residual")
    if not -180 <= x <= 180:
        raise ValueError("residual outside signed circular degrees")
    return float(x)


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("empty frozen block")
    return math.fsum(values) / len(values)


def assert_equal(a: object, b: object, label: str) -> None:
    if a != b:
        raise ValueError(f"{label} mismatch")


def valid_time(text: str) -> datetime:
    if not isinstance(text, str) or not text.endswith("Z"):
        raise ValueError("non-UTC ISO epoch")
    t = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if t.tzinfo != timezone.utc:
        raise ValueError("non-UTC epoch")
    return t


def compare(p3: dict, quadratic: dict) -> dict:
    """Validate provenance/epoch identity before comparing any heldout error."""
    assert_equal(p3["schema"], "conde.secondary-fitfield-j2-outoftime/v1", "P3 schema")
    assert_equal(quadratic["schema"], "conde.texugo-quadratic-raan-ablation/v1", "quadratic schema")
    for field in ("parquet_sha256", "csv_sha256", "raan_json_sha256"):
        assert_equal(p3["source"][field], quadratic["source"][field], field)
    assert_equal(p3["source"]["split_manifest_sha256"],
                 quadratic["source"]["frozen_split_sha256"], "frozen split hash")
    assert_equal(p3["method"]["fit_before_utc"],
                 quadratic["design"]["fit_epoch_cutoff"], "fit cutoff")
    if p3["method"]["domain_reduction"] != "NONE_NO_PRIMARY_TRACKING_FRAME_OR_SENSOR_ERRORS":
        raise ValueError("P3 domain status changed")
    if quadratic["design"]["physical_domain_reduction"] != "NONE":
        raise ValueError("quadratic domain status changed")
    assert_equal(sorted(p3["objects"]), list(IDS), "P3 object set")
    assert_equal(sorted(quadratic["objects"]), list(IDS), "quadratic object set")

    result = {"schema": SCHEMA, "sources": {
        "parquet_sha256": p3["source"]["parquet_sha256"],
        "derived_csv_sha256": p3["source"]["csv_sha256"],
        "raan_json_sha256": p3["source"]["raan_json_sha256"],
        "frozen_split_sha256": p3["source"]["split_manifest_sha256"],
        "lineage": "ONE_SECONDARY_TRACKING_MIRROR_NOT_INDEPENDENT"
    }, "question": "P3 beats fit-only quadratic on each identical frozen holdout?",
        "status": "RETROSPECTIVE_SECONDARY_CATALOGUE_CONTROL",
        "physical_domain_change": "NONE_NOT_CALIBRATED", "objects": {}}
    for sat in IDS:
        a, b = p3["objects"][sat], quadratic["objects"][sat]
        assert_equal(a["fit_n"], b["fit_n"], "FIT membership count")
        assert_equal(a["anchor_epoch_utc"], b["last_fit_epoch_utc"], "FIT anchor")
        anchor = valid_time(a["anchor_epoch_utc"])
        blocks: dict = {}
        for block in BLOCKS:
            left, right = a[block], b[block]
            assert_equal(left["n"], right["n"], f"{sat} {block} row count")
            assert_equal(len(left["details"]), left["n"], "P3 details count")
            assert_equal(len(right["per_epoch"]), right["n"], "quadratic details count")
            if block == "evaluation":
                assert_equal(left["n"], COUNTS[sat], "frozen evaluation inventory")
            epoch_rows = []
            last_epoch = anchor
            for ld, rd in zip(left["details"], right["per_epoch"]):
                assert_equal(ld["epoch_utc"], rd["epoch_utc"], "paired epoch identity")
                t = valid_time(ld["epoch_utc"])
                if t <= last_epoch:
                    raise ValueError("holdout leakage, unordered or repeated epoch")
                if (block == "validation" and not FIT_END_UTC <= t < EVALUATION_FROM_UTC) or (
                    block == "evaluation" and not EVALUATION_FROM_UTC <= t < EVALUATION_END_UTC
                ):
                    raise ValueError("frozen validation/evaluation boundary violation")
                last_epoch = t
                pe = finite_angle(ld["signed_residual_deg"])
                qe = finite_angle(rd["quadratic_signed_error_deg"])
                obs = ld["observed_secondary_raan_deg"]
                pred = ld["predicted_raan_deg"]
                if not all(isinstance(v, (float, int)) and math.isfinite(v) and 0 <= v < 360
                           for v in (obs, pred)):
                    raise ValueError("invalid P3 observation or prediction")
                if abs(((obs - pred + 180) % 360) - 180 - pe) > 1e-8:
                    raise ValueError("P3 signed residual disagrees with observation")
                epoch_rows.append({
                    "epoch_utc": ld["epoch_utc"], "source_rows": ld["source_rows"],
                    "p3_abs_error_deg": abs(pe), "quadratic_abs_error_deg": abs(qe),
                    "p3_minus_quadratic_abs_error_deg": abs(pe)-abs(qe),
                })
            p_mae = mean([r["p3_abs_error_deg"] for r in epoch_rows])
            q_mae = mean([r["quadratic_abs_error_deg"] for r in epoch_rows])
            if abs(p_mae - left["metrics"]["mae_deg"]) > 1e-8:
                raise ValueError("P3 reported MAE mismatch")
            if abs(q_mae - right["models"]["fitonly_quadratic"]["mae_deg"]) > 1e-8:
                raise ValueError("quadratic reported MAE mismatch")
            blocks[block] = {
                "n": len(epoch_rows), "p3_mae_deg": p_mae,
                "quadratic_mae_deg": q_mae, "p3_minus_quadratic_mae_deg": p_mae-q_mae,
                "p3_beats_quadratic": p_mae < q_mae,
                "p3_better_epoch_count": sum(r["p3_abs_error_deg"] < r["quadratic_abs_error_deg"] for r in epoch_rows),
                "quadratic_better_epoch_count": sum(r["quadratic_abs_error_deg"] < r["p3_abs_error_deg"] for r in epoch_rows),
                "equal_epoch_count": sum(r["quadratic_abs_error_deg"] == r["p3_abs_error_deg"] for r in epoch_rows),
                "per_epoch": epoch_rows,
            }
        result["objects"][sat] = {"fit_n": a["fit_n"], "anchor_epoch_utc": a["anchor_epoch_utc"], **blocks}
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--p3", required=True, type=Path)
    p.add_argument("--quadratic", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    report = compare(json.loads(args.p3.read_text()), json.loads(args.quadratic.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for sat, item in report["objects"].items():
        d = item["evaluation"]
        print("C241_P4", sat, "n", d["n"], "P3_MAE_DEG", round(d["p3_mae_deg"], 6),
              "QUAD_MAE_DEG", round(d["quadratic_mae_deg"], 6),
              "DELTA_DEG", round(d["p3_minus_quadratic_mae_deg"], 6))


if __name__ == "__main__":
    main()
