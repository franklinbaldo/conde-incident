#!/usr/bin/env python3
"""C241-P18: source-deletion influence of the NASA SSR documentary model.

Exact *integer* Chebyshev fits with source-locked April/June/July/August
printed period values. Deleting a published table is a sensitivity exercise:
it is not an independent holdout, a sensor sigma, or a physical state filter.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from formal.scripts import compile_ssr_four_editions as parent

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "research/constraints/C241-P18_ssr_source_influence.json"
LEAN = ROOT / "formal/Conde1963/SsrInfluence.lean"
OBJECTS = ("527", "528", "529")


def need(value: bool, message: str) -> None:
    if not value:
        raise ValueError("C241-P18: " + message)


def fit_at_radius(periods: dict[str, list[int]], objects: tuple[str, ...],
                  editions: tuple[int, ...], radius: int) -> dict | None:
    """Integer difference constraints for printed = object + edition + residual.

    Let x_i=object offset and y_j=-edition offset. For every retained cell,
    p-E <= x_i-y_j <= p+E. Bellman-Ford returns integral potentials or
    proves infeasibility through a negative cycle. No external LP package.
    """
    need(radius >= 0 and len(objects) >= 2 and len(editions) >= 2, "invalid fit")
    need(len(set(objects)) == len(objects) and len(set(editions)) == len(editions),
         "duplicate row or edition")
    need(all(obj in periods for obj in objects), "unknown object")
    need(all(0 <= j < 4 for j in editions), "unknown edition")
    need(all(len(periods[obj]) == 4 for obj in objects), "source panel shape")
    n, m = len(objects), len(editions)
    edges = []
    for i, obj in enumerate(objects):
        for j, ed in enumerate(editions):
            p = periods[obj][ed]
            need(type(p) is int, "noninteger printed cell")
            edges.extend(((n+j, i, p+radius), (i, n+j, radius-p)))
    distances = [0] * (n+m)
    for _ in range(n+m):
        changed = False
        for source, target, weight in edges:
            if distances[target] > distances[source] + weight:
                distances[target] = distances[source] + weight
                changed = True
        if not changed:
            shift = distances[0]
            baselines = {obj: distances[i] - shift for i, obj in enumerate(objects)}
            biases = [shift - distances[n+j] for j in range(m)]
            residuals = {
                obj: [periods[obj][ed] - baselines[obj] - biases[j]
                      for j, ed in enumerate(editions)]
                for obj in objects
            }
            need(all(abs(e) <= radius for rr in residuals.values() for e in rr),
                 "invalid certificate")
            return {"baselines": baselines, "edition_biases": biases,
                    "residuals": residuals}
    return None


def minimum(periods: dict[str, list[int]], objects: tuple[str, ...],
            editions: tuple[int, ...]) -> dict:
    # The upper bound is conservative and finite for these positive
    # centiminute cells; never use a floating-point optimization tolerance.
    lo, hi = 0, 10000
    need(fit_at_radius(periods, objects, editions, hi) is not None,
         "upper feasibility bound failed")
    while lo < hi:
        mid = (lo + hi) // 2
        if fit_at_radius(periods, objects, editions, mid) is None:
            lo = mid + 1
        else:
            hi = mid
    witness = fit_at_radius(periods, objects, editions, lo)
    need(witness is not None and (lo == 0 or
         fit_at_radius(periods, objects, editions, lo-1) is None),
         "nonoptimal radius")
    return {"radius_centiminute": lo, "radius_seconds_tenths": lo*6,
            "objects": list(objects), "editions": list(editions),
            "witness": witness}


def build(docs: tuple[dict, ...]) -> dict:
    # Parent verifies all four contemporary NASA table ledger identities,
    # pinned PDF hashes, object crosswalk, units, uncertainty flags and 12
    # original cells. Reuse the audit, not an unaudited constant array.
    source = parent.build(docs)
    periods = source["printed_period_by_object"]
    all_ed = tuple(range(4))
    full = minimum(periods, OBJECTS, all_ed)
    by_edition = {
        source["source_documents"][i]["publication"]:
            minimum(periods, OBJECTS, tuple(j for j in all_ed if j != i))
        for i in all_ed
    }
    by_object = {
        obj: minimum(periods, tuple(other for other in OBJECTS if other != obj), all_ed)
        for obj in OBJECTS
    }
    need(full["radius_centiminute"] == 20, "parent minimax mismatch")
    need([by_edition[doc["publication"]]["radius_centiminute"]
          for doc in source["source_documents"]] == [10, 20, 20, 13],
         "unexpected edition-deletion sensitivity")
    need([by_object[obj]["radius_centiminute"] for obj in OBJECTS] == [8, 13, 20],
         "unexpected object-deletion sensitivity")
    return {
        "schema": "conde.ssr-three-object-source-influence/v1",
        "id": "C241-P18",
        "parent_id": source["id"],
        "source_documents": source["source_documents"],
        "crosswalk": source["crosswalk"],
        "printed_period_by_object": periods,
        "printed_unit": "0.01 minute (integer centiminute)",
        "model": source["model"],
        "complete_panel": full,
        "leave_one_edition_out": by_edition,
        "leave_one_object_out": by_object,
        "source_priority_result": (
            "April 30 and August 15 1963 facsimiles jointly provide the "
            "20-centiminute extremal bound in this model. Removing April "
            "reduces exact E to 10; removing August to 13; removing June "
            "or July does not reduce E. Verify April/August first. "
            "Other object pairs still reject a 5-centiminute print-only "
            "residual, conditional on the same additive model."
        ),
        "conditional_print_rounding_halfunit_centiminute": 5,
        "publication_date_is_instrument_epoch": False,
        "independent_instrument_observations_added": 0,
        "instrument_sigma": None,
        "physical_admissible_domain": "THETA_UNCHANGED",
        "historical_conclusion": "INDETERMINATE",
        "rejected_edges": [
            "deleted_edition_sensitivity -> historical_sensor_uncertainty",
            "printed_period_change -> drag_coefficient",
            "model_rejection -> orbital_decay_or_impact_site",
            "multiple_compiled_reports -> independent_instrument_samples",
        ],
        "lean_file": str(LEAN.relative_to(ROOT)),
    }


def lower_theorem(name: str, periods: dict[str, list[int]],
                  first: int, last: int, e: int) -> list[str]:
    obj_a, obj_b = "527", "528"
    lines = [
        "/-- Conditional extremal pair: no tracking epoch or sensor precision. -/",
        "theorem " + name,
        "    (baseA baseB hFirst hLast eaFirst eaLast ebFirst ebLast E : Int)",
        f"    (aFirst : {periods[obj_a][first]} = baseA + hFirst + eaFirst)",
        f"    (aLast : {periods[obj_a][last]} = baseA + hLast + eaLast)",
        f"    (bFirst : {periods[obj_b][first]} = baseB + hFirst + ebFirst)",
        f"    (bLast : {periods[obj_b][last]} = baseB + hLast + ebLast)",
    ]
    for residual in ("eaFirst", "eaLast", "ebFirst", "ebLast"):
        lines.extend((f"    ({residual}Lo : -E ≤ {residual})",
                      f"    ({residual}Hi : {residual} ≤ E)"))
    return lines + [f"    : {e} ≤ E := by", "  omega", ""]


def witness_theorem(name: str, periods: dict[str, list[int]], case: dict) -> list[str]:
    indices = case["editions"]
    witness = case["witness"]
    names = ("h0", "h1", "h2")
    basenames = ("baseA", "baseB", "baseC")
    clauses = []
    for i, obj in enumerate(OBJECTS):
        for j, ed in enumerate(indices):
            val = periods[obj][ed]
            residual = witness["residuals"][obj][j]
            clauses.append(f"      ({val} = {basenames[i]} + {names[j]} + ({residual}))")
    values = ([witness["baselines"][obj] for obj in OBJECTS] +
              witness["edition_biases"])
    return [
        "/-- All retained cells attain the certified integer minimax radius. -/",
        "theorem " + name + " :",
        "    ∃ (baseA baseB baseC h0 h1 h2 : Int),",
        " ∧".join(clauses) + " := by",
        "  refine ⟨" + ", ".join(str(v) for v in values) + ", ?_⟩",
        "  omega", "",
    ]


def render_lean(report: dict) -> str:
    p = report["printed_period_by_object"]
    e = report["leave_one_edition_out"]
    lines = [
        "import Lean", "",
        "namespace Conde1963.SsrInfluence", "",
        "/-! C241-P18 conditional *documentary* source-deletion sensitivity.",
        "The dates are editions, not sensor epochs. No physical Theta filter. -/", "",
    ]
    # The two endpoint publications are pivotal for the original E=20.
    cases = [
        ("without_april_needs_ten", "without_april_attains_ten",
         "1963-04-30", 1, 3, 10),
        ("without_august_needs_thirteen", "without_august_attains_thirteen",
         "1963-08-15", 0, 2, 13),
    ]
    for lower, attain, date, i, j, expected in cases:
        case = e[date]
        need(case["radius_centiminute"] == expected, "Lean threshold changed")
        lines += lower_theorem(lower, p, i, j, expected)
        lines += witness_theorem(attain, p, case)
    return "\n".join(lines + ["end Conde1963.SsrInfluence", ""])


def run(check: bool) -> None:
    docs = tuple(json.loads(path.read_text()) for path in parent.LEDGERS)
    result = build(docs)
    blob = json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    proof = render_lean(result)
    if check:
        need(REPORT.read_text() == blob, "source influence report out of sync")
        need(LEAN.read_text() == proof, "Lean proof out of sync")
        parent.run(True)
        print("C241-P18 PASS: source-influence exact certificates; Theta unchanged")
    else:
        REPORT.write_text(blob)
        LEAN.write_text(proof)
        print("C241-P18 generated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    run(parser.parse_args().check)
