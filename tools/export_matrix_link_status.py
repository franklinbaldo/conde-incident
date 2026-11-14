#!/usr/bin/env python3
"""C241-P28: exact-occurrence inventory of *links*, not of verified events.

Replays the two source-qualified feeds and the published SSG index.  A direct
scientific dependency is not a curated citation; an index gap is not a missing
historic observation.  Never infer independent sensors or activate Theta.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import audit_matrix_coverage as coverage
import export_ssg_evidence_index as ssg
import provenance_graph as pg

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/data/conde-matrix-link-status.json"
STATES = (
    "CURATED_AND_DOCUMENTARY_DEPENDENCY",
    "CURATED_DOCUMENTARY_ONLY",
    "DOCUMENTARY_DEPENDENCY_ONLY_NOT_CURATED",
    "NOT_LINKED_IN_TWO_QUALIFIED_FEEDS",
)


def require(ok: bool, detail: str) -> None:
    if not ok:
        raise ValueError("matrix link status: " + detail)


def classify(rows: list[dict], citations: dict, bridges: dict,
             index_curated: set[str], index_gaps: set[str]) -> dict:
    """Each Cnn#occurrence gets one tier, never a guessed observation."""
    base = coverage.audit(rows, citations, bridges)
    by_ref = {r["snapshot_ref"]: r for r in rows}
    cited = {r["snapshot_ref"] for r in citations["records"]}
    linked = {e["matrix_occurrence"]
              for kind in coverage.BRIDGE_SECTIONS for e in bridges[kind]}
    require(len(index_curated | index_gaps) == len(by_ref)
            and not index_curated & index_gaps
            and index_curated == {by_ref[r]["occurrence"] for r in cited},
            "SSG curated/gap index disagrees with validated citations")
    require(index_curated | index_gaps == {r["occurrence"] for r in rows},
            "SSG index silently dropped or injected a matrix occurrence")
    members = {key: [] for key in STATES}
    for r in rows:
        ref = r["snapshot_ref"]
        state = (STATES[0] if ref in cited and ref in linked else
                 STATES[1] if ref in cited else
                 STATES[2] if ref in linked else STATES[3])
        members[state].append(r["occurrence"])
    require(len(set(sum(members.values(), []))) == len(rows),
            "repeated or unclassified occurrence")
    require(len(members[STATES[2]]) == base["bridge_only"]
            and len(members[STATES[3]]) == base["not_represented_in_these_feeds"]
            and len(members[STATES[0]]) == base["both_feeds"],
            "cross-feed counts do not reconcile")
    # Index's 'unmapped' refers to curated citations, not scientific links.
    require(set(members[STATES[2]]) <= index_gaps,
            "bridge-only occurrences mislabeled as curated in index")
    return {
        "schema": "conde.matrix-link-status/v1",
        "matrix_snapshot_id": pg.MATRIX_SNAPSHOT_ID,
        "classification_scope": [coverage.CITATIONS.name, coverage.OBSERVABLES.name],
        "index_scope": "SSG original curated citations and explicitly unmapped rows",
        "matrix_occurrences": len(rows),
        "index_curated_occurrences": len(index_curated),
        "index_uncurated_occurrences": len(index_gaps),
        "reconciled_direct_links": base["represented_in_either"],
        "categories": members,
        "counts": {key: len(value) for key, value in members.items()},
        "scientific_links_in_index_uncurated": members[STATES[2]],
        "epistemic_limits": {
            "classification_is_not_a_proof_of_source_independence": True,
            "not_linked_does_not_mean_missing_historical_evidence": True,
            "documentary_dependency_does_not_mean_instrumental_measurement": True,
            "nasa_ntrs_and_ssr_can_refer_to_same_work": True,
            "physical_domain_effect": "THETA_UNCHANGED",
            "new_instrumental_observations": 0,
            "new_lean_physical_predicates": 0,
        },
    }


def rebuild(root: Path = ROOT) -> dict:
    # Rebuild upstream exports independently and check the actual published
    # bytes. This is not a text search for Cnn patterns in arbitrary JSON.
    coverage.rebuild(root)
    all_artifacts = ssg.build(root)
    for path, expected in all_artifacts.items():
        target = root / path
        require(target.is_file() and target.read_bytes() == expected,
                "published SSG shard or manifest differs from original source: " + str(path))
    manifest = json.loads((root / "public/data/conde-evidence-index-manifest.json").read_bytes())
    require(manifest["schema"] == "conde.evidence-index/v1"
            and manifest["matrix_git_blob_sha1"] == pg.MATRIX_BLOB_SHA,
            "index snapshot/schema changed")
    curated, gaps = set(), set()
    for shard in manifest["shards"]:
        data = json.loads((root / shard["path"]).read_bytes())
        require(data["schema"] == "conde.evidence-index-shard/v1", "invalid curated index shard")
        for item in data["records"]:
            curated.add(item["occurrence"])
    for shard in manifest["unmapped_shards"]:
        data = json.loads((root / shard["path"]).read_bytes())
        require(data["schema"] == "conde.evidence-gap-shard/v1", "invalid uncurated index shard")
        for item in data["records"]:
            require(item["occurrence"] not in gaps, "duplicate uncurated occurrence")
            gaps.add(item["occurrence"])
    rows = pg.matrix_occurrences((root / pg.MATRIX.relative_to(ROOT)).read_bytes())
    return classify(
        rows,
        json.loads((root / coverage.CITATIONS.relative_to(ROOT)).read_bytes()),
        json.loads((root / coverage.OBSERVABLES.relative_to(ROOT)).read_bytes()),
        curated, gaps)


def encode(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_mutually_exclusive_group()
    commands.add_argument("--write-site", action="store_true")
    commands.add_argument("--check-site", action="store_true")
    args = p.parse_args()
    result = encode(rebuild())
    require(len(result) < 20_000, "output exceeds 20 KB")
    if args.write_site:
        OUTPUT.write_bytes(result)
    elif args.check_site:
        require(OUTPUT.read_bytes() == result, "published crosswalk is stale")
    else:
        print(result.decode(), end="")


if __name__ == "__main__":
    main()
