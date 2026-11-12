#!/usr/bin/env python3
"""Import curated Cnn#occurrence documentary lineage into a Lean DATA contract.

The generated Lean rows are NOT empirical proofs. They link snapshot-qualified
matrix occurrences and 528's six mirrored elements to the primary/secondary
documentary custody. No unfounded hard constraints are activated.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.provenance_graph import build, MATRIX, LINEAGES, SITE, serialize  # noqa: E402

GRAPH = ROOT / "research/constraints/ssr_1963_observable_graph.json"
TARGET = ROOT / "formal/Conde1963/Documentary.lean"
REFERENCE = re.compile(r"^C(0?[1-9]|[1-9][0-9]{1,2})#([1-9][0-9]*)$")


def ref_parts(label: str, known: set[str]) -> tuple[int, int]:
    match = REFERENCE.fullmatch(label)
    if match is None or label not in known:
        raise ValueError("unresolved or ambiguous Cnn#occurrence: " + repr(label))
    return int(match[1]), int(match[2])


def lean_str(v: str) -> str:
    return json.dumps(v, ensure_ascii=False)


def assemble(lineages: dict, raw: bytes, graph: dict) -> tuple[str, dict]:
    documentary, feed = build(lineages, raw, root=ROOT)
    rows = documentary["matrix_occurrences"]
    known = {r["occurrence"] for r in rows}
    src = {r["id"]: r for r in documentary["sources"]}
    citation_records = feed["records"]
    distinct_curated = {record["occurrence"] for record in citation_records}
    if (len(rows) != 241 or len(distinct_curated) < 24 or
            feed["curated_occurrences"] != len(distinct_curated) or
            feed["unmapped_occurrences"] != len(rows) - len(distinct_curated)):
        raise ValueError("unexpected corpus coverage: re-audit inventory")
    refs = []
    for record in citation_records:
        num, variant = ref_parts(record["occurrence"], known)
        if record["source_id"] not in src:
            raise ValueError("unresolved source")
        refs.append(
            '  { matrixRef := { snapshot := '+lean_str(feed["matrix_git_blob_sha1"])
            + f', label := {num}, variant := {variant} }}, matrixLine := {record["matrix_line"]}'
            + ', rowSha256 := ' + lean_str(record["row_sha256"])
            + ', sourceId := ' + lean_str(record["source_id"])
            + ', sourceFamily := ' + lean_str(record["source_family"])
            + ', workId := ' + lean_str(record["work_id"])
            + ', relation := ' + lean_str(record["relation"])
            + ', scope := ' + lean_str(record["scope"]) + ' }'
        )
    curated = {row["occurrence"]: row for row in citation_records}
    nasa = curated["C197#1"]
    ntrs = curated["C198#1"]
    mirror = curated["C179#1"]
    if (nasa["source_id"] != "NASA_SSR_19631115" or
        nasa["scope"] != "CATALOGUED_DAY_ONLY" or
        ntrs["source_id"] != "NTRS_19640001198" or
        ntrs["work_id"] != nasa["work_id"] or
        ntrs["source_family"] != nasa["source_family"] or
        mirror["source_id"] != "AFSPC_MIRROR_528" or
        mirror["relation"] != "secondary_orbital_elements"):
        raise ValueError("critical C179/C197/C198 custody or shared work lost")
    key = "AFSPC-SECONDARY-528-1963-10-27"
    sources = {s["id"]: s for s in graph["sources"]}
    if sources[key]["evidence_occurrence"] != "C179#1":
        raise ValueError("orbital graph lost C179#1 physical bridge")
    if sources[key]["upstream_tracking_family"] != "NORAD_AFS_SHARED_TRACKING_NOT_INDEPENDENT":
        raise ValueError("C179 tracking lineage changed")
    linked = [x for x in graph["observations"] if x["object_id"] == 528]
    if len(linked) != 6 or {x["observable"] for x in linked} != {
        "inclination", "raan", "eccentricity", "arg_perigee", "mean_anomaly", "mean_motion"
    }:
        raise ValueError("528 mirrored six-field inventory changed")
    fields = []
    for record in sorted(linked, key=lambda row: row["observable"]):
        if (record["source_id"] != key or record["matrix_local_id"] != "C179#1"
            or record["constraint_status"] != "CANDIDATE_NOT_ACTIVATED"
            or record["observed_at_utc"] is not None or record["measurement_error"] is not None
            or record["element_epoch_utc"] != "1963-10-27T14:40:16.132512Z"
            or record["source_independence_family"] != "SECONDARY_MIRROR_AFSPC_ATTRIBUTED_TLE"):
            raise ValueError("528 physical field prematurely promoted or corrupted")
        fields.append(
            '  { source := { snapshot := '+lean_str(feed["matrix_git_blob_sha1"])
            + ', label := 179, variant := 1 }, norad := 528'
            + ', field := '+lean_str(record["observable"])
            + ', reportedDecimal := '+lean_str(str(record["value"]))
            + ', unit := '+lean_str(record["unit"])
            + ', elementEpochUtc := '+lean_str(record["element_epoch_utc"])
            + ', provenanceSource := "AFSPC_MIRROR_528", calibrationStatus := "CONNECTED_PENDING_CALIBRATION" }'
        )
    if SITE.read_text(encoding="utf-8") != serialize(feed):
        raise ValueError("stale site citation feed; update provenance first")
    out = f'''import Conde1963.Core

/-!
AUTOGENERATED by formal/scripts/compile_documentary_links.py.
Documentary custody only: {len(refs)} curated citations across {len(distinct_curated)} occurrences from {len(rows)} rows.
Source: frozen matrix git blob {feed["matrix_git_blob_sha1"]}.
Original NORAD tracker observations and covariance not recovered.
Do not edit this file by hand; do not treat this as a proof of orbital impact.
-/

namespace Conde1963

structure MatrixRef where
  snapshot : String
  label : Nat
  variant : Nat
  deriving Repr, BEq

structure DocumentaryCitation where
  matrixRef : MatrixRef
  matrixLine : Nat
  rowSha256 : String
  sourceId : String
  sourceFamily : String
  workId : String
  relation : String
  scope : String
  deriving Repr

def documentaryCitations : Array DocumentaryCitation := #[
{",\n".join(refs)}
]

-- Typed handoff to Castor: these are SECONDARY catalogued TLE element
-- literals, not calibrated tracking samples. The 284.1520° legacy RAAN
-- has no instrument record and is deliberately absent here.
structure MirroredElement where
  source : MatrixRef
  norad : Nat
  field : String
  reportedDecimal : String
  unit : String
  elementEpochUtc : String
  provenanceSource : String
  calibrationStatus : String
  deriving Repr

def mirrored528Elements : Array MirroredElement := #[
{",\n".join(fields)}
]

end Conde1963
'''
    report = {
        "matrix_occurrences": len(rows),
        "curated_documentary_links": len(refs),
        "curated_documentary_occurrences": len(distinct_curated),
        "unmapped_documentary_occurrences": feed["unmapped_occurrences"],
        "secondary_528_fields": len(fields),
        "provenance_work_count_for_C197_C198": len({nasa["work_id"],ntrs["work_id"]}),
        "linked_physical_source": "C179#1",
        "no_new_physical_constraint": True,
    }
    return out, report


def main() -> None:
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = p.parse_args()
    code, stats = assemble(json.loads(LINEAGES.read_text(encoding="utf-8")),
                           MATRIX.read_bytes(),
                           json.loads(GRAPH.read_text(encoding="utf-8")))
    if args.check:
        if TARGET.read_text(encoding="utf-8") != code:
            raise SystemExit("Lean documentary linkage is stale; run --write, inspect diff")
    else:
        TARGET.write_text(code, encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
