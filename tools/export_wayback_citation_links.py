#!/usr/bin/env python3
"""Join Lontra's verified Wayback pilot to existing citations, without new sensors."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PILOT = "research/archive/wayback_pilot_2026-11-12.json"
DEPENDENCE = "public/data/conde-declared-dependence.json"
BRIDGES = "public/data/conde-scientific-bridges.json"
OUTPUT = "public/data/conde-wayback-citation-links.json"
INPUTS = (PILOT, DEPENDENCE, BRIDGES)
EXPECTED = {
    "WB-NASA-SSR-19631115": (
        "NO_EXACT_CAPTURE_IN_QUERIED_INDEX", "NASA_NORAD_SSR_SINGLE_DOCUMENT",
        "https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf",
        ("C197#1", "C198#1"),
    ),
    "WB-NORAD-1963-H2": (
        "VERIFIED_REPLAY", "NORAD_CONAD_HISTORICAL_SUMMARY_1963",
        "https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/11.pdf",
        ("C241-P8",),
    ),
    "WB-SAO-RU301": (
        "VERIFIED_REPLAY", "SMITHSONIAN_SAO_INSTITUTIONAL_ARCHIVE",
        "https://sirismm.si.edu/EADpdfs/SIA.FARU0301.pdf",
        ("SIA-FARU0301", "BN-RU301-20261112-01"),
    ),
}
EXPECTED_CAPTURE_HASHES = {
    "WB-NORAD-1963-H2": (
        "cb3a9c4dc8bbdae6d2f72711d4dbb50887e576975e7f0e84f2e434c90fcee52b",
        "FPRMCHQXINYIABHFGSOEOIT6ZAZOWVDF",
    ),
    "WB-SAO-RU301": (
        "e3acb2332415332dd14167db8d3d8c3d83ad2ef8897991f50f8b86c166b365cc",
        "HHOYNIA3AQIBS73W2JDXYTUCZESQA2SW",
    ),
}
NASA_SOURCE_IDS = {"C197#1": "NASA_SSR_19631115", "C198#1": "NTRS_19640001198"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("wayback crosswalk: " + message)


def encode(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")


def build(root: Path = ROOT) -> dict:
    raw = {name: (root / name).read_bytes() for name in INPUTS}
    feeds = {name: json.loads(value) for name, value in raw.items()}
    pilot, documentary, science = (feeds[name] for name in INPUTS)
    require(pilot["schema"] == "conde.wayback-capture-pilot/v1"
            and pilot["rules"]["historical_authentication"] is False
            and pilot["rules"]["no_new_orbital_constraint"] is True,
            "pilot epistemic scope")
    require(science["epistemic_limits"]["activated_constraints"] == 0
            and science["epistemic_limits"]["independent_physical_observation_count"] is None,
            "scientific parent promoted observations")
    require(documentary["matrix_git_blob_sha1"] == science["matrix_git_blob_sha1"],
            "mixed matrix snapshots")
    require(any(f["path"] == DEPENDENCE
                and f["sha256"] == hashlib.sha256(raw[DEPENDENCE]).hexdigest()
                for f in science["source_feeds_sha256"]), "scientific parent stale")
    cite = {(x["snapshot_ref"].rsplit(":", 1)[-1], x["source_id"]): x
            for x in documentary["citation_lineages"]}
    cover = {(x["occurrence_ref"].rsplit(":", 1)[-1], x["source_id"]): x
             for x in science["citation_coverage"]}
    require(len(cite) == len(documentary["citation_lineages"])
            and len(cover) == len(science["citation_coverage"]),
            "ambiguous occurrence")
    records = pilot["records"]
    require(len(records) == len(EXPECTED)
            and {r["id"] for r in records} == set(EXPECTED),
            "pilot identifiers missing/duplicated/expanded without review")

    nodes, edges = [], []
    verified = negative = 0
    for r in records:
        rid = r["id"]
        expected_status, family, original, refs = EXPECTED[rid]
        require(r["status"] == expected_status
                and r["source_family"] == family
                and r["original_url"] == original
                and tuple(r["source_refs"]) == refs
                and len(set(refs)) == len(refs), "record identity: " + rid)
        require(urlsplit(original).scheme == "https"
                and r["cdx_lookup"]["http_status"] == 200,
                "original URL/CDX lookup: " + rid)
        nodes.append({
            "id": rid, "kind": "DOCUMENTARY_SOURCE", "original_url": original,
            "source_family": family, "source_refs": list(refs),
            "publication_date": r["publication_date"],
            "capture_status": r["status"], "new_physical_observations": 0,
        })
        if expected_status == "VERIFIED_REPLAY":
            verified += 1
            cd, replay = r["cdx_record"], r["replay"]
            timestamp = cd["timestamp"]
            when = datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            require(when.isoformat().replace("+00:00", "Z") == r["capture_utc"],
                    "capture date mismatch: " + rid)
            archive = "https://web.archive.org/web/" + timestamp + "id_/" + original
            require(r["archived_url"] == archive
                    and cd["original"] == original
                    and cd["statuscode"] == "200"
                    and cd["mimetype"] == "application/pdf"
                    and re.fullmatch(r"[A-Z2-7]{32}", cd["digest"]) is not None
                    and replay["sha1_base32"] == cd["digest"]
                    and (replay["sha256"], cd["digest"]) == EXPECTED_CAPTURE_HASHES[rid]
                    and re.fullmatch(r"[0-9a-f]{64}", replay["sha256"]) is not None
                    and replay["http_status"] == 200
                    and replay["content_type"] == "application/pdf"
                    and replay["bytes"] > 0
                    and replay["pdf_magic"] is True and replay["pdf_eof"] is True,
                    "archive bytes/CDX identity: " + rid)
            capture_id = rid + ":CAPTURE:" + timestamp
            nodes.append({
                "id": capture_id, "kind": "VERIFIED_ARCHIVAL_COPY",
                "archived_url": archive, "capture_utc": r["capture_utc"],
                "mime": cd["mimetype"], "http_status": 200,
                "cdx_digest_base32_sha1": cd["digest"],
                "retrieved_bytes_sha256": replay["sha256"],
                "retrieved_bytes_length": replay["bytes"],
                "cdx_record_length_not_pdf_bytes": cd["length"],
                "new_physical_observations": 0,
            })
            edges.append({"from": capture_id, "to": rid,
                          "kind": "PRESERVED_COPY_NOT_SECOND_OBSERVATION"})
        else:
            negative += 1
            require(r["capture_utc"] is None and r["archived_url"] is None
                    and r["cdx_record"] is None and r["replay"] is None
                    and r["cdx_lookup"]["exact_results"] == 0
                    and r["availability_lookup"]["archived_snapshots"] == {},
                    "negative lookup must not have an implied capture: " + rid)
            negative_id = rid + ":EXACT_URL_LOOKUP"
            nodes.append({"id": negative_id, "kind": "NEGATIVE_EXACT_URL_LOOKUP",
                          "query_url": original, "capture_utc": None,
                          "scope": "EXACT_URL_ONLY_NOT_ABSENCE_OF_WORK"})
            edges.append({"from": negative_id, "to": rid,
                          "kind": "NO_EXACT_CAPTURE_IN_QUERIED_INDEX"})

        for ref in refs:
            node_id = rid + ":REF:" + ref
            if ref in NASA_SOURCE_IDS:
                source_id = NASA_SOURCE_IDS[ref]
                c, b = cite[(ref, source_id)], cover[(ref, source_id)]
                require(c["source_id"] == b["source_id"] == source_id
                        and c["snapshot_ref"] == b["occurrence_ref"]
                        and c["matrix_line"] == b["matrix_line"]
                        and c["row_sha256"] == b["row_sha256"]
                        and c["family_id"] == b["source_family"] == "NORAD_NASA_TRACKING"
                        and b["activation"] is False
                        and b["hypothesis_link"] == "H_528_REENTRY_EVENT_TIME_UNKNOWN"
                        and b["simulator_parameter"] == "reentry_terminal_timestamp_528",
                        "NASA citation/Lean/simulation mismatch: " + ref)
                nodes.append({
                    "id": node_id, "kind": "FROZEN_MATRIX_CITATION",
                    "source_id": source_id, "snapshot_ref": c["snapshot_ref"],
                    "matrix_line": c["matrix_line"], "row_sha256": c["row_sha256"],
                    "hypothesis": b["hypothesis_link"],
                    "lean_status": b["lean_status"],
                    "simulator_parameter": b["simulator_parameter"],
                    "simulator_value": None, "activation": False,
                    "new_physical_observations": 0,
                })
                edges.append({"from": rid, "to": node_id,
                              "kind": "DOC_SOURCE_TO_SNAPSHOT_CITATION"})
            else:
                require(rid != "WB-NASA-SSR-19631115",
                        "unmapped NASA occurrence")
                nodes.append({
                    "id": node_id, "kind": "SUPPLEMENTARY_SOURCE_REF_NOT_MATRIX",
                    "source_ref": ref, "matrix_snapshot_ref": None,
                    "lean_status": "NOT_ASSESSED_NO_OBJECT_528_MEASUREMENT",
                    "simulator_parameter": None, "simulator_value": None,
                    "activation": False,
                })
                edges.append({"from": rid, "to": node_id,
                              "kind": "DOCUMENTARY_CONTEXT_ONLY"})
    require(verified == 2 and negative == 1, "pilot status census")
    # NASA and its NTRS catalogue cite one SSR work; neither is a new sensor.
    require(cite[("C198#1", "NTRS_19640001198")]["declared_upstream_paths"][0]["upstream_source_id"]
            == NASA_SOURCE_IDS["C197#1"], "NTRS/NASA lineage broken")
    edges.append({
        "from": "WB-NASA-SSR-19631115:REF:C198#1",
        "to": "WB-NASA-SSR-19631115:REF:C197#1",
        "kind": "NTRS_CATALOG_OF_SAME_NASA_WORK_NOT_INDEPENDENT",
    })
    return {
        "schema": "conde.wayback-citation-links/v1",
        "source_file_sha256": {name: hashlib.sha256(value).hexdigest()
                               for name, value in raw.items()},
        "matrix_git_blob_sha1": documentary["matrix_git_blob_sha1"],
        "nodes": nodes, "edges": edges,
        "counts": {
            "documentary_works": len(records), "verified_archived_copies": verified,
            "negative_exact_url_lookups": negative,
            "matrix_occurrences_linked": 2, "supplementary_refs_not_matrix": 3,
            "independent_physical_observations_added": 0,
        },
        "epistemic_limits": {
            "archived_bytes_do_not_authenticate_1963_measurement": True,
            "NASA_NTRS_same_work_not_two_independent_sensors": True,
            "CDX_digest_is_base32_sha1_not_sha256": True,
            "negative_exact_lookup_does_not_prove_absence_at_other_urls": True,
            "no_active_lean_constraint": True, "no_simulator_parameter_activated": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write-site", action="store_true")
    group.add_argument("--check-site", action="store_true")
    opts = parser.parse_args()
    output = encode(build())
    require(len(output) <= 20_000, "output exceeds 20,000 bytes")
    target = ROOT / OUTPUT
    if opts.write_site:
        target.write_bytes(output)
    else:
        require(target.read_bytes() == output, "stale website graph")
    print("WAYBACK_CITATION_GRAPH_OK", len(output))


if __name__ == "__main__":
    main()
