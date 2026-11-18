#!/usr/bin/env python3
"""Load byte-pinned documentary overlays without changing physical observations.

The output is a separate, typed documentary index. It is NOT an orbital
observation, Lean proof, or a new constraint on 528/637.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = Path("research/constraints/documentary_overlay_registry.json")
SITE = Path("public/data/conde-documentary-overlay-index.json")
KINDS = {
    "SRC": "SOURCE",
    "DOC": "DOCUMENT",
    "OCC": "OCCURRENCE",
    "LATENT": "LATENT",
    "LEAN": "LEAN_CANDIDATE",
    "PARAM": "SIMULATOR_PARAMETER",
}
RELATIONS = {
    ("SOURCE", "DOCUMENT"): {"SOURCE_MANIFEST_OR_BOUNDED_AUDIT"},
    ("DOCUMENT", "OCCURRENCE"): {"DOCUMENTS_CLAIM_OR_SEARCH_RESULT"},
    ("OCCURRENCE", "LATENT"): {
        "DOES_NOT_IDENTIFY_EVENT_HOUR", "DOES_NOT_PROVE_PRIMARY_WITNESS"
    },
    ("LATENT", "LEAN_CANDIDATE"): {"PREMISE_NOT_ESTABLISHED"},
    ("LEAN_CANDIDATE", "SIMULATOR_PARAMETER"): {"NOT_ACTIVATED"},
}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(data: bytes) -> dict:
    value = json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs)
    require(isinstance(value, dict), "expected JSON object")
    return value


def safe_file(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and relative and
            not Path(relative).is_absolute(), "invalid relative path")
    root = root.resolve()
    file = (root / relative).resolve()
    require(file.is_relative_to(root) and file.is_file(), "missing or unsafe file: " + relative)
    return file


def load_index(root: Path = ROOT, registry: dict | None = None) -> dict:
    root = root.resolve()
    if registry is None:
        registry = read_json(safe_file(root, str(REGISTRY)).read_bytes())
    require(registry.get("schema") == "conde.documentary-overlay-registry/v1", "registry schema")
    parent_path = registry.get("parent_graph")
    require(parent_path == "research/constraints/ssr_1963_observable_graph.json",
            "unexpected parent graph")
    parent = read_json(safe_file(root, parent_path).read_bytes())
    require(parent.get("schema") == "conde.cumulative-constraint-graph/v1",
            "parent schema")
    before_observations = len(parent["observations"])
    before_bridges = len(parent["physical_bridges"])
    all_nodes: dict[str, dict] = {}
    all_edges: set[tuple[str, str, str]] = set()
    crosswalk: list[dict] = []
    loaded: dict[str, tuple[str, str]] = {}
    feed_receipts: list[dict] = []
    feeds = registry.get("feeds")
    require(isinstance(feeds, list) and bool(feeds), "empty or invalid registry")
    for ref in feeds:
        feed_id, path, digest = ref["id"], ref["path"], ref["sha256"]
        require(isinstance(digest, str) and len(digest) == 64 and
                all(c in "0123456789abcdef" for c in digest), "invalid SHA-256")
        previous = loaded.get(feed_id)
        if previous is not None:
            require(previous == (path, digest), "conflicting duplicate feed id")
            continue  # import is idempotent
        raw = safe_file(root, path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, "documentary feed SHA-256 mismatch")
        feed = read_json(raw)
        require(feed.get("id") == feed_id and feed.get("schema") == ref["schema"],
                "feed identity or schema")
        require(feed.get("parent_graph") == parent_path, "feed parent reference")
        nodes = feed["nodes"]
        edges = feed["edges"]
        occurrences = feed["occurrences"]
        sources = feed["sources"]
        require(len(nodes) == ref["nodes"] and len(edges) == ref["edges"] and
                len(occurrences) == ref["occurrences"], "feed cardinality")
        kinds: dict[str, str] = {}
        for node in nodes:
            node_id = node["id"]
            require(isinstance(node_id, str) and ":" in node_id, "invalid node id")
            kind = KINDS.get(node_id.split(":", 1)[0])
            require(node["kind"] == kind and node_id not in kinds, "node class or duplicate id")
            kinds[node_id] = kind
            if kind in {"LATENT", "SIMULATOR_PARAMETER"}:
                require(node.get("value") is None and node.get("activation") is False,
                        "physical node promoted")
            if kind == "LEAN_CANDIDATE":
                require(node.get("status") == "NOT_COMPILED_NOT_PROMOTED" and
                        node.get("activation") is False, "Lean candidate promoted")
        edge_keys = set()
        for edge in edges:
            src, dst, rel = edge["source"], edge["target"], edge["relation"]
            require(src in kinds and dst in kinds, "orphan documentary edge")
            require(rel in RELATIONS.get((kinds[src], kinds[dst]), set()),
                    "invalid documentary edge or physical promotion")
            key = (src, dst, rel)
            require(key not in edge_keys, "duplicate edge within feed")
            edge_keys.add(key)
        source_map = {s["id"]: s for s in sources}
        require(len(source_map) == len(sources), "duplicate source")
        occurrence_ids = set()
        for occurrence in occurrences:
            oid, sid, doc = occurrence["id"], occurrence["source_id"], occurrence["doc_id"]
            require(oid not in occurrence_ids and kinds.get(oid) == "OCCURRENCE",
                    "duplicate or unknown occurrence")
            occurrence_ids.add(oid)
            require(sid in source_map and kinds.get(sid) == "SOURCE" and
                    kinds.get(doc) == "DOCUMENT", "orphan source or document")
            require((sid, doc, "SOURCE_MANIFEST_OR_BOUNDED_AUDIT") in edge_keys and
                    (doc, oid, "DOCUMENTS_CLAIM_OR_SEARCH_RESULT") in edge_keys,
                    "missing occurrence provenance path")
            require(occurrence.get("event_time_utc") is None and
                    occurrence.get("named_event_eyewitness") is None and
                    occurrence.get("identified_norad_object") is None and
                    occurrence.get("active") is False and
                    occurrence.get("state") == "CANDIDATE_NOT_ACTIVATED",
                    "documentary occurrence promoted to physical observation")
            source = source_map[sid]
            if feed_id == "ABELHA-R37-P1-PRESS-20261117":
                # A 2026 research synthesis is not a 1963 newspaper edition.
                if sid == "SRC:871-CORE":
                    require(occurrence["publication_date"] is None and
                            occurrence["research_date"] == "2026-11-16",
                            "research date promoted to publication date")
                else:
                    require(occurrence["publication_date"] in {
                        "1963-11-10", "1963-11-14"
                    } and occurrence["research_date"] is None,
                            "historical publication date conflated with research")
            crosswalk.append({
                "feed_id": feed_id,
                "occurrence_id": oid,
                "document_id": doc,
                "source_id": sid,
                "editorial_family": source["editorial_family"],
                "source_url": source["source_url"],
                "source_pdf_sha256": source["source_pdf_sha256"],
                "publication_date": occurrence["publication_date"],
                "research_date": occurrence["research_date"],
                "occurrence_type": occurrence["type"],
                "source_independence": occurrence["source_independence"],
                "state": occurrence["state"],
            })
        require(occurrence_ids == set(ref["occurrence_ids"]), "occurrence identity drift")
        indep = feed["independence"]
        ep = feed["epistemic"]
        require(indep["independent_instrumental_observations_added"] == 0 and
                indep["primary_event_witnesses_identified"] == 0 and
                indep["underlying_news_independence_proven"] is False,
                "fabricated independent observation")
        require(ep["event_time_utc"] is None and ep["physical_constraints_active"] == 0 and
                ep["delta_physical_domain"] == 0 and ep["theta"] == "UNCHANGED" and
                ep["historical_mcmc"] == "NOT_RUN" and
                ep["norad_528_excluded"] is False and
                ep["norad_637_excluded"] is False,
                "physical inference incorrectly activated")
        require(ep["delta_links"] == len(edges), "documentary link count mismatch")
        if feed_id == "ABELHA-R37-P1-PRESS-20261117":
            coverage = feed["coverage"]
            require(len(coverage["editions"]) == 16 and
                    coverage["examined_pdf_pages_total"] == 144 and
                    coverage["partially_illegible_pages_total"] == 4 and
                    coverage["no_hour_found_in_examined_scope"] is True and
                    coverage["negative_for_complete_editions"] is False and
                    coverage["physical_absence_proven"] is False,
                    "bounded search promoted to historical absence")
            require(source_map["SRC:R79"]["editorial_family"] ==
                    source_map["SRC:R86"]["editorial_family"] ==
                    "CORREIO_DA_MANHA", "Correio duplicate editorial family")
            require(source_map["SRC:871-CORE"]["editorial_family"] ==
                    "RESEARCH_SYNTHESIS_NOT_HISTORICAL_WITNESS",
                    "research summary promoted to contemporary source")
        for node in nodes:
            old = all_nodes.get(node["id"])
            require(old is None or old == node, "cross-feed node id conflict")
            all_nodes[node["id"]] = node
        all_edges.update(edge_keys)
        loaded[feed_id] = (path, digest)
        feed_receipts.append({"id": feed_id, "path": path, "schema": feed["schema"],
                              "sha256": digest, "nodes": len(nodes),
                              "edges": len(edges), "occurrences": len(occurrences)})
    return {
        "schema": "conde.documentary-overlay-index/v1",
        "parent_graph": parent_path,
        "parent_graph_schema": parent["schema"],
        "interpretation": "DOCUMENTARY_ONLY_NOT_PHYSICAL_OBSERVATIONS",
        "feeds": sorted(feed_receipts, key=lambda r: r["id"]),
        "nodes": [{"feed_node_id": key, **node} for key, node in sorted(all_nodes.items())],
        "edges": [{"source": s, "target": t, "relation": r}
                  for s, t, r in sorted(all_edges)],
        "occurrence_crosswalk": sorted(crosswalk, key=lambda item: item["occurrence_id"]),
        "counts": {
            "documentary_nodes": len(all_nodes),
            "documentary_edges": len(all_edges),
            "documentary_occurrences": len(crosswalk),
            "parent_observations_before": before_observations,
            "parent_observations_after": before_observations,
            "parent_physical_bridges_before": before_bridges,
            "parent_physical_bridges_after": before_bridges,
            "parent_added_observations": 0,
            "parent_added_physical_bridges": 0,
            "delta_physical_domain": 0,
        },
    }


def serialize(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write-site", action="store_true")
    group.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    content = serialize(load_index())
    target = ROOT / SITE
    if args.write_site:
        target.write_text(content, encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)}")
    else:
        require(read_json(target.read_bytes()) == load_index(),
                "generated documentary overlay index differs")
        print("documentary overlay index unchanged; physical domain unchanged")


if __name__ == "__main__":
    main()
