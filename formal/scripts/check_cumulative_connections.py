#!/usr/bin/env python3
"""Validate accumulated evidence -> observable -> model links.

This is a provenance and dimension check, NOT a physical orbital fit.
Unknown epochs, covariance or reference conventions remain missing. Connected
pending edges are scientific progress even if they do not narrow Theta today.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "research/constraints/ssr_1963_observable_graph.json"
CANONICAL = {"min": ("s", 60.0), "deg": ("rad", math.pi / 180), "km": ("m", 1000.0)}
PENDING = "CANDIDATE_NOT_ACTIVATED"


def validate(graph: dict) -> dict:
    if graph.get("schema") != "conde.cumulative-constraint-graph/v1":
        raise ValueError("unknown cumulative-constraint graph schema")
    sources = {s["id"]: s for s in graph.get("sources", [])}
    params = {p["id"]: p for p in graph.get("parameters", [])}
    ops = {op["id"]: op for op in graph.get("operators", [])}
    obs = graph.get("observations", [])
    if (not sources or not params or not ops or not obs or
        len(sources) != len(graph["sources"]) or
        len(params) != len(graph["parameters"]) or
        len(ops) != len(graph["operators"])):
        raise ValueError("graph missing elements or duplicate source/parameter/operator IDs")
    output = []
    ids = set()
    families = set()
    for o in obs:
        oid = o["id"]
        if oid in ids:
            raise ValueError(f"duplicate observation ID: {oid}")
        ids.add(oid)
        if o["source_id"] not in sources:
            raise ValueError(f"orphan observation source: {oid}")
        src = sources[o["source_id"]]
        if o["source_independence_family"] != src["source_family"]:
            raise ValueError(f"source lineage mismatch: {oid}")
        families.add(src["source_family"])
        if o["forward_operator_id"] not in ops:
            raise ValueError(f"unmapped forward operator: {oid}")
        if not o.get("input_parameters") or any(p not in params for p in o["input_parameters"]):
            raise ValueError(f"orphan parameter link: {oid}")
        if o["unit"] not in CANONICAL:
            raise ValueError(f"unknown physical unit: {oid}")
        number = o["value"]
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number):
            raise ValueError(f"non-finite reported measurement: {oid}")
        if o["observed_at_utc"] is None and "observed_epoch" not in o["pending"]:
            raise ValueError(f"missing epoch not tracked: {oid}")
        if o["measurement_error"] is None and "error_interval" not in o["pending"]:
            raise ValueError(f"unknown uncertainty not tracked: {oid}")
        if not o.get("matrix_local_id") or not o.get("source_independence_family"):
            raise ValueError(f"missing evidence lineage: {oid}")
        if o["constraint_status"] != PENDING:
            if o["observed_at_utc"] is None or o["measurement_error"] is None or o["pending"]:
                raise ValueError(f"cannot activate an underdetermined constraint: {oid}")
            raise ValueError(f"active scientific constraints require a separately validated physical solver: {oid}")
        canonical_unit, factor = CANONICAL[o["unit"]]
        output.append({
            "observation": oid,
            "evidence": o["matrix_local_id"],
            "source": o["source_id"],
            "independence_family": src["source_family"],
            "model_variable": o["variable_id"],
            "operator": o["forward_operator_id"],
            "input_parameters": o["input_parameters"],
            "reported_value": number,
            "reported_unit": o["unit"],
            "canonical_value": number * factor,
            "canonical_unit": canonical_unit,
            "observed_at_utc": o["observed_at_utc"],
            "measurement_error": o["measurement_error"],
            "pending": o["pending"],
            "status": PENDING,
        })
    # Accumulate comparisons between published records without treating
    # publication timestamps as physical observation epochs.
    derived_ids = set()
    compared_pairs = set()
    for edge in graph.get("derived_connections", []):
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id or edge_id in ids or edge_id in derived_ids:
            raise ValueError(f"duplicate or invalid derived edge ID: {edge_id}")
        derived_ids.add(edge_id)
        if edge.get("operator_id") != "difference_between_published_values":
            raise ValueError(f"unexpected derived operator: {edge_id}")
        inputs = edge.get("inputs", [])
        if len(inputs) != 2 or any(item not in ids for item in inputs):
            raise ValueError(f"orphan derived edge: {edge_id}")
        # Reversed subtraction of the same two rows is not a new observation.
        pair = frozenset(inputs)
        if len(pair) != 2 or pair in compared_pairs:
            raise ValueError(f"duplicate derived observation pair: {edge_id}")
        compared_pairs.add(pair)
        left, right = (next(o for o in obs if o["id"] == item) for item in inputs)
        if left["object_id"] != right["object_id"] or left["observable"] != right["observable"]:
            raise ValueError(f"mixed comparison: {edge_id}")
        if left["unit"] != right["unit"] or edge.get("unit") != left["unit"]:
            raise ValueError(f"mixed units in derived comparison: {edge_id}")
        reported_delta = edge.get("derived_arithmetic")
        if (isinstance(reported_delta, bool) or not isinstance(reported_delta, (int, float))
                or not math.isfinite(reported_delta)):
            raise ValueError(f"non-finite or nonnumeric derived arithmetic: {edge_id}")
        delta = right["value"] - left["value"]
        if abs(delta - reported_delta) > 1e-8:
            raise ValueError(f"invalid arithmetic or unit: {edge_id}")
        if edge.get("status") != "CONNECTED_PENDING_EPOCH_AND_COVARIANCE":
            raise ValueError(f"comparison prematurely turned into a physical trend: {edge.get('id')}")
        if "source_specific_observation_epochs" not in edge.get("missing", []):
            raise ValueError(f"missing time caveat in comparison: {edge.get('id')}")
    for edge in graph.get("couplings", []):
        if not edge["parameters"] or any(p not in params for p in edge["parameters"]):
            raise ValueError(f"orphan coupling: {edge['id']}")
        if edge.get("hard_constraint_active"):
            raise ValueError(f"unvalidated coupling active: {edge['id']}")
    # Information accumulates even without narrowing; this is not a 'not run' failure.
    return {
        "schema": "conde.cumulative-constraint-handoff/v1",
        "input_observations": len(obs),
        "connected_observations": len(output),
        "unique_source_families": len(families),
        "latent_parameters": len(params),
        "candidate_constraints_recorded": len(output),
        "derived_connections_recorded": len(graph.get("derived_connections", [])),
        "constraints_activated": 0,
        "physical_domain_status": "PENDING_CALIBRATION_NOT_DISCARDED",
        "observations": output,
        "couplings": graph.get("couplings", []),
        "derived_connections": graph.get("derived_connections", []),
        "next_action": "Resolve epochs/error/forward operators; then activate interval constraints and cross-check independent 527/529 holdouts.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    validated = validate(json.loads(args.input.read_text(encoding="utf-8")))
    result = json.dumps(validated, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    print(json.dumps({
        "connected": validated["connected_observations"],
        "candidate": validated["candidate_constraints_recorded"],
        "derived_connections": validated["derived_connections_recorded"],
        "activated": validated["constraints_activated"],
        "status": validated["physical_domain_status"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
