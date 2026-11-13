#!/usr/bin/env python3
"""Compile NORAD documentary-source identities to Lean without a 528 sensor edge.

Authoritative input is the audited Abelha/Morcego export, not historical
tracking data. Fail closed on cross-identification or accidental physics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import export_norad_context as export  # noqa: E402

INPUT = ROOT / export.OUTPUT
TARGET = ROOT / "formal/Conde1963/NoradContext.lean"
REF = re.compile(r"matrix:([0-9a-f]{40}):C([0-9]+)#([1-9][0-9]*)\Z")
EXPECTED_IDS = {
    "MOR-NORAD-1961-AGREEMENT": (),
    "MOR-NORAD-1963-NOV12": (687, 688),
    "MOR-NORAD-1963-NOV14": (688,),
    "MOR-NORAD-1964-NOV30-09": (),
    "MOR-NORAD-1964-NOV30-10": (943,),
}
EXPECTED_DATES = {
    "MOR-NORAD-1961-AGREEMENT": ("1961-01-16", None),
    "MOR-NORAD-1963-NOV12": ("1963-11-12", None),
    "MOR-NORAD-1963-NOV14": ("1963-11-14", None),
    "MOR-NORAD-1964-NOV30-09": ("1964-11-30", "1963-11-30"),
    "MOR-NORAD-1964-NOV30-10": ("1964-11-30", "1963-11-30"),
}


def quote(s: str) -> str:
    if not isinstance(s, str):
        raise ValueError("expected string in audited source")
    return json.dumps(s, ensure_ascii=False)


def maybe(v: str | None) -> str:
    return "none" if v is None else f"some {quote(v)}"


def validate(data: dict, regenerated: dict) -> None:
    if data != regenerated or data.get("schema") != "conde.norad-documentary-context/v1":
        raise ValueError("NORAD contextual export is stale or not audited")
    if len(data["records"]) != 5:
        raise ValueError("unexpected count of MOR documentary records")
    ids = [r["source_id"] for r in data["records"]]
    if len(set(ids)) != 5 or set(ids) != set(EXPECTED_IDS):
        raise ValueError("unexpected NORAD documentary source identity")
    occurrences = [r["occurrence_id"] for r in data["records"]]
    if len(set(occurrences)) != 5 or any(x.startswith("C") for x in occurrences):
        raise ValueError("MOR occurrence was misidentified as Cnn")
    for r in data["records"]:
        key = r["source_id"]
        if tuple(r["object_ids_reported_in_this_document"]) != EXPECTED_IDS[key]:
            raise ValueError("catalogue objects changed: 687/688/943 are not 528")
        if (r["source_date"], r["catalogue_date_claim"]) != EXPECTED_DATES[key]:
            raise ValueError("document year or catalogue discrepancy lost")
        if (r["matrix_occurrence_ref"] is not None
            or r["physical_528_constraint"] is not None
            or r["independent_528_physical_observation_count"] is not None
            or r["original_pdf_sha256"] is not None):
            raise ValueError("MOR record gained invented Cnn/528/physical/hash identity")
        if r["role"] != "DOCUMENTARY_CONTEXT_NOT_528_MEASUREMENT":
            raise ValueError("unjustified physical claim")
    if not all(data["epistemic_limits"].get(k) is True for k in
               ("do_not_merge_mor_nor_ids_with_Cnn_matrix_occurrences",
                "no_new_528_trajectory_or_decay_bound",
                "no_source_is_an_observation_of_norad_528")):
        raise ValueError("NORAD epistemic guard was relaxed")
    bridge = data["nasa_norad_policy_bridge"]
    if (bridge["actual_528_measurement_upstream"] is not None or
        bridge["relation"] != "DATA_EXCHANGE_POSSIBLE_NOT_PROOF_OF_MEASUREMENT_LINEAGE"):
        raise ValueError("unverified 528 measurement lineage attached")
    expected = {(197, "NASA_SSR_19631115"), (198, "NTRS_19640001198")}
    refs = set()
    for c in bridge["contextual_matrix_citations"]:
        match = REF.fullmatch(c["snapshot_ref"])
        if not match or match.group(1) != data["matrix_git_blob_sha1"]:
            raise ValueError("non-snapshot-qualified Cnn citation")
        if len(c["row_sha256"]) != 64:
            raise ValueError("unhashed Cnn citation")
        refs.add((int(match.group(2)), c["source_id"]))
    if refs != expected:
        raise ValueError("policy bridge replaced canonical documentary citations")


def assemble(data: dict, regenerated: dict) -> str:
    validate(data, regenerated)
    items = []
    for r in data["records"]:
        ids = ", ".join(map(str, r["object_ids_reported_in_this_document"]))
        items.append("  { occurrenceId := " + quote(r["occurrence_id"])
                     + ", sourceId := " + quote(r["source_id"])
                     + ", sourceDate := " + quote(r["source_date"])
                     + ", cataloguedDate := " + maybe(r["catalogue_date_claim"])
                     + ", reportedObjectIds := #[" + ids + "]"
                     + ", originalPdfSha256 := none"
                     + ", physical528Constraint := none }")
    refs = []
    for c in data["nasa_norad_policy_bridge"]["contextual_matrix_citations"]:
        m = REF.fullmatch(c["snapshot_ref"])
        assert m is not None
        refs.append("  { matrixRef := { snapshot := " + quote(m.group(1))
                    + ", label := " + str(int(m.group(2)))
                    + ", variant := " + str(int(m.group(3))) + " }"
                    + ", sourceId := " + quote(c["source_id"])
                    + ", rowSha256 := " + quote(c["row_sha256"])
                    + ", relation := " + quote(c["relationship"]) + " }")
    return '''import Conde1963.Documentary

/-!
Typed export of Abelha/Morcego's NORAD contextual-source audit, not orbit data.
Only five original documentary source IDs: 1961 policy, two 1963 reports
about objects 687/688, two 1964 originals (one about 943) misdated in catalogue.
C197/C198 are snapshot-qualified contextual citations; no Cnn identity is
assigned to MOR occurrences. This module has NO 528 tracking observations,
calibrated error model, decay-time inference, or active physical constraints.
Generated by formal/scripts/compile_norad_context.py; do not hand edit.
-/

namespace Conde1963

structure NoradContextDocument where
  occurrenceId : String
  sourceId : String
  sourceDate : String
  cataloguedDate : Option String
  reportedObjectIds : Array Nat
  originalPdfSha256 : Option String
  physical528Constraint : Option String
  deriving Repr

structure NoradContextCitation where
  matrixRef : MatrixRef
  sourceId : String
  rowSha256 : String
  relation : String
  deriving Repr

-- "Not mentioned in THESE records" never means "not observed by NORAD".
def noradContextDocuments : Array NoradContextDocument := #[
''' + ",\n".join(items) + '''
]

-- Documentary comparison only; a 1961 data-sharing agreement does not
-- identify the upstream radar or measurement of any 528 TLE.
def noradPolicyContext : String :=
  "DATA_EXCHANGE_POSSIBLE_NOT_PROOF_OF_MEASUREMENT_LINEAGE"

def noradContextCitations : Array NoradContextCitation := #[
''' + ",\n".join(refs) + '''
]

end Conde1963
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    regenerated = export.build()
    if export.serialize(regenerated) != INPUT.read_text(encoding="utf-8"):
        raise ValueError("NORAD export differs from independent source audit build")
    code = assemble(data, regenerated)
    if args.check:
        if TARGET.read_text(encoding="utf-8") != code:
            raise SystemExit("stale generated NoradContext.lean")
    else:
        TARGET.write_text(code, encoding="utf-8")
    print("NORAD_CONTEXT_LEAN", len(code.encode()), "bytes", len(data["records"]), "records")


if __name__ == "__main__":
    main()
