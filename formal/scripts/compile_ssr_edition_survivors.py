#!/usr/bin/env python3
"""C241-P21: maximum SSR publication subset in a print-only nuisance model.

Conditional errors <=0.05 minute, baseline per object and offset per edition.
Publications, not individual print cells, are removed as complete units.
No instrumental accuracy, epoch, orbital dynamics or impact location inferred.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path
from formal.scripts import compile_ssr_nine_editions as parent

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "research/constraints/C241-P21_ssr_edition_survivors.json"
LEAN = ROOT / "formal/Conde1963/SsrEditionSurvivors.lean"
E = 5  # 0.05 min: assumed HALF PRINT STEP, NOT sensor error


def subcells(cells, publications):
    dates = set(publications)
    return {key: value for key, value in cells.items() if key[1] in dates}


def pair_screens(cells, a, b):
    """Necessary 4E gap-change bounds for each common object pair."""
    objs = sorted(o for o in {k[0] for k in cells} if (o, a) in cells and (o, b) in cells)
    return [
        {"objects": [i, j], "gap_a": cells[i, a] - cells[j, a],
         "gap_b": cells[i, b] - cells[j, b],
         "change": (cells[i, a] - cells[j, a]) - (cells[i, b] - cells[j, b])}
        for i, j in combinations(objs, 2)
    ]


def build(model=None, ledgers=None, decay=None):
    cells, sources = parent.source_rows(model, ledgers, decay)
    days = [s["publication"] for s in sources]
    if len(days) != 9 or len(cells) != 23:
        raise ValueError("expected 9 locked publications and 23 printed cells")
    ac = [cells[527, d] - cells[529, d] for d in days]
    ab = [cells[527, d] - cells[528, d] if (528, d) in cells else None for d in days]
    first_screen, fully_screened, feasible_pairs = [], [], []
    for a, b in combinations(days, 2):
        gaps = pair_screens(cells, a, b)
        ac_gap = next(x for x in gaps if x["objects"] == [527, 529])
        if abs(ac_gap["change"]) > 4 * E:
            continue
        first_screen.append([a, b])
        if not all(abs(x["change"]) <= 4 * E for x in gaps):
            continue
        fully_screened.append([a, b])
        if parent.feasible(subcells(cells, (a, b)), E) is not None:
            feasible_pairs.append([a, b])
    # 84 exact 3-edition candidates; supplement pairwise Lean certificate.
    feasible_triples = [
        list(group) for group in combinations(days, 3)
        if parent.feasible(subcells(cells, group), E) is not None
    ]
    if (len(first_screen), fully_screened, feasible_pairs, feasible_triples) != (
        3, [["1963-06-30", "1963-07-31"]],
        [["1963-06-30", "1963-07-31"]], [],
    ):
        raise ValueError("locked subset classification changed")
    pair = feasible_pairs[0]
    witness = parent.feasible(subcells(cells, pair), E)
    assert witness is not None
    baselines, offsets, residuals = witness
    return {
        "schema": "conde.ssr-edition-survivors/v1", "id": "C241-P21",
        "parent_evidence": ["C241-L27", "C241-P20"],
        "sources": sources, "unit": "centiminute (0.01 minute)",
        "model": "printed=obj_baseline+publication_offset+cell_residual",
        "print_half_step_ASSUMED_not_sensor_sigma": E,
        "gap_527_minus_529": ac, "gap_527_minus_528_or_null_if_absent": ab,
        "pairs_passing_527_529_screen": first_screen,
        "pairs_passing_all_shared_object_screens": fully_screened,
        "exact_feasible_pairs": feasible_pairs, "exact_feasible_triples": feasible_triples,
        "maximum_retained_editions": 2, "unique_maximal_survivors": pair,
        "min_removed_editions": 7,
        "removed_editions_NOT_errata": [d for d in days if d not in pair],
        "witness": {
            "baselines": baselines, "offsets": offsets,
            "residuals": [
                {"object": obj, "publication": day, "printed": cells[obj, day],
                 "residual": residuals[obj, day]}
                for obj, day in sorted(residuals)
            ],
        },
        "instrument_epochs": None, "instrument_sigma": None,
        "new_instrument_observations": 0, "physical_domain": "THETA_UNCHANGED",
        "interpretation": (
            "Only Jun30/Jul31 can both be retained under shared additive edition "
            "bias and assumed <=0.05min per-cell residual. NOT seven actual errata, "
            "independent instrument measurements, or an orbital constraint."
        ),
    }


def render_lean(r):
    def cases(name, vals):
        conds = " else\n    ".join(
            f"if i.val = {i} then {v}" for i, v in enumerate(vals) if v is not None
        )
        return f"def {name} (i : Fin 9) : Int :=\n  {conds} else 0\n"
    ac = cases("gapAC", r["gap_527_minus_529"])
    ab = cases("gapAB", r["gap_527_minus_528_or_null_if_absent"])
    pair = r["unique_maximal_survivors"]
    vars_by_day = {pair[0]: "hJun", pair[1]: "hJul"}
    terms = []
    for row in r["witness"]["residuals"]:
        x = f'({row["printed"]} - b{row["object"]} - {vars_by_day[row["publication"]]})'
        terms.append(f"(-5 ≤ {x} ∧ {x} ≤ 5)")
    conjunction = " ∧\n      ".join(terms)
    w = r["witness"]
    vals = [w["baselines"][o] for o in [527, 528, 529]]
    vals += [w["offsets"][day] for day in pair]
    witnesses = ", ".join(map(str, vals))
    return f'''import Lean

namespace Conde1963.SsrEditionSurvivors

/-! C241-P21: conditional print-only NASA SSR compilation test.
Publication is NOT an instrument epoch. Missing 528 is never treated as zero.
The gapAB fallback is inaccessible to the tested case (indices both < 5).
No seven real errata demonstrated; Theta remains unchanged. -/

{ac}
{ab}
def within20 (x y : Int) : Prop := -20 ≤ x - y ∧ x - y ≤ 20

/-- If 2 objects share a publication offset at 2 editions, then 4
residuals each bounded by 5 centimin imply a gap change at most 20. -/
theorem gap_change_necessary
    (a1 c1 a2 c2 ba bc h1 h2 : Int)
    (ha1lo : -5 ≤ a1 - ba - h1) (ha1hi : a1 - ba - h1 ≤ 5)
    (hc1lo : -5 ≤ c1 - bc - h1) (hc1hi : c1 - bc - h1 ≤ 5)
    (ha2lo : -5 ≤ a2 - ba - h2) (ha2hi : a2 - ba - h2 ≤ 5)
    (hc2lo : -5 ≤ c2 - bc - h2) (hc2hi : c2 - bc - h2 ≤ 5) :
    within20 (a1 - c1) (a2 - c2) := by
  dsimp [within20]
  omega

/-- Exhaustive classification of all 36 ordered publication pairs, using
527/529 always and 527/528 only when both publications list object 528. -/
theorem unique_pair_under_necessary_screens :
    ∀ (i j : Fin 9), i.val < j.val →
      within20 (gapAC i) (gapAC j) →
      ((i.val < 5 ∧ j.val < 5) → within20 (gapAB i) (gapAB j)) →
      i.val = 1 ∧ j.val = 2 := by
  intro i j hij hac hab
  have hi : i.val < 9 := i.isLt
  have hj : j.val < 9 := j.isLt
  have hi_cases : i.val = 0 ∨ i.val = 1 ∨ i.val = 2 ∨ i.val = 3 ∨
      i.val = 4 ∨ i.val = 5 ∨ i.val = 6 ∨ i.val = 7 ∨ i.val = 8 := by omega
  have hj_cases : j.val = 0 ∨ j.val = 1 ∨ j.val = 2 ∨ j.val = 3 ∨
      j.val = 4 ∨ j.val = 5 ∨ j.val = 6 ∨ j.val = 7 ∨ j.val = 8 := by omega
  rcases hi_cases with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 <;>
    rcases hj_cases with k0 | k1 | k2 | k3 | k4 | k5 | k6 | k7 | k8 <;>
    simp_all [gapAC, gapAB, within20] <;> omega

/-- Any three survivors would contain two different ordered pairs, each
forced to be indices 1 and 2, contradiction. -/
theorem no_three_screened
    (i j k : Fin 9)
    (hij : i.val < j.val) (hjk : j.val < k)
    (acij : within20 (gapAC i) (gapAC j))
    (acjk : within20 (gapAC j) (gapAC k))
    (abij : (i.val < 5 ∧ j.val < 5) → within20 (gapAB i) (gapAB j))
    (abjk : (j.val < 5 ∧ k.val < 5) → within20 (gapAB j) (gapAB k)) :
    False := by
  have h1 := unique_pair_under_necessary_screens i j hij acij abij
  have h2 := unique_pair_under_necessary_screens j k hjk acjk abjk
  omega

/-- Constructive witness for all six printed Jun30/Jul31 cells. -/
theorem june_july_attaining_witness :
    ∃ (b527 b528 b529 hJun hJul : Int),
      {conjunction} := by
  refine ⟨{witnesses}, ?_⟩
  omega

end Conde1963.SsrEditionSurvivors
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    report = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    lean = render_lean(result)
    if args.check:
        if not REPORT.is_file() or REPORT.read_text() != report:
            raise SystemExit("C241-P21 report differs from pinned originals")
        if not LEAN.is_file() or LEAN.read_text() != lean:
            raise SystemExit("C241-P21 Lean differs from pinned originals")
    else:
        REPORT.write_text(report)
        LEAN.write_text(lean)
    print("C241-P21: 9 editions, 23 cells; 2 survivors; no Theta reduction")


if __name__ == "__main__":
    main()
