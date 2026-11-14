#!/usr/bin/env python3
"""Scope-limited, occurrence-aware coverage audit for the frozen 241-row matrix.

Only two explicit, independently replayed contracts contribute to DIRECT
coverage: the curated citation feed and the observable-dependency feed.
Additional archival and cartographic feeds are revalidated as contextual layers
without inflating direct coverage. Their absence is not missing historical data,
nor evidence against reentry in Conde. No free-text matching promotes a source.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import provenance_graph as pg
import export_observable_dependency_links as observable
import export_wayback_citation_links as wayback
import export_cgeo35_raster_bridge as cgeo35
import export_fbis_operational_lineage as fbis

ROOT = Path(__file__).resolve().parents[1]
CITATIONS = ROOT / "public/data/conde-source-citations.json"
OBSERVABLES = ROOT / "public/data/conde-observable-dependency-links.json"
BRIDGE_SECTIONS = ("edges", "pending_december_compilation_edges")
ARCHIVE = ROOT / "public/data/conde-wayback-citation-links.json"
CARTOGRAPHY = ROOT / "public/data/conde-cgeo35-raster-anchor-bridge.json"
FBIS = fbis.OUTPUT


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


def audit_context_layers(rows: list[dict], citations: dict,
                         archive: dict, cartography: dict) -> dict:
    """Account for documentary reuse and map context, not physical observations.

    Snapshot-qualified archival copies can certify preservation of an already
    curated citation. The historic map only provides an *unqualified context*
    for C24#1: it does not certify the modern IBGE coordinate/boundary claim.
    Neither layer may increase the direct source/observable coverage count.
    """
    by_ref = {row["snapshot_ref"]: row for row in rows}
    by_occ = {row["occurrence"]: row for row in rows}
    curated = {(r["snapshot_ref"], r["source_id"]): r
               for r in citations["records"]}
    require(archive.get("schema") == "conde.wayback-citation-links/v1"
            and archive.get("matrix_git_blob_sha1") == pg.MATRIX_BLOB_SHA,
            "archival provenance snapshot mismatch")
    require(archive.get("counts", {}).get("independent_physical_observations_added") == 0
            and archive.get("epistemic_limits", {}).get("no_active_lean_constraint") is True
            and archive["epistemic_limits"].get("no_simulator_parameter_activated") is True,
            "archival capture promoted to physical observation")
    frozen = [n for n in archive["nodes"]
              if n.get("kind") == "FROZEN_MATRIX_CITATION"]
    require(len(frozen) == 2 and len({n["id"] for n in frozen}) == 2
            and archive["counts"].get("matrix_occurrences_linked") == 2,
            "archival citation multiplicity changed")
    expected_ids = {"C197#1", "C198#1"}
    require({n["snapshot_ref"].rsplit(":", 1)[-1] for n in frozen} == expected_ids,
            "archival reference outside verified NASA/NTRS work")
    for n in frozen:
        ref = n["snapshot_ref"]
        require(ref in by_ref and (ref, n["source_id"]) in curated,
                "archival citation without authenticated matrix parent")
        row, cite = by_ref[ref], curated[(ref, n["source_id"])]
        require(n["row_sha256"] == cite["row_sha256"] == row["row_sha256"]
                and n["matrix_line"] == cite["matrix_line"] == row["matrix_line"],
                "archival citation row/line mutated")
        require(n.get("activation") is False and n.get("simulator_value") is None
                and n.get("new_physical_observations") == 0,
                "archival citation falsely activated")
    require(archive["counts"].get("nasa_legacy_distinct_pdf_payloads") == 1
            and archive["epistemic_limits"].get("NASA_NTRS_same_work_not_two_independent_sensors") is True,
            "NASA/NTRS lineage incorrectly multiplied")

    # CGEO-35 links an original 1954/1961 cartographic image to one historical
    # matrix row. No content-addressed matrix citation is carried in this feed;
    # its contextual edge must NOT count as evidence for C24's *modern* GIS.
    require(cartography.get("schema") == "conde.cgeo35-raster-anchor-scientific-bridge/v1"
            and cartography.get("matrix_context") == "C24#1"
            and "C24#1" in by_occ,
            "map contextual occurrence unidentified")
    links = [edge for edge in cartography.get("dependency_graph", [])
             if edge.get("to") == "C24#1"]
    require(len(links) == 1
            and links[0].get("from") == "CGEO-35"
            and links[0].get("relation") == "CARTOGRAPHIC_CONTEXT_VIA_CGEO34_NO_NEW_WITNESS"
            and links[0].get("active_geographic_constraint") is False,
            "map context promoted or relabeled")
    coords = cartography.get("image_coordinate_datum", {})
    require(coords.get("coordinate_system") == "ORIGINAL_JP2_PIXEL_XY_TOP_LEFT"
            and coords.get("geographic_coordinates") is None
            and coords.get("ground_tolerance_m") is None,
            "map pixels falsely georeferenced")
    require(cartography.get("activation") is False
            and cartography.get("new_numeric_orbital_constraints") == 0
            and cartography.get("independent_physical_witnesses_added") == 0
            and cartography.get("physical_domain_effect") == "THETA_UNCHANGED"
            and all(not p.get("activation") and p.get("value") is None
                    and p.get("uncertainty") is None
                    for p in cartography["simulator_latent_parameters"]),
            "map label promoted to observed fall/geodetic constraint")
    return {
        "archival_feed": ARCHIVE.name,
        "archival_citations": len(frozen),
        "archival_distinct_matrix_occurrences": len({n["snapshot_ref"] for n in frozen}),
        "archival_new_matrix_occurrences": 0,
        "archival_new_independent_instrument_observations": 0,
        "cartographic_feed": CARTOGRAPHY.name,
        "unqualified_cartographic_context_ids": ["C24#1"],
        "unqualified_cartographic_context_not_counted_as_direct_support": 1,
        "physical_domain_effect": "THETA_UNCHANGED",
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
    archived = wayback.build(root)
    require((root / ARCHIVE.relative_to(ROOT)).read_bytes() == wayback.encode(archived),
            "Wayback archival feed stale; regenerate original exporter")
    mapped = (root / CARTOGRAPHY.relative_to(ROOT)).read_bytes()
    require(mapped == cgeo35.render(),
            "cartographic feed stale; regenerate original exporter")
    result = audit(rows, original_citations, current_bridges)
    result["supplemental_context_layers"] = audit_context_layers(
        rows, original_citations, archived, json.loads(mapped))
    # A third, independently replayed documentary layer must not inflate the
    # original two-feed source/observable metric.  C212-C214 share ONE work.
    fbis_doc = fbis.build(root)
    require((root / FBIS.relative_to(ROOT)).read_bytes() == fbis.encoded(fbis_doc),
            "FBIS operational source graph stale")
    fbis.audit(fbis_doc, rows)
    fbis_refs = {edge["matrix_occurrence"] for edge in fbis_doc["edges"]}
    previously_linked = {
        item["snapshot_ref"] for item in original_citations["records"]
    } | {
        edge["matrix_occurrence"]
        for section in BRIDGE_SECTIONS for edge in current_bridges[section]
    }
    new_refs = fbis_refs - previously_linked
    require(len(fbis_refs) == 3 and len(new_refs) == 3,
            "FBIS source work unexpectedly duplicated or previously linked")
    result["supplemental_context_layers"]["fbis_operational_history"] = {
        "feed": FBIS.name,
        "source_works": 1,
        "snapshotted_documentary_connections": len(fbis_refs),
        "new_connections_outside_two_feed_scope": len(new_refs),
        "occurrences": sorted(x.rsplit(":", 1)[-1] for x in fbis_refs),
        "new_independent_physical_sensors": 0,
        "physical_domain_effect": "THETA_UNCHANGED",
    }
    result["supplemental_documentary_links_distinct_occurrences"] = len(new_refs)
    result["documented_in_either_two_feeds_or_fbis"] = result["represented_in_either"] + len(new_refs)
    return result


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
