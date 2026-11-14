#!/usr/bin/env python3
"""C241-P34: exact closed-envelope vs deterministic-tie print uncertainty.

No independent sensor records or observation epochs are inferred. Rebuild
26 source-locked UN/NASA P23 table cells. The CLOSED +/-0.05-minute envelope
admits both endpoint ties (E=130); on integer-centiminute inputs, deterministic
round-half-up OR round-half-even yield E=131. Neither bound is sensor sigma.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal.scripts import compile_un_ssr_cross_compilation as cross

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "research/constraints/C241-P34_un_ssr_print_rounding.json"
LEAN = ROOT / "formal/Conde1963/UnSsrPrintRounding.lean"
RADIUS = 5  # 0.05 min = 3 sec: hypothetical print rounding, NOT sensor error
MODEL = "P(obj,doc) = baseline(obj) + shared_offset(doc) + residual(obj,doc)"


def build(un=None, nasa_model=None, nasa_ledgers=None, nasa_decay=None):
    p23 = cross.build(un=un, nasa_model=nasa_model,
                      nasa_ledgers=nasa_ledgers, nasa_decay=nasa_decay)
    if (p23["schema"] != "conde.un-ssr-cross-compilation-print-model/v1"
            or p23["id"] != "C241-P23"
            or p23["minimum_uniform_residual_centiminute"] != 135
            or p23["print_half_step_ASSUMED_not_instrument_sigma"] != RADIUS
            or len(p23["printed_period_cells"]) != 26
            or len(p23["nasa_sources"]) != 9
            or p23["physical_domain"] != "THETA_UNCHANGED"):
        raise ValueError("C241-P23 data/model contract changed")
    bases = p23["attaining_witness"]["baselines"]
    offsets = p23["attaining_witness"]["document_offsets"]
    E = 135 - RADIUS   # CLOSED ±R envelope: endpoint ties both accepted
    strict_E = E + 1   # canonical integer-centiminute round-half-up/even
    rows = []
    for row in p23["printed_period_cells"]:
        obj, doc = row["object"], row["document_or_cutoff"]
        p, old_r = row["period_centiminute"], row["residual_centiminute"]
        if p % 10:
            raise ValueError("the assumed nearest-tenth precision is not valid for all cells")
        # For the P23 exact-print witness, correct each extreme residual just
        # enough to lie inside E=130, never changing a printed value by >5.
        correction = (1 if old_r > 0 else -1) * max(0, abs(old_r) - E)
        latent = p - correction
        residual = latent - bases[str(obj)] - offsets[doc]
        if abs(correction) > RADIUS or abs(residual) > E:
            raise ValueError("closed-envelope 26-cell witness not attainable")
        strict_delta = (1 if old_r > 0 else -1) * max(0, abs(old_r) - strict_E)
        strict_latent = p - strict_delta
        strict_residual = strict_latent - bases[str(obj)] - offsets[doc]
        if abs(strict_delta) > RADIUS - 1 or abs(strict_residual) > strict_E:
            raise ValueError("strict-interior 26-cell witness not attainable")
        # Integer 0.01 min source grid: |strict_delta| <= 4 is inside all
        # half-step tie conventions (round-half-up and round-half-even).
        rows.append({
            "object": obj, "document_or_cutoff": doc,
            "printed_centiminute": p, "latent_centiminute": latent,
            "print_minus_latent_centiminute": correction,
            "offset_model_residual_centiminute": residual,
            "strict_latent_centiminute": strict_latent,
            "strict_print_minus_latent_centiminute": strict_delta,
            "strict_offset_model_residual_centiminute": strict_residual,
        })
    cmap = {(r["object"], r["document_or_cutoff"]): r["printed_centiminute"] for r in rows}
    key_un = cross.CUTOFF_KEY
    first_gap = cmap[527, key_un] - cmap[529, key_un]
    last_gap = cmap[527, "1963-12-31"] - cmap[529, "1963-12-31"]
    if (first_gap, last_gap) != (0, 540):
        raise ValueError("four-cell sharp certificate changed")
    if any(abs(r["offset_model_residual_centiminute"]) > E for r in rows):
        raise ValueError("residual witness failed")
    if max(abs(r["offset_model_residual_centiminute"]) for r in rows) != E:
        raise ValueError("expected sharp closed-envelope witness not attained")
    if max(abs(r["strict_offset_model_residual_centiminute"]) for r in rows) != strict_E:
        raise ValueError("expected sharp strict-integer witness not attained")
    return {
        "schema": "conde.c241-p34-un-ssr-print-rounding/v1",
        "id": "C241-P34", "parent": "C241-P23",
        "parent_report": str(cross.REPORT.relative_to(ROOT)),
        "un_source": p23["un_source"],
        "nasa_sources": p23["nasa_sources"],
        "model_ASSUMED_not_physics": MODEL,
        "units": "integer centiminute = 0.01 minute",
        "nearest_tenth_print_rounding_ASSUMED_centiminute": RADIUS,
        "discrete_centiminute_grid_ASSUMED": True,
        "cross_agency_common_offset_validated": False,
        "printed_no_rounding_optimum_centiminute": 135,
        "printed_no_rounding_optimum_seconds": "81.0",
        "rounded_print_optimum_centiminute": E,
        "rounded_print_optimum_seconds": "78.0",
        "rounded_print_optimum_means": "CLOSED_SYMMETRIC_ENVELOPE_ALLOWING_BOTH_ENDPOINT_TIES",
        "closed_envelope_endpoint_ties_used": sum(abs(r["print_minus_latent_centiminute"]) == RADIUS for r in rows),
        "discrete_round_half_up_optimum_centiminute": strict_E,
        "discrete_round_half_even_optimum_centiminute": strict_E,
        "discrete_round_half_up_or_even_optimum_seconds": "78.6",
        "half_step_tie_convention_of_historical_printing": "UNKNOWN",
        "strict_interior_witness_all_26_cells_attained": True,
        "all_26_cells_attained": True,
        "sharp_certificate": {
            "objects": [527, 529],
            "documents": [key_un, "1963-12-31"],
            "printed_gaps_centiminute": [first_gap, last_gap],
            "difference_centiminute": 540,
            "conditional_inequality": "4*(E+R) >= 540; E+R >= 135",
            "rounded_consequence": "CLOSED +/-5 envelope: E >= 130",
            "discrete_half_up_even_inequality": "4*E + 18 >= 540",
            "discrete_half_up_even_consequence": "E >= 131; half-step ties have a chosen direction",
        },
        "witness_baselines": bases, "witness_offsets": offsets,
        "cells": rows,
        "rounding_corrections_nonzero": sum(r["print_minus_latent_centiminute"] != 0 for r in rows),
        "un_administrative_cutoff_is_sensor_epoch": False,
        "publication_date_is_observation_epoch": False,
        "instrument_covariance": None,
        "independent_tracking_rows_added": 0,
        "physical_domain": "THETA_UNCHANGED",
        "interpretation": (
            "The exact-print documentary residual bound 81 seconds becomes "
            "78 seconds under an explicitly hypothetical CLOSED symmetric +/-0.05-min "
            "print-value envelope (both endpoint ties allowed), but 78.6 seconds "
            "under integer-centiminute round-half-up or half-even conventions. "
            "The historical printer tie convention is UNKNOWN. These are "
            "SHARP bounds on a common-offset printed-table model, NOT historical "
            "sensor accuracy, physical orbital dynamics, or a reentry location." 
        )
    }


def render_lean(report):
    rows = report["cells"]
    offsets = report["witness_offsets"]
    bases = report["witness_baselines"]
    days = sorted(offsets)
    names = {d: "hUn" if d == cross.CUTOFF_KEY else "h" + d[5:].replace("-", "")
             for d in days}
    vars_head = ["b527", "b528", "b529", *[names[d] for d in days]]
    latent_names = [f"x{i}" for i in range(len(rows))]
    terms = [
        f"withinPrinted {row['printed_centiminute']} {latent_names[i]} b{row['object']} "
        f"{names[row['document_or_cutoff']]} 130 5"
        for i, row in enumerate(rows)
    ]
    witness = [
        *[bases[str(o)] for o in (527, 528, 529)],
        *[offsets[d] for d in days],
        *[r["latent_centiminute"] for r in rows],
    ]
    if len(witness) != len(vars_head) + len(latent_names):
        raise ValueError("Lean witness arity changed")

    def tie_rule_theorem(name: str, intervals: dict[str, tuple[int, int]], doc: str) -> str:
        equations = [
            "aUn = b527 + hUn + eaUn",
            "aDec = b527 + hDec + eaDec",
            "cUn = b529 + hUn + ecUn",
            "cDec = b529 + hDec + ecDec",
        ]
        params = ["aUn", "aDec", "cUn", "cDec"]
        prints = [9470, 9460, 9470, 8920]
        lines = []
        for label, eqn in zip(params, equations):
            lines.append(f"    ({label}Def : {eqn})")
        for label, p, (lo, hi) in zip(params, prints,
                                       (intervals[x] for x in params)):
            lines.extend([
                f"    ({label}RoundLo : {lo} ≤ {p} - {label})",
                f"    ({label}RoundHi : {p} - {label} ≤ {hi})",
            ])
        for label in ("eaUn", "eaDec", "ecUn", "ecDec"):
            lines.extend([f"    ({label}Lo : -E ≤ {label})",
                          f"    ({label}Hi : {label} ≤ E)"])
        return (f"/-- {doc} -/\n"
                + f"theorem {name}\n"
                + "    (b527 b529 hUn hDec : Int)\n"
                + "    (aUn aDec cUn cDec eaUn eaDec ecUn ecDec E : Int)\n"
                + "\n".join(lines) + " :\n"
                + "    131 ≤ E := by\n  omega\n\n")

    # For strictly positive source periods, round-half-up allows
    # q=printed-latent in [-4,5] integer centiminute. Half-even allows
    # q in [-4,4] at odd tenths (9470) and [-5,5] at even tenths.
    half_up = tie_rule_theorem(
        "half_up_discrete_lower_bound",
        {x: (-4, 5) for x in ("aUn", "aDec", "cUn", "cDec")},
        "Round-half-up (positive periods) on integer centiminutes: four cells force E ≥ 131")
    half_even = tie_rule_theorem(
        "half_even_discrete_lower_bound",
        {"aUn": (-4, 4), "aDec": (-5, 5),
         "cUn": (-4, 4), "cDec": (-5, 5)},
        "Round-half-to-even on integer centiminutes: odd/even final digits force E ≥ 131")
    strict_latents = [f"y{i}" for i in range(len(rows))]
    strict_terms = [
        f"withinStrictInterior {row['printed_centiminute']} {strict_latents[i]} "
        f"b{row['object']} {names[row['document_or_cutoff']]} 131"
        for i, row in enumerate(rows)
    ]
    strict_witness = [*[bases[str(o)] for o in (527, 528, 529)],
                      *[offsets[d] for d in days],
                      *[r["strict_latent_centiminute"] for r in rows]]
    if len(strict_witness) != len(vars_head) + len(strict_latents):
        raise ValueError("strict Lean witness arity changed")
    return '''import Lean

namespace Conde1963.UnSsrPrintRounding

/-! C241-P34. Documentary UN/NASA COMMON-offset thought experiment.
Centiminute is 0.01 minute. Each printed tenth-minute value may differ by
at most 5 centiminutes from an unobserved input under a CLOSED envelope.
The two printed-half-step ties cannot BOTH be accepted by a deterministic
rounding convention. For integer-centiminute inputs, round-half-up/even
have a distinct 131-centiminute sharp residual bound (78.6 seconds).
This is NOT a bound on orbital sensor errors. March UN publication and
January administrative cutoff are NOT instrumental observation times.
No physical-domain reduction, independence claim, or decay location. -/

def withinPrinted (printed latent baseline offset E R : Int) : Prop :=
  -R ≤ printed - latent ∧ printed - latent ≤ R ∧
  -E ≤ latent - baseline - offset ∧ latent - baseline - offset ≤ E

/-- Four contrasting UN/December printed values force E+R >= 135,
even after allowing a symmetric rounding margin R at EACH cell. -/
theorem round_robust_lower_bound
    (b527 b529 hUn hDec : Int)
    (aUn aDec cUn cDec eaUn eaDec ecUn ecDec E R : Int)
    (aUnDef : aUn = b527 + hUn + eaUn)
    (aDecDef : aDec = b527 + hDec + eaDec)
    (cUnDef : cUn = b529 + hUn + ecUn)
    (cDecDef : cDec = b529 + hDec + ecDec)
    (aUnRoundLo : -R ≤ 9470 - aUn) (aUnRoundHi : 9470 - aUn ≤ R)
    (aDecRoundLo : -R ≤ 9460 - aDec) (aDecRoundHi : 9460 - aDec ≤ R)
    (cUnRoundLo : -R ≤ 9470 - cUn) (cUnRoundHi : 9470 - cUn ≤ R)
    (cDecRoundLo : -R ≤ 8920 - cDec) (cDecRoundHi : 8920 - cDec ≤ R)
    (eaUnLo : -E ≤ eaUn) (eaUnHi : eaUn ≤ E)
    (eaDecLo : -E ≤ eaDec) (eaDecHi : eaDec ≤ E)
    (ecUnLo : -E ≤ ecUn) (ecUnHi : ecUn ≤ E)
    (ecDecLo : -E ≤ ecDec) (ecDecHi : ecDec ≤ E) :
    135 ≤ E + R := by
  omega

/-- Under R=5, at least 130 centiminutes = 78 seconds remain
unexplained by a single additive offset per publication. -/
theorem rounded_half_step_lower_bound
    (b527 b529 hUn hDec : Int)
    (aUn aDec cUn cDec eaUn eaDec ecUn ecDec E : Int)
    (aUnDef : aUn = b527 + hUn + eaUn)
    (aDecDef : aDec = b527 + hDec + eaDec)
    (cUnDef : cUn = b529 + hUn + ecUn)
    (cDecDef : cDec = b529 + hDec + ecDec)
    (aUnRoundLo : -5 ≤ 9470 - aUn) (aUnRoundHi : 9470 - aUn ≤ 5)
    (aDecRoundLo : -5 ≤ 9460 - aDec) (aDecRoundHi : 9460 - aDec ≤ 5)
    (cUnRoundLo : -5 ≤ 9470 - cUn) (cUnRoundHi : 9470 - cUn ≤ 5)
    (cDecRoundLo : -5 ≤ 8920 - cDec) (cDecRoundHi : 8920 - cDec ≤ 5)
    (eaUnLo : -E ≤ eaUn) (eaUnHi : eaUn ≤ E)
    (eaDecLo : -E ≤ eaDec) (eaDecHi : eaDec ≤ E)
    (ecUnLo : -E ≤ ecUn) (ecUnHi : ecUn ≤ E)
    (ecDecLo : -E ≤ ecDec) (ecDecHi : ecDec ≤ E) :
    130 ≤ E := by
  omega

/-- A SINGLE baseline/offset set and 26 inputs attain E=130 under the
CLOSED ±5 envelope, including endpoint ties from both sides.
This is NOT a deterministic tie-breaking rounding convention. -/
theorem all_26_cells_attain_130 :
    ∃ (''' + " ".join(vars_head + latent_names) + ''' : Int),
      ''' + "\n      ∧ ".join(terms) + ''' := by
  refine ⟨''' + ", ".join(map(str, witness)) + ''', ?_⟩
  simp only [withinPrinted]
  omega

''' + '\n' + half_up + half_even + f'''
/-- Strictly interior, so valid under BOTH round-half-up and half-even. -/
def withinStrictInterior (printed latent baseline offset E : Int) : Prop :=
  -4 ≤ printed - latent ∧ printed - latent ≤ 4 ∧
  -E ≤ latent - baseline - offset ∧ latent - baseline - offset ≤ E

/-- A single witness for all 26 cells achieves E=131 with |rounding| ≤4.
Neither a publication day nor an administrative cutoff is a sensor epoch. -/
theorem all_26_strict_interior_attain_131 :
    ∃ ({" ".join(vars_head + strict_latents)} : Int),
      {" ∧".join(chr(10) + "      " + t for t in strict_terms)[2:]} := by
  refine ⟨{", ".join(map(str, strict_witness))}, ?_⟩
  simp only [withinStrictInterior]
  omega

end Conde1963.UnSsrPrintRounding
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    r = build()
    payload = json.dumps(r, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    proof = render_lean(r)
    if args.check:
        if REPORT.read_text(encoding="utf-8") != payload:
            raise SystemExit("C241-P34 source-locked report differs")
        if LEAN.read_text(encoding="utf-8") != proof:
            raise SystemExit("C241-P34 source-locked Lean proof differs")
    else:
        REPORT.write_text(payload, encoding="utf-8")
        LEAN.write_text(proof, encoding="utf-8")
    print("C241-P34: 26 cells; closed envelope E=130 (78 s), "
          "integer half-up/even E=131 (78.6 s); Theta unchanged")


if __name__ == "__main__":
    main()
