#!/usr/bin/env python3
"""C241-P19: minimal printed-cell exceptions in a source-locked NASA SSR panel.

An exception only suspends a *documentary-model* equality: it is NOT a claimed
transcription error, sensor failure, independent observation or orbital filter.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path

from formal.scripts import compile_ssr_four_editions as source
from formal.scripts import compile_ssr_influence as minimax

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "research/constraints/C241-P19_ssr_cell_repairs.json"
LEAN = ROOT / "formal/Conde1963/SsrCellRepairs.lean"
CELLS = tuple((i, j) for i in range(3) for j in range(4))
OBJECTS = minimax.OBJECTS
RADIUS = 5  # +/- 0.05 minute of conditional printed rounding, NOT sensor sigma
EXPECTED_EXCEPTIONS = ((0, 0), (1, 3))


def require(ok: bool, detail: str) -> None:
    if not ok:
        raise ValueError("C241-P19: " + detail)


def fit(periods: dict[str, list[int]], kept: tuple[tuple[int, int], ...],
        radius: int = RADIUS) -> dict | None:
    """Integer difference constraints; Bellman-Ford detects all negative cycles."""
    require(type(radius) is int and radius >= 0, "radius invalid")
    require(set(periods) == set(OBJECTS) and
            all(len(v) == 4 and all(type(x) is int for x in v)
                for v in periods.values()), "panel invalid")
    require(len(set(kept)) == len(kept) and set(kept) <= set(CELLS), "cell indices invalid")
    edges: list[tuple[int, int, int]] = []
    for i, j in kept:
        p = periods[OBJECTS[i]][j]
        edges.extend(((3+j, i, p+radius), (i, 3+j, radius-p)))
    distance = [0]*7
    for _ in range(7):
        changed = False
        for a, b, w in edges:
            if distance[b] > distance[a] + w:
                distance[b] = distance[a] + w
                changed = True
        if not changed:
            shift = distance[0]
            baselines = {name: distance[i]-shift for i, name in enumerate(OBJECTS)}
            offsets = [shift-distance[3+j] for j in range(4)]
            residuals = [
                {"object": OBJECTS[i], "edition_index": j,
                 "printed_centiminute": periods[OBJECTS[i]][j],
                 "residual_centiminute": periods[OBJECTS[i]][j]-baselines[OBJECTS[i]]-offsets[j]}
                for i, j in kept
            ]
            require(all(abs(x["residual_centiminute"]) <= radius for x in residuals),
                    "invalid solver witness")
            return {"baselines": baselines, "edition_offsets": offsets, "retained": residuals}
    return None


def exhaustive_minimum(periods: dict[str, list[int]]) -> dict:
    """Find all optimizers at the first feasible exception count, no heuristic."""
    for deleted_count in range(13):
        solutions = []
        for deleted in combinations(CELLS, deleted_count):
            keep = tuple(c for c in CELLS if c not in deleted)
            witness = fit(periods, keep)
            if witness is not None:
                solutions.append((deleted, witness))
        if solutions:
            return {"minimum_exception_count": deleted_count,
                    "optimal_sets": [{"excluded": [list(c) for c in dropped],
                                      "witness": witness}
                                     for dropped, witness in solutions]}
    raise AssertionError("all-deleted panel must fit")


def contrast(periods: dict[str, list[int]], j: int, k: int) -> int:
    return (periods["527"][j] - periods["528"][j] -
            periods["527"][k] + periods["528"][k])


def build(docs: tuple[dict, ...]) -> dict:
    # Ledger auditor is authoritative for all four PDF identities and 12 cells.
    parent = source.build(docs)
    periods = parent["printed_period_by_object"]
    cert = exhaustive_minimum(periods)
    require(cert["minimum_exception_count"] == 2, "minimum exceptions changed")
    require(len(cert["optimal_sets"]) == 1 and
            cert["optimal_sets"][0]["excluded"] == [list(p) for p in EXPECTED_EXCEPTIONS],
            "unexpected optimal exception location")
    rectangles = []
    for a, b in ((0, 1), (2, 3)):
        value = contrast(periods, a, b)
        require(abs(value) > 4*RADIUS, "independent rectangle no longer falsifies model")
        rectangles.append({
            "editions": [parent["source_documents"][a]["publication"],
                         parent["source_documents"][b]["publication"]],
            "indices": [[0, a], [0, b], [1, a], [1, b]],
            "contrast_centiminute": value,
            "max_abs_contrast_under_print_only_rounding": 4*RADIUS,
        })
    require(set(map(tuple, rectangles[0]["indices"])).isdisjoint(
            set(map(tuple, rectangles[1]["indices"]))),
            "rectangles overlap: invalid lower bound")
    return {
        "schema": "conde.ssr-three-object-minimum-cell-exceptions/v1",
        "id": "C241-P19", "parent_id": parent["id"],
        "source_documents": parent["source_documents"],
        "crosswalk": parent["crosswalk"],
        "printed_period_by_object": periods,
        "printed_unit": parent["unit"],
        "model": parent["model"],
        "conditional_print_rounding_halfunit_centiminute": RADIUS,
        "two_disjoint_contradiction_rectangles": rectangles,
        "exact_enumeration": cert,
        "interpretation": ("Under the restricted common-additive-edition model and "
            "at most 0.05 minute per retained printed cell, any one arbitrary "
            "exception among all 12 cells is insufficient. Exactly two "
            "exceptions are sufficient; the only two-cell deletion set is "
            "527/30-Apr and 528/15-Aug. Exclusions do not prove erroneous "
            "transcription; the common-additive model itself may be false."),
        "source_priority": ["1963-04-30:527", "1963-08-15:528"],
        "independent_instrument_observations_added": 0,
        "publication_date_is_instrument_epoch": False,
        "instrument_sigma": None,
        "physical_admissible_domain": "THETA_UNCHANGED",
        "historical_conclusion": "INDETERMINATE",
        "rejected_edges": [
            "exception_cell -> actual_transcription_error",
            "exception_cell -> sensor_failure",
            "printed_delta -> orbital_force_or_decay_location",
            "compilation_source -> independent_instrument_measurement",
        ],
        "lean_file": str(LEAN.relative_to(ROOT)),
    }


def render_lean(report: dict) -> str:
    p = report["printed_period_by_object"]
    solution = report["exact_enumeration"]["optimal_sets"][0]["witness"]
    cells = [
        (0, 0, "aApr", "baseA", "hApr"), (0, 1, "aJun", "baseA", "hJun"),
        (0, 2, "aJul", "baseA", "hJul"), (0, 3, "aAug", "baseA", "hAug"),
        (1, 0, "bApr", "baseB", "hApr"), (1, 1, "bJun", "baseB", "hJun"),
        (1, 2, "bJul", "baseB", "hJul"), (1, 3, "bAug", "baseB", "hAug"),
    ]
    lines = ["import Lean", "", "namespace Conde1963.SsrCellRepairs", "",
        "/-! C241-P19: original NASA print cells, not measured orbits.",
        "The four dates denote *publications*, never tracking epochs.",
        "The theorem refutes one freely discarded printed cell under the",
        "restricted additive publication-offset model and E=5 centiminutes.",
        "It does not establish any real-world misprint or constrain Theta. -/", "",
        "theorem no_single_print_cell_exception",
        "    (k : Nat) (baseA baseB hApr hJun hJul hAug : Int)",
        "    (eaApr eaJun eaJul eaAug ebApr ebJun ebJul ebAug : Int)"]
    for i,j,name,base,edition in cells:
        idx = 4*i+j
        v = p[OBJECTS[i]][j]
        var = "e"+name
        lines.extend([
            f"    ({name}Eq : k ≠ {idx} → {v} = {base} + {edition} + {var})",
            f"    ({name}Lo : k ≠ {idx} → -{RADIUS} ≤ {var})",
            f"    ({name}Hi : k ≠ {idx} → {var} ≤ {RADIUS})",
        ])
    lines += [
        "    : False := by",
        "  have disjoint : (k ≠ 0 ∧ k ≠ 1 ∧ k ≠ 4 ∧ k ≠ 5) ∨",
        "      (k ≠ 2 ∧ k ≠ 3 ∧ k ≠ 6 ∧ k ≠ 7) := by omega",
        "  rcases disjoint with h | h",
    ]
    for case, names in ((0,("aApr","aJun","bApr","bJun")),
                        (1,("aJul","aAug","bJul","bAug"))):
        lines.append("  " + ("·" if case == 0 else "·"))
        for index, name in enumerate(names):
            path = ("h.1", "h.2.1", "h.2.2.1", "h.2.2.2")[index]
            for suff in ("Eq", "Lo", "Hi"):
                lines.append(f"    have h{name}{suff} := {name}{suff} {path}")
        lines.append("    omega")
    # A second theorem certifies the remaining 10 exact equalities, and all
    # individual +/-5 bounds, with the integer witness from the solver.
    kept = solution["retained"]
    lines.extend(["", "/-- Ten retained cells admit a source-conditional exact integer witness. -/",
       "theorem ten_retained_cells_fit :",
       "    ∃ (baseA baseB baseC hApr hJun hJul hAug : Int),"])
    clauses = []
    basenames = ("baseA", "baseB", "baseC")
    ednames = ("hApr", "hJun", "hJul", "hAug")
    for cell in kept:
        i = OBJECTS.index(cell["object"])
        j = cell["edition_index"]
        e = cell["residual_centiminute"]
        v = cell["printed_centiminute"]
        expr = f"({v} - {basenames[i]} - {ednames[j]})"
        clauses.extend((f"      ({expr} = {e})",f"      (-{RADIUS} ≤ {expr})",
                        f"      ({expr} ≤ {RADIUS})"))
    lines.append(" ∧\n".join(clauses) + " := by")
    w = solution
    vals = [w["baselines"][obj] for obj in OBJECTS] + w["edition_offsets"]
    lines.extend(["  refine ⟨"+", ".join(str(v) for v in vals)+", ?_⟩",
                  "  omega", "", "end Conde1963.SsrCellRepairs", ""])
    return "\n".join(lines)


def run(check: bool) -> None:
    docs = tuple(json.loads(path.read_text()) for path in source.LEDGERS)
    report = build(docs)
    blob = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    lean = render_lean(report)
    if check:
        require(REPORT.read_text() == blob, "report not deterministic")
        require(LEAN.read_text() == lean, "Lean is not source-locked")
        source.run(True)
        print("C241-P19 PASS: minimum 2 cell exceptions, unique set; Theta unchanged")
    else:
        REPORT.write_text(blob)
        LEAN.write_text(lean)
        print("C241-P19 generated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    run(parser.parse_args().check)
