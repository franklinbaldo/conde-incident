#!/usr/bin/env python3
"""C241-P13: exact minimax nuisance residual for a common NASA edition bias.

Data must pass the C241-P12 source-locked audit. Results concern printed
periods only; neither instrument uncertainty nor physical constraints.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal.scripts.compile_ssr_edition_offset import NOV, OCT, SUR, DEC, GRAPH, build as audited_parent

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "research/constraints/C241-P13_offset_robustness.json"
LEAN = ROOT / "formal/Conde1963/SsrOffsetThreshold.lean"


def minimax_radius(periods: dict[str, list[int]]) -> int:
    """Smallest integer E admitting common edition bias and |residual| <= E.

    For each edition, D_i = printed_527_i - printed_529_i = B + e_527_i - e_529_i.
    Therefore a feasible B must lie within 2E of every D_i. With integral
    centiminute data, minimum E is ceil((max D - min D)/4).
    """
    if set(periods) != {"527", "529"}:
        raise ValueError("expected precisely 527 and 529")
    a, c = periods["527"], periods["529"]
    if len(a) < 2 or len(a) != len(c) or any(type(v) is not int for v in a + c):
        raise ValueError("invalid edition series")
    d = [x - y for x, y in zip(a, c)]
    return (max(d) - min(d) + 3) // 4


def build(nov: dict, octo: dict, survivors: dict, dec: dict, graph: dict) -> dict:
    parent = audited_parent(nov, octo, survivors, dec, graph)
    periods = parent["printed_period_centimin"]
    if periods != {"527": [9460, 9460, 9460], "529": [9260, 9220, 9160]}:
        raise ValueError("unexpected source-locked P12 series")
    threshold = minimax_radius(periods)
    if threshold != 25:
        raise ValueError("unexpected exact residual threshold")
    witness = {
        "base_527_centimin": 9500,
        "base_529_centimin": 9250,
        "shared_edition_bias_centimin": [-15, -35, -65],
        "residual_527_centimin": [-25, -5, 25],
        "residual_529_centimin": [25, 5, -25],
    }
    for obj in ("527", "529"):
        base = witness[f"base_{obj}_centimin"]
        for observed, bias, residual in zip(
            periods[obj], witness["shared_edition_bias_centimin"],
            witness[f"residual_{obj}_centimin"],
        ):
            if observed != base + bias + residual or abs(residual) > threshold:
                raise ValueError("invalid minimax witness")
    return {
        "schema": "conde.ssr-common-edition-minimax/v1",
        "id": "C241-P13",
        "parent_id": parent["id"],
        "parent_result": parent["result"],
        "source_editions": parent["source_editions"],
        "source_family": parent["source_family"],
        "printed_period_centimin": periods,
        "printed_object_differences_centimin": [a - c for a, c in zip(periods["527"], periods["529"])],
        "model": "P_object,edition = base_object + shared_bias_edition + object_edition_residual",
        "exact_minimum_uniform_residual_centimin": threshold,
        "nearest_tenth_printing_half_unit_centimin": 5,
        "minimum_to_half_unit_factor": 5,
        "attaining_witness": witness,
        "result": "COMMON_EDITION_BIAS_REQUIRES_AT_LEAST_0.25_MINUTE_PER_CELL",
        "conditional_on": [
            "exact pinned values and edition alignments from C241-P12",
            "one constant object baseline and one additive bias shared by both objects per edition",
            "one free object-and-edition residual bounded uniformly in absolute value",
        ],
        "does_not_measure": ["sensor_error", "actual_editorial_error", "drag", "orbital_phase", "reentry_location"],
        "instrument_epoch_utc": None,
        "tracking_covariance": None,
        "independent_tracking_sensors": False,
        "active_physical_constraint": False,
        "admissible_domain": "THETA_UNCHANGED",
        "status": "CONNECTED_PENDING_CALIBRATION",
        "lean_contract": "formal/Conde1963/SsrOffsetThreshold.lean",
    }


def render_lean(report: dict) -> str:
    p = report["printed_period_centimin"]
    a, c = p["527"], p["529"]
    e = report["exact_minimum_uniform_residual_centimin"]
    w = report["attaining_witness"]
    return f"""import Lean

namespace Conde1963.SsrOffsetThreshold

/-! Source-locked C241-P13, units: 0.01 minute. This is a *printing model*
threshold, not a measurement of the tracking system or a bound on Theta.
Publication dates do not identify orbital observation epochs. -/

/-- Even permitting independent residuals for both objects and both endpoint
editions, a single edition-wide additive bias demands >= {e} centiminutes of
residual budget for at least one cell. -/
theorem shared_edition_bias_requires_25_centimin
    (baseA baseC biasFirst biasLast errAFirst errALast errCFirst errCLast E : Int)
    (ha0 : {a[0]} = baseA + biasFirst + errAFirst)
    (ha2 : {a[2]} = baseA + biasLast + errALast)
    (hc0 : {c[0]} = baseC + biasFirst + errCFirst)
    (hc2 : {c[2]} = baseC + biasLast + errCLast)
    (ha0lo : -E ≤ errAFirst) (ha0hi : errAFirst ≤ E)
    (ha2lo : -E ≤ errALast) (ha2hi : errALast ≤ E)
    (hc0lo : -E ≤ errCFirst) (hc0hi : errCFirst ≤ E)
    (hc2lo : -E ≤ errCLast) (hc2hi : errCLast ≤ E)
    : {e} ≤ E := by
  omega

/-- All six published cells are attainable at exactly {e} centiminutes.
Together with the lower bound above, the minimax threshold is sharp. -/
theorem all_six_editions_attain_25_centimin :
    ∃ (baseA baseC biasFirst biasMiddle biasLast : Int),
      ({a[0]} = baseA + biasFirst + ({w['residual_527_centimin'][0]})) ∧
      ({a[1]} = baseA + biasMiddle + ({w['residual_527_centimin'][1]})) ∧
      ({a[2]} = baseA + biasLast + ({w['residual_527_centimin'][2]})) ∧
      ({c[0]} = baseC + biasFirst + ({w['residual_529_centimin'][0]})) ∧
      ({c[1]} = baseC + biasMiddle + ({w['residual_529_centimin'][1]})) ∧
      ({c[2]} = baseC + biasLast + ({w['residual_529_centimin'][2]})) := by
  refine ⟨{w['base_527_centimin']}, {w['base_529_centimin']}, {w['shared_edition_bias_centimin'][0]}, {w['shared_edition_bias_centimin'][1]}, {w['shared_edition_bias_centimin'][2]}, ?_⟩
  omega

end Conde1963.SsrOffsetThreshold
"""


def run(check: bool) -> None:
    report = build(*(json.loads(p.read_text()) for p in (NOV, OCT, SUR, DEC, GRAPH)))
    blob = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    lean = render_lean(report)
    if check:
        if REPORT.read_text() != blob or LEAN.read_text() != lean:
            raise SystemExit("C241-P13 generated outputs differ from audited inputs")
        print("C241-P13 PASS: minimum uniform residual 25 centimin; Theta unchanged")
    else:
        REPORT.write_text(blob)
        LEAN.write_text(lean)
        print("C241-P13 generated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    run(parser.parse_args().check)
