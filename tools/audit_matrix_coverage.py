#!/usr/bin/env python3
"""Scope-limited, occurrence-aware coverage audit for the frozen 241-row matrix.

Only two explicit, independently replayed contracts are counted:
the curated citation feed and the observable-dependency feed. Other scientific
bridges may exist; absence from these TWO feeds is not missing historical data,
nor evidence against reentry in Conde. No free-text matching promotes a source.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import provenance_graph as pg
import export_observable_dependency_links as observable

ROOT = Path(__file__).resolve().parents[1]
CITATIONS = ROOT / "public/data/conde-source-citations.json"
OBSERVABLES = ROOT / "public/data/conde-observable-dependency-links.json"
BRIDGE_SECTIONS = ("edges", "pending_december_compilation_edges")


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("matrix coverage: " + reason)


def audit(rows: list[dict], citations: dict, bridges: dict) -> dict:
    by_ref = {row["snapshot_ref"]: row for row in rows}
    require(len(rows) == 241 and len(by_ref) == 241,
            "matrix cardinality or snapshot-unique IDs changed")
    require(citations.get("schema") == "conde.source-citations/v1"
            and bridges.get("schema") == "conde.observable-dependency-links/v1",
            "feed schema changed")
    require(citations.get("matrix_git_blob_sha1") == pg.MATRIX_BLOB_SHA
            and bridges.get("matrix_git_blob_sha1") == pg.MATRIX_BLOB_SHA,
            "cross-snapshot reference forbidden")
    require(citations.get("total_matrix_occurrences") == len(rows),
            "citation inventory differs from frozen matrix")
    curated = set()
    for item in citations["records"]:
        ref = item.get("snapshot_ref")
        # post-matrix records use their own source IDs and never count toward 241
        require(ref in by_ref and item.get("occurrence") == by_ref[ref]["occurrence"],
                "citation without canonical matrix occurrence")
        require(item.get("row_sha256") == by_ref[ref]["row_sha256"]
                and item.get("matrix_line") == by_ref[ref]["matrix_line"],
                "citation row hash or line drift")
        # Multiple curated citations may support the *same* matrix claim.
        # Count unique source occurrences, not citation edges.
        curated.add(ref)
    require(citations.get("curated_occurrences") == len(curated)
            and citations.get("unmapped_occurrences") == len(rows) - len(curated),
            "citation counts diverge")

    bridged = set()
    n_edges = 0
    for section in BRIDGE_SECTIONS:
        require(isinstance(bridges.get(section), list), "bridge section missing")
        for edge in bridges[section]:
            ref = edge.get("matrix_occurrence")
            require(ref in by_ref, "bridge contains missing or unsnapshotted claim")
            require(edge.get("matrix_line") == by_ref[ref]["matrix_line"],
                    "bridge line disagrees with matrix")
            if "matrix_row_sha256" in edge:
                require(edge["matrix_row_sha256"] == by_ref[ref]["row_sha256"],
                        "bridge row sha disagrees with matrix")
            # An edge is not a physical measurement and cannot grant domain reduction.
            require(edge.get("activation") is False,
                    "one uncalibrated documentary edge activated as physical constraint")
            if section == "pending_december_compilation_edges":
                require(edge.get("independent_sensor") is False
                        and edge.get("instrument_epoch_utc") is None
                        and edge.get("instrument_covariance") is None
                        and edge.get("physical_domain_effect") == "THETA_UNCHANGED",
                        "December compilation promoted to instrument")
            bridged.add(ref)
            n_edges += 1
    # Do not count pending_documentary_edges: they refer to C197#1 only as
    # unqualified context, rather than content-addressed source occurrences.
    missing = [row for row in rows
               if row["snapshot_ref"] not in curated | bridged]
    return {
        "schema": "conde.matrix-two-feed-coverage-audit/v1",
        "matrix_snapshot_id": pg.MATRIX_SNAPSHOT_ID,
        "scope": ["conde-source-citations.json",
                  "conde-observable-dependency-links.json"],
        "scope_limit": ("NOT a complete audit of all project bridges; no automatic"
                        " source inference, no physical filtering, no claim of missing evidence"),
        "matrix_occurrences": len(rows),
        "curated_occurrences": len(curated),
        "bridge_occurrences": len(bridged),
        "bridge_edges": n_edges,
        "both_feeds": len(curated & bridged),
        "bridge_only": len(bridged - curated),
        "represented_in_either": len(curated | bridged),
        "not_represented_in_these_feeds": len(missing),
        "bridge_only_occurrence_ids": sorted(by_ref[r]["occurrence"] for r in bridged-curated),
        "not_represented_ids": [r["occurrence"] for r in missing],
        "activated_physical_constraints_from_these_bridges": 0,
    }


def rebuild(root: Path = ROOT) -> dict:
    rows = pg.matrix_occurrences((root / pg.MATRIX.relative_to(ROOT)).read_bytes())
    config = json.loads((root / pg.LINEAGES.relative_to(ROOT)).read_bytes())
    _, original_citations = pg.build(config, (root / pg.MATRIX.relative_to(ROOT)).read_bytes())
    current_bridges = observable.build(root)
    cite_bytes = pg.serialize(original_citations).encode()
    dep_bytes = observable.encoded(current_bridges)
    require((root / CITATIONS.relative_to(ROOT)).read_bytes() == cite_bytes,
            "curated feed stale; regenerate original exporter")
    require((root / OBSERVABLES.relative_to(ROOT)).read_bytes() == dep_bytes,
            "dependency feed stale; regenerate original exporter")
    return audit(rows, original_citations, current_bridges)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list-unrepresented", action="store_true")
    args = ap.parse_args()
    result = rebuild()
    if not args.list_unrepresented:
        result.pop("not_represented_ids")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
