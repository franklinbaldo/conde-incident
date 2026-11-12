#!/usr/bin/env python3
"""Compile snapshot-qualified document ancestry for existing Lean contracts.

Consume the Abelha companion, never interpret missing edges as independence and
never activate a physical predicate. Read-only reproducible transform: frozen
matrix -> curated citations -> declared dependence -> executable Lean literals.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import provenance_graph as pg  # noqa: E402
import export_documentary_dependence as depend  # noqa: E402

SOURCE = ROOT / "public/data/conde-declared-dependence.json"
CANONICAL = ROOT / "public/data/conde-source-citations.json"
TARGET = ROOT / "formal/Conde1963/ContractLineage.lean"
SNAPSHOT_REF = re.compile(r"^matrix:([0-9a-f]{40}):C([0-9]{2,3})#([1-9][0-9]*)$")


def string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def ref_components(ref: str, expected_snapshot: str) -> tuple[int, int]:
    match = SNAPSHOT_REF.fullmatch(ref)
    if not match or match.group(1) != expected_snapshot:
        raise ValueError("unqualified or wrong-snapshot matrix occurrence: " + ref)
    return int(match.group(2)), int(match.group(3))


def assemble(companion: dict, canonical: dict, expected: dict) -> tuple[str, dict]:
    # Expected derives from pinned custody, not from a second editable reference.
    if companion != expected:
        raise ValueError("dependency companion differs from independently regenerated custody")
    if canonical["matrix_git_blob_sha1"] != companion["matrix_git_blob_sha1"]:
        raise ValueError("matrix snapshot disagreement between feeds")
    if (companion["schema"] != "conde.declared-documentary-dependence/v1"
        or canonical["matrix_snapshot_id"] != companion["matrix_snapshot_id"]):
        raise ValueError("source schema/snapshot changed")
    cited = {(row["snapshot_ref"], row["source_id"]): row
             for row in canonical["records"]}
    lineages = {(row["snapshot_ref"], row["source_id"]): row
                for row in companion["citation_lineages"]}
    if set(cited) != set(lineages):
        raise ValueError("canonical and companion citation keys differ")
    expected_snapshot = companion["matrix_git_blob_sha1"]
    records = []
    report = {"contracts": 0, "contract_occurrences": 0,
              "contract_citation_links": 0, "declared_upstream_paths": 0,
              "new_numeric_observations": 0, "active_constraints_added": 0}
    seen = set()
    for contract in companion["contract_citation_crosswalk"]:
        report["contracts"] += 1
        for occurrence in contract["occurrences"]:
            report["contract_occurrences"] += 1
            ref = occurrence["snapshot_ref"]
            label, variant = ref_components(ref, expected_snapshot)
            if occurrence["citation_status"] not in ("CURATED", "UNMAPPED_NOT_CLEARED"):
                raise ValueError("unknown citation status")
            if occurrence["citation_status"] == "UNMAPPED_NOT_CLEARED":
                if occurrence["cited_source_ids"] or occurrence["declared_upstream_source_ids"]:
                    raise ValueError("unmapped citation was silently given a source")
                continue
            upstream = set()
            for source_id in occurrence["cited_source_ids"]:
                key = ref, source_id
                if key not in lineages or key not in cited:
                    raise ValueError("contract cites a noncanonical source")
                lineage = lineages[key]
                if lineage["family_id"] != cited[key]["source_family"]:
                    raise ValueError("citation family changed")
                if lineage["independent_physical_observation_count"] is not None:
                    raise ValueError("independent instrument count has been invented")
                path_rows = []
                for path in lineage["declared_upstream_paths"]:
                    edges = path["edges"]
                    if not edges or edges[0]["from"] != source_id:
                        raise ValueError("path does not start at cited source")
                    cursor = source_id
                    for edge in edges:
                        if edge["from"] != cursor:
                            raise ValueError("broken ancestry chain")
                        cursor = edge["to"]
                    if cursor != path["upstream_source_id"]:
                        raise ValueError("path destination differs from last edge")
                    upstream.add(cursor)
                    edge_rows = ", ".join(
                        "{ sourceId := " + string(edge["from"])
                        + ", targetId := " + string(edge["to"])
                        + ", relation := " + string(edge["kind"]) + " }"
                        for edge in edges)
                    path_rows.append("{ ancestorSourceId := " + string(cursor)
                                     + ", edges := #[" + edge_rows + "] }")
                    report["declared_upstream_paths"] += 1
                matrix_ref = ('{ snapshot := ' + string(expected_snapshot)
                              + f', label := {label}, variant := {variant} }}')
                record = ('  { contractId := ' + string(contract["contract_id"])
                          + ', contractStatus := ' + string(contract["contract_status"])
                          + ', matrixRef := ' + matrix_ref
                          + ', sourceId := ' + string(source_id)
                          + ', familyId := ' + string(lineage["family_id"])
                          + ', workId := ' + string(cited[key]["work_id"])
                          + ', ancestry := #[' + ", ".join(path_rows) + '] }')
                records.append(record)
                report["contract_citation_links"] += 1
                seen.add((contract["contract_id"], ref, source_id))
            if sorted(upstream) != occurrence["declared_upstream_source_ids"]:
                raise ValueError("contract's ancestor IDs disagree with declared paths")
    if len(seen) != len(records):
        raise ValueError("duplicate contract/citation/occurrence key")
    if report["contracts"] != 3 or report["contract_occurrences"] != 8:
        raise ValueError("contract inventory changed: re-audit rather than silently accept")
    # These are concrete inputs from two DIFFERENT archives, NOT aliases of C151.
    snapshot_c151 = "matrix:" + expected_snapshot + ":C151#1"
    bridges = {(c["contract_id"], o["snapshot_ref"]): o
               for c in companion["contract_citation_crosswalk"] for o in c["occurrences"]}
    if bridges["C179_C151_BRIDGE", snapshot_c151]["cited_source_ids"] != ["NOAA_IGRA_RECIFE_1963"]:
        raise ValueError("modern C151#1 confused with 154-register legacy C151")
    snapshot_c198 = "matrix:" + expected_snapshot + ":C198#1"
    ntrs = lineages[snapshot_c198, "NTRS_19640001198"]
    if ntrs["declared_upstream_paths"] != [{
        "upstream_source_id": "NASA_SSR_19631115",
        "edges": [{"from": "NTRS_19640001198", "to": "NASA_SSR_19631115",
                   "kind": "catalogue_of_same_work"}],
    }]:
        raise ValueError("NTRS catalogue ancestry lost")
    result = '''import Conde1963.Documentary

/-!
Generated from Abelha's declared-dependence/v1 companion and the pinned
matrix snapshot. These are real documentary chains attached to existing
formal contracts, not new tracking observations, sensors or orbital bounds.
No hand editing: formal/scripts/compile_contract_lineage.py --check.
-/

namespace Conde1963

structure DeclaredDocumentEdge where
  sourceId : String
  targetId : String
  relation : String
  deriving Repr, BEq

structure DeclaredDocumentAncestry where
  ancestorSourceId : String
  edges : Array DeclaredDocumentEdge
  deriving Repr

structure ContractDocumentaryLineage where
  contractId : String
  contractStatus : String
  matrixRef : MatrixRef
  sourceId : String
  familyId : String
  workId : String
  ancestry : Array DeclaredDocumentAncestry
  deriving Repr

def contractDocumentaryLineages : Array ContractDocumentaryLineage := #[
'''+",\n".join(records)+'''
]

end Conde1963
'''
    if len(result.encode("utf-8")) > 20_000:
        raise ValueError("generated Lean exceeds 20,000-byte hard limit")
    return result, report


def main() -> None:
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = p.parse_args()
    expected = depend.build()
    canonical = json.loads(CANONICAL.read_text())
    companion = json.loads(SOURCE.read_text())
    content, report = assemble(companion, canonical, expected)
    if args.check:
        if TARGET.read_text(encoding="utf-8") != content:
            raise SystemExit("stale Lean contract ancestry; re-run --write and inspect diff")
    else:
        TARGET.write_text(content, encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
