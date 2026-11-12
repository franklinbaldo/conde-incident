#!/usr/bin/env python3
"""Export explicit documentary ancestry for the site and Lean consumers.

This is a companion to the canonical source-citation feed. It avoids
mutating any frozen large legacy blobs under the project's 20KB policy.
No source is automatically regarded as an independent observation.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

import provenance_graph as pg

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/data/conde-declared-dependence.json"


def declared_paths(source_id: str, edges: list[dict]) -> list[dict]:
    outgoing = defaultdict(list)
    for edge in edges:
        outgoing[edge["from"]].append(edge)
    result = []

    def walk(source: str, path: list[dict]):
        for edge in sorted(outgoing[source], key=lambda x: (x["to"], x["kind"])):
            chain = path + [{
                "from": edge["from"],
                "to": edge["to"],
                "kind": edge["kind"],
            }]
            result.append({
                "upstream_source_id": edge["to"],
                "edges": chain,
            })
            walk(edge["to"], chain)

    walk(source_id, [])
    return sorted(result, key=lambda x: (
        x["upstream_source_id"], len(x["edges"]),
        tuple((e["from"], e["to"], e["kind"]) for e in x["edges"])
    ))


def build(root: Path = ROOT) -> dict:
    """Validate the original ledger and emit only declared links.

    A missing edge is an unresolved documentary relation, not evidence
    that the missing source is distinct or an independent sensor.
    """
    config = json.loads((root / "research/provenance/lineages.json").read_text())
    graph, citations = pg.build(config, pg.MATRIX.read_bytes(), root)
    existing = (root / "public/data/conde-source-citations.json").read_text()
    if pg.serialize(citations) != existing:
        raise ValueError("canonical citation feed out of sync; update it first")
    records = citations["records"]
    matrix_rows = {item["snapshot_ref"]: item
                   for item in graph["matrix_occurrences"]}
    by_source = {s["id"]: s for s in graph["sources"]}
    # A row's hash and line come from the pinned matrix, never inferred from
    # citation text, a reused Cnn label, or a downstream consumer.
    for item in records:
        matrix = matrix_rows[item["snapshot_ref"]]
        if (item["matrix_line"], item["row_sha256"]) != (
                matrix["matrix_line"], matrix["row_sha256"]):
            raise ValueError("citation row identity differs from pinned matrix")
    trace = [{
        "snapshot_ref": item["snapshot_ref"],
        "matrix_line": matrix_rows[item["snapshot_ref"]]["matrix_line"],
        "row_sha256": matrix_rows[item["snapshot_ref"]]["row_sha256"],
        "source_id": item["source_id"],
        "family_id": item["source_family"],
        "declared_upstream_paths": declared_paths(
            item["source_id"], graph["source_dependencies"]),
        "independent_physical_observation_count": None,
    } for item in records]
    groups = defaultdict(lambda: {
        "source_ids": set(), "work_ids": set(), "snapshot_refs": set(),
        "citation_edges": 0,
    })
    for item in records:
        group = groups[item["source_family"]]
        group["source_ids"].add(item["source_id"])
        group["work_ids"].add(item["work_id"])
        group["snapshot_refs"].add(item["snapshot_ref"])
        group["citation_edges"] += 1
    grouped = [{
        "family_id": family,
        "cited_source_ids": sorted(item["source_ids"]),
        "cited_work_ids": sorted(item["work_ids"]),
        "snapshot_refs": sorted(item["snapshot_refs"]),
        "citation_edges": item["citation_edges"],
        "independent_physical_observation_count": None,
    } for family, item in sorted(groups.items())]

    cited_by_occurrence = defaultdict(list)
    for item in trace:
        cited_by_occurrence[item["snapshot_ref"]].append(item)
    contracts = []
    for contract in graph["contracts"]:
        rows = []
        for occ in contract["occurrences"]:
            ref = pg.matrix_ref(occ)
            matched = cited_by_occurrence[ref]
            rows.append({
                "snapshot_ref": ref,
                "matrix_line": matrix_rows[ref]["matrix_line"],
                "row_sha256": matrix_rows[ref]["row_sha256"],
                "citation_status": "CURATED" if matched else "UNMAPPED_NOT_CLEARED",
                "cited_source_ids": sorted({r["source_id"] for r in matched}),
                "declared_upstream_source_ids": sorted({
                    path["upstream_source_id"]
                    for row in matched
                    for path in row["declared_upstream_paths"]
                }),
                "independent_physical_observation_count": None,
            })
        contracts.append({
            "contract_id": contract["id"],
            "contract_path": contract["path"],
            "contract_status": contract["status"],
            "occurrences": rows,
        })
    addenda = [{
        "id": item["id"],
        "source_id": item["source_id"],
        "source_family": by_source[item["source_id"]]["family"],
        "declared_upstream_paths": declared_paths(
            item["source_id"], graph["source_dependencies"]),
        "independent_physical_observation_count": None,
    } for item in graph["post_matrix_occurrences"]]
    return {
        "schema": "conde.declared-documentary-dependence/v1",
        "matrix_git_blob_sha1": graph["matrix_git_blob_sha1"],
        "matrix_snapshot_id": graph["matrix_snapshot_id"],
        "canonical_citations_path": "public/data/conde-source-citations.json",
        "epistemic_limits": {
            "absence_of_edge_does_not_prove_independence": True,
            "family_id_does_not_identify_physical_sensor": True,
            "independent_physical_observation_count": None,
            "verified_reentry_place": None,
            "verified_reentry_time": None,
        },
        "citation_edges": len(trace),
        "curated_occurrences": citations["curated_occurrences"],
        "unmapped_occurrences": citations["unmapped_occurrences"],
        "citation_lineages": trace,
        "independence_groups": grouped,
        "contract_citation_crosswalk": contracts,
        "post_matrix_lineages": addenda,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-site", action="store_true")
    parser.add_argument("--check-site", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.write_site and args.check_site:
        parser.error("write and check are mutually exclusive")
    payload = build()
    content = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")) + "\n"
    if len(content.encode()) > 20_000:
        raise SystemExit("new companion feed exceeds project 20KB policy")
    if args.write_site:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check_site and (not OUTPUT.is_file()
                            or OUTPUT.read_text(encoding="utf-8") != content):
        raise SystemExit("stale documentary dependence feed; use --write-site")
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    print(json.dumps({
        "citation_edges": len(payload["citation_lineages"]),
        "families": len(payload["independence_groups"]),
        "contract_crosswalks": len(payload["contract_citation_crosswalk"]),
        "curated_occurrences": payload["curated_occurrences"],
        "unmapped_occurrences": payload["unmapped_occurrences"],
        "bytes": len(content.encode()),
    }))


if __name__ == "__main__":
    main()
