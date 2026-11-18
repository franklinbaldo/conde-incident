"""Read-only, hash-pinned documentary crosswalk. No graph, Lean or simulator writes.

Run: python3 tools/inspect_documentary_overlay.py --check
The registry points to an autonomous feed; loading it is not physical graph ingestion.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = "research/constraints/conde_documentary_overlay_registry_r37.json"
PARENT_PATH = "research/constraints/ssr_1963_observable_graph.json"
FEED_PATH = "public/data/conde-press-nucleus-provenance-r37.json"
FEED_GIT_SHA1 = "3446ff3ef8deb339dfff50bda8cbc9f55bcd545b"

EXPECTED_LINKS = {
    "OCC:CM21658:DENIAL": ("SRC:R79", "DOC:CM21658:P8",
        "EDITORIAL_OUTSIDE_DIARIOS_ASSOCIADOS_UNDERLYING_REPORT_UNDETERMINED"),
    "OCC:CM21661:CURVELLO": ("SRC:R86", "DOC:CM21661:P7",
        "INDEPENDENT_EDITORIAL_EXPERT_COMMENT_NOT_PRIMARY_EYEWITNESS"),
    "OCC:UH00477:STANISLAW": ("SRC:CGEO77", "DOC:UH00477:P7",
        "SATIRE_DEPENDENCY_ON_EARLIER_REPORTS_NOT_ESTABLISHED"),
    "OCC:CORE871:NO_EVENT_HOUR": ("SRC:871-CORE", "DOC:CORE871:READING",
        "SEARCH_RESULT_NOT_HISTORICAL_WITNESS"),
}
EXPECTED_FAMILIES = {
    "SRC:R79": "CORREIO_DA_MANHA",
    "SRC:R86": "CORREIO_DA_MANHA",
    "SRC:CGEO77": "ULTIMA_HORA_NE",
    "SRC:871-CORE": "RESEARCH_SYNTHESIS_NOT_HISTORICAL_WITNESS",
}
KINDS = {"SRC": "SOURCE", "DOC": "DOCUMENT", "OCC": "OCCURRENCE",
         "LATENT": "LATENT", "LEAN": "LEAN_CANDIDATE",
         "PARAM": "SIMULATOR_PARAMETER"}
RELATIONS = {
    ("SOURCE", "DOCUMENT"): {"SOURCE_MANIFEST_OR_BOUNDED_AUDIT"},
    ("DOCUMENT", "OCCURRENCE"): {"DOCUMENTS_CLAIM_OR_SEARCH_RESULT"},
    ("OCCURRENCE", "LATENT"): {
        "DOES_NOT_IDENTIFY_EVENT_HOUR", "DOES_NOT_PROVE_PRIMARY_WITNESS"},
    ("LATENT", "LEAN_CANDIDATE"): {"PREMISE_NOT_ESTABLISHED"},
    ("LEAN_CANDIDATE", "SIMULATOR_PARAMETER"): {"NOT_ACTIVATED"},
}
# Scope and publication dates are edition-specific. Totals are not custody proof.
EXPECTED_DATES = {
    "OCC:CM21658:DENIAL": ("1963-11-10", None),
    "OCC:CM21661:CURVELLO": ("1963-11-14", None),
    "OCC:UH00477:STANISLAW": ("1963-11-14", None),
    "OCC:CORE871:NO_EVENT_HOUR": (None, "2026-11-16"),
}
EXPECTED_COVERAGE = (
    "UH_NE|00472|1963-11-09|1,2,3,4,5,6,7,8,9,10|4,6,9",
    "UH_NE|00473|1963-11-10|1,4,5,6|",
    "UH_NE|00474|1963-11-11|1,2,3,4,6|",
    "UH_NE|00475|1963-11-12|1,4,5,6,7|",
    "UH_NE|00476|1963-11-13|1,4,5,6|",
    "UH_NE|00477|1963-11-14|1,4,5,6,7|",
    "UH_RIO|04200|1963-11-09|1,2,4,6,7,8,9,13|8",
    "UH_RIO|04201|1963-11-11|1,2,4,6,8,12|",
    "UH_RIO|04202|1963-11-12|1,2,4,5,6,8,9,10|",
    "UH_RIO|04203|1963-11-13|1,2,3,4,5,6,8|",
    "UH_RIO|04204|1963-11-14|1,2,3,4,5,6,8,10,16|",
    "CORREIO|21657|1963-11-09|1,2,3,4,5,6,7,8,9,10,11,12,21|",
    "CORREIO|21658|1963-11-10|1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19|",
    "CORREIO|21659|1963-11-12|1,2,3,4,5,6,7,8,9,10,11,12,13,14,15|",
    "CORREIO|21660|1963-11-13|1,2,3,4,5,6,7,8,9,10,11,12|",
    "CORREIO|21661|1963-11-14|1,2,3,4,5,6,7,8,9,10,11,12,13,21|",
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs)


def blob_sha1(raw):
    return hashlib.sha1(f"blob {len(raw)}".encode() + bytes([0]) + raw).hexdigest()


def validate_feed(feed):
    require(feed.get("schema") == "conde.press-nucleus-documentary-bridge/v1", "feed schema")
    require(feed.get("id") == "ABELHA-R37-P1-PRESS-20261117", "feed ID")
    require(feed.get("parent_graph") == PARENT_PATH, "declarative parent path")
    sources = feed["sources"]
    require(len(sources) == 4 and {s["id"] for s in sources} == set(EXPECTED_FAMILIES),
            "source IDs")
    source_map = {s["id"]: s for s in sources}
    for sid, family in EXPECTED_FAMILIES.items():
        require(source_map[sid]["editorial_family"] == family, "editorial family " + sid)
    require(source_map["SRC:871-CORE"]["source_pdf_sha256"] is None
            and source_map["SRC:871-CORE"]["path"] is None, "search synthesis is not historical PDF")

    nodes = feed["nodes"]
    ids = [n["id"] for n in nodes]
    require(len(ids) == len(set(ids)) == 17, "node count/duplicate")
    kinds = {n["id"]: n["kind"] for n in nodes}
    for nid, kind in kinds.items():
        require(KINDS.get(nid.split(":", 1)[0]) == kind, "node type: " + nid)
    for node in nodes:
        if node["kind"] in {"LATENT", "LEAN_CANDIDATE", "SIMULATOR_PARAMETER"}:
            require(node.get("activation") is False, "premature activation")
            if node["kind"] == "LEAN_CANDIDATE":
                require(node.get("status") == "NOT_COMPILED_NOT_PROMOTED", "Lean promotion")
            else:
                require(node.get("value") is None, "invented clock/parameter")

    edges = feed["edges"]
    keys = [(e["source"], e["target"], e["relation"]) for e in edges]
    require(len(keys) == len(set(keys)) == 20, "edge count/duplicate")
    require(all(a in kinds and b in kinds and
                rel in RELATIONS.get((kinds[a], kinds[b]), set())
                for a, b, rel in keys), "orphan, mistyped or promoted edge")
    require(len({(a, b) for a, b, _ in keys}) == 20,
            "duplicate source-target edge")
    edge_set = set(keys)
    expected_terminal = {
        ("LATENT:CONDE:EVENT_HOUR", "LEAN:candidatePressClockCompatibility",
         "PREMISE_NOT_ESTABLISHED"),
        ("LATENT:CONDE:PRIMARY_NEWS_INDEPENDENCE",
         "LEAN:candidatePressClockCompatibility", "PREMISE_NOT_ESTABLISHED"),
        ("LEAN:candidatePressClockCompatibility", "PARAM:reentry_528_time_window",
         "NOT_ACTIVATED"),
        ("LEAN:candidatePressClockCompatibility", "PARAM:reentry_637_time_window",
         "NOT_ACTIVATED"),
    }
    require(expected_terminal <= edge_set, "missing inactive terminal dependency")
    rows = []
    occurrences = feed["occurrences"]
    require(len(occurrences) == 4 and {c["id"] for c in occurrences} == set(EXPECTED_LINKS),
            "occurrence identity/cardinality")
    for occ in sorted(occurrences, key=lambda x: x["id"]):
        oid = occ["id"]
        source, document, independence = EXPECTED_LINKS[oid]
        require((occ["source_id"], occ["doc_id"], occ["source_independence"]) ==
                (source, document, independence), "crosswalk/independence: " + oid)
        require(occ["state"] == "CANDIDATE_NOT_ACTIVATED"
                and occ["active"] is False
                and occ["event_time_utc"] is None
                and occ["named_event_eyewitness"] is None
                and occ["identified_norad_object"] is None, "invented event/activation")
        require((source, document, "SOURCE_MANIFEST_OR_BOUNDED_AUDIT") in edge_set
                and (document, oid, "DOCUMENTS_CLAIM_OR_SEARCH_RESULT") in edge_set,
                "incomplete source-document-occurrence chain: " + oid)
        require((oid, "LATENT:CONDE:EVENT_HOUR", "DOES_NOT_IDENTIFY_EVENT_HOUR") in edge_set
                and (oid, "LATENT:CONDE:PRIMARY_NEWS_INDEPENDENCE",
                     "DOES_NOT_PROVE_PRIMARY_WITNESS") in edge_set, "false physical link")
        require((occ["publication_date"], occ["research_date"]) == EXPECTED_DATES[oid],
                "publication/research date by occurrence: " + oid)
        src = source_map[source]
        rows.append({"occurrence_id": oid, "document_id": document, "source_id": source,
                     "editorial_family": src["editorial_family"],
                     "source_url": src["source_url"],
                     "source_pdf_sha256": src["source_pdf_sha256"],
                     "source_manifest_path": src["path"],
                     "occurrence_type": occ["type"],
                     "source_independence": occ["source_independence"],
                     "publication_date": occ["publication_date"],
                     "research_date": occ["research_date"],
                     "classification": "DOCUMENTARY_ONLY", "physical_observation": False})

    cover = feed["coverage"]
    actual_coverage = tuple(
        "|".join((e["family"], e["edition"], e["publication_date"],
                  ",".join(map(str, e["examined_pdf_pages"])),
                  ",".join(map(str, e["partially_illegible_pdf_pages"]))))
        for e in cover["editions"])
    require(actual_coverage == EXPECTED_COVERAGE, "edition/page custody drift")
    require(all(len(e["examined_pdf_pages"]) == len(set(e["examined_pdf_pages"]))
                and set(e["partially_illegible_pdf_pages"]) <= set(e["examined_pdf_pages"])
                for e in cover["editions"]), "invalid page selection")
    require(len(cover["editions"]) == 16
            and sum(len(e["examined_pdf_pages"]) for e in cover["editions"]) == 144
            and sum(len(e["partially_illegible_pdf_pages"]) for e in cover["editions"]) == 4
            and cover["no_hour_found_in_examined_scope"] is True
            and cover["negative_for_complete_editions"] is False
            and cover["physical_absence_proven"] is False, "bounded negative scope")
    ep = feed["epistemic"]
    indep = feed["independence"]
    require(ep["event_time_utc"] is None
            and ep["physical_constraints_active"] == 0
            and ep["delta_physical_domain"] == 0
            and ep["theta"] == "UNCHANGED"
            and ep["historical_mcmc"] == "NOT_RUN"
            and ep["norad_528_excluded"] is False
            and ep["norad_637_excluded"] is False, "fabricated physical restriction")
    require(indep["independent_instrumental_observations_added"] == 0
            and indep["primary_event_witnesses_identified"] == 0
            and indep["underlying_news_independence_proven"] is False,
            "falsely independent witness")
    return rows


def inspect_registry(root=ROOT):
    registry = decode((root / REGISTRY_PATH).read_bytes())
    require(registry["schema"] == "conde.documentary-overlay-registry/v1", "registry schema")
    require(registry["id"] == "CONDE-PRESS-R37-READONLY-OVERLAY", "registry ID")
    parent = registry["parent_graph"]
    ref = registry["feed"]
    require(parent == {"path": PARENT_PATH, "schema": "conde.cumulative-constraint-graph/v1"},
            "parent identity")
    require(ref == {"path": FEED_PATH, "id": "ABELHA-R37-P1-PRESS-20261117",
                    "schema": "conde.press-nucleus-documentary-bridge/v1",
                    "git_blob_sha1": FEED_GIT_SHA1}, "feed identity")
    require(registry["allowed_effects"] == {
        "physical_observations_added": 0, "physical_bridges_added": 0,
        "physical_domain_delta": 0, "lean_activation": False,
        "simulator_activation": False}, "effect contract")
    require(decode((root / PARENT_PATH).read_bytes())["schema"] ==
            parent["schema"], "parent schema changed")
    raw = (root / FEED_PATH).read_bytes()
    require(blob_sha1(raw) == ref["git_blob_sha1"], "feed blob changed")
    feed = decode(raw)
    rows = validate_feed(feed)
    return {"schema": "conde.documentary-overlay-inspection/v1",
            "registry_id": registry["id"], "feed_git_blob_sha1": ref["git_blob_sha1"],
            "feed_nodes": len(feed["nodes"]), "feed_edges": len(feed["edges"]),
            "documentary_occurrences": len(rows), "parent_added_observations": 0,
            "parent_added_physical_bridges": 0, "delta_physical_domain": 0,
            "parent_ingestion": "NOT_IMPLEMENTED",
            "negative_scope": {
                "examined_editions": 16, "examined_pdf_pages": 144,
                "partially_illegible_pdf_pages": 4,
                "no_hour_found_in_examined_scope": True,
                "physical_absence_proven": False,
                "outside_scope": feed["coverage"]["outside_scope"],
            },
            "crosswalk": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only schema and custody check")
    parser.parse_args()
    print(json.dumps(inspect_registry(), sort_keys=True, ensure_ascii=False))
